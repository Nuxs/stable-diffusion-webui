#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查系统依赖和 PyQt6 安装
"""

import sys
import os

def check_vc_redist():
    """检查 Visual C++ Redistributable"""
    vc_redist_paths = [
        r"C:\Windows\System32\vcruntime140.dll",
        r"C:\Windows\System32\msvcp140.dll",
    ]
    
    print("检查 Visual C++ Redistributable:")
    for path in vc_redist_paths:
        exists = os.path.exists(path)
        print(f"  {os.path.basename(path)}: {'✓ 已安装' if exists else '✗ 未找到'}")
    print()

def check_pyqt6():
    """检查 PyQt6 安装"""
    print("检查 PyQt6 安装:")
    try:
        import PyQt6
        pyqt6_path = os.path.dirname(PyQt6.__file__)
        print(f"  PyQt6 路径: {pyqt6_path}")
        
        # 检查关键文件
        qt6_bin = os.path.join(pyqt6_path, 'Qt6', 'bin')
        qt6_core_dll = os.path.join(qt6_bin, 'Qt6Core.dll')
        qt6_widgets_dll = os.path.join(qt6_bin, 'Qt6Widgets.dll')
        
        print(f"  Qt6/bin 目录: {'✓ 存在' if os.path.exists(qt6_bin) else '✗ 不存在'}")
        print(f"  Qt6Core.dll: {'✓ 存在' if os.path.exists(qt6_core_dll) else '✗ 不存在'}")
        print(f"  Qt6Widgets.dll: {'✓ 存在' if os.path.exists(qt6_widgets_dll) else '✗ 不存在'}")
        
        # 尝试导入
        try:
            from PyQt6.QtCore import Qt
            print("  PyQt6.QtCore: ✓ 可以导入")
        except Exception as e:
            print(f"  PyQt6.QtCore: ✗ 导入失败 - {e}")
            
        try:
            from PyQt6.QtWidgets import QApplication
            print("  PyQt6.QtWidgets: ✓ 可以导入")
        except Exception as e:
            print(f"  PyQt6.QtWidgets: ✗ 导入失败 - {e}")
            
    except ImportError as e:
        print(f"  ✗ PyQt6 未安装: {e}")
    print()

def check_python():
    """检查 Python 环境"""
    print("检查 Python 环境:")
    print(f"  Python 版本: {sys.version}")
    print(f"  Python 路径: {sys.executable}")
    print(f"  架构: {sys.platform}")
    print()

def main():
    print("=" * 60)
    print("系统依赖检查")
    print("=" * 60)
    print()
    
    check_python()
    check_vc_redist()
    check_pyqt6()
    
    print("=" * 60)
    print("建议:")
    print("1. 如果 Visual C++ Redistributable 未安装，请下载安装:")
    print("   https://aka.ms/vs/17/release/vc_redist.x64.exe")
    print("2. 如果 PyQt6 无法导入，尝试重新安装:")
    print("   pip uninstall PyQt6 PyQt6-WebEngine")
    print("   pip install PyQt6 PyQt6-WebEngine")
    print("=" * 60)

if __name__ == "__main__":
    main()

