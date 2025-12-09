# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_dynamic_libs

block_cipher = None

# 收集 PyQt6 的所有数据、二进制文件和隐藏导入
datas, binaries, hiddenimports = collect_all('PyQt6')

# 添加资源文件
import sys
spec_dir = os.path.dirname(os.path.abspath(SPEC))
resources_path = os.path.join(spec_dir, 'resources')
if os.path.exists(resources_path):
    for root, dirs, files in os.walk(resources_path):
        for file in files:
            if file != 'README.md':
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, resources_path)
                datas.append((src_path, os.path.join('resources', os.path.dirname(rel_path)) if os.path.dirname(rel_path) else 'resources'))

# 确保包含所有必要的 DLL
pyqt6_binaries = collect_dynamic_libs('PyQt6')
binaries += pyqt6_binaries

# 添加额外的隐藏导入
hiddenimports += [
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.QtWebEngineWidgets',
    'PyQt6.QtWebEngineCore',
    'requests',
    # 标准库模块
    'pkgutil',
    'importlib',
    'importlib.util',
    'importlib.metadata',
]

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=binaries,
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='StableDiffusionWebUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icon.ico' if os.path.exists('resources/icon.ico') else None,
)
