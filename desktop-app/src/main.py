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
                internal_dir = os.path.join(exe_dir, '_internal')
                dll_paths = [
                    # 优先检查 _internal 目录（PyInstaller 目录模式的标准位置）
                    os.path.join(internal_dir, 'PyQt6', 'Qt6', 'bin'),
                    os.path.join(internal_dir, 'PyQt6', 'Qt6', 'bin'),  # 确保这个路径被检查
                    internal_dir,  # _internal 目录本身
                    # 也检查 exe 同级目录（某些配置可能将文件放在这里）
                    os.path.join(exe_dir, 'PyQt6', 'Qt6', 'bin'),
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

# 执行 DLL 路径设置 - 必须在导入 PyQt6 之前！
# 这是最关键的一步，必须在任何 PyQt6 导入之前执行
setup_pyqt6_dll_path()

# 验证 DLL 路径是否设置成功（仅在打包模式下）
if getattr(sys, 'frozen', False):
    exe_dir = os.path.dirname(sys.executable)
    internal_dir = os.path.join(exe_dir, '_internal')
    qt6_bin = os.path.join(internal_dir, 'PyQt6', 'Qt6', 'bin')
    if os.path.exists(qt6_bin):
        # 再次确保路径已设置（双重保险）
        current_path = os.environ.get('PATH', '')
        if qt6_bin not in current_path:
            os.environ['PATH'] = qt6_bin + os.pathsep + current_path
            print(f"调试: 已再次添加 DLL 路径: {qt6_bin}")

# 添加项目根目录到路径
# 在打包模式下，项目根目录应该在 exe 所在目录
if getattr(sys, 'frozen', False):
    # 打包模式：从 exe 所在目录查找项目根目录
    if hasattr(sys, '_MEIPASS'):
        # 单文件模式：_MEIPASS 是临时解压目录
        exe_dir = Path(sys.executable).parent
    else:
        # 目录模式：exe 所在目录就是项目根目录（因为我们已经将项目文件打包到那里）
        exe_dir = Path(sys.executable).parent
    
    # 在打包模式下，首先尝试设置运行时环境（分离式打包方案）
    try:
        from src.utils.environment_manager import setup_runtime_environment
        python_exe = setup_runtime_environment(exe_dir)
        if python_exe:
            print(f"✓ 运行时环境已准备好: {python_exe}")
    except Exception as e:
        print(f"警告: 设置运行时环境时出错: {e}")
        print("将尝试使用系统Python或项目venv")
    
    # 在打包模式下，stable-diffusion-webui 的核心文件应该在 exe 所在目录
    # 检查是否存在 launch.py 或 webui.py 来确定项目根目录
    if (exe_dir / "launch.py").exists() or (exe_dir / "webui.py").exists():
        project_root = exe_dir
    else:
        # 如果不在 exe 目录，尝试在 _internal 目录查找（PyInstaller 目录模式）
        internal_dir = exe_dir / "_internal"
        if (internal_dir / "launch.py").exists() or (internal_dir / "webui.py").exists():
            project_root = internal_dir
        else:
            # 如果都找不到，使用 exe 目录作为项目根目录
            project_root = exe_dir
            print(f"警告: 在打包模式下未找到 launch.py 或 webui.py，使用 {project_root} 作为项目根目录")
    
    desktop_app_root = exe_dir  # 在打包模式下，desktop-app 目录可能不存在
    data_dir = exe_dir / "data"
else:
    # 开发模式：使用原来的逻辑
    project_root = Path(__file__).parent.parent.parent
    desktop_app_root = Path(__file__).parent.parent
    data_dir = desktop_app_root / "data"

data_dir.mkdir(parents=True, exist_ok=True)

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
        window = MainWindow(project_root, data_dir)
        window.show()
        logger.info("应用程序启动成功")
        
        # 运行应用
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"启动应用程序时发生错误: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()

