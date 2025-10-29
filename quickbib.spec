# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for QuickBib.

This spec collects PyQt6 resources and the project's `assets` directory. It builds
an --onedir (COLLECT) output named `QuickBib` which the NSIS script packages.

If you want an exe-only single-file build set `onefile=True` and adjust the NSIS script.
"""
import sys
from PyInstaller.utils.hooks import collect_all, Tree

block_cipher = None

# Collect PyQt6 related datas/binaries/hiddenimports handled by PyInstaller's helpers
pyqt_datas, pyqt_binaries, pyqt_hiddenimports = collect_all('PyQt6')

# Include application assets (icons, screenshots, etc.)
datas = pyqt_datas + Tree('assets', prefix='assets')
binaries = pyqt_binaries
hiddenimports = pyqt_hiddenimports + ['doi2bib3']

a = Analysis(
    ['quickbib_launcher.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='QuickBib',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    # Use the provided Windows .ico file from the repo's assets
    icon='assets/icon/64x64/io.github.archisman_panigrahi.quickbib.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='QuickBib',
)
