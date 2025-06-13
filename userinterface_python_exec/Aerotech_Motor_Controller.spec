# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['Aerotech_Motor_Controller.py'],
    pathex=[],
    binaries=[('C:\\Program Files\\Aerotech\\Automation1-MDK\\APIs\\Python\\automation1\\build\\lib\\automation1\\references\\Automation1C64.dll', '.'), ('C:\\Program Files\\Aerotech\\Automation1-MDK\\APIs\\Python\\automation1\\build\\lib\\automation1\\references\\Automation1Compiler64.dll', '.')],
    datas=[],
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
    a.binaries,
    a.datas,
    [],
    name='Aerotech_Motor_Controller',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
