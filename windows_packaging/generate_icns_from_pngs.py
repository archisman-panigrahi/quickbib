#!/usr/bin/env python3
"""
Generate a minimal .icns file from PNG assets without requiring macOS tools.

This script looks for PNGs in `assets/icon/<size>/` (e.g. 16x16, 32x32,
64x64, 128x128) and packs them into a simple ICNS container using PNG data
entries. It's intentionally conservative: it writes entries for these sizes
using common icns type codes that macOS recognizes when PNG-formatted data is
embedded.

Limitations:
- This produces a basic .icns suitable for development and packaging. It may
  not include all retina variants and won't replace a properly produced
  icns created by `iconutil` on macOS for final release.

Output: `assets/icon/QuickBib.icns`
"""
from __future__ import annotations

import struct
from pathlib import Path
from typing import Dict
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ICONS_DIR = ROOT / "assets" / "icon"
OUT_ICNS = ICONS_DIR / "QuickBib.icns"

# Map folder names (or sizes) to icns type codes. This is a pragmatic mapping
# that covers common icon sizes. The type codes expect PNG data for modern
# macOS systems.
MAPPING: Dict[str, str] = {
    "16x16": "icp4",   # 16x16
    "32x32": "icp5",   # 32x32
    "64x64": "icp6",   # 64x64
    "128x128": "ic07", # 128x128
    "192x192": "ic13", # 192x192 (best-effort mapping)
}


def find_svg() -> Path | None:
    """Look for an SVG in the scalable folder and return the first match.

    Returns the Path to the svg or None if not found.
    """
    scalable = ICONS_DIR / "scalable"
    if not scalable.exists() or not scalable.is_dir():
        return None

    for p in scalable.iterdir():
        if p.suffix.lower() == ".svg":
            return p
    return None


def inkscape_available() -> bool:
    """Return True if an 'inkscape' executable is available on PATH."""
    return shutil.which("inkscape") is not None


def _try_run(cmd: list[str]) -> bool:
    try:
        res = subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return res.returncode == 0
    except Exception:
        return False


def render_svg_to_pngs(svg: Path) -> None:
    """Render the provided SVG into PNG files for the sizes defined in MAPPING.

    This will create/overwrite files at assets/icon/<size>/<svgname>.png.
    The function attempts to use the modern Inkscape CLI first and falls back
    to the legacy CLI form when needed.
    """
    if not inkscape_available():
        raise RuntimeError("Inkscape not found on PATH. Install Inkscape to render SVG to PNG.")

    svg_name = svg.name
    # for each mapping key like '16x16', render that pixel size
    for key in MAPPING.keys():
        try:
            size = int(key.split("x")[0])
        except Exception:
            print(f"Skipping invalid size key: {key}")
            continue

        out_dir = ICONS_DIR / key
        out_dir.mkdir(parents=True, exist_ok=True)
        out_png = out_dir / (svg_name.rsplit('.', 1)[0] + ".png")

        # Try modern inkscape CLI (1.0+): `inkscape input.svg --export-type=png --export-filename=out.png --export-width=Wx --export-height=Hx`
        modern_cmd = [
            "inkscape",
            str(svg),
            "--export-type=png",
            f"--export-filename={str(out_png)}",
            f"--export-width={size}",
            f"--export-height={size}",
        ]

        # Legacy CLI: `inkscape -z -e out.png -w W -h H input.svg`
        legacy_cmd = [
            "inkscape",
            "-z",
            "-e",
            str(out_png),
            "-w",
            str(size),
            "-h",
            str(size),
            str(svg),
        ]

        print(f"Rendering SVG {svg} -> {out_png} at {size}x{size}")
        ok = _try_run(modern_cmd)
        if not ok:
            ok = _try_run(legacy_cmd)

        if not ok:
            # If rendering failed, surface a helpful error and abort.
            raise RuntimeError(
                f"Failed to render SVG to PNG for size {size}. Tried inkscape commands."
            )



def find_pngs() -> Dict[str, Path]:
    found = {}
    if not ICONS_DIR.exists():
        return found

    for key, code in MAPPING.items():
        d = ICONS_DIR / key
        if d.exists() and d.is_dir():
            # pick the first png file we find
            for p in d.iterdir():
                if p.suffix.lower() == ".png":
                    found[code] = p
                    break
    return found


def build_icns(entries: Dict[str, bytes]) -> bytes:
    # ICNS header 'icns' + total length (8 + sum(entry lengths))
    parts = []
    total = 8
    for typ, data in entries.items():
        # Each entry: 4-byte type, 4-byte length, then data
        entry_len = 8 + len(data)
        parts.append((typ.encode("ascii"), entry_len, data))
        total += entry_len

    out = bytearray()
    out += b"icns"
    out += struct.pack(">I", total)
    for typ, entry_len, data in parts:
        out += typ
        out += struct.pack(">I", entry_len)
        out += data

    return bytes(out)


def main():
    # If an SVG exists, try to render PNGs from it first. If inkscape is not
    # available, we fall back to existing PNGs if present.
    svg = find_svg()
    if svg is not None:
        try:
            print(f"Found SVG: {svg}. Attempting to render PNGs using Inkscape...")
            render_svg_to_pngs(svg)
        except RuntimeError as exc:
            print("SVG rendering failed:", exc)
            print("Proceeding to look for existing PNGs (if any)...")

    pngs = find_pngs()
    if not pngs:
        print("No PNG icon sources found in assets/icon/* folders and no SVG rendering available. Nothing to do.")
        return

    entries = {}
    for typ, p in pngs.items():
        print(f"Adding {p} as icns type {typ}")
        entries[typ] = p.read_bytes()

    icns_data = build_icns(entries)
    ICONS_DIR.mkdir(parents=True, exist_ok=True)
    OUT_ICNS.write_bytes(icns_data)
    print("Wrote:", OUT_ICNS)


if __name__ == "__main__":
    main()
