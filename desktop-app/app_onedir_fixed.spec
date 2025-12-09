# -*- mode: python ; coding: utf-8 -*-
# 完善的目录模式打包配置 - 解决 DLL 加载问题

import os
import sys
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_dynamic_libs

block_cipher = None

# 收集 PyQt6 的所有数据、二进制文件和隐藏导入
datas, binaries, hiddenimports = collect_all('PyQt6')

# 添加 PyQt6 插件目录（非常重要！）
try:
    import PyQt6
    pyqt6_path = os.path.dirname(PyQt6.__file__)
    
    # 添加 Qt6/bin 目录下的所有 DLL
    qt6_bin_path = os.path.join(pyqt6_path, 'Qt6', 'bin')
    if os.path.exists(qt6_bin_path):
        for dll_file in os.listdir(qt6_bin_path):
            if dll_file.endswith('.dll'):
                dll_full_path = os.path.join(qt6_bin_path, dll_file)
                binaries.append((dll_full_path, '.'))
    
    # 添加 Qt6/plugins 目录（关键！）
    qt6_plugins_path = os.path.join(pyqt6_path, 'Qt6', 'plugins')
    if os.path.exists(qt6_plugins_path):
        for root, dirs, files in os.walk(qt6_plugins_path):
            for file in files:
                if file.endswith(('.dll', '.so')):
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(root, qt6_plugins_path)
                    dest_path = os.path.join('PyQt6', 'Qt6', 'plugins', rel_path) if rel_path != '.' else os.path.join('PyQt6', 'Qt6', 'plugins')
                    datas.append((src_path, dest_path))
    
    # 添加 Qt6/qml 目录
    qt6_qml_path = os.path.join(pyqt6_path, 'Qt6', 'qml')
    if os.path.exists(qt6_qml_path):
        datas.append((qt6_qml_path, 'PyQt6/Qt6/qml'))
        
except Exception as e:
    print(f"警告: 无法添加 PyQt6 资源: {e}")

# 确保包含所有必要的 DLL
pyqt6_binaries = collect_dynamic_libs('PyQt6')
binaries += pyqt6_binaries

# 添加资源文件
spec_dir = os.path.dirname(os.path.abspath(SPEC))
resources_path = os.path.join(spec_dir, 'resources')
if os.path.exists(resources_path):
    for root, dirs, files in os.walk(resources_path):
        for file in files:
            if file != 'README.md':
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, resources_path)
                datas.append((src_path, os.path.join('resources', os.path.dirname(rel_path)) if os.path.dirname(rel_path) else 'resources'))

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
    runtime_hooks=['rthook_pyqt6_fix.py'],
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
    exclude_binaries=True,  # 不打包二进制文件到 exe
    name='StableDiffusionWebUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=True,  # 临时启用控制台以查看错误
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

