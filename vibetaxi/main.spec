# -*- mode: python ; coding: utf-8 -*-
import sys

# Seleccionar icono según el sistema
app_icon = 'assets/graphics/icon.icns' if sys.platform == 'darwin' else 'assets/graphics/icon.ico'

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets')],
    hiddenimports=[],
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
    name='VibeTaxi',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=app_icon,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)

if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='VibeTaxi.app',
        icon='assets/graphics/icon.icns',
        bundle_identifier='com.vibetaxi.game',
    )