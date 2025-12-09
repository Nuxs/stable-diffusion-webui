#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务器管理器
负责启动和管理 WebUI 服务器
"""

import logging
import os
import subprocess
import sys
import time
import socket
import requests
from pathlib import Path
from typing import Optional
from threading import Thread

from PyQt6.QtCore import QObject, pyqtSignal, QTimer

logger = logging.getLogger(__name__)


class ServerManager(QObject):
    """服务器管理器"""
    
    server_ready = pyqtSignal(str)  # 服务器就绪信号
    server_error = pyqtSignal(str)  # 服务器错误信号
    server_stopped = pyqtSignal()  # 服务器停止信号
    
    def __init__(self, project_root: Path, config):
        super().__init__()
        self.project_root = project_root
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.server_url: Optional[str] = None
        self.port = self.find_available_port(self.config.get_port())
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_server_status)
        self.server_thread: Optional[Thread] = None
        
    def start_server(self):
        """启动服务器"""
        if self.process and self.process.poll() is None:
            logger.warning("服务器已在运行")
            return
            
        try:
            # 确定 Python 解释器
            python_exe = sys.executable
            
            # 构建启动命令 - 使用 launch.py 以确保环境正确设置
            launch_script = self.project_root / "launch.py"
            webui_script = self.project_root / "webui.py"
            
            # 优先使用 launch.py，如果不存在则使用 webui.py
            if launch_script.exists():
                script_to_run = launch_script
            elif webui_script.exists():
                script_to_run = webui_script
            else:
                raise FileNotFoundError(f"找不到启动脚本: {launch_script} 或 {webui_script}")
            
            # 设置环境变量
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            
            # 设置命令行参数
            cmd = [
                python_exe,
                str(script_to_run),
                "--port", str(self.port),
            ]
            
            # 添加额外的参数
            # 注意: launch.py 会自动处理环境，不需要 --listen 参数
            # 但我们需要确保不自动打开浏览器
            if script_to_run.name == "webui.py":
                cmd.extend(["--no-open", "--listen", "127.0.0.1"])
            
            # 如果配置了其他参数，添加它们
            if self.config.get("api", False):
                cmd.append("--api")
                
            logger.info(f"启动服务器命令: {' '.join(cmd)}")
            
            # 在后台线程中启动服务器
            self.server_thread = Thread(target=self._start_server_process, args=(cmd, env), daemon=True)
            self.server_thread.start()
            
            # 开始检查服务器状态
            self.check_timer.start(2000)  # 每2秒检查一次
            
        except Exception as e:
            logger.error(f"启动服务器失败: {e}", exc_info=True)
            self.server_error.emit(str(e))
            
    def _start_server_process(self, cmd, env):
        """在后台线程中启动服务器进程"""
        try:
            self.process = subprocess.Popen(
                cmd,
                cwd=str(self.project_root),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # 读取输出
            if self.process.stdout:
                for line in iter(self.process.stdout.readline, ''):
                    if not line:
                        break
                    logger.debug(f"服务器输出: {line.strip()}")
                    if self.process.poll() is not None:
                        break
                        
        except Exception as e:
            logger.error(f"启动服务器进程失败: {e}", exc_info=True)
            self.server_error.emit(str(e))
            
    def check_server_status(self):
        """检查服务器状态"""
        if not self.process:
            return
            
        # 检查进程是否还在运行
        if self.process.poll() is not None:
            # 进程已退出
            self.check_timer.stop()
            error_msg = "服务器进程意外退出"
            if self.process.returncode != 0:
                error_msg += f" (退出码: {self.process.returncode})"
            self.server_error.emit(error_msg)
            return
            
        # 检查端口是否可访问
        if self.is_port_open(self.port):
            url = f"http://127.0.0.1:{self.port}"
            try:
                # 尝试访问服务器
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    if not self.server_url:
                        self.server_url = url
                        self.check_timer.stop()
                        self.server_ready.emit(url)
            except requests.RequestException:
                pass  # 服务器可能还在启动中
                
    def find_available_port(self, start_port: int, max_attempts: int = 10) -> int:
        """查找可用端口"""
        port = start_port
        for _ in range(max_attempts):
            if not self.is_port_open(port):
                return port
            port += 1
        # 如果所有端口都被占用，返回最后一个尝试的端口
        logger.warning(f"未找到可用端口，使用 {port}")
        return port
        
    def is_port_open(self, port: int) -> bool:
        """检查端口是否开放"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('127.0.0.1', port))
                return result == 0
        except Exception:
            return False
            
    def stop_server(self):
        """停止服务器"""
        if self.process:
            self.check_timer.stop()
            try:
                logger.info("正在停止服务器...")
                self.process.terminate()
                
                # 等待进程结束
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning("服务器未在5秒内响应，强制终止...")
                    self.process.kill()
                    self.process.wait()
                    
                logger.info("服务器已停止")
                self.server_url = None
                self.server_stopped.emit()
                
            except Exception as e:
                logger.error(f"停止服务器失败: {e}", exc_info=True)
                self.server_error.emit(f"停止服务器失败: {e}")
                
    def restart_server(self):
        """重启服务器"""
        self.stop_server()
        time.sleep(1)
        self.start_server()
        
    def is_running(self) -> bool:
        """检查服务器是否运行"""
        return self.process is not None and self.process.poll() is None
        
    def get_url(self) -> Optional[str]:
        """获取服务器 URL"""
        return self.server_url

