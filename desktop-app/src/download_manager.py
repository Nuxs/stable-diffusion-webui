#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载管理器
支持断点续传、多线程下载、镜像切换
"""

import os
import hashlib
import requests
import zipfile
import time
from pathlib import Path
from typing import Optional, Callable, List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logger = logging.getLogger(__name__)


class DownloadError(Exception):
    """下载错误"""
    pass


class DownloadManager:
    """下载管理器"""
    
    def __init__(self, cache_dir: Path):
        """
        初始化下载管理器
        
        Args:
            cache_dir: 缓存目录，用于存放下载的文件
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def download_file(self,
                      url: str,
                      output_path: Optional[Path] = None,
                      filename: Optional[str] = None,
                      expected_size: Optional[int] = None,
                      expected_md5: Optional[str] = None,
                      progress_callback: Optional[Callable[[int, int], None]] = None,
                      mirrors: Optional[List[str]] = None) -> Path:
        """
        下载文件
        
        Args:
            url: 下载链接
            output_path: 输出路径（如果为 None，使用 cache_dir）
            filename: 文件名（如果为 None，从 URL 推断）
            expected_size: 预期文件大小（字节）
            expected_md5: 预期 MD5 值
            progress_callback: 进度回调函数 (当前字节数, 总字节数)
            mirrors: 镜像列表
        
        Returns:
            Path: 下载的文件路径
        
        Raises:
            DownloadError: 下载失败
        """
        # 确定输出路径
        if output_path is None:
            if filename is None:
                filename = url.split('/')[-1].split('?')[0]
            output_path = self.cache_dir / filename
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 检查是否已下载且完整
        if output_path.exists():
            if self._verify_file(output_path, expected_size, expected_md5):
                logger.info(f"文件已存在且完整: {output_path}")
                if progress_callback:
                    file_size = output_path.stat().st_size
                    progress_callback(file_size, file_size)
                return output_path
            else:
                logger.info(f"文件已存在但不完整，重新下载: {output_path}")
                output_path.unlink()
        
        # 尝试所有可用的 URL（原始 URL + 镜像）
        urls_to_try = [url]
        if mirrors:
            urls_to_try.extend(mirrors)
        
        last_error = None
        for attempt_url in urls_to_try:
            try:
                logger.info(f"开始下载: {attempt_url}")
                self._download_with_resume(
                    url=attempt_url,
                    output_path=output_path,
                    expected_size=expected_size,
                    progress_callback=progress_callback
                )
                
                # 验证下载的文件
                if not self._verify_file(output_path, expected_size, expected_md5):
                    raise DownloadError("文件校验失败")
                
                logger.info(f"下载成功: {output_path}")
                return output_path
                
            except Exception as e:
                last_error = e
                logger.warning(f"从 {attempt_url} 下载失败: {e}")
                if output_path.exists():
                    output_path.unlink()
                continue
        
        # 所有 URL 都失败了
        raise DownloadError(f"下载失败，已尝试 {len(urls_to_try)} 个URL: {last_error}")
    
    def _download_with_resume(self,
                              url: str,
                              output_path: Path,
                              expected_size: Optional[int] = None,
                              progress_callback: Optional[Callable[[int, int], None]] = None):
        """
        支持断点续传的下载
        
        Args:
            url: 下载链接
            output_path: 输出路径
            expected_size: 预期文件大小
            progress_callback: 进度回调
        """
        # 检查是否支持断点续传
        temp_path = output_path.with_suffix(output_path.suffix + '.part')
        
        # 获取已下载的大小
        downloaded_size = 0
        if temp_path.exists():
            downloaded_size = temp_path.stat().st_size
            logger.debug(f"检测到部分下载文件，已下载: {downloaded_size} 字节")
        
        # 发起请求
        headers = {}
        if downloaded_size > 0:
            headers['Range'] = f'bytes={downloaded_size}-'
        
        try:
            response = self.session.get(url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            
            # 检查是否支持断点续传
            if downloaded_size > 0 and response.status_code != 206:
                logger.warning("服务器不支持断点续传，重新下载")
                downloaded_size = 0
                if temp_path.exists():
                    temp_path.unlink()
            
            # 获取总大小
            total_size = downloaded_size
            content_length = response.headers.get('Content-Length')
            if content_length:
                total_size += int(content_length)
            elif expected_size:
                total_size = expected_size
            
            # 下载文件
            mode = 'ab' if downloaded_size > 0 else 'wb'
            with open(temp_path, mode) as f:
                start_time = time.time()
                last_update_time = start_time
                
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # 更新进度（每 0.5 秒更新一次）
                        current_time = time.time()
                        if progress_callback and (current_time - last_update_time >= 0.5 or downloaded_size >= total_size):
                            progress_callback(downloaded_size, total_size if total_size > 0 else downloaded_size)
                            last_update_time = current_time
            
            # 下载完成，重命名文件
            if output_path.exists():
                output_path.unlink()
            temp_path.rename(output_path)
            
            # 最后一次进度更新
            if progress_callback:
                progress_callback(downloaded_size, downloaded_size)
            
            elapsed_time = time.time() - start_time
            speed_mbps = (downloaded_size / (1024 * 1024)) / elapsed_time if elapsed_time > 0 else 0
            logger.info(f"下载完成: {downloaded_size} 字节, 耗时: {elapsed_time:.1f}秒, 速度: {speed_mbps:.2f} MB/s")
            
        except Exception as e:
            logger.error(f"下载出错: {e}")
            raise
    
    def _verify_file(self,
                     file_path: Path,
                     expected_size: Optional[int] = None,
                     expected_md5: Optional[str] = None) -> bool:
        """
        验证文件
        
        Args:
            file_path: 文件路径
            expected_size: 预期大小（字节）
            expected_md5: 预期 MD5
        
        Returns:
            bool: 是否验证通过
        """
        if not file_path.exists():
            return False
        
        # 检查大小
        if expected_size is not None:
            actual_size = file_path.stat().st_size
            if actual_size != expected_size:
                logger.warning(f"文件大小不匹配: 预期 {expected_size}, 实际 {actual_size}")
                return False
        
        # 检查 MD5
        if expected_md5:
            actual_md5 = self._calculate_md5(file_path)
            if actual_md5.lower() != expected_md5.lower():
                logger.warning(f"MD5 不匹配: 预期 {expected_md5}, 实际 {actual_md5}")
                return False
            logger.debug(f"MD5 校验通过: {actual_md5}")
        
        return True
    
    def _calculate_md5(self, file_path: Path) -> str:
        """计算文件的 MD5"""
        md5_hash = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
    
    def extract_archive(self,
                       archive_path: Path,
                       target_dir: Path,
                       progress_callback: Optional[Callable[[int, int], None]] = None) -> bool:
        """
        解压归档文件
        
        Args:
            archive_path: 归档文件路径
            target_dir: 目标目录
            progress_callback: 进度回调
        
        Returns:
            bool: 是否成功
        """
        target_dir = Path(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"开始解压: {archive_path} -> {target_dir}")
        
        try:
            if archive_path.suffix.lower() == '.zip':
                return self._extract_zip(archive_path, target_dir, progress_callback)
            elif archive_path.suffix.lower() in ['.7z', '.7zip']:
                return self._extract_7z(archive_path, target_dir, progress_callback)
            else:
                logger.error(f"不支持的归档格式: {archive_path.suffix}")
                return False
        except Exception as e:
            logger.error(f"解压失败: {e}", exc_info=True)
            return False
    
    def _extract_zip(self,
                    zip_path: Path,
                    target_dir: Path,
                    progress_callback: Optional[Callable[[int, int], None]] = None) -> bool:
        """解压 ZIP 文件"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                members = zipf.namelist()
                total = len(members)
                
                for i, member in enumerate(members):
                    zipf.extract(member, target_dir)
                    
                    if progress_callback and (i % 10 == 0 or i == total - 1):
                        progress_callback(i + 1, total)
            
            logger.info(f"ZIP 解压完成: {total} 个文件")
            return True
        except Exception as e:
            logger.error(f"ZIP 解压失败: {e}")
            return False
    
    def _extract_7z(self,
                   archive_path: Path,
                   target_dir: Path,
                   progress_callback: Optional[Callable[[int, int], None]] = None) -> bool:
        """解压 7z 文件"""
        # 尝试使用 7z 命令
        import shutil
        if shutil.which("7z"):
            try:
                import subprocess
                cmd = ['7z', 'x', str(archive_path), f'-o{target_dir}', '-y']
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # TODO: 解析输出以更新进度
                stdout, stderr = process.communicate()
                
                if process.returncode == 0:
                    logger.info("7z 解压完成")
                    if progress_callback:
                        progress_callback(1, 1)
                    return True
                else:
                    logger.error(f"7z 解压失败: {stderr}")
                    return False
            except Exception as e:
                logger.error(f"调用 7z 命令失败: {e}")
        
        # 尝试使用 py7zr
        try:
            import py7zr
            with py7zr.SevenZipFile(archive_path, mode='r') as archive:
                archive.extractall(path=target_dir)
            logger.info("py7zr 解压完成")
            if progress_callback:
                progress_callback(1, 1)
            return True
        except ImportError:
            logger.error("未安装 py7zr，无法解压 7z 文件")
            logger.error("请安装 7-Zip: https://www.7-zip.org/")
            return False
        except Exception as e:
            logger.error(f"py7zr 解压失败: {e}")
            return False


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.DEBUG)
    
    cache_dir = Path("test_cache")
    dm = DownloadManager(cache_dir)
    
    # 测试下载小文件
    def progress(current, total):
        percent = (current / total * 100) if total > 0 else 0
        print(f"\r下载进度: {percent:.1f}% ({current}/{total})", end='')
    
    try:
        test_url = "https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip"
        file_path = dm.download_file(
            url=test_url,
            filename="python-test.zip",
            progress_callback=progress
        )
        print(f"\n下载成功: {file_path}")
    except DownloadError as e:
        print(f"\n下载失败: {e}")

