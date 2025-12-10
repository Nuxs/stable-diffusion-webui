#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt6 环境修复脚本
修复 PyQt6 在 Windows 上的 DLL 加载问题
"""

import sys
import os
import subprocess
from pathlib import Path


def fix_pyqt6_dll():
    """修复 PyQt6 DLL 加载问题"""
    print("=" * 60)
    print("PyQt6 环境修复工具")
    print("=" * 60)
    
    # 1. 检查 Python 环境
    print(f"\nPython 版本: {sys.version}")
    print(f"Python 路径: {sys.executable}")
    
    # 2. 检查 PyQt6 安装
    try:
        import PyQt6
        pyqt6_path = Path(PyQt6.__file__).parent
        print(f"\n[OK] PyQt6 已安装: {pyqt6_path}")
    except ImportError:
        print("\n[X] PyQt6 未安装")
        print("正在安装 PyQt6...")
        subprocess.run([sys.executable, "-m", "pip", "install", "PyQt6>=6.6.0", "PyQt6-WebEngine>=6.6.0"])
        return
    
    # 3. 检查 Qt6 DLL 目录
    qt6_bin = pyqt6_path / "Qt6" / "bin"
    if qt6_bin.exists():
        print(f"[OK] Qt6 DLL 目录存在: {qt6_bin}")
        
        # 列出关键 DLL
        key_dlls = ["Qt6Core.dll", "Qt6Gui.dll", "Qt6Widgets.dll"]
        missing_dlls = []
        
        for dll in key_dlls:
            dll_path = qt6_bin / dll
            if dll_path.exists():
                print(f"  [OK] {dll}")
            else:
                print(f"  [X] {dll} 缺失")
                missing_dlls.append(dll)
        
        if missing_dlls:
            print(f"\n[!] 缺少 {len(missing_dlls)} 个关键 DLL")
            print("尝试重新安装 PyQt6...")
            subprocess.run([sys.executable, "-m", "pip", "install", "--force-reinstall", "PyQt6>=6.6.0"])
    else:
        print(f"[X] Qt6 DLL 目录不存在: {qt6_bin}")
        print("尝试重新安装 PyQt6...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--force-reinstall", "PyQt6>=6.6.0"])
    
    # 4. 测试导入
    print("\n测试 PyQt6 导入...")
    try:
        # 添加 DLL 路径到环境变量
        if qt6_bin.exists():
            os.environ['PATH'] = str(qt6_bin) + os.pathsep + os.environ.get('PATH', '')
            
            # 使用 ctypes 添加 DLL 目录
            try:
                import ctypes
                kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
                kernel32.AddDllDirectory(str(qt6_bin))
            except Exception as e:
                print(f"  警告: 无法使用 AddDllDirectory: {e}")
        
        from PyQt6.QtCore import QT_VERSION_STR
        from PyQt6.QtWidgets import QApplication
        
        print(f"[OK] PyQt6 导入成功")
        print(f"  Qt 版本: {QT_VERSION_STR}")
        
        # 尝试创建应用实例
        app = QApplication([])
        print(f"[OK] QApplication 创建成功")
        
        print("\n" + "=" * 60)
        print("修复完成！PyQt6 环境正常")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n[X] PyQt6 导入失败: {e}")
        print("\n建议:")
        print("1. 重新安装 PyQt6:")
        print(f"   {sys.executable} -m pip uninstall PyQt6 PyQt6-Qt6 PyQt6-sip -y")
        print(f"   {sys.executable} -m pip install PyQt6>=6.6.0 PyQt6-WebEngine>=6.6.0")
        print("2. 检查是否安装了 Visual C++ Redistributable 2015-2022")
        print("   下载地址: https://aka.ms/vs/17/release/vc_redist.x64.exe")
        return False


if __name__ == "__main__":
    success = fix_pyqt6_dll()
    sys.exit(0 if success else 1)

