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
        self.start_time: Optional[float] = None
        self.max_startup_time = 300  # 最多等待5分钟
        
    def start_server(self):
        """启动服务器"""
        if self.process and self.process.poll() is None:
            logger.warning("服务器已在运行")
            return
            
        try:
            # 确定 Python 解释器
            # 优先使用项目根目录下的 venv 环境（网页版环境），避免重复安装依赖
            venv_python = self.project_root / "venv" / "Scripts" / "python.exe"
            use_venv = venv_python.exists()
            if use_venv:
                python_exe = str(venv_python)
                logger.info(f"使用项目 venv 环境: {python_exe}")
            else:
                python_exe = sys.executable
                logger.info(f"使用当前 Python 环境: {python_exe}")
            
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
                "--skip-python-version-check",  # 跳过 Python 版本检查
            ]
            
            # 如果使用 venv 环境，venv 环境应该已经安装了所有依赖（包括 PyTorch）
            # launch.py 会自动检测已安装的包，不会重复安装
            if use_venv:
                logger.info("使用 venv 环境，将复用已安装的依赖（包括 PyTorch）")
            
            # 添加额外的参数
            # 注意: launch.py 会自动处理环境，默认只监听 localhost
            # 但我们需要确保不自动打开浏览器
            if script_to_run.name == "webui.py":
                cmd.extend(["--listen", "127.0.0.1"])
            # launch.py 默认不自动打开浏览器，但为了保险起见，我们可以设置环境变量
            # 实际上 launch.py 会检查 --autolaunch 参数，默认是 False，所以不需要额外设置
            
            # 如果配置了其他参数，添加它们
            if self.config.get("api", False):
                cmd.append("--api")
                
            logger.info(f"启动服务器命令: {' '.join(cmd)}")
            
            # 在后台线程中启动服务器
            self.server_thread = Thread(target=self._start_server_process, args=(cmd, env), daemon=True)
            self.server_thread.start()
            
            # 记录启动时间
            self.start_time = time.time()
            
            # 开始检查服务器状态
            self.check_timer.start(2000)  # 每2秒检查一次
            
        except Exception as e:
            logger.error(f"启动服务器失败: {e}", exc_info=True)
            self.server_error.emit(str(e))
            
    def _start_server_process(self, cmd, env):
        """在后台线程中启动服务器进程"""
        try:
            # 设置环境变量以确保无缓冲输出
            env["PYTHONUNBUFFERED"] = "1"
            
            self.process = subprocess.Popen(
                cmd,
                cwd=str(self.project_root),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,  # 行缓冲
                universal_newlines=True
            )
            
            # 在单独的线程中读取输出，避免阻塞
            output_thread = Thread(target=self._read_server_output, daemon=True)
            output_thread.start()
                        
        except Exception as e:
            logger.error(f"启动服务器进程失败: {e}", exc_info=True)
            self.server_error.emit(str(e))
    
    def _read_server_output(self):
        """在后台线程中读取服务器输出"""
        try:
            if self.process and self.process.stdout:
                import re
                while True:
                    line = self.process.stdout.readline()
                    if not line:
                        # 检查进程是否已退出
                        if self.process.poll() is not None:
                            logger.info(f"服务器进程已退出，退出码: {self.process.returncode}")
                            break
                        # 如果没有输出但进程还在运行，短暂休眠
                        import time
                        time.sleep(0.1)
                        continue
                    
                    line = line.rstrip('\n\r')
                    # 过滤掉一些噪音输出，但保留重要信息
                    if line and not line.startswith('force_push:'):
                        logger.info(f"服务器输出: {line}")
                        # 检查是否包含 URL 信息
                        if 'Running on' in line or 'Local URL' in line or 'http://' in line or '127.0.0.1' in line:
                            # 尝试从输出中提取 URL
                            url_match = re.search(r'http://[^\s\)]+', line)
                            if url_match:
                                extracted_url = url_match.group(0)
                                if not self.server_url:
                                    self.server_url = extracted_url
                                    logger.info(f"从服务器输出中提取 URL: {extracted_url}")
                        # 检查错误信息
                        if any(keyword in line.lower() for keyword in ['error', 'exception', 'traceback', 'failed', '失败', 'cannot', '无法']):
                            logger.warning(f"服务器输出可能包含错误: {line}")
                        # 检查启动成功消息
                        if any(keyword in line.lower() for keyword in ['launching', 'started', 'ready', 'running on']):
                            logger.info(f"服务器启动信息: {line}")
        except Exception as e:
            logger.error(f"读取服务器输出失败: {e}", exc_info=True)
            
    def check_server_status(self):
        """检查服务器状态"""
        if not self.process:
            return
        
        # 检查启动超时
        if self.start_time and (time.time() - self.start_time) > self.max_startup_time:
            self.check_timer.stop()
            self.server_error.emit(f"服务器启动超时（超过 {self.max_startup_time} 秒）")
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
                    elapsed_time = time.time() - self.start_time if self.start_time else 0
                    logger.info(f"服务器启动成功，耗时 {elapsed_time:.1f} 秒")
                    self.server_ready.emit(self.server_url or url)
            except requests.RequestException as e:
                # 记录详细的错误信息以便调试
                logger.debug(f"服务器可能还在启动中: {e}")
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
        if self.server_url:
            return self.server_url
        # 如果 server_url 未设置但服务器正在运行，构造 URL
        if self.is_running():
            return f"http://127.0.0.1:{self.port}"
        return None
    
    def get_port(self) -> int:
        """获取服务器端口"""
        return self.port

