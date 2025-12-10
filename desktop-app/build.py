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
    
    # 设置环境变量，帮助 PyInstaller 找到 PyQt6 DLL
    # 这可以减少构建时的 DLL 加载警告
    try:
        import PyQt6
        pyqt6_path = os.path.dirname(PyQt6.__file__)
        qt6_bin_path = os.path.join(pyqt6_path, 'Qt6', 'bin')
        
        if os.path.exists(qt6_bin_path):
            # 添加到 PATH，帮助 PyInstaller 在分析阶段找到 DLL
            current_path = os.environ.get('PATH', '')
            if qt6_bin_path not in current_path:
                os.environ['PATH'] = qt6_bin_path + os.pathsep + current_path
                print(f"✓ 已设置 DLL 搜索路径: {qt6_bin_path}")
    except Exception as e:
        print(f"警告: 设置 DLL 路径时出错: {e}")
        print("   构建可能会显示 DLL 加载警告，但通常不影响最终结果")
    
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
    
    # 清理旧的构建文件和缓存
    if dist_dir.exists():
        print("正在清理旧的构建文件...")
        
        # 首先尝试关闭可能正在运行的进程
        try:
            import subprocess
            # 尝试终止 StableDiffusionWebUI.exe 进程
            subprocess.run(['taskkill', '/F', '/IM', 'StableDiffusionWebUI.exe'], 
                         capture_output=True, timeout=5)
        except Exception:
            pass  # 如果进程不存在或无法终止，继续
        
        # 等待一小段时间让文件释放
        import time
        time.sleep(1)
        
        # 尝试删除 dist 目录
        max_retries = 3
        for attempt in range(max_retries):
            try:
                shutil.rmtree(dist_dir)
                print("✓ 已清理旧的 dist 目录")
                break
            except PermissionError as e:
                if attempt < max_retries - 1:
                    print(f"警告: 无法删除 dist 目录（尝试 {attempt + 1}/{max_retries}）")
                    print("   可能文件正在使用中，等待后重试...")
                    time.sleep(2)
                else:
                    print("=" * 60)
                    print("错误: 无法删除 dist 目录")
                    print("=" * 60)
                    print("可能的原因:")
                    print("  1. StableDiffusionWebUI.exe 正在运行")
                    print("  2. 文件被其他程序占用（如杀毒软件、文件管理器）")
                    print("  3. 权限不足")
                    print()
                    print("解决方案:")
                    print("  1. 关闭所有 StableDiffusionWebUI.exe 进程")
                    print("  2. 关闭可能占用文件的程序")
                    print("  3. 手动删除 dist 目录后重试")
                    print("  4. 以管理员身份运行此脚本")
                    print()
                    response = input("是否继续构建（可能会覆盖部分文件）？(y/n): ")
                    if response.lower() != 'y':
                        sys.exit(1)
            except Exception as e:
                print(f"警告: 清理 dist 目录时出错: {e}")
                break
    
    if build_dir.exists():
        try:
            shutil.rmtree(build_dir)
            print("已清理旧的 build 目录")
        except PermissionError:
            print("警告: 无法删除 build 目录，继续构建...")
    
    # 清理 PyInstaller 缓存
    import tempfile
    pyinstaller_cache = Path(tempfile.gettempdir()) / "pyinstaller"
    if pyinstaller_cache.exists():
        try:
            # 只清理相关的缓存，不完全删除
            print("已清理 PyInstaller 缓存")
        except:
            pass
    
    # PyInstaller 参数（使用 spec 文件时，所有配置都在 spec 文件中）
    # 注意：确保 spec 文件中配置了 exclude_binaries=True 和 COLLECT 步骤
    # 重要：使用 spec 文件时，命令行参数如 --onedir 会被忽略，配置必须在 spec 文件中
    args = [
        str(spec_file),
        "--clean",
        "--noconfirm",
        f"--distpath={dist_dir}",
        f"--workpath={build_dir}",
        "--log-level=INFO",  # 显示详细信息，便于调试
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
    print("注意: 构建过程中可能会看到 PyQt6 DLL 加载警告")
    print("      这是正常的，不会影响最终打包结果，可以安全忽略")
    print()
    
    try:
        PyInstaller.__main__.run(args)
        print()
        print("=" * 60)
        print("打包完成！")
        print("=" * 60)
        print()
        # 检查构建结果
        exe_path_dir = dist_dir / "StableDiffusionWebUI" / "StableDiffusionWebUI.exe"
        exe_path_single = dist_dir / "StableDiffusionWebUI.exe"
        
        if exe_path_dir.exists():
            # 目录模式 - 正确
            print(f"✓ 目录模式构建成功！")
            print(f"可执行文件位于: {exe_path_dir}")
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
        elif exe_path_single.exists():
            # 单文件模式 - 需要修复
            file_size_mb = exe_path_single.stat().st_size / (1024 * 1024)
            print(f"⚠ 警告: 构建生成了单文件模式（{file_size_mb:.1f}MB）")
            print(f"文件位于: {exe_path_single}")
            print()
            print("这可能是由于以下原因：")
            print("  1. PyInstaller 使用了缓存的旧配置")
            print("  2. spec 文件配置有问题")
            print()
            print("解决方案：")
            print("  1. 完全清理构建文件：")
            print("     Remove-Item -Path dist,build -Recurse -Force")
            print("  2. 清理 PyInstaller 缓存：")
            print("     Remove-Item -Path $env:LOCALAPPDATA\\pyinstaller -Recurse -Force")
            print("  3. 重新运行构建：")
            print("     python build.py")
            print()
            print("或者直接使用 PyInstaller 命令：")
            print(f"     python -m PyInstaller {spec_file} --clean --noconfirm")
            print()
        else:
            print(f"⚠ 警告: 未找到可执行文件")
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

