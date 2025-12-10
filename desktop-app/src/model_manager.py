#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型管理器
管理 Stable Diffusion 模型的下载、安装和验证
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Callable

logger = logging.getLogger(__name__)


class ModelManager:
    """模型管理器"""
    
    def __init__(self, data_dir: Path, download_manager):
        """
        初始化模型管理器
        
        Args:
            data_dir: 数据目录
            download_manager: 下载管理器实例
        """
        self.data_dir = Path(data_dir)
        self.models_dir = self.data_dir / "models" / "Stable-diffusion"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.dm = download_manager
        self.available_models = self._load_model_catalog()
    
    def _load_model_catalog(self) -> Dict:
        """从配置文件加载模型目录"""
        try:
            # 查找配置文件
            config_paths = [
                Path(__file__).parent.parent / "config" / "components.json",
                Path(__file__).parent.parent.parent / "config" / "components.json",
            ]
            
            config_path = None
            for path in config_paths:
                if path.exists():
                    config_path = path
                    break
            
            if not config_path:
                logger.error("未找到 components.json 配置文件")
                return {}
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('models', {})
        except Exception as e:
            logger.error(f"加载模型目录失败: {e}")
            return {}
    
    def list_available_models(self, filter_by_vram: Optional[int] = None) -> List[Dict]:
        """
        列出可用的模型
        
        Args:
            filter_by_vram: 根据显存过滤（字节）
        
        Returns:
            List[Dict]: 模型信息列表
        """
        models = []
        
        for model_id, model_info in self.available_models.items():
            # 检查显存要求
            if filter_by_vram is not None:
                required_vram = model_info.get('requirements', {}).get('vram_bytes', 0)
                if required_vram > filter_by_vram:
                    # 显存不足，标记但仍然列出
                    model_info['vram_insufficient'] = True
            
            # 检查是否已安装
            model_info['installed'] = self.is_model_installed(model_id)
            model_info['id'] = model_id
            
            models.append(model_info)
        
        # 推荐的模型排在前面
        models.sort(key=lambda m: (not m.get('recommended', False), m['name']))
        
        return models
    
    def is_model_installed(self, model_id: str) -> bool:
        """
        检查模型是否已安装
        
        Args:
            model_id: 模型ID
        
        Returns:
            bool: 是否已安装
        """
        model_info = self.available_models.get(model_id)
        if not model_info:
            return False
        
        filename = model_info.get('filename')
        if not filename:
            return False
        
        model_path = self.models_dir / filename
        return model_path.exists()
    
    def get_installed_models(self) -> List[str]:
        """
        获取已安装的模型列表
        
        Returns:
            List[str]: 模型ID列表
        """
        installed = []
        for model_id in self.available_models.keys():
            if self.is_model_installed(model_id):
                installed.append(model_id)
        return installed
    
    def download_model(self,
                      model_id: str,
                      progress_callback: Optional[Callable[[int, int], None]] = None) -> Optional[Path]:
        """
        下载模型
        
        Args:
            model_id: 模型ID
            progress_callback: 进度回调函数 (当前字节数, 总字节数)
        
        Returns:
            Path: 模型文件路径，失败返回 None
        """
        model_info = self.available_models.get(model_id)
        if not model_info:
            logger.error(f"未知的模型ID: {model_id}")
            return None
        
        # 检查是否已安装
        if self.is_model_installed(model_id):
            logger.info(f"模型已安装: {model_id}")
            return self.models_dir / model_info['filename']
        
        try:
            logger.info(f"开始下载模型: {model_info['name']}")
            
            # 下载模型文件
            model_file = self.dm.download_file(
                url=model_info['url'],
                output_path=self.models_dir / model_info['filename'],
                expected_size=model_info.get('size_bytes'),
                expected_md5=model_info.get('md5'),
                progress_callback=progress_callback,
                mirrors=model_info.get('mirrors', [])
            )
            
            logger.info(f"模型下载成功: {model_file}")
            return model_file
            
        except Exception as e:
            logger.error(f"下载模型失败: {e}", exc_info=True)
            return None
    
    def download_models(self,
                       model_ids: List[str],
                       progress_callback: Optional[Callable[[str, int, int], None]] = None) -> Dict[str, bool]:
        """
        批量下载模型
        
        Args:
            model_ids: 模型ID列表
            progress_callback: 进度回调 (模型名称, 当前字节数, 总字节数)
        
        Returns:
            Dict[str, bool]: 下载结果 {model_id: 是否成功}
        """
        results = {}
        
        for model_id in model_ids:
            model_info = self.available_models.get(model_id)
            if not model_info:
                results[model_id] = False
                continue
            
            # 包装进度回调，添加模型名称
            def wrapped_callback(current, total):
                if progress_callback:
                    progress_callback(model_info['name'], current, total)
            
            model_path = self.download_model(model_id, wrapped_callback)
            results[model_id] = model_path is not None
        
        return results
    
    def get_model_info(self, model_id: str) -> Optional[Dict]:
        """
        获取模型信息
        
        Args:
            model_id: 模型ID
        
        Returns:
            Dict: 模型信息，不存在返回 None
        """
        return self.available_models.get(model_id)
    
    def delete_model(self, model_id: str) -> bool:
        """
        删除模型
        
        Args:
            model_id: 模型ID
        
        Returns:
            bool: 是否成功
        """
        model_info = self.available_models.get(model_id)
        if not model_info:
            return False
        
        model_path = self.models_dir / model_info['filename']
        if not model_path.exists():
            return False
        
        try:
            model_path.unlink()
            logger.info(f"模型已删除: {model_id}")
            return True
        except Exception as e:
            logger.error(f"删除模型失败: {e}")
            return False
    
    def get_models_total_size(self, model_ids: List[str]) -> int:
        """
        计算模型的总大小
        
        Args:
            model_ids: 模型ID列表
        
        Returns:
            int: 总大小（字节）
        """
        total = 0
        for model_id in model_ids:
            model_info = self.available_models.get(model_id)
            if model_info:
                total += model_info.get('size_bytes', 0)
        return total


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.DEBUG)
    
    from pathlib import Path
    from download_manager import DownloadManager
    
    data_dir = Path("test_data")
    cache_dir = Path("test_cache")
    
    dm = DownloadManager(cache_dir)
    mm = ModelManager(data_dir, dm)
    
    print("可用模型:")
    for model in mm.list_available_models():
        status = "已安装" if model['installed'] else "未安装"
        print(f"  - {model['name']} ({model['size_display']}) [{status}]")
    
    print(f"\n已安装模型: {mm.get_installed_models()}")

