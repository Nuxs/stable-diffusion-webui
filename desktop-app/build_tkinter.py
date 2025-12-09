#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建 Tkinter 版本的桌面应用
"""

import os
import sys
import shutil
from pathlib import Path

try:
    import PyInstaller.__main__
except ImportError:
    print("错误: 未安装 PyInstaller")
    print("请运行: pip install pyinstaller")
    sys.exit(1)


def build():
    """构建应用"""
    project_root = Path(__file__).parent
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"
    spec_file = project_root / "app_tkinter.spec"
    
    # 清理旧的构建文件
    if dist_dir.exists():
        try:
            shutil.rmtree(dist_dir)
        except PermissionError:
            print("警告: 无法删除 dist 目录，可能文件正在使用中")
            print("请关闭正在运行的应用后重试")
    
    if build_dir.exists():
        try:
            shutil.rmtree(build_dir)
        except PermissionError:
            print("警告: 无法删除 build 目录，继续构建...")
    
    # 使用 spec 文件进行打包
    args = [
        str(spec_file),
        "--clean",
        "--noconfirm",
        f"--distpath={dist_dir}",
        f"--workpath={build_dir}",
    ]
    
    # 执行打包
    print("=" * 60)
    print("开始打包 Tkinter 版本的桌面应用...")
    print("=" * 60)
    print()
    
    try:
        PyInstaller.__main__.run(args)
        print()
        print("=" * 60)
        print("打包完成！")
        print("=" * 60)
        print()
        print(f"可执行文件位于: {dist_dir / 'StableDiffusionWebUI'}")
        print()
        print("使用方法:")
        print(f"  1. 进入目录: cd {dist_dir / 'StableDiffusionWebUI'}")
        print("  2. 运行: StableDiffusionWebUI.exe")
        print()
    except Exception as e:
        print()
        print("=" * 60)
        print(f"打包失败: {e}")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    build()

