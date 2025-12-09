# -*- mode: python ; coding: utf-8 -*-
# Tkinter 版本打包配置

import os

block_cipher = None

# 添加资源文件
datas = []
import sys
spec_dir = os.path.dirname(os.path.abspath(SPEC))
resources_path = os.path.join(spec_dir, 'resources')
if os.path.exists(resources_path):
    for root, dirs, files in os.walk(resources_path):
        for file in files:
            if file != "README.md":
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, resources_path)
                dest_path = os.path.join("resources", os.path.dirname(rel_path)) if os.path.dirname(rel_path) != "." else "resources"
                datas.append((src_path, dest_path))

# 隐藏导入
hiddenimports = [
    "tkinter",
    "tkinter.ttk",
    "tkinter.messagebox",
    "tkinter.scrolledtext",
    "requests",
    "threading",
    "subprocess",
    "socket",
    "webbrowser",
    "logging",
    "json",
    "pathlib",
    "pkgutil",
    "importlib",
]

a = Analysis(
    ['src/main_tkinter.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='StableDiffusionWebUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False,  # 不显示控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icon.ico' if os.path.exists('resources/icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='StableDiffusionWebUI',
)

