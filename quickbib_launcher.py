#!/usr/bin/env python3
"""Launcher script used by PyInstaller for building the Windows executable.

This imports the package entrypoint and calls main(argv).
"""
import sys

from quickbib.quickbib import main


def _entry():
    sys.exit(main(sys.argv))


if __name__ == "__main__":
    _entry()
