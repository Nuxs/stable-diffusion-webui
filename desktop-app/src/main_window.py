#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口类
"""

import logging
import webbrowser
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QToolBar, QStatusBar, QProgressBar, QLabel, QMessageBox,
    QMenuBar, QMenu
)
from PyQt6.QtCore import Qt, QUrl, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings

from src.server_manager import ServerManager
from src.utils.config import Config

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """主窗口类"""
    
    server_ready = pyqtSignal(str)  # 服务器就绪信号
    server_error = pyqtSignal(str)  # 服务器错误信号
    
    def __init__(self, project_root: Path):
        super().__init__()
        self.project_root = project_root
        self.config = Config()
        self.server_manager: Optional[ServerManager] = None
        self.web_view: Optional[QWebEngineView] = None
        self.status_label: Optional[QLabel] = None
        self.progress_bar: Optional[QProgressBar] = None
        
        self.init_ui()
        self.init_server()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("Stable Diffusion WebUI")
        self.setMinimumSize(1200, 800)
        
        # 设置窗口图标
        icon_path = self.project_root / "desktop-app" / "resources" / "icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建状态栏
        self.create_status_bar()
        
        # 创建中央部件
        self.create_central_widget()
        
        # 设置样式
        self.setStyleSheet(self.get_stylesheet())
        
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        open_browser_action = QAction("在浏览器中打开", self)
        open_browser_action.setShortcut("Ctrl+B")
        open_browser_action.triggered.connect(self.open_in_browser)
        file_menu.addAction(open_browser_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图(&V)")
        
        reload_action = QAction("重新加载(&R)", self)
        reload_action.setShortcut("F5")
        reload_action.triggered.connect(self.reload_page)
        view_menu.addAction(reload_action)
        
        view_menu.addSeparator()
        
        zoom_in_action = QAction("放大(&+)", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("缩小(&-)", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        reset_zoom_action = QAction("重置缩放(&0)", self)
        reset_zoom_action.setShortcut("Ctrl+0")
        reset_zoom_action.triggered.connect(self.reset_zoom)
        view_menu.addAction(reset_zoom_action)
        
        # 服务器菜单
        server_menu = menubar.addMenu("服务器(&S)")
        
        restart_action = QAction("重启服务器(&R)", self)
        restart_action.triggered.connect(self.restart_server)
        server_menu.addAction(restart_action)
        
        stop_action = QAction("停止服务器(&S)", self)
        stop_action.triggered.connect(self.stop_server)
        server_menu.addAction(stop_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        
        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏", self)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # 重新加载按钮
        reload_action = QAction("重新加载", self)
        reload_action.setIcon(QIcon.fromTheme("view-refresh"))
        reload_action.triggered.connect(self.reload_page)
        toolbar.addAction(reload_action)
        
        toolbar.addSeparator()
        
        # 在浏览器中打开按钮
        browser_action = QAction("在浏览器中打开", self)
        browser_action.setIcon(QIcon.fromTheme("web-browser"))
        browser_action.triggered.connect(self.open_in_browser)
        toolbar.addAction(browser_action)
        
    def create_status_bar(self):
        """创建状态栏"""
        status_bar = QStatusBar(self)
        self.setStatusBar(status_bar)
        
        # 状态标签
        self.status_label = QLabel("正在启动服务器...")
        status_bar.addWidget(self.status_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        status_bar.addPermanentWidget(self.progress_bar)
        
    def create_central_widget(self):
        """创建中央部件"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建 WebView
        self.web_view = QWebEngineView()
        
        # 配置 WebEngine 设置
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
        
        # 连接信号
        self.web_view.loadStarted.connect(self.on_load_started)
        self.web_view.loadProgress.connect(self.on_load_progress)
        self.web_view.loadFinished.connect(self.on_load_finished)
        self.web_view.urlChanged.connect(self.on_url_changed)
        
        layout.addWidget(self.web_view)
        
    def init_server(self):
        """初始化服务器"""
        self.server_manager = ServerManager(self.project_root, self.config)
        
        # 连接信号
        self.server_manager.server_ready.connect(self.on_server_ready)
        self.server_manager.server_error.connect(self.on_server_error)
        self.server_manager.server_stopped.connect(self.on_server_stopped)
        
        # 启动服务器
        self.server_manager.start_server()
        self.status_label.setText("正在启动服务器...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        
    def on_server_ready(self, url: str):
        """服务器就绪回调"""
        logger.info(f"服务器已就绪: {url}")
        self.status_label.setText(f"服务器运行中: {url}")
        self.progress_bar.setVisible(False)
        
        # 加载页面
        self.web_view.setUrl(QUrl(url))
        
    def on_server_error(self, error: str):
        """服务器错误回调"""
        logger.error(f"服务器错误: {error}")
        self.status_label.setText(f"错误: {error}")
        self.progress_bar.setVisible(False)
        
        QMessageBox.critical(
            self,
            "服务器错误",
            f"无法启动服务器:\n{error}\n\n请检查配置和依赖。"
        )
        
    def on_server_stopped(self):
        """服务器停止回调"""
        logger.info("服务器已停止")
        self.status_label.setText("服务器已停止")
        self.progress_bar.setVisible(False)
        
    def on_load_started(self):
        """页面加载开始"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
    def on_load_progress(self, progress: int):
        """页面加载进度"""
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(progress)
        
    def on_load_finished(self, success: bool):
        """页面加载完成"""
        self.progress_bar.setVisible(False)
        if success:
            self.status_label.setText("页面加载完成")
        else:
            self.status_label.setText("页面加载失败")
            
    def on_url_changed(self, url: QUrl):
        """URL 改变"""
        logger.debug(f"URL 改变: {url.toString()}")
        
    def reload_page(self):
        """重新加载页面"""
        if self.web_view:
            self.web_view.reload()
            
    def open_in_browser(self):
        """在浏览器中打开"""
        if self.server_manager and self.server_manager.is_running():
            url = self.server_manager.get_url()
            if url:
                webbrowser.open(url)
            else:
                # 如果 URL 未设置，尝试从端口构造
                port = self.server_manager.get_port()
                url = f"http://127.0.0.1:{port}"
                webbrowser.open(url)
        else:
            QMessageBox.warning(
                self,
                "服务器未运行",
                "服务器尚未启动，无法在浏览器中打开。"
            )
            
    def zoom_in(self):
        """放大"""
        if self.web_view:
            self.web_view.setZoomFactor(self.web_view.zoomFactor() + 0.1)
            
    def zoom_out(self):
        """缩小"""
        if self.web_view:
            self.web_view.setZoomFactor(max(0.25, self.web_view.zoomFactor() - 0.1))
            
    def reset_zoom(self):
        """重置缩放"""
        if self.web_view:
            self.web_view.setZoomFactor(1.0)
            
    def restart_server(self):
        """重启服务器"""
        if self.server_manager:
            self.status_label.setText("正在重启服务器...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            self.server_manager.restart_server()
            
    def stop_server(self):
        """停止服务器"""
        if self.server_manager:
            reply = QMessageBox.question(
                self,
                "确认停止",
                "确定要停止服务器吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.server_manager.stop_server()
                
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 Stable Diffusion WebUI",
            "<h2>Stable Diffusion WebUI</h2>"
            "<p>版本: 1.0.0</p>"
            "<p>基于 PyQt6 的桌面应用程序</p>"
            "<p>将 Stable Diffusion WebUI 打包为 Windows 桌面应用</p>"
        )
        
    def closeEvent(self, event):
        """关闭事件"""
        if self.server_manager:
            reply = QMessageBox.question(
                self,
                "确认退出",
                "确定要退出应用程序吗？\n这将停止服务器。",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.server_manager.stop_server()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
            
    def get_stylesheet(self) -> str:
        """获取样式表"""
        return """
        QMainWindow {
            background-color: #f5f5f5;
        }
        QStatusBar {
            background-color: #e0e0e0;
            border-top: 1px solid #ccc;
        }
        QToolBar {
            background-color: #ffffff;
            border-bottom: 1px solid #ccc;
            spacing: 5px;
        }
        QToolBar QToolButton {
            padding: 5px;
        }
        QProgressBar {
            border: 1px solid #ccc;
            border-radius: 3px;
            text-align: center;
        }
        """

