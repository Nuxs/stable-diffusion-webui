#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt6 DLL 依赖诊断工具
使用 Dependencies.exe 或 dumpbin 分析 DLL 依赖
"""

import sys
import os
import subprocess
from pathlib import Path


def check_dll_dependencies():
    """检查 Qt6Core.dll 的依赖项"""
    print("=" * 60)
    print("PyQt6 DLL 依赖诊断")
    print("=" * 60)
    
    # 查找 Qt6Core.dll
    try:
        import PyQt6
        pyqt6_path = Path(PyQt6.__file__).parent
        qt6_bin = pyqt6_path / "Qt6" / "bin"
        qt6core_dll = qt6_bin / "Qt6Core.dll"
        
        if not qt6core_dll.exists():
            print(f"[X] 找不到 Qt6Core.dll: {qt6core_dll}")
            return
        
        print(f"\n[OK] 找到 Qt6Core.dll: {qt6core_dll}")
        print(f"  大小: {qt6core_dll.stat().st_size / 1024 / 1024:.2f} MB")
        
        # 列出 Qt6/bin 目录中的所有 DLL
        print(f"\nQt6/bin 目录内容:")
        dll_files = list(qt6_bin.glob("*.dll"))
        print(f"  共 {len(dll_files)} 个 DLL 文件")
        
        # 关键 DLL
        key_dlls = [
            "Qt6Core.dll",
            "Qt6Gui.dll",
            "Qt6Widgets.dll",
            "Qt6Network.dll",
            "Qt6WebEngineCore.dll",
            "libGLESv2.dll",
            "libEGL.dll",
        ]
        
        print("\n关键 DLL 检查:")
        for dll_name in key_dlls:
            dll_path = qt6_bin / dll_name
            if dll_path.exists():
                size_mb = dll_path.stat().st_size / 1024 / 1024
                print(f"  [OK] {dll_name} ({size_mb:.2f} MB)")
            else:
                print(f"  [X] {dll_name} (缺失)")
        
        # 尝试使用 where 命令查找系统 DLL
        print("\n检查系统 DLL:")
        system_dlls = ["msvcp140.dll", "vcruntime140.dll", "vcruntime140_1.dll"]
        for dll_name in system_dlls:
            try:
                result = subprocess.run(
                    ["where", dll_name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    print(f"  [OK] {dll_name}")
                    for line in result.stdout.strip().split('\n'):
                        print(f"    {line}")
                else:
                    print(f"  [X] {dll_name} (未找到)")
            except Exception as e:
                print(f"  ? {dll_name} (检查失败: {e})")
        
        # 尝试加载 DLL
        print("\n尝试直接加载 DLL:")
        try:
            import ctypes
            
            # 先添加 Qt6/bin 到 PATH
            os.environ['PATH'] = str(qt6_bin) + os.pathsep + os.environ.get('PATH', '')
            
            # 尝试添加 DLL 目录
            try:
                kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
                kernel32.AddDllDirectory(str(qt6_bin))
                print(f"  [OK] 已添加 DLL 目录: {qt6_bin}")
            except Exception as e:
                print(f"  [!] AddDllDirectory 失败: {e}")
            
            # 尝试加载 Qt6Core.dll
            try:
                qt6core = ctypes.CDLL(str(qt6core_dll))
                print(f"  [OK] 成功加载 Qt6Core.dll")
            except OSError as e:
                print(f"  [X] 加载 Qt6Core.dll 失败: {e}")
                print(f"\n    错误码: {ctypes.get_last_error()}")
                
                # 尝试获取更详细的错误信息
                import ctypes.wintypes
                kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
                FormatMessageW = kernel32.FormatMessageW
                FormatMessageW.argtypes = [
                    ctypes.wintypes.DWORD,
                    ctypes.wintypes.LPCVOID,
                    ctypes.wintypes.DWORD,
                    ctypes.wintypes.DWORD,
                    ctypes.wintypes.LPWSTR,
                    ctypes.wintypes.DWORD,
                    ctypes.wintypes.LPCVOID
                ]
                FormatMessageW.restype = ctypes.wintypes.DWORD
                
                FORMAT_MESSAGE_FROM_SYSTEM = 0x00001000
                buffer = ctypes.create_unicode_buffer(256)
                FormatMessageW(
                    FORMAT_MESSAGE_FROM_SYSTEM,
                    None,
                    ctypes.get_last_error(),
                    0,
                    buffer,
                    256,
                    None
                )
                print(f"    详细错误: {buffer.value}")
                
        except Exception as e:
            print(f"  [X] DLL 加载测试失败: {e}")
        
        # 检查环境变量
        print("\n环境变量:")
        print(f"  PATH 包含 Qt6/bin: {str(qt6_bin) in os.environ.get('PATH', '')}")
        print(f"  QT_PLUGIN_PATH: {os.environ.get('QT_PLUGIN_PATH', '(未设置)')}")
        
    except ImportError:
        print("[X] PyQt6 未安装")
    except Exception as e:
        print(f"[X] 诊断过程出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    check_dll_dependencies()

