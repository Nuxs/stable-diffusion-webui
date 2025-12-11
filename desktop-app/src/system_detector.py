#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统信息检测器
检测操作系统、GPU、磁盘空间等信息
"""

import subprocess
import shutil
import platform
import re
from pathlib import Path
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class SystemDetector:
    """系统信息检测器"""
    
    @staticmethod
    def detect_all() -> Dict:
        """检测所有系统信息"""
        logger.info("开始检测系统信息...")
        
        system_info = {
            "os": SystemDetector.detect_os(),
            "gpu": SystemDetector.detect_gpu(),
            "disk": SystemDetector.detect_disk_space(),
            "runtime": SystemDetector.detect_runtime(),
        }
        
        logger.info(f"系统信息检测完成: {system_info}")
        return system_info
    
    @staticmethod
    def detect_os() -> Dict:
        """检测操作系统"""
        os_info = {
            "system": platform.system(),  # Windows
            "release": platform.release(),  # 10
            "version": platform.version(),  # 10.0.19041
            "machine": platform.machine(),  # AMD64
            "processor": platform.processor(),
            "platform": platform.platform(),
        }
        logger.debug(f"操作系统信息: {os_info}")
        return os_info
    
    @staticmethod
    def detect_gpu() -> Dict:
        """检测 GPU 信息"""
        gpu_info = {
            "vendor": None,  # NVIDIA, AMD, Intel
            "name": None,
            "vram": None,  # MB
            "vram_bytes": None,
            "cuda_available": False,
            "cuda_version": None,
            "driver_version": None,
        }
        
        # 尝试检测 NVIDIA GPU
        if shutil.which("nvidia-smi"):
            try:
                # 查询 GPU 名称和显存
                result = subprocess.run(
                    ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if lines and lines[0]:
                        parts = lines[0].split(', ')
                        if len(parts) >= 2:
                            gpu_info["vendor"] = "NVIDIA"
                            gpu_info["name"] = parts[0].strip()
                            # "12288 MiB" -> 12288
                            vram_str = parts[1].strip().split()[0]
                            gpu_info["vram"] = int(vram_str)
                            gpu_info["vram_bytes"] = gpu_info["vram"] * 1024 * 1024
                            gpu_info["cuda_available"] = True
                            
                            logger.info(f"检测到 NVIDIA GPU: {gpu_info['name']}, 显存: {gpu_info['vram']} MB")
                
                # 检测 CUDA 版本
                cuda_result = subprocess.run(
                    ["nvidia-smi"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if cuda_result.returncode == 0:
                    # 解析 "CUDA Version: 12.1"
                    cuda_match = re.search(r'CUDA Version:\s*([\d.]+)', cuda_result.stdout)
                    if cuda_match:
                        gpu_info["cuda_version"] = cuda_match.group(1)
                        logger.info(f"CUDA 版本: {gpu_info['cuda_version']}")
                    
                    # 解析驱动版本
                    driver_match = re.search(r'Driver Version:\s*([\d.]+)', cuda_result.stdout)
                    if driver_match:
                        gpu_info["driver_version"] = driver_match.group(1)
                        logger.info(f"驱动版本: {gpu_info['driver_version']}")
                        
            except Exception as e:
                logger.warning(f"检测 NVIDIA GPU 时出错: {e}")
        
        # TODO: 检测 AMD GPU (使用 rocm-smi)
        # TODO: 检测 Intel GPU
        
        if gpu_info["vendor"] is None:
            logger.info("未检测到独立显卡")
        
        return gpu_info
    
    @staticmethod
    def detect_disk_space(path: Optional[Path] = None) -> Dict:
        """检测磁盘空间"""
        if path is None:
            path = Path.cwd()
        
        try:
            usage = shutil.disk_usage(path)
            
            disk_info = {
                "total": usage.total,  # bytes
                "used": usage.used,
                "free": usage.free,
                "total_gb": round(usage.total / (1024**3), 2),
                "free_gb": round(usage.free / (1024**3), 2),
                "used_gb": round(usage.used / (1024**3), 2),
                "percent_used": round((usage.used / usage.total) * 100, 1),
            }
            
            logger.info(f"磁盘空间: 总计 {disk_info['total_gb']} GB, "
                       f"可用 {disk_info['free_gb']} GB ({100 - disk_info['percent_used']:.1f}%)")
            
            return disk_info
        except Exception as e:
            logger.error(f"检测磁盘空间时出错: {e}")
            return {
                "total": 0,
                "used": 0,
                "free": 0,
                "total_gb": 0,
                "free_gb": 0,
                "used_gb": 0,
                "percent_used": 0,
            }
    
    @staticmethod
    def detect_runtime() -> Dict:
        """检测运行时依赖"""
        runtime_info = {
            "vcredist_installed": False,
            "vcredist_version": None,
        }
        
        # 检测 VC++ Redistributable（检查注册表）
        try:
            import winreg
            key_paths = [
                r"SOFTWARE\\Microsoft\\VisualStudio\\14.0\\VC\\Runtimes\\x64",
                r"SOFTWARE\\WOW6432Node\\Microsoft\\VisualStudio\\14.0\\VC\\Runtimes\\x64",
            ]
            for key_path in key_paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                    try:
                        version, _ = winreg.QueryValueEx(key, "Version")
                        runtime_info["vcredist_installed"] = True
                        runtime_info["vcredist_version"] = version
                        logger.info(f"检测到 VC++ Redistributable: {version}")
                    except:
                        runtime_info["vcredist_installed"] = True
                    winreg.CloseKey(key)
                    break
                except FileNotFoundError:
                    continue
        except Exception as e:
            logger.warning(f"检测 VC++ Redistributable 时出错: {e}")
        
        if not runtime_info["vcredist_installed"]:
            logger.warning("未检测到 Visual C++ Redistributable")
        
        return runtime_info
    
    @staticmethod
    def recommend_python_env(system_info: Dict) -> str:
        """根据系统信息推荐 Python 环境类型
        
        Returns:
            str: 'cpu', 'cuda118', 'cuda121'
        """
        gpu = system_info.get("gpu", {})
        
        # 没有 NVIDIA GPU，使用 CPU 版本
        if not gpu.get("cuda_available"):
            logger.info("推荐 Python 环境: CPU 版本（无 CUDA 支持）")
            return "cpu"
        
        # 检查 CUDA 版本
        cuda_version = gpu.get("cuda_version", "")
        if cuda_version:
            major_version = cuda_version.split('.')[0]
            if major_version == "11":
                logger.info(f"推荐 Python 环境: CUDA 11.8（当前 CUDA: {cuda_version}）")
                return "cuda118"
            elif major_version == "12":
                logger.info(f"推荐 Python 环境: CUDA 12.1（当前 CUDA: {cuda_version}）")
                return "cuda121"
        
        # 默认使用 CUDA 11.8（兼容性最好）
        logger.info("推荐 Python 环境: CUDA 11.8（默认）")
        return "cuda118"
    
    @staticmethod
    def check_minimum_requirements(system_info: Dict) -> tuple[bool, list[str]]:
        """检查是否满足最低系统要求
        
        Returns:
            tuple: (是否满足, 错误信息列表)
        """
        errors = []
        
        # 检查操作系统
        os_info = system_info.get("os", {})
        if os_info.get("system") != "Windows":
            errors.append("当前仅支持 Windows 操作系统")
        
        # 检查磁盘空间（至少需要 10GB）
        disk = system_info.get("disk", {})
        free_gb = disk.get("free_gb", 0)
        if free_gb < 10:
            errors.append(f"磁盘空间不足（可用: {free_gb:.1f} GB, 需要: 至少 10 GB）")
        
        # 检查 VC++ Redistributable
        runtime = system_info.get("runtime", {})
        if not runtime.get("vcredist_installed"):
            errors.append("未安装 Visual C++ Redistributable 2015-2022")
        
        # 如果有 GPU，检查显存（至少需要 4GB）
        gpu = system_info.get("gpu", {})
        if gpu.get("cuda_available"):
            vram = gpu.get("vram", 0)
            if vram < 4096:  # 4GB in MB
                # 这不是致命错误，只是警告
                logger.warning(f"显存较低（{vram} MB），建议至少 4GB 显存以获得更好性能")
        
        return len(errors) == 0, errors


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.DEBUG)
    
    detector = SystemDetector()
    system_info = detector.detect_all()
    
    print("\n=== 系统信息 ===")
    print(f"操作系统: {system_info['os']['platform']}")
    print(f"处理器: {system_info['os']['processor']}")
    print(f"\nGPU: {system_info['gpu']['name'] or '未检测到'}")
    if system_info['gpu']['cuda_available']:
        print(f"显存: {system_info['gpu']['vram']} MB")
        print(f"CUDA: {system_info['gpu']['cuda_version']}")
    print(f"\n磁盘空间: {system_info['disk']['free_gb']} GB 可用 / {system_info['disk']['total_gb']} GB 总计")
    print(f"VC++ Runtime: {'已安装' if system_info['runtime']['vcredist_installed'] else '未安装'}")
    
    print(f"\n推荐环境: {detector.recommend_python_env(system_info)}")
    
    meets_req, errors = detector.check_minimum_requirements(system_info)
    if meets_req:
        print("\n✓ 系统满足最低要求")
    else:
        print("\n✗ 系统不满足最低要求:")
        for error in errors:
            print(f"  - {error}")

