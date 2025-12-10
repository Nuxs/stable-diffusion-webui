#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志配置
"""

import logging
import sys
from pathlib import Path


def setup_logging(log_level=logging.INFO):
    """设置日志"""
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "app.log"
    
    # 配置日志格式
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # 配置日志
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # 设置第三方库的日志级别
    logging.getLogger("PyQt6").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)



