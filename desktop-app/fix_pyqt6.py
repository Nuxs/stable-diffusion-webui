#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 PyQt6 DLL 加载问题
"""

import subprocess
import sys
import os

def install_vc_redist():
    """提示安装 Visual C++ Redistributable"""
    print("=" * 60)
    print("PyQt6 需要 Visual C++ Redistributable")
    print("=" * 60)
    print()
    print("请下载并安装 Visual C++ Redistributable:")
    print("https://aka.ms/vs/17/release/vc_redist.x64.exe")
    print()
    print("安装完成后，重新运行此脚本。")
    print()

def reinstall_pyqt6():
    """重新安装 PyQt6"""
    print("正在重新安装 PyQt6...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "PyQt6", "PyQt6-WebEngine"], check=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "PyQt6", "PyQt6-WebEngine"], check=True)
        print("✓ PyQt6 重新安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 重新安装失败: {e}")
        return False

def test_pyqt6():
    """测试 PyQt6 是否可以导入"""
    try:
        from PyQt6.QtWidgets import QApplication
        print("✓ PyQt6 可以正常导入")
        return True
    except ImportError as e:
        print(f"✗ PyQt6 无法导入: {e}")
        return False

def main():
    print("=" * 60)
    print("PyQt6 DLL 加载问题修复工具")
    print("=" * 60)
    print()
    
    # 测试当前状态
    if test_pyqt6():
        print("\n✓ PyQt6 工作正常，无需修复")
        return
    
    print("\n检测到 PyQt6 无法加载，开始修复...")
    print()
    
    # 选项 1: 重新安装 PyQt6
    print("选项 1: 重新安装 PyQt6")
    response = input("是否重新安装 PyQt6? (y/n): ").strip().lower()
    if response == 'y':
        if reinstall_pyqt6():
            if test_pyqt6():
                print("\n✓ 修复成功！")
                return
    
    # 选项 2: 安装 VC++ Redistributable
    print("\n选项 2: 安装 Visual C++ Redistributable")
    install_vc_redist()
    
    print("\n如果问题仍然存在，请:")
    print("1. 确保已安装 Visual C++ Redistributable")
    print("2. 重启计算机")
    print("3. 重新运行此脚本")

if __name__ == "__main__":
    main()

