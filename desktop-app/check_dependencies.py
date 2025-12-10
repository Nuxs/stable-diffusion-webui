#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖项检查脚本
检查所有必需的 Python 包是否已安装
"""

import sys
import subprocess
from pathlib import Path


def check_package(package_name: str, version_spec: str = None) -> tuple[bool, str]:
    """
    检查包是否已安装
    
    Args:
        package_name: 包名
        version_spec: 版本要求（可选）
    
    Returns:
        tuple: (是否已安装, 当前版本)
    """
    try:
        # 尝试导入包
        if package_name == "PyQt6":
            from PyQt6.QtCore import QT_VERSION_STR
            version = QT_VERSION_STR
        elif package_name == "PyQt6-WebEngine":
            try:
                from PyQt6 import QtWebEngineWidgets
                version = "已安装"
            except ImportError:
                # 尝试备用导入
                import PyQt6_WebEngine
                version = getattr(PyQt6_WebEngine, '__version__', '已安装')
        elif package_name == "requests":
            import requests
            version = requests.__version__
        elif package_name == "pyinstaller":
            import PyInstaller
            version = PyInstaller.__version__
        elif package_name == "py7zr":
            import py7zr
            version = py7zr.__version__
        else:
            # 通用方法
            module = __import__(package_name.replace("-", "_"))
            version = getattr(module, '__version__', '未知')
        
        return True, version
    except (ImportError, AttributeError):
        return False, None


def main():
    """主函数"""
    print("=" * 60)
    print("依赖项检查")
    print("=" * 60)
    
    # 必需的包
    required_packages = [
        ("PyQt6", "6.6.1"),
        ("requests", "2.31.0+"),
        ("pyinstaller", "6.0.0+"),
    ]
    
    # 可选的包
    optional_packages = [
        ("PyQt6-WebEngine", "6.6.0"),
        ("py7zr", "0.20.0+"),
    ]
    
    print("\n必需的包:")
    required_ok = True
    for package_name, version_spec in required_packages:
        installed, version = check_package(package_name, version_spec)
        if installed:
            print(f"  [OK] {package_name}: {version}")
        else:
            print(f"  [X] {package_name}: 未安装")
            required_ok = False
    
    print("\n可选的包:")
    for package_name, version_spec in optional_packages:
        installed, version = check_package(package_name, version_spec)
        if installed:
            print(f"  [OK] {package_name}: {version}")
        else:
            print(f"  [!] {package_name}: 未安装（可选）")
    
    # 检查系统依赖
    print("\n系统依赖:")
    
    # 检查 VC++ Redistributable
    try:
        import winreg
        key_paths = [
            r"SOFTWARE\\Microsoft\\VisualStudio\\14.0\\VC\\Runtimes\\x64",
            r"SOFTWARE\\WOW6432Node\\Microsoft\\VisualStudio\\14.0\\VC\\Runtimes\\x64",
        ]
        vcredist_found = False
        for key_path in key_paths:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                vcredist_found = True
                winreg.CloseKey(key)
                break
            except FileNotFoundError:
                continue
        
        if vcredist_found:
            print("  [OK] Visual C++ Redistributable: 已安装")
        else:
            print("  [X] Visual C++ Redistributable: 未安装")
            print("      下载地址: https://aka.ms/vs/17/release/vc_redist.x64.exe")
            required_ok = False
    except Exception as e:
        print(f"  [!] 无法检查 VC++ Redistributable: {e}")
    
    # 检查 7-Zip (可选)
    try:
        result = subprocess.run(["7z"], capture_output=True, timeout=5)
        print("  [OK] 7-Zip: 已安装")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("  [!] 7-Zip: 未安装（可选，用于环境包压缩）")
    
    # 总结
    print("\n" + "=" * 60)
    if required_ok:
        print("[OK] 所有必需依赖项已满足")
        print("\n可以运行:")
        print("  python src/launcher.py  # 启动应用")
        print("  python build.py         # 构建应用")
        return 0
    else:
        print("[X] 缺少必需的依赖项")
        print("\n请安装缺失的包:")
        print("  pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())

