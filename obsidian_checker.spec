# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['obsidian_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include any additional files your app needs
        ('STANDALONE_README.md', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        # AI dependencies (optional)
        'sentence_transformers',
        'sklearn',
        'numpy',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ObsidianChecker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # This creates a windowed app, not console
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # You can add an icon file here if you have one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ObsidianChecker',
)

app = BUNDLE(
    coll,
    name='Obsidian Checker.app',
    icon=None,  # You can add an icon file here if you have one
    bundle_identifier='com.ericaustin.obsidian-checker',
    version='1.0.0',
    info_plist={
        'CFBundleName': 'Obsidian Checker',
        'CFBundleDisplayName': 'Obsidian Checker',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': 'OBCH',
        'CFBundleExecutable': 'ObsidianChecker',
        'CFBundleIconFile': '',  # Icon filename (without extension)
        'NSHighResolutionCapable': True,
        'NSPrincipalClass': 'NSApplication',
        'NSRequiresAquaSystemAppearance': False,
        'LSMinimumSystemVersion': '10.13.0',
        'NSHumanReadableCopyright': 'Copyright © 2025 Eric Austin. All rights reserved.',
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'Obsidian Vault',
                'CFBundleTypeRole': 'Viewer',
                'LSItemContentTypes': ['public.folder'],
                'LSHandlerRank': 'None'
            }
        ]
    },
)