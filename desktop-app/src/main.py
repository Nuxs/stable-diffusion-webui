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
                app_dir = sys._MEIPASS
                dll_paths = [
                    os.path.join(app_dir, 'PyQt6', 'Qt6', 'bin'),
                    os.path.join(app_dir, '_internal'),
                    os.path.dirname(sys.executable),
                ]
        else:
            # 开发模式 - 自动检测 PyQt6 路径
            try:
                import site
                for site_packages in site.getsitepackages():
                    pyqt6_bin = os.path.join(site_packages, 'PyQt6', 'Qt6', 'bin')
                    if os.path.exists(pyqt6_bin):
                        dll_paths = [pyqt6_bin]
                        break
                else:
                    # 用户安装目录
                    user_site = site.getusersitepackages()
                    pyqt6_bin = os.path.join(user_site, 'PyQt6', 'Qt6', 'bin')
                    if os.path.exists(pyqt6_bin):
                        dll_paths = [pyqt6_bin]
                    else:
                        # 硬编码路径（最后手段）
                        pyqt6_bin = r'C:\Users\25292\AppData\Roaming\Python\Python312\site-packages\PyQt6\Qt6\bin'
                        if os.path.exists(pyqt6_bin):
                            dll_paths = [pyqt6_bin]
                        else:
                            return
            except:
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
                    if not handle:
                        raise Exception("AddDllDirectory returned NULL")
                except:
                    pass
                
                # 方法2: 使用 os.add_dll_directory (Python 3.8+)
                try:
                    os.add_dll_directory(dll_dir)
                except:
                    pass
                
                # 方法3: 设置 PATH 环境变量
                current_path = os.environ.get('PATH', '')
                if dll_dir not in current_path:
                    os.environ['PATH'] = dll_dir + os.pathsep + current_path
    except Exception:
        pass

# 执行 DLL 路径设置
setup_pyqt6_dll_path()

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

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
    
    # 设置高DPI支持
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
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

