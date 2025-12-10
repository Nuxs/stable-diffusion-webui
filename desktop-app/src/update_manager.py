#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新管理器
检查和应用应用程序更新
"""

import json
import logging
import requests
from pathlib import Path
from typing import Dict, Optional, List
from packaging import version

logger = logging.getLogger(__name__)


class UpdateManager:
    """更新管理器"""
    
    # 更新服务器配置
    UPDATE_CHECK_URL = "https://api.github.com/repos/AUTOMATIC1111/stable-diffusion-webui/releases/latest"
    VERSION_FILE = "version.json"
    
    def __init__(self, app_dir: Path, current_version: str = "2.0.0"):
        """
        初始化更新管理器
        
        Args:
            app_dir: 应用目录
            current_version: 当前版本号
        """
        self.app_dir = Path(app_dir)
        self.current_version = current_version
        self.version_file = self.app_dir / self.VERSION_FILE
        
        # 加载版本信息
        self.version_info = self._load_version_info()
    
    def _load_version_info(self) -> Dict:
        """加载版本信息文件"""
        default_info = {
            "app": self.current_version,
            "webui": "unknown",
            "python_env": "1.0.0",
            "last_check": None,
        }
        
        if not self.version_file.exists():
            return default_info
        
        try:
            with open(self.version_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载版本信息失败: {e}")
            return default_info
    
    def _save_version_info(self):
        """保存版本信息"""
        try:
            with open(self.version_file, 'w', encoding='utf-8') as f:
                json.dump(self.version_info, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存版本信息失败: {e}")
    
    def check_for_updates(self, component: str = "webui") -> Optional[Dict]:
        """
        检查更新
        
        Args:
            component: 组件名称 ('app', 'webui', 'python_env')
        
        Returns:
            Dict: 更新信息，如果没有更新则返回 None
            {
                "component": "webui",
                "current_version": "1.7.0",
                "latest_version": "1.8.0",
                "release_notes": "...",
                "download_url": "...",
                "size": 52428800,
            }
        """
        try:
            logger.info(f"检查 {component} 更新...")
            
            if component == "webui":
                return self._check_webui_update()
            elif component == "app":
                return self._check_app_update()
            else:
                logger.warning(f"不支持的组件: {component}")
                return None
                
        except Exception as e:
            logger.error(f"检查更新失败: {e}")
            return None
    
    def _check_webui_update(self) -> Optional[Dict]:
        """检查 WebUI 更新"""
        try:
            # 从 GitHub API 获取最新版本
            response = requests.get(
                self.UPDATE_CHECK_URL,
                timeout=10,
                headers={'Accept': 'application/vnd.github.v3+json'}
            )
            response.raise_for_status()
            
            release_data = response.json()
            latest_version = release_data['tag_name'].lstrip('v')
            current_version = self.version_info.get('webui', '0.0.0')
            
            # 比较版本
            if version.parse(latest_version) > version.parse(current_version):
                logger.info(f"发现新版本: {latest_version} (当前: {current_version})")
                
                # 获取下载链接和大小
                assets = release_data.get('assets', [])
                download_url = None
                file_size = 0
                
                # 查找 ZIP 文件
                for asset in assets:
                    if asset['name'].endswith('.zip'):
                        download_url = asset['browser_download_url']
                        file_size = asset['size']
                        break
                
                # 如果没有资产，使用源代码 ZIP
                if not download_url:
                    download_url = release_data.get('zipball_url')
                
                return {
                    "component": "webui",
                    "current_version": current_version,
                    "latest_version": latest_version,
                    "release_notes": release_data.get('body', ''),
                    "download_url": download_url,
                    "size": file_size,
                    "published_at": release_data.get('published_at'),
                }
            else:
                logger.info(f"已是最新版本: {current_version}")
                return None
                
        except Exception as e:
            logger.error(f"检查 WebUI 更新失败: {e}")
            return None
    
    def _check_app_update(self) -> Optional[Dict]:
        """检查应用本身的更新"""
        # TODO: 实现应用更新检查
        # 这通常需要一个专门的更新服务器
        logger.info("应用更新检查暂未实现")
        return None
    
    def apply_update(self,
                     update_info: Dict,
                     download_callback: Optional[callable] = None) -> bool:
        """
        应用更新
        
        Args:
            update_info: 更新信息（来自 check_for_updates）
            download_callback: 下载进度回调
        
        Returns:
            bool: 是否成功
        """
        component = update_info["component"]
        
        try:
            if component == "webui":
                return self._apply_webui_update(update_info, download_callback)
            elif component == "app":
                return self._apply_app_update(update_info, download_callback)
            else:
                logger.error(f"不支持的组件: {component}")
                return False
        except Exception as e:
            logger.error(f"应用更新失败: {e}", exc_info=True)
            return False
    
    def _apply_webui_update(self,
                           update_info: Dict,
                           download_callback: Optional[callable] = None) -> bool:
        """应用 WebUI 更新"""
        # TODO: 实现 WebUI 更新逻辑
        # 1. 下载新版本
        # 2. 备份当前版本
        # 3. 解压并替换文件
        # 4. 更新版本信息
        logger.info("WebUI 更新应用暂未完全实现")
        return False
    
    def _apply_app_update(self,
                         update_info: Dict,
                         download_callback: Optional[callable] = None) -> bool:
        """应用应用程序更新"""
        # TODO: 实现应用程序自更新
        # 这通常需要一个单独的更新程序
        logger.info("应用程序自更新暂未实现")
        return False
    
    def get_update_history(self) -> List[Dict]:
        """获取更新历史"""
        # TODO: 从某个地方读取更新历史
        return []
    
    def rollback(self, component: str) -> bool:
        """
        回滚到上一个版本
        
        Args:
            component: 组件名称
        
        Returns:
            bool: 是否成功
        """
        # TODO: 实现回滚功能
        logger.info(f"回滚 {component} 暂未实现")
        return False


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.DEBUG)
    
    um = UpdateManager(Path("."))
    
    print("当前版本信息:")
    print(json.dumps(um.version_info, indent=2, ensure_ascii=False))
    
    print("\n检查 WebUI 更新...")
    update = um.check_for_updates("webui")
    
    if update:
        print(f"\n发现更新:")
        print(f"  当前版本: {update['current_version']}")
        print(f"  最新版本: {update['latest_version']}")
        print(f"  大小: {update.get('size', 0) / (1024*1024):.2f} MB")
        print(f"  下载地址: {update['download_url']}")
    else:
        print("\n已是最新版本")
