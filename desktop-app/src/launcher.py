#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stable Diffusion WebUI 桌面应用 - 智能启动器
主入口文件，集成智能引导和环境管理
"""

import sys
import os
import logging
from pathlib import Path
from typing import Dict

# 修复 PyQt6 DLL 加载问题 - 必须在导入 PyQt6 之前执行
def setup_pyqt6_dll_path():
    """设置 PyQt6 DLL 搜索路径"""
    try:
        import ctypes
        from ctypes import wintypes
        
        if getattr(sys, 'frozen', False):
            # 打包后的应用
            exe_dir = os.path.dirname(sys.executable)
            internal_dir = os.path.join(exe_dir, '_internal')
            
            dll_paths = [
                os.path.join(internal_dir, 'PyQt6', 'Qt6', 'bin'),
                internal_dir,
                exe_dir,
            ]
        else:
            # 开发模式
            dll_paths = []
            try:
                import site
                # 获取所有 site-packages 路径
                site_packages_list = []
                try:
                    site_packages_list = site.getsitepackages()
                except AttributeError:
                    # 某些环境可能没有 getsitepackages
                    import sys
                    for path in sys.path:
                        if 'site-packages' in path or 'dist-packages' in path:
                            site_packages_list.append(path)
                
                for site_packages in site_packages_list:
                    pyqt6_bin = os.path.join(site_packages, 'PyQt6', 'Qt6', 'bin')
                    if os.path.exists(pyqt6_bin):
                        dll_paths.append(pyqt6_bin)
                        print(f"找到 PyQt6 DLL 路径: {pyqt6_bin}")
            except Exception as e:
                print(f"查找 PyQt6 DLL 路径时出错: {e}")
        
        # 设置 DLL 搜索路径
        for dll_path in dll_paths:
            if os.path.exists(dll_path):
                dll_dir = os.path.abspath(dll_path)
                
                # 方法1: 使用 AddDllDirectory
                try:
                    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
                    AddDllDirectory = kernel32.AddDllDirectory
                    AddDllDirectory.argtypes = [wintypes.LPCWSTR]
                    AddDllDirectory.restype = wintypes.HANDLE
                    AddDllDirectory(dll_dir)
                except:
                    pass
                
                # 方法2: 添加到 PATH
                current_path = os.environ.get('PATH', '')
                if dll_dir not in current_path:
                    os.environ['PATH'] = dll_dir + os.pathsep + current_path
    except Exception as e:
        print(f"警告: 设置 PyQt6 DLL 路径时出错: {e}")

# 执行 DLL 路径设置
setup_pyqt6_dll_path()

# 现在可以安全导入 PyQt6
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

# 导入应用模块
try:
    from src.main_window import MainWindow
    from src.system_detector import SystemDetector
    from src.utils.logger import setup_logging
    from src.utils.config import Config
except ImportError:
    # 如果在打包模式下，尝试不带 src 前缀
    from main_window import MainWindow
    from system_detector import SystemDetector
    from utils.logger import setup_logging
    from utils.config import Config

logger = logging.getLogger(__name__)


class SmartLauncher:
    """智能启动器"""
    
    def __init__(self):
        # 确定应用目录
        if getattr(sys, 'frozen', False):
            self.app_dir = Path(sys.executable).parent
        else:
            self.app_dir = Path(__file__).parent.parent
        
        # 数据目录（存放 Python 环境、模型等）
        self.data_dir = self.app_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置
        self.config = Config()
        
        # 项目根目录（stable-diffusion-webui）
        self.project_root = self._find_project_root()
    
    def _find_project_root(self) -> Path:
        """查找 stable-diffusion-webui 项目根目录"""
        # 在打包模式下，项目文件应该在 _internal 目录
        if getattr(sys, 'frozen', False):
            internal_dir = self.app_dir / "_internal"
            if (internal_dir / "launch.py").exists():
                return internal_dir
            elif (internal_dir / "webui.py").exists():
                return internal_dir
        
        # 开发模式：往上查找
        current = Path(__file__).parent.parent.parent
        if (current / "launch.py").exists() or (current / "webui.py").exists():
            return current
        
        # 默认返回 app_dir
        logger.warning(f"未找到项目根目录，使用应用目录: {self.app_dir}")
        return self.app_dir
    
    def check_and_setup_environment(self) -> bool:
        """
        检查并设置环境
        
        Returns:
            bool: 是否成功
        """
        try:
            # 1. 检测系统信息
            logger.info("检测系统信息...")
            system_info = SystemDetector.detect_all()
            
            # 2. 检查最低要求
            meets_req, errors = SystemDetector.check_minimum_requirements(system_info)
            if not meets_req:
                error_msg = "系统不满足最低要求:\n\n" + "\n".join(f"• {e}" for e in errors)
                self._show_error("系统要求不满足", error_msg)
                return False
            
            # 3. 检查是否需要首次运行向导
            python_env_dir = self.data_dir / "python-env"
            webui_dir = self.data_dir / "webui"
            models_dir = self.data_dir / "models" / "Stable-diffusion"
            
            needs_setup = (
                not (python_env_dir / "python.exe").exists() or
                not webui_dir.exists() or
                not any(models_dir.glob("*.safetensors")) if models_dir.exists() else True
            )
            
            if needs_setup:
                logger.info("需要首次运行设置")
                return self._run_first_time_setup(system_info)
            
            logger.info("环境已就绪")
            return True
            
        except Exception as e:
            logger.error(f"环境检查失败: {e}", exc_info=True)
            self._show_error("环境检查失败", str(e))
            return False
    
    def _run_first_time_setup(self, system_info: Dict) -> bool:
        """
        运行首次设置向导
        
        Args:
            system_info: 系统信息
        
        Returns:
            bool: 是否成功
        """
        try:
            from src.first_run_wizard import FirstRunWizard
        except ImportError:
            from first_run_wizard import FirstRunWizard
        
        logger.info("启动首次运行向导...")
        
        wizard = FirstRunWizard(system_info, self.data_dir, parent=None)
        result = wizard.exec()
        
        if result == wizard.DialogCode.Accepted:
            logger.info("首次设置完成")
            return True
        else:
            logger.info("用户取消了首次设置")
            return False
    
    def _show_error(self, title: str, message: str):
        """显示错误对话框"""
        from PyQt6.QtWidgets import QMessageBox
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()
    
    def launch(self):
        """启动应用"""
        # 设置日志
        setup_logging()
        logger.info("=" * 60)
        logger.info("Stable Diffusion WebUI 桌面版启动")
        logger.info("=" * 60)
        
        # 创建 Qt 应用
        app = QApplication(sys.argv)
        app.setApplicationName("Stable Diffusion WebUI")
        app.setApplicationVersion("2.0.0")
        app.setOrganizationName("SD-WebUI")
        
        # 设置应用图标
        icon_path = self.app_dir / "resources" / "icon.ico"
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
        
        # 检查并设置环境
        if not self.check_and_setup_environment():
            logger.error("环境设置失败，退出应用")
            sys.exit(1)
        
        # 创建主窗口
        try:
            window = MainWindow(self.project_root)
            window.show()
            logger.info("应用程序启动成功")
            
            # 运行应用
            sys.exit(app.exec())
        except Exception as e:
            logger.error(f"启动应用程序时发生错误: {e}", exc_info=True)
            self._show_error("启动失败", f"无法启动应用:\n{e}")
            sys.exit(1)


def main():
    """主函数"""
    launcher = SmartLauncher()
    launcher.launch()


if __name__ == "__main__":
    main()

