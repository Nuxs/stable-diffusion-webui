#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合测试脚本
运行所有测试并生成测试报告
"""

import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime


def run_test(test_name: str, test_script: str) -> tuple[bool, str]:
    """
    运行单个测试脚本
    
    Args:
        test_name: 测试名称
        test_script: 测试脚本路径
    
    Returns:
        tuple: (是否成功, 输出信息)
    """
    print(f"\n{'=' * 60}")
    print(f"运行测试: {test_name}")
    print(f"{'=' * 60}")
    
    try:
        result = subprocess.run(
            [sys.executable, test_script],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print(result.stdout)
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        
        success = result.returncode == 0
        
        if success:
            print(f"✓ {test_name} 测试通过")
        else:
            print(f"✗ {test_name} 测试失败 (返回码: {result.returncode})")
        
        return success, result.stdout + result.stderr
        
    except subprocess.TimeoutExpired:
        print(f"✗ {test_name} 测试超时")
        return False, "测试超时"
    except Exception as e:
        print(f"✗ {test_name} 测试异常: {e}")
        return False, str(e)


def main():
    """主函数"""
    print("=" * 60)
    print("Stable Diffusion WebUI Desktop - 综合测试")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 测试列表
    tests = [
        ("PyQt6 环境", "fix_pyqt6_env.py"),
        ("模块功能", "test_modules.py"),
    ]
    
    results = []
    
    # 运行所有测试
    for test_name, test_script in tests:
        script_path = Path(__file__).parent / test_script
        if not script_path.exists():
            print(f"⚠ 跳过测试 {test_name}: 脚本不存在 ({test_script})")
            results.append((test_name, False, "脚本不存在"))
            continue
        
        success, output = run_test(test_name, str(script_path))
        results.append((test_name, success, output))
    
    # 生成测试报告
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for test_name, success, _ in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{status}: {test_name}")
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    # 保存报告
    report_file = Path(__file__).parent / "logs" / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"测试报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            for test_name, success, output in results:
                f.write(f"{'=' * 60}\n")
                f.write(f"测试: {test_name}\n")
                f.write(f"结果: {'通过' if success else '失败'}\n")
                f.write(f"{'=' * 60}\n")
                f.write(output)
                f.write("\n\n")
            
            f.write(f"{'=' * 60}\n")
            f.write(f"总计: {passed}/{total} 个测试通过\n")
        
        print(f"\n报告已保存: {report_file}")
    except Exception as e:
        print(f"\n⚠ 保存报告失败: {e}")
    
    # 系统信息
    print("\n" + "=" * 60)
    print("系统信息")
    print("=" * 60)
    print(f"Python 版本: {sys.version}")
    print(f"工作目录: {Path.cwd()}")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

