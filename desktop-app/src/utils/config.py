#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


class Config:
    """配置类"""
    
    def __init__(self, config_file: Path = None):
        if config_file is None:
            # 检测是否在打包环境中
            import sys
            if getattr(sys, 'frozen', False):
                # 打包后，配置文件放在 exe 所在目录
                if hasattr(sys, '_MEIPASS'):
                    config_file = Path(sys.executable).parent / "config" / "app_config.json"
                else:
                    config_file = Path(sys.executable).parent / "config" / "app_config.json"
            else:
                # 开发模式
                config_file = Path(__file__).parent.parent.parent / "config" / "app_config.json"
            
        self.config_file = config_file
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self._config: Dict[str, Any] = self.load()
        
    def load(self) -> Dict[str, Any]:
        """加载配置"""
        default_config = {
            "port": 7860,
            "api": False,
            "listen": "127.0.0.1",
            "theme": "default",
            "window_width": 1200,
            "window_height": 800,
            "webui_project_path": None,  # WebUI 项目路径，None 表示自动检测
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.error(f"加载配置失败: {e}")
                
        return default_config
        
    def save(self):
        """保存配置"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self._config.get(key, default)
        
    def set(self, key: str, value: Any):
        """设置配置值"""
        self._config[key] = value
        self.save()
        
    def get_port(self) -> int:
        """获取端口号"""
        return self.get("port", 7860)
        
    def set_port(self, port: int):
        """设置端口号"""
        self.set("port", port)

