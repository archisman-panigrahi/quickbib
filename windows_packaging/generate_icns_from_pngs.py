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
}


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
    pngs = find_pngs()
    if not pngs:
        print("No PNG icon sources found in assets/icon/* folders. Nothing to do.")
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
