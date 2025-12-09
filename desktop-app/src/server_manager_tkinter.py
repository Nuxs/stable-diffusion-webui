#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务器管理器 - Tkinter 版本（不依赖 PyQt6）
"""

import logging
import os
import subprocess
import sys
import time
import socket
import requests
import threading
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ServerManager:
    """服务器管理器"""
    
    def __init__(self, project_root: Path, config):
        self.project_root = project_root
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.server_url: Optional[str] = None
        self.port = self.find_available_port(self.config.get_port())
        
        # 回调函数
        self.on_ready = None
        self.on_error = None
        self.on_stopped = None
        
    def find_available_port(self, start_port: int, max_attempts: int = 50) -> int:
        """查找可用端口"""
        port = start_port
        for _ in range(max_attempts):
            if not self.is_port_open(port):
                logger.info(f"找到可用端口: {port}")
                return port
            logger.debug(f"端口 {port} 被占用，尝试下一个")
            port += 1
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
        
    def start_server(self):
        """启动服务器"""
        if self.process and self.process.poll() is None:
            logger.warning("服务器已在运行")
            return
            
        try:
            # 优先使用 WebUI 项目的虚拟环境
            venv_python = self.project_root / "venv" / "Scripts" / "python.exe"
            if venv_python.exists():
                python_exe = str(venv_python)
                logger.info(f"使用虚拟环境 Python: {python_exe}")
            else:
                python_exe = sys.executable
                logger.info(f"使用系统 Python: {python_exe}")
                
            launch_script = self.project_root / "launch.py"
            webui_script = self.project_root / "webui.py"
            
            if launch_script.exists():
                script_to_run = launch_script
            elif webui_script.exists():
                script_to_run = webui_script
            else:
                error_msg = f"找不到启动脚本: {launch_script} 或 {webui_script}"
                logger.error(error_msg)
                if self.on_error:
                    self.on_error(error_msg)
                return
            
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            
            cmd = [
                python_exe,
                str(script_to_run),
                "--port", str(self.port),
                "--skip-python-version-check",  # 跳过 Python 版本检查
            ]
            
            if script_to_run.name == "webui.py":
                cmd.extend(["--no-open", "--listen", "127.0.0.1"])
                
            logger.info(f"启动服务器命令: {' '.join(cmd)}")
            
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
            
            # 在后台线程中读取输出和检查状态
            threading.Thread(target=self.read_server_output, daemon=True).start()
            threading.Thread(target=self.check_server_status, daemon=True).start()
            
        except Exception as e:
            logger.error(f"启动服务器失败: {e}", exc_info=True)
            if self.on_error:
                self.on_error(str(e))
                
    def read_server_output(self):
        """读取服务器输出"""
        if not self.process or not self.process.stdout:
            return
            
        output_lines = []
        try:
            for line in iter(self.process.stdout.readline, ''):
                if not line:
                    break
                line = line.strip()
                if line:
                    output_lines.append(line)
                    logger.debug(f"服务器输出: {line}")
                    
                    # 如果进程已退出，保存输出并报告错误
                    if self.process.poll() is not None:
                        if self.process.returncode != 0:
                            error_output = '\n'.join(output_lines[-20:])  # 最后20行
                            error_msg = f"服务器启动失败 (退出码: {self.process.returncode})"
                            if error_output:
                                error_msg += f"\n\n错误输出:\n{error_output}"
                            if self.on_error:
                                self.on_error(error_msg)
                        break
        except Exception as e:
            logger.error(f"读取服务器输出失败: {e}")
                
    def check_server_status(self):
        """检查服务器状态"""
        max_wait = 120  # 最多等待 2 分钟
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            if not self.process:
                break
                
            if self.process.poll() is not None:
                # 错误已在 read_server_output 中处理
                return
                
            if self.is_port_open(self.port):
                url = f"http://127.0.0.1:{self.port}"
                try:
                    response = requests.get(url, timeout=2)
                    if response.status_code == 200:
                        self.server_url = url
                        if self.on_ready:
                            self.on_ready(url)
                        return
                except requests.RequestException:
                    pass
                    
            time.sleep(2)
            
        if self.on_error:
            self.on_error("服务器启动超时")
            
    def stop_server(self):
        """停止服务器"""
        if self.process:
            try:
                logger.info("正在停止服务器...")
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning("服务器未在5秒内响应，强制终止...")
                    self.process.kill()
                    self.process.wait()
                    
                logger.info("服务器已停止")
                self.server_url = None
                if self.on_stopped:
                    self.on_stopped()
                    
            except Exception as e:
                logger.error(f"停止服务器失败: {e}", exc_info=True)
                if self.on_error:
                    self.on_error(f"停止服务器失败: {e}")
                    
    def restart_server(self):
        """重启服务器"""
        self.stop_server()
        time.sleep(1)
        self.start_server()
