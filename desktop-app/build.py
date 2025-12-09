#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建脚本
使用 PyInstaller 打包应用
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
    src_dir = project_root / "src"
    resources_dir = project_root / "resources"
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"
    spec_file = project_root / "app.spec"
    
    # 清理旧的构建文件
    if dist_dir.exists():
        try:
            shutil.rmtree(dist_dir)
        except PermissionError:
            print("警告: 无法删除 dist 目录，可能文件正在使用中")
            print("请关闭正在运行的应用后重试")
            # 只删除单个文件而不是整个目录
            exe_file = dist_dir / "StableDiffusionWebUI.exe"
            if exe_file.exists():
                try:
                    exe_file.unlink()
                except PermissionError:
                    print(f"警告: 无法删除 {exe_file}，请手动关闭应用")
    if build_dir.exists():
        try:
            shutil.rmtree(build_dir)
        except PermissionError:
            print("警告: 无法删除 build 目录，继续构建...")
    
    # 使用 spec 文件进行打包
    spec_file = project_root / "app.spec"
    
    # PyInstaller 参数（使用 spec 文件时，所有配置都在 spec 文件中）
    args = [
        str(spec_file),
        "--clean",
        f"--distpath={dist_dir}",
        f"--workpath={build_dir}",
    ]
    
    # 执行打包
    print("开始打包应用...")
    print(f"参数: {' '.join(args)}")
    
    try:
        PyInstaller.__main__.run(args)
        print("\n打包完成！")
        print(f"可执行文件位于: {dist_dir}")
    except Exception as e:
        print(f"\n打包失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    build()

