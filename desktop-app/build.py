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
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"
    spec_file = project_root / "app.spec"
    
    # 检查 spec 文件是否存在
    if not spec_file.exists():
        print("=" * 60)
        print("错误: 找不到 app.spec 文件")
        print("=" * 60)
        sys.exit(1)
    
    # 检查运行时 hook 文件
    rthook_file = project_root / "rthook_pyqt6_fix.py"
    if not rthook_file.exists():
        print("=" * 60)
        print("警告: 找不到 rthook_pyqt6_fix.py 文件")
        print("DLL 加载可能有问题")
        print("=" * 60)
    
    # 清理旧的构建文件
    if dist_dir.exists():
        try:
            shutil.rmtree(dist_dir)
            print("已清理旧的 dist 目录")
        except PermissionError:
            print("警告: 无法删除 dist 目录，可能文件正在使用中")
            print("请关闭正在运行的应用后重试")
            # 只删除单个文件而不是整个目录
            exe_dir = dist_dir / "StableDiffusionWebUI"
            if exe_dir.exists():
                try:
                    exe_file = exe_dir / "StableDiffusionWebUI.exe"
                    if exe_file.exists():
                        exe_file.unlink()
                except PermissionError:
                    print(f"警告: 无法删除 {exe_file}，请手动关闭应用")
    
    if build_dir.exists():
        try:
            shutil.rmtree(build_dir)
            print("已清理旧的 build 目录")
        except PermissionError:
            print("警告: 无法删除 build 目录，继续构建...")
    
    # PyInstaller 参数（使用 spec 文件时，所有配置都在 spec 文件中）
    args = [
        str(spec_file),
        "--clean",
        "--noconfirm",
        f"--distpath={dist_dir}",
        f"--workpath={build_dir}",
    ]
    
    # 执行打包
    print()
    print("=" * 60)
    print("开始打包 PyQt6 桌面应用（完整版）...")
    print("=" * 60)
    print()
    print(f"使用配置文件: {spec_file}")
    print(f"输出目录: {dist_dir}")
    print(f"构建目录: {build_dir}")
    print()
    
    try:
        PyInstaller.__main__.run(args)
        print()
        print("=" * 60)
        print("打包完成！")
        print("=" * 60)
        print()
        exe_path = dist_dir / "StableDiffusionWebUI" / "StableDiffusionWebUI.exe"
        if exe_path.exists():
            print(f"可执行文件位于: {exe_path}")
            print()
            print("使用方法:")
            print(f"  1. 进入目录: cd {dist_dir / 'StableDiffusionWebUI'}")
            print("  2. 运行: StableDiffusionWebUI.exe")
            print()
            print("分发说明:")
            print("  - 整个 StableDiffusionWebUI 文件夹可以复制到其他电脑使用")
            print("  - 目标电脑需要安装 Visual C++ Redistributable 2015-2022")
            print("  - 下载地址: https://aka.ms/vs/17/release/vc_redist.x64.exe")
            print()
        else:
            print(f"警告: 未找到可执行文件 {exe_path}")
            print("请检查构建日志以了解问题")
            print()
    except Exception as e:
        print()
        print("=" * 60)
        print(f"打包失败: {e}")
        print("=" * 60)
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    build()

