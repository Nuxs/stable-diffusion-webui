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
            # WebUI 推荐使用 Python 3.10，torch 2.1.2 也支持 Python 3.10
            # 必须使用 Python 3.10，不能使用其他版本（如 3.13）
            
            import shutil
            import subprocess
            
            python_exe = None
            use_venv = False
            
            # 0. 如果是打包模式，优先使用环境管理器（分离式打包方案）
            if getattr(sys, 'frozen', False):
                try:
                    from src.utils.environment_manager import EnvironmentManager
                    exe_dir = Path(sys.executable).parent
                    env_manager = EnvironmentManager(exe_dir)
                    if env_manager.setup_environment():
                        python_exe = str(env_manager.get_python_exe())
                        use_venv = True
                        logger.info(f"✓ 使用打包的Python环境: {python_exe}")
                except Exception as e:
                    logger.debug(f"环境管理器不可用: {e}")
            
            # 1. 优先查找项目根目录下的 venv 环境（应该包含 Python 3.10）
            # 在打包模式下，项目根目录可能在上级目录
            possible_project_roots = [self.project_root]
            
            # 如果是打包模式，优先查找打包的venv（在exe同级目录）
            if getattr(sys, 'frozen', False):
                # 打包模式下，venv应该在exe所在目录
                exe_dir = Path(sys.executable).parent
                
                # 优先检查exe同级目录的venv（打包后的venv位置）
                exe_venv = exe_dir / "venv" / "Scripts" / "python.exe"
                if exe_venv.exists():
                    possible_project_roots.insert(0, exe_dir)
                    logger.info(f"✓ 在打包模式下找到打包的venv: {exe_venv}")
                
                # 也检查_internal目录（如果venv被打包到_internal）
                internal_venv = exe_dir / "_internal" / "venv" / "Scripts" / "python.exe"
                if internal_venv.exists():
                    possible_project_roots.insert(0, exe_dir / "_internal")
                    logger.info(f"✓ 在打包模式下找到_internal中的venv: {internal_venv}")
                
                # 然后检查项目根目录（向上查找）
                current = Path(self.project_root)
                if current.name == "_internal":
                    # 从 _internal 向上查找
                    for _ in range(5):
                        current = current.parent
                        venv_check = current / "venv" / "Scripts" / "python.exe"
                        if venv_check.exists():
                            possible_project_roots.append(current)
                            logger.info(f"在打包模式下找到上级目录的venv: {venv_check}")
                            break
                        elif ((current / "launch.py").exists() or (current / "webui.py").exists()) and current.name != "_internal":
                            possible_project_roots.append(current)
                else:
                    # 如果 project_root 不是 _internal，也尝试向上查找
                    for _ in range(3):
                        current = current.parent
                        venv_check = current / "venv" / "Scripts" / "python.exe"
                        if venv_check.exists():
                            possible_project_roots.append(current)
                            break
                        elif ((current / "launch.py").exists() or (current / "webui.py").exists()) and current.name != "_internal":
                            possible_project_roots.append(current)
            
            # 检查所有可能的项目根目录中的 venv
            checked_venv_paths = []
            for project_root in possible_project_roots:
                venv_python = project_root / "venv" / "Scripts" / "python.exe"
                checked_venv_paths.append(str(venv_python))
                if venv_python.exists():
                    # 验证 venv 中的 Python 版本
                    try:
                        result = subprocess.run(
                            [str(venv_python), "--version"],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        version_str = result.stdout.strip()
                        if "3.10" in version_str:
                            python_exe = str(venv_python)
                            use_venv = True
                            logger.info(f"✓ 找到并使用项目 venv 环境: {python_exe} ({version_str})")
                            break
                        else:
                            logger.warning(f"项目 venv 中的 Python 版本不是 3.10: {version_str} (路径: {venv_python})")
                    except Exception as e:
                        logger.warning(f"验证 venv Python 版本时出错: {e} (路径: {venv_python})")
            
            if not python_exe:
                logger.info(f"未找到项目 venv，已检查的路径: {checked_venv_paths}")
            
            # 2. 如果没有找到 venv，查找系统安装的 Python 3.10
            if not python_exe:
                # 优先查找 Python 3.10
                python310_paths = [
                    r"C:\Python310\python.exe",
                    r"C:\Program Files\Python310\python.exe",
                    r"C:\Program Files (x86)\Python310\python.exe",
                ]
                
                # 检查常见的 Python 3.10 安装路径
                for path in python310_paths:
                    if os.path.exists(path):
                        # 验证是否为 Python 3.10
                        try:
                            result = subprocess.run(
                                [path, "--version"],
                                capture_output=True,
                                text=True,
                                timeout=5
                            )
                            if "3.10" in result.stdout:
                                python_exe = path
                                logger.info(f"找到 Python 3.10: {python_exe}")
                                break
                        except Exception:
                            continue
                
                # 如果找不到，尝试使用 python3.10 命令
                if not python_exe:
                    python_exe = shutil.which("python3.10")
                    if python_exe:
                        # 验证版本
                        try:
                            result = subprocess.run(
                                [python_exe, "--version"],
                                capture_output=True,
                                text=True,
                                timeout=5
                            )
                            if "3.10" not in result.stdout:
                                python_exe = None
                            else:
                                logger.info(f"使用系统 Python 3.10: {python_exe}")
                        except Exception:
                            python_exe = None
            
            # 3. 如果找不到 Python 3.10，直接报错（不允许使用其他版本）
            if not python_exe:
                checked_paths_str = "\n".join([f"  - {path}" for path in checked_venv_paths])
                error_msg = (
                    "未找到 Python 3.10 解释器。\n\n"
                    "WebUI 必须使用 Python 3.10，torch 2.1.2 仅支持 Python 3.10。\n\n"
                    "请执行以下操作之一：\n"
                    "1. 安装 Python 3.10: https://www.python.org/downloads/release/python-3106/\n"
                    "2. 在项目根目录创建 venv 环境（包含 Python 3.10）\n"
                    "   命令: python3.10 -m venv venv\n"
                    "3. 确保项目根目录下有 venv 文件夹\n\n"
                    f"当前项目根目录: {self.project_root}\n"
                    f"已检查的 venv 路径:\n{checked_paths_str}\n\n"
                    "注意: 在打包模式下，venv 应该在项目根目录（stable-diffusion-webui），而不是在 dist 目录中。"
                )
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            # 4. 最终验证 Python 版本（双重保险）
            try:
                result = subprocess.run(
                    [python_exe, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                version_str = result.stdout.strip()
                if "3.10" not in version_str:
                    error_msg = (
                        f"Python 版本不匹配: {version_str}\n\n"
                        "WebUI 必须使用 Python 3.10，当前版本不兼容。\n"
                        "请安装 Python 3.10 或使用项目的 venv 环境。"
                    )
                    logger.error(error_msg)
                    raise RuntimeError(error_msg)
            except Exception as e:
                logger.warning(f"验证 Python 版本时出错: {e}")
            
            logger.info(f"使用 Python: {python_exe}")
            
            # 构建启动命令 - 使用项目根目录的 launch.py（不是 _internal 中的）
            # 在打包模式下，需要找到真正的项目根目录
            actual_project_root = self.project_root
            
            # 如果是打包模式且 project_root 指向 _internal，向上查找真正的项目根目录
            if getattr(sys, 'frozen', False):
                current = Path(self.project_root)
                if current.name == "_internal":
                    # 从 _internal 向上查找，直到找到包含 launch.py 且不在 _internal 中的目录
                    for _ in range(5):
                        current = current.parent
                        launch_check = current / "launch.py"
                        webui_check = current / "webui.py"
                        if (launch_check.exists() or webui_check.exists()) and current.name != "_internal":
                            actual_project_root = current
                            logger.info(f"在打包模式下找到真正的项目根目录: {actual_project_root}")
                            break
            
            launch_script = actual_project_root / "launch.py"
            webui_script = actual_project_root / "webui.py"
            
            # 优先使用 launch.py，如果不存在则使用 webui.py
            if launch_script.exists():
                script_to_run = launch_script
                logger.info(f"使用启动脚本: {script_to_run}")
            elif webui_script.exists():
                script_to_run = webui_script
                logger.info(f"使用启动脚本: {script_to_run}")
            else:
                # 如果都找不到，尝试使用 _internal 中的作为后备（不推荐，但至少能运行）
                if getattr(sys, 'frozen', False):
                    internal_launch = self.project_root / "launch.py"
                    if internal_launch.exists():
                        script_to_run = internal_launch
                        logger.warning(f"使用 _internal 中的启动脚本（可能有问题）: {script_to_run}")
                    else:
                        raise FileNotFoundError(f"找不到启动脚本。已检查:\n- {launch_script}\n- {webui_script}\n- {internal_launch}")
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

