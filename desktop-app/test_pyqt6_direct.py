#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试 PyQt6 导入
"""

import sys
import os

print("=" * 60)
print("PyQt6 导入测试")
print("=" * 60)
print()

# 方法1: 设置 PATH
pyqt6_bin = r'C:\Users\25292\AppData\Roaming\Python\Python312\site-packages\PyQt6\Qt6\bin'
if os.path.exists(pyqt6_bin):
    os.environ['PATH'] = os.path.abspath(pyqt6_bin) + os.pathsep + os.environ.get('PATH', '')
    print(f"✓ 已设置 PATH: {pyqt6_bin}")

# 方法2: 使用 os.add_dll_directory
try:
    os.add_dll_directory(pyqt6_bin)
    print(f"✓ 已使用 os.add_dll_directory: {pyqt6_bin}")
except Exception as e:
    print(f"✗ os.add_dll_directory 失败: {e}")

# 方法3: 使用 AddDllDirectory
try:
    import ctypes
    from ctypes import wintypes
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    AddDllDirectory = kernel32.AddDllDirectory
    AddDllDirectory.argtypes = [wintypes.LPCWSTR]
    AddDllDirectory.restype = wintypes.HANDLE
    handle = AddDllDirectory(os.path.abspath(pyqt6_bin))
    if handle:
        print(f"✓ 已使用 AddDllDirectory: {pyqt6_bin}")
    else:
        error_code = ctypes.get_last_error()
        print(f"✗ AddDllDirectory 返回 NULL, 错误码: {error_code}")
except Exception as e:
    print(f"✗ AddDllDirectory 失败: {e}")

print()
print("尝试导入 PyQt6...")
print()

try:
    from PyQt6.QtCore import Qt
    print("✓ PyQt6.QtCore 导入成功")
except Exception as e:
    print(f"✗ PyQt6.QtCore 导入失败: {e}")

try:
    from PyQt6.QtWidgets import QApplication
    print("✓ PyQt6.QtWidgets 导入成功")
    print()
    print("=" * 60)
    print("✓ 测试通过！PyQt6 可以正常使用")
    print("=" * 60)
except Exception as e:
    print(f"✗ PyQt6.QtWidgets 导入失败: {e}")
    print()
    print("=" * 60)
    print("✗ 测试失败")
    print("=" * 60)
    print()
    print("可能的原因:")
    print("1. 缺少 Visual C++ Redistributable（需要重启）")
    print("2. Qt6 DLL 依赖的其他系统 DLL 缺失")
    print("3. Python 和 PyQt6 架构不匹配（32位 vs 64位）")
    print("4. 系统环境问题")

