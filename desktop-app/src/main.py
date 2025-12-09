#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stable Diffusion WebUI 桌面应用程序
主入口文件
"""

import sys
import os
import logging
from pathlib import Path

# 修复 PyQt6 DLL 加载问题 - 必须在导入 PyQt6 之前执行
def setup_pyqt6_dll_path():
    """设置 PyQt6 DLL 搜索路径"""
    try:
        import ctypes
        from ctypes import wintypes
        
        if getattr(sys, 'frozen', False):
            # 打包后的应用
            if hasattr(sys, '_MEIPASS'):
                # 单文件模式：使用 _MEIPASS
                app_dir = sys._MEIPASS
                dll_paths = [
                    os.path.join(app_dir, 'PyQt6', 'Qt6', 'bin'),
                    os.path.join(app_dir, '_internal'),
                    os.path.dirname(sys.executable),
                ]
            else:
                # 目录模式：可执行文件所在目录
                exe_dir = os.path.dirname(sys.executable)
                dll_paths = [
                    os.path.join(exe_dir, 'PyQt6', 'Qt6', 'bin'),
                    os.path.join(exe_dir, '_internal'),
                    exe_dir,
                ]
        else:
            # 开发模式 - 收集所有可能的 PyQt6 路径
            dll_paths = []
            try:
                import site
                
                # 1. 检查系统 site-packages
                for site_packages in site.getsitepackages():
                    pyqt6_bin = os.path.join(site_packages, 'PyQt6', 'Qt6', 'bin')
                    if os.path.exists(pyqt6_bin):
                        dll_paths.append(pyqt6_bin)
                
                # 2. 检查用户安装目录
                user_site = site.getusersitepackages()
                if user_site:
                    pyqt6_bin = os.path.join(user_site, 'PyQt6', 'Qt6', 'bin')
                    if os.path.exists(pyqt6_bin):
                        dll_paths.append(pyqt6_bin)
                
                # 3. 检查常见安装位置（作为后备）
                common_paths = [
                    os.path.expanduser(r'~\AppData\Roaming\Python\Python312\site-packages\PyQt6\Qt6\bin'),
                    os.path.expanduser(r'~\AppData\Roaming\Python\Python311\site-packages\PyQt6\Qt6\bin'),
                    os.path.expanduser(r'~\AppData\Roaming\Python\Python310\site-packages\PyQt6\Qt6\bin'),
                ]
                for path in common_paths:
                    if os.path.exists(path) and path not in dll_paths:
                        dll_paths.append(path)
                
            except Exception as e:
                print(f"警告: 检测 PyQt6 路径时出错: {e}")
        
        # 去重
        dll_paths = list(set(dll_paths))
        
        if not dll_paths:
            print("警告: 未找到 PyQt6 DLL 目录")
            return
        
        # 设置 DLL 搜索路径
        for dll_path in dll_paths:
            if os.path.exists(dll_path):
                dll_dir = os.path.abspath(dll_path)
                
                # 方法1: 使用 AddDllDirectory (Windows 8+)
                try:
                    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
                    AddDllDirectory = kernel32.AddDllDirectory
                    AddDllDirectory.argtypes = [wintypes.LPCWSTR]
                    AddDllDirectory.restype = wintypes.HANDLE
                    handle = AddDllDirectory(dll_dir)
                    if handle:
                        print(f"✓ 已使用 AddDllDirectory 添加: {dll_dir}")
                except:
                    pass
                
                # 方法2: 使用 os.add_dll_directory (Python 3.8+)
                try:
                    os.add_dll_directory(dll_dir)
                    print(f"✓ 已使用 os.add_dll_directory 添加: {dll_dir}")
                except:
                    pass
                
                # 方法3: 设置 PATH 环境变量（最可靠的方法）
                current_path = os.environ.get('PATH', '')
                if dll_dir not in current_path:
                    os.environ['PATH'] = dll_dir + os.pathsep + current_path
                    print(f"✓ 已添加到 PATH: {dll_dir}")
                
                # 方法4: 尝试预加载 Qt6Core.dll（确保依赖 DLL 可用）
                try:
                    qt6core = os.path.join(dll_dir, 'Qt6Core.dll')
                    if os.path.exists(qt6core):
                        # 使用 LoadLibraryEx 预加载，确保依赖 DLL 被找到
                        LoadLibraryExW = kernel32.LoadLibraryExW
                        LoadLibraryExW.argtypes = [wintypes.LPCWSTR, ctypes.c_void_p, wintypes.DWORD]
                        LoadLibraryExW.restype = wintypes.HMODULE
                        LOAD_WITH_ALTERED_SEARCH_PATH = 0x00000008
                        handle = LoadLibraryExW(qt6core, None, LOAD_WITH_ALTERED_SEARCH_PATH)
                        if handle:
                            # 不立即释放，让 Python 的 PyQt6 模块使用
                            print(f"✓ 已预加载 Qt6Core.dll")
                except:
                    pass
    except Exception as e:
        print(f"警告: 设置 PyQt6 DLL 路径时出错: {e}")

# 执行 DLL 路径设置
setup_pyqt6_dll_path()

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
desktop_app_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(desktop_app_root))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QLoggingCategory
from PyQt6.QtGui import QIcon

from src.main_window import MainWindow
from src.utils.logger import setup_logging

# 禁用 Qt WebEngine 的日志
QLoggingCategory.setFilterRules("qt.webenginecontext.info=false")

def main():
    """主函数"""
    # 设置日志
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("Stable Diffusion WebUI")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SD-WebUI")
    
    # 设置应用图标
    icon_path = Path(__file__).parent.parent / "resources" / "icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # 设置高DPI支持（PyQt6 中这些属性已移除，高DPI自动支持）
    # app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)  # PyQt6 中已移除
    # app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)  # PyQt6 中已移除
    
    # 创建主窗口
    try:
        window = MainWindow(project_root)
        window.show()
        logger.info("应用程序启动成功")
        
        # 运行应用
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"启动应用程序时发生错误: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()

