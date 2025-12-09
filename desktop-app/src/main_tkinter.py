#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stable Diffusion WebUI 桌面应用程序 - Tkinter 版本
使用 Python 内置的 tkinter，无需额外依赖
"""

import sys
import os
import logging
import webbrowser
import subprocess
import threading
import time
from pathlib import Path
from typing import Optional

# 添加项目路径
# 在开发模式下设置基本路径
if getattr(sys, 'frozen', False):
    desktop_app_root = Path(sys.executable).parent
else:
    desktop_app_root = Path(__file__).parent.parent
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

sys.path.insert(0, str(desktop_app_root))

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, scrolledtext
except ImportError:
    print("错误: tkinter 未安装")
    print("请安装 Python 时选择 'tcl/tk and IDLE' 选项")
    sys.exit(1)

from src.server_manager_tkinter import ServerManager
from src.utils.config import Config
from src.utils.logger import setup_logging


logger = logging.getLogger(__name__)


class MainWindow:
    """主窗口类 - Tkinter 版本"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config = Config()
        self.server_manager: Optional[ServerManager] = None
        self.server_url: Optional[str] = None
        
        # 设置日志
        setup_logging()
        
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("Stable Diffusion WebUI")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # 创建界面
        self.create_ui()
        
        # 初始化服务器
        self.init_server()
        
    def create_ui(self):
        """创建用户界面"""
        # 菜单栏
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="在浏览器中打开", command=self.open_in_browser, accelerator="Ctrl+B")
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_closing, accelerator="Ctrl+Q")
        
        # 服务器菜单
        server_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="服务器", menu=server_menu)
        server_menu.add_command(label="重启服务器", command=self.restart_server)
        server_menu.add_command(label="停止服务器", command=self.stop_server)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
        
        # 工具栏
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="在浏览器中打开", command=self.open_in_browser).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="重启服务器", command=self.restart_server).pack(side=tk.LEFT, padx=2)
        
        # 状态栏
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(self.status_frame, text="正在启动服务器...", relief=tk.SUNKEN)
        self.status_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        self.progress = ttk.Progressbar(self.status_frame, mode='indeterminate')
        self.progress.pack(side=tk.RIGHT, padx=5, pady=2)
        self.progress.start()
        
        # 主内容区域 - 使用 WebView 或显示信息
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 信息显示区域
        info_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, state=tk.DISABLED)
        info_text.pack(fill=tk.BOTH, expand=True)
        
        self.info_text = info_text
        
        # 添加欢迎信息
        self.add_info("欢迎使用 Stable Diffusion WebUI 桌面应用")
        self.add_info("正在启动服务器，请稍候...")
        self.add_info("")
        self.add_info("提示: 服务器启动后，可以点击'在浏览器中打开'按钮")
        
        # 绑定快捷键
        self.root.bind('<Control-b>', lambda e: self.open_in_browser())
        self.root.bind('<Control-q>', lambda e: self.on_closing())
        
        # 窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def add_info(self, text: str):
        """添加信息到文本区域"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.insert(tk.END, text + "\n")
        self.info_text.see(tk.END)
        self.info_text.config(state=tk.DISABLED)
        
    def init_server(self):
        """初始化服务器"""
        self.server_manager = ServerManager(self.project_root, self.config)
        self.server_manager.on_ready = self.on_server_ready
        self.server_manager.on_error = self.on_server_error
        self.server_manager.on_stopped = self.on_server_stopped
        
        # 在后台线程中启动服务器
        threading.Thread(target=self.server_manager.start_server, daemon=True).start()
        
    def on_server_ready(self, url: str):
        """服务器就绪回调"""
        self.server_url = url
        self.root.after(0, lambda: self.update_status(f"服务器运行中: {url}"))
        self.root.after(0, lambda: self.progress.stop())
        self.root.after(0, lambda: self.add_info(f"\n✓ 服务器已启动: {url}"))
        self.root.after(0, lambda: self.add_info("可以点击'在浏览器中打开'按钮访问 WebUI"))
        
    def on_server_error(self, error: str):
        """服务器错误回调"""
        self.root.after(0, lambda: self.update_status(f"错误: {error}"))
        self.root.after(0, lambda: self.progress.stop())
        self.root.after(0, lambda: self.add_info(f"\n✗ 服务器启动失败: {error}"))
        
        # 显示错误对话框（限制长度，避免对话框过大）
        error_preview = error[:500] + "..." if len(error) > 500 else error
        error_dialog = f"无法启动服务器:\n\n{error_preview}\n\n请检查:\n1. Stable Diffusion WebUI 依赖是否已安装\n2. Python 版本兼容性（推荐 3.10.6）\n3. 查看日志文件: logs/app.log\n4. 尝试手动运行: python launch.py"
        self.root.after(0, lambda: messagebox.showerror("服务器错误", error_dialog))
        
    def on_server_stopped(self):
        """服务器停止回调"""
        self.root.after(0, lambda: self.update_status("服务器已停止"))
        self.root.after(0, lambda: self.progress.stop())
        
    def update_status(self, text: str):
        """更新状态栏"""
        self.status_label.config(text=text)
        
    def open_in_browser(self):
        """在浏览器中打开"""
        if self.server_url:
            webbrowser.open(self.server_url)
            self.add_info(f"\n已在浏览器中打开: {self.server_url}")
        else:
            messagebox.showwarning("服务器未运行", "服务器尚未启动，无法在浏览器中打开。")
            
    def restart_server(self):
        """重启服务器"""
        if self.server_manager:
            self.update_status("正在重启服务器...")
            self.progress.start()
            threading.Thread(target=self.server_manager.restart_server, daemon=True).start()
            
    def stop_server(self):
        """停止服务器"""
        if self.server_manager:
            reply = messagebox.askyesno("确认停止", "确定要停止服务器吗？")
            if reply:
                threading.Thread(target=self.server_manager.stop_server, daemon=True).start()
                
    def show_about(self):
        """显示关于对话框"""
        messagebox.showinfo(
            "关于 Stable Diffusion WebUI",
            "Stable Diffusion WebUI 桌面应用\n\n"
            "版本: 1.0.0\n"
            "基于 Tkinter 的桌面应用程序\n"
            "将 Stable Diffusion WebUI 打包为 Windows 桌面应用"
        )
        
    def on_closing(self):
        """窗口关闭事件"""
        if self.server_manager:
            reply = messagebox.askyesno("确认退出", "确定要退出应用程序吗？\n这将停止服务器。")
            if reply:
                self.server_manager.stop_server()
                time.sleep(1)
                self.root.destroy()
        else:
            self.root.destroy()
            
    def run(self):
        """运行应用"""
        self.root.mainloop()


def find_webui_project(config: Config = None) -> Path:
    """查找 WebUI 项目目录"""
    # 首先检查配置文件中是否指定了路径
    if config is None:
        config = Config()
    config_path = config.get("webui_project_path")
    if config_path:
        path = Path(config_path)
        if path.exists() and ((path / "launch.py").exists() or (path / "webui.py").exists()):
            return path
    
    # 自动检测
    if getattr(sys, 'frozen', False):
        # 打包后的环境
        if hasattr(sys, '_MEIPASS'):
            app_dir = Path(sys.executable).parent
            # 尝试从 exe 所在目录向上查找 WebUI 项目
            possible_roots = [
                app_dir.parent.parent,  # dist/StableDiffusionWebUI -> dist -> project_root
                app_dir.parent.parent.parent,  # 如果结构不同
                Path(sys.executable).parent.parent.parent,  # 另一种可能
            ]
            for root in possible_roots:
                if root.exists() and ((root / "launch.py").exists() or (root / "webui.py").exists()):
                    return root
            
            # 如果找不到，尝试从当前工作目录查找
            cwd = Path.cwd()
            if (cwd / "launch.py").exists() or (cwd / "webui.py").exists():
                return cwd
            
            # 最后尝试从 exe 目录向上查找
            current = Path(sys.executable).parent
            for _ in range(5):  # 最多向上查找 5 级
                if (current / "launch.py").exists() or (current / "webui.py").exists():
                    return current
                current = current.parent
    else:
        # 开发模式
        return Path(__file__).parent.parent.parent
    
    # 如果都找不到，返回默认路径
    return Path(sys.executable).parent.parent.parent if getattr(sys, 'frozen', False) else Path(__file__).parent.parent.parent


def main():
    """主函数"""
    # 加载配置
    config = Config()
    
    # 查找 WebUI 项目目录
    project_root = find_webui_project(config)
    
    # 验证项目目录
    if not project_root.exists():
        error_msg = f"找不到 WebUI 项目目录: {project_root}\n\n请在配置文件中设置正确的路径。"
        try:
            messagebox.showerror("错误", error_msg)
        except:
            print(f"错误: {error_msg}")
        sys.exit(1)
    
    if not (project_root / "launch.py").exists() and not (project_root / "webui.py").exists():
        error_msg = f"在 {project_root} 中找不到 launch.py 或 webui.py\n\n请确保路径正确。"
        try:
            messagebox.showerror("错误", error_msg)
        except:
            print(f"错误: {error_msg}")
        sys.exit(1)
    
    try:
        app = MainWindow(project_root)
        app.run()
    except Exception as e:
        logger.error(f"启动应用程序时发生错误: {e}", exc_info=True)
        try:
            messagebox.showerror("错误", f"启动应用程序时发生错误:\n{e}")
        except:
            print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

