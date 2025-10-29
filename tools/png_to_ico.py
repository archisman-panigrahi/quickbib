#!/usr/bin/env python3
"""Small helper to convert a PNG to a multi-size ICO using Pillow.

Usage:
    python tools/png_to_ico.py <input-png> <output-ico>

This is used by CI to create a Windows .ico from an existing PNG in the repo.
"""
import sys
from pathlib import Path


def png_to_ico(input_path: Path, output_path: Path):
    try:
        from PIL import Image
    except Exception as exc:
        raise SystemExit("Pillow is required to convert PNG to ICO. Install with `pip install pillow`.") from exc

    im = Image.open(input_path)
    # Ensure RGBA
    if im.mode != 'RGBA':
        im = im.convert('RGBA')

    # ICO should include several sizes; Pillow will handle the conversion when saving multiple sizes.
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    # Resize copies for each size
    icons = [im.resize(s, Image.LANCZOS) for s in sizes]

    # Save the first image with the different sizes as an .ico file
    icons[0].save(output_path, format='ICO', sizes=sizes)


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        raise SystemExit(2)
    input_path = Path(argv[1])
    output_path = Path(argv[2])
    if not input_path.exists():
        raise SystemExit(f"Input PNG not found: {input_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    png_to_ico(input_path, output_path)
    print(f"Wrote ICO: {output_path}")


if __name__ == '__main__':
    main(sys.argv)
