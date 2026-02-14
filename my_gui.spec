# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules

rich_hiddenimports = collect_submodules('rich._unicode_data')

a = Analysis(
    ['my_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('book_of_mormon.txt', '.'),
        ('titles_of_christ.txt', '.'),
        ('chosen.titles.txt', '.'),
        ('book_of_mormon.ico', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=rich_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='my_gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['book_of_mormon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='my_gui',
)
