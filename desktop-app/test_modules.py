#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块测试脚本
测试各个模块能否独立运行
"""

import sys
import os
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_imports():
    """测试所有模块导入"""
    print("=" * 60)
    print("模块导入测试")
    print("=" * 60)
    
    modules_to_test = [
        ("system_detector", "SystemDetector"),
        ("download_manager", "DownloadManager"),
        ("model_manager", "ModelManager"),
        ("utils.config", "Config"),
        ("utils.logger", "setup_logging"),
        ("utils.portable_python", "PortablePythonManager"),
    ]
    
    failed = []
    
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"[OK] {module_name}.{class_name}")
        except Exception as e:
            print(f"[X] {module_name}.{class_name}: {e}")
            failed.append((module_name, class_name, e))
    
    if failed:
        print(f"\n{len(failed)} 个模块导入失败")
        return False
    else:
        print(f"\n所有模块导入成功")
        return True


def test_system_detector():
    """测试系统检测器"""
    print("\n" + "=" * 60)
    print("系统检测器测试")
    print("=" * 60)
    
    try:
        from system_detector import SystemDetector
        
        # 测试检测功能
        system_info = SystemDetector.detect_all()
        
        print(f"\n操作系统: {system_info['os']['system']} {system_info['os']['release']}")
        print(f"GPU: {system_info['gpu'].get('name', '未检测到')}")
        if system_info['gpu'].get('cuda_available'):
            print(f"  CUDA: {system_info['gpu'].get('cuda_version', 'N/A')}")
            print(f"  显存: {system_info['gpu'].get('vram', 0)} MB")
        
        print(f"磁盘: {system_info['disk']['free_gb']} GB 可用 / {system_info['disk']['total_gb']} GB 总计")
        print(f"VC++ Runtime: {'已安装' if system_info['runtime']['vcredist_installed'] else '未安装'}")
        
        # 测试推荐环境
        recommended = SystemDetector.recommend_python_env(system_info)
        print(f"\n推荐 Python 环境: {recommended}")
        
        # 测试最低要求检查
        meets_req, errors = SystemDetector.check_minimum_requirements(system_info)
        if meets_req:
            print("[OK] 系统满足最低要求")
        else:
            print("[X] 系统不满足最低要求:")
            for error in errors:
                print(f"  - {error}")
        
        return True
        
    except Exception as e:
        print(f"[X] 系统检测器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config():
    """测试配置管理"""
    print("\n" + "=" * 60)
    print("配置管理测试")
    print("=" * 60)
    
    try:
        from utils.config import Config
        
        config = Config()
        
        # 测试加载组件配置
        python_envs = config.get_python_environments()
        print(f"\n可用 Python 环境: {len(python_envs)}")
        for env_id, env_info in python_envs.items():
            print(f"  - {env_id}: {env_info['name']}")
        
        models = config.get_models()
        print(f"\n可用模型: {len(models)}")
        for model_id, model_info in models.items():
            print(f"  - {model_id}: {model_info['name']} ({model_info['size_display']})")
        
        return True
        
    except Exception as e:
        print(f"[X] 配置管理测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_logger():
    """测试日志系统"""
    print("\n" + "=" * 60)
    print("日志系统测试")
    print("=" * 60)
    
    try:
        from utils.logger import setup_logging
        import logging
        
        setup_logging()
        logger = logging.getLogger("test")
        
        logger.debug("调试信息")
        logger.info("普通信息")
        logger.warning("警告信息")
        logger.error("错误信息")
        
        print("[OK] 日志系统正常")
        return True
        
    except Exception as e:
        print(f"[X] 日志系统测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n开始测试各个模块...\n")
    
    tests = [
        ("模块导入", test_imports),
        ("系统检测器", test_system_detector),
        ("配置管理", test_config),
        ("日志系统", test_logger),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n[X] 测试 {test_name} 时发生异常: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "[OK] 通过" if success else "[X] 失败"
        print(f"{status}: {test_name}")
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

