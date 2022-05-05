# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

switcher_a = Analysis(
    ['switcher.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
config_editor_a = Analysis(
    ['config_editor.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

switcher_a.datas += [('config.ini', '.\\config.ini', 'DATA')]
config_editor_a.datas += [('config.ini', '.\\config.ini', 'DATA')]

switcher_pyz = PYZ(switcher_a.pure, switcher_a.zipped_data, cipher=block_cipher)
config_editor_pyz = PYZ(config_editor_a.pure, config_editor_a.zipped_data, cipher=block_cipher)

switcher_exe = EXE(
    switcher_pyz,
    switcher_a.scripts,
    switcher_a.binaries,
    switcher_a.zipfiles,
    switcher_a.datas,
    [],
    name='switcher',
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
config_editor_exe = EXE(
    config_editor_pyz,
    config_editor_a.scripts,
    config_editor_a.binaries,
    config_editor_a.zipfiles,
    config_editor_a.datas,
    [],
    name='config_editor',
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
