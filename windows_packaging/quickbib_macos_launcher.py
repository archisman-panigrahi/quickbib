#!/usr/bin/env python3
"""Launcher script used for building a macOS .app with PyInstaller/py2app.

This mirrors the Windows launcher but is kept separate to allow mac-specific
build-time tweaks (paths, icons, etc.). It ensures the repository root is on
sys.path so the `quickbib` package is importable when the launcher is executed
from the `windows_packaging` directory.
"""
import sys
import os

# Ensure the repository root is on sys.path so the `quickbib` package located at
# ../quickbib is importable when this launcher is executed from the
# `windows_packaging` directory (e.g. during development or when run directly).
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from quickbib.quickbib import main


def _entry():
    # call the package entrypoint and exit with return code
    sys.exit(main(sys.argv))


if __name__ == "__main__":
    _entry()
