#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Portable Python 管理器
管理独立的 Python 环境（embeddable package）
"""

import subprocess
import logging
from pathlib import Path
from typing import Optional, Callable, Dict

logger = logging.getLogger(__name__)


class PortablePythonManager:
    """Portable Python 管理器"""
    
    # Python 3.10.11 embeddable package
    PYTHON_EMBED_URL = "https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip"
    PYTHON_EMBED_MD5 = "608619f8619075629c9c69f361352a85"
    
    # get-pip.py
    GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"
    
    # PyPI 镜像（国内加速）
    PYPI_MIRRORS = [
        "https://pypi.tuna.tsinghua.edu.cn/simple",
        "https://mirrors.aliyun.com/pypi/simple",
        "https://pypi.mirrors.ustc.edu.cn/simple",
    ]
    
    def __init__(self, data_dir: Path, download_manager):
        """
        初始化管理器
        
        Args:
            data_dir: 数据目录
            download_manager: 下载管理器实例
        """
        self.data_dir = Path(data_dir)
        self.python_env_dir = self.data_dir / "python-env"
        self.dm = download_manager
        self.current_env_type: Optional[str] = None
    
    def is_environment_ready(self) -> bool:
        """检查 Python 环境是否已准备好"""
        python_exe = self.python_env_dir / "python.exe"
        pip_exe = self.python_env_dir / "Scripts" / "pip.exe"
        return python_exe.exists() and pip_exe.exists()
    
    def setup_environment(self,
                         env_type: str = 'cpu',
                         progress_callback: Optional[Callable[[str, int, int], None]] = None) -> bool:
        """
        设置 Python 环境
        
        Args:
            env_type: 环境类型 ('cpu', 'cuda118', 'cuda121')
            progress_callback: 进度回调 (步骤名称, 当前进度, 总步骤数)
        
        Returns:
            bool: 是否成功
        """
        try:
            total_steps = 4
            current_step = 0
            
            def update_progress(step_name):
                nonlocal current_step
                current_step += 1
                if progress_callback:
                    progress_callback(step_name, current_step, total_steps)
            
            # 步骤 1: 下载 Python embeddable package
            update_progress("下载 Python 环境")
            if not self._download_python():
                return False
            
            # 步骤 2: 解压 Python
            update_progress("解压 Python 环境")
            if not self._extract_python():
                return False
            
            # 步骤 3: 安装 pip
            update_progress("安装 pip")
            if not self._install_pip():
                return False
            
            # 步骤 4: 安装依赖
            update_progress("安装依赖包")
            if not self._install_dependencies(env_type):
                return False
            
            self.current_env_type = env_type
            logger.info("Python 环境设置完成")
            return True
            
        except Exception as e:
            logger.error(f"设置 Python 环境失败: {e}", exc_info=True)
            return False
    
    def _download_python(self) -> bool:
        """下载 Python embeddable package"""
        try:
            logger.info("下载 Python embeddable package...")
            
            python_zip = self.dm.download_file(
                url=self.PYTHON_EMBED_URL,
                filename="python-3.10.11-embed-amd64.zip",
                expected_md5=self.PYTHON_EMBED_MD5
            )
            
            self.python_zip_path = python_zip
            logger.info(f"Python 下载完成: {python_zip}")
            return True
            
        except Exception as e:
            logger.error(f"下载 Python 失败: {e}")
            return False
    
    def _extract_python(self) -> bool:
        """解压 Python"""
        try:
            logger.info(f"解压 Python 到: {self.python_env_dir}")
            
            # 确保目标目录存在
            self.python_env_dir.mkdir(parents=True, exist_ok=True)
            
            # 解压
            success = self.dm.extract_archive(
                archive_path=self.python_zip_path,
                target_dir=self.python_env_dir
            )
            
            if not success:
                return False
            
            # 修改 python310._pth 以启用 site-packages
            pth_file = self.python_env_dir / "python310._pth"
            if pth_file.exists():
                content = pth_file.read_text()
                if "import site" not in content:
                    content = content.replace("#import site", "import site")
                    if "import site" not in content:
                        content += "\nimport site\n"
                    pth_file.write_text(content)
                    logger.info("已启用 site-packages")
            
            logger.info("Python 解压完成")
            return True
            
        except Exception as e:
            logger.error(f"解压 Python 失败: {e}")
            return False
    
    def _install_pip(self) -> bool:
        """安装 pip"""
        try:
            logger.info("安装 pip...")
            
            # 下载 get-pip.py
            get_pip = self.dm.download_file(
                url=self.GET_PIP_URL,
                filename="get-pip.py"
            )
            
            # 运行 get-pip.py
            python_exe = self.python_env_dir / "python.exe"
            result = subprocess.run(
                [str(python_exe), str(get_pip), "--no-warn-script-location"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                logger.error(f"安装 pip 失败: {result.stderr}")
                return False
            
            logger.info("pip 安装完成")
            return True
            
        except Exception as e:
            logger.error(f"安装 pip 失败: {e}")
            return False
    
    def _install_dependencies(self, env_type: str) -> bool:
        """
        安装依赖
        
        Args:
            env_type: 环境类型 ('cpu', 'cuda118', 'cuda121')
        """
        try:
            pip_exe = self.python_env_dir / "Scripts" / "pip.exe"
            
            # 使用国内镜像加速
            index_url = self.PYPI_MIRRORS[0]
            
            logger.info(f"安装基础依赖 (环境类型: {env_type})...")
            
            # 1. 先安装 PyTorch
            if env_type == 'cpu':
                torch_index = "https://download.pytorch.org/whl/cpu"
                packages = ["torch==2.1.2", "torchvision"]
            elif env_type == 'cuda118':
                torch_index = "https://download.pytorch.org/whl/cu118"
                packages = ["torch==2.1.2", "torchvision", "xformers"]
            elif env_type == 'cuda121':
                torch_index = "https://download.pytorch.org/whl/cu121"
                packages = ["torch==2.1.2", "torchvision", "xformers"]
            else:
                logger.error(f"未知的环境类型: {env_type}")
                return False
            
            logger.info(f"安装 PyTorch ({env_type})...")
            result = subprocess.run(
                [str(pip_exe), "install"] + packages + 
                ["--index-url", torch_index],
                capture_output=True,
                text=True,
                timeout=1800  # 30分钟超时
            )
            
            if result.returncode != 0:
                logger.warning(f"安装 PyTorch 出现警告: {result.stderr}")
                # 不是致命错误，继续
            
            # 2. 安装 WebUI 依赖
            # 查找 requirements_versions.txt
            webui_requirements = None
            possible_paths = [
                self.data_dir / "webui" / "requirements_versions.txt",
                self.data_dir.parent / "requirements_versions.txt",
            ]
            
            for path in possible_paths:
                if path.exists():
                    webui_requirements = path
                    break
            
            if webui_requirements:
                logger.info(f"安装 WebUI 依赖: {webui_requirements}")
                result = subprocess.run(
                    [str(pip_exe), "install", "-r", str(webui_requirements),
                     "-i", index_url],
                    capture_output=True,
                    text=True,
                    timeout=1800
                )
                
                if result.returncode != 0:
                    logger.warning(f"安装 WebUI 依赖出现警告: {result.stderr}")
            else:
                logger.warning("未找到 requirements_versions.txt，跳过 WebUI 依赖安装")
                # 安装基础包
                basic_packages = [
                    "gradio",
                    "transformers",
                    "accelerate",
                    "safetensors",
                    "Pillow",
                    "numpy",
                    "requests",
                ]
                
                logger.info("安装基础 Python 包...")
                result = subprocess.run(
                    [str(pip_exe), "install"] + basic_packages + ["-i", index_url],
                    capture_output=True,
                    text=True,
                    timeout=1800
                )
            
            logger.info("依赖安装完成")
            return True
            
        except Exception as e:
            logger.error(f"安装依赖失败: {e}")
            return False
    
    def get_python_exe(self) -> Optional[Path]:
        """获取 Python 解释器路径"""
        if self.is_environment_ready():
            return self.python_env_dir / "python.exe"
        return None
    
    def get_environment_state(self) -> Dict[str, Optional[str]]:
        """返回供运行时写入的环境状态"""
        python_exe = self.get_python_exe()
        return {
            "type": self.current_env_type,
            "path": str(self.python_env_dir),
            "python_exe": str(python_exe) if python_exe else None,
        }
    
    def run_command(self, command: list, **kwargs) -> subprocess.CompletedProcess:
        """
        使用环境中的 Python 运行命令
        
        Args:
            command: 命令列表
            **kwargs: 传递给 subprocess.run 的参数
        
        Returns:
            CompletedProcess: 运行结果
        """
        python_exe = self.get_python_exe()
        if not python_exe:
            raise RuntimeError("Python 环境未就绪")
        
        full_command = [str(python_exe)] + command
        return subprocess.run(full_command, **kwargs)


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.DEBUG)
    
    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from download_manager import DownloadManager
    
    data_dir = Path("test_data")
    cache_dir = Path("test_cache")
    
    dm = DownloadManager(cache_dir)
    ppm = PortablePythonManager(data_dir, dm)
    
    if ppm.is_environment_ready():
        print("✓ Python 环境已就绪")
        print(f"Python 路径: {ppm.get_python_exe()}")
    else:
        print("Python 环境未就绪，开始设置...")
        
        def progress(step, current, total):
            print(f"[{current}/{total}] {step}")
        
        success = ppm.setup_environment('cpu', progress)
        if success:
            print("✓ Python 环境设置成功")
        else:
            print("✗ Python 环境设置失败")

