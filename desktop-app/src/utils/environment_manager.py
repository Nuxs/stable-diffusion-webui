#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境管理器：处理venv环境的解压和设置
用于分离式打包方案
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class EnvironmentManager:
    """环境管理器"""
    
    def __init__(self, app_dir: Path):
        """
        初始化环境管理器
        
        Args:
            app_dir: 应用目录（exe所在目录）
        """
        self.app_dir = Path(app_dir)
        self.venv_dir = self.app_dir / "venv"
        # 支持.7z和.zip两种格式
        env_dir = self.app_dir / "environment"
        if (env_dir / "venv.7z").exists():
            self.env_package = env_dir / "venv.7z"
        elif (env_dir / "venv.zip").exists():
            self.env_package = env_dir / "venv.zip"
        else:
            self.env_package = env_dir / "venv.7z"  # 默认
        self.python_exe = self.venv_dir / "Scripts" / "python.exe"
        
    def is_environment_ready(self) -> bool:
        """检查环境是否已准备好"""
        return self.python_exe.exists()
    
    def extract_environment(self) -> bool:
        """解压环境包"""
        if not self.env_package.exists():
            logger.error(f"环境包不存在: {self.env_package}")
            return False
        
        if self.venv_dir.exists():
            logger.warning(f"venv目录已存在: {self.venv_dir}")
            response = input("是否删除现有环境并重新解压? (y/n): ")
            if response.lower() != 'y':
                return False
            shutil.rmtree(self.venv_dir)
        
        logger.info(f"开始解压环境包: {self.env_package}")
        logger.info(f"目标目录: {self.venv_dir}")
        logger.info("这可能需要5-10分钟，请耐心等待...")
        
        # 检查7z是否可用
        if self._check_7zip():
            return self._extract_with_7zip()
        else:
            # 使用Python的zipfile（如果7z不可用，尝试其他方法）
            logger.warning("7z不可用，尝试其他解压方法...")
            return self._extract_with_python()
    
    def _check_7zip(self) -> bool:
        """检查7-Zip是否可用"""
        try:
            result = subprocess.run(['7z'], capture_output=True, text=True, timeout=5)
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _extract_with_7zip(self) -> bool:
        """使用7z解压"""
        try:
            cmd = ['7z', 'x', str(self.env_package), f'-o{self.app_dir}', '-y']
            result = subprocess.run(cmd, check=True, text=True, capture_output=True)
            logger.info("✓ 环境解压完成")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"解压失败: {e}")
            logger.error(f"错误输出: {e.stderr}")
            return False
    
    def _extract_with_python(self) -> bool:
        """使用Python解压（备用方案）"""
        # 如果是.7z格式，尝试使用py7zr
        if self.env_package.suffix == '.7z':
            try:
                import py7zr
                logger.info("使用py7zr解压7z文件...")
                with py7zr.SevenZipFile(self.env_package, mode='r') as archive:
                    archive.extractall(path=self.app_dir)
                logger.info("✓ 环境解压完成")
                return True
            except ImportError:
                logger.warning("py7zr未安装，尝试使用zipfile...")
            except Exception as e:
                logger.error(f"py7zr解压失败: {e}")
        
        # 如果是.zip格式或py7zr不可用，使用zipfile
        if self.env_package.suffix == '.zip':
            try:
                import zipfile
                logger.info("使用zipfile解压zip文件...")
                with zipfile.ZipFile(self.env_package, 'r') as zipf:
                    zipf.extractall(path=self.app_dir)
                logger.info("✓ 环境解压完成")
                return True
            except Exception as e:
                logger.error(f"zipfile解压失败: {e}")
                return False
        
        # 如果都不行，提示用户
        logger.error("无法解压环境包")
        logger.error("请安装以下工具之一：")
        logger.error("1. 7-Zip: https://www.7-zip.org/")
        logger.error("2. 或安装py7zr: pip install py7zr")
        logger.error("")
        logger.error("或者手动解压:")
        logger.error(f"  将 {self.env_package} 解压到 {self.app_dir}")
        return False
    
    def setup_environment(self) -> bool:
        """设置环境（解压并验证）"""
        if self.is_environment_ready():
            logger.info("环境已准备好")
            return True
        
        logger.info("环境未准备好，开始解压...")
        if not self.extract_environment():
            return False
        
        # 验证环境
        if not self.is_environment_ready():
            logger.error("环境解压后验证失败")
            return False
        
        logger.info("✓ 环境设置完成")
        return True
    
    def get_python_exe(self) -> Optional[Path]:
        """获取Python解释器路径"""
        if self.is_environment_ready():
            return self.python_exe
        return None


def setup_runtime_environment(app_dir: Path) -> Optional[Path]:
    """
    设置运行时环境
    
    Args:
        app_dir: 应用目录
        
    Returns:
        Python解释器路径，如果设置失败返回None
    """
    manager = EnvironmentManager(app_dir)
    
    if not manager.setup_environment():
        return None
    
    return manager.get_python_exe()

