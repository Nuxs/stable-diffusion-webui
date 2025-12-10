#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建环境包：将venv压缩为7z格式
用于分离式打包方案
"""

import os
import sys
import subprocess
from pathlib import Path

def check_7zip():
    """检查7-Zip是否可用"""
    try:
        result = subprocess.run(['7z'], capture_output=True, text=True, timeout=5)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def compress_venv_with_python(venv_path, output_path):
    """使用Python压缩venv（备用方案）"""
    print("使用Python压缩（较慢，但无需7-Zip）...")
    
    try:
        import zipfile
        import time
        
        exclude_dirs = {'__pycache__', '.git', 'test', 'tests', 'doc', 'docs'}
        exclude_exts = {'.pyc', '.pyo', '.pyd.cache', '.log'}
        
        total_files = 0
        compressed_files = 0
        start_time = time.time()
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
            for root, dirs, files in os.walk(venv_path):
                # 排除目录
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                
                for file in files:
                    if any(file.endswith(ext) for ext in exclude_exts):
                        continue
                    
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, venv_path)
                    total_files += 1
                    
                    try:
                        zipf.write(file_path, arcname)
                        compressed_files += 1
                        if compressed_files % 100 == 0:
                            elapsed = time.time() - start_time
                            print(f"  已压缩 {compressed_files} 个文件... ({elapsed:.1f}秒)")
                    except Exception as e:
                        print(f"  警告: 跳过文件 {file_path}: {e}")
        
        elapsed = time.time() - start_time
        print(f"✓ Python压缩完成: {compressed_files}/{total_files} 个文件 ({elapsed:.1f}秒)")
        return True
    except Exception as e:
        print(f"错误: Python压缩失败: {e}")
        return False

def compress_venv(venv_path, output_path):
    """压缩venv目录为7z格式（优先）或zip格式（备用）"""
    if not os.path.exists(venv_path):
        print(f"错误: venv路径不存在: {venv_path}")
        return False
    
    print(f"开始压缩venv环境...")
    print(f"源目录: {venv_path}")
    print(f"输出文件: {output_path}")
    
    # 首先尝试使用7z（更快，压缩率更好）
    if check_7zip():
        exclude_patterns = [
            '__pycache__',
            '*.pyc',
            '*.pyo',
            '*.pyd.cache',
            '*.log',
            'test',
            'tests',
            'doc',
            'docs',
        ]
        
        # 构建7z命令
        cmd = ['7z', 'a', '-t7z', '-mx=5', '-mmt']  # mx=5是中等压缩，mmt是多线程
        
        # 添加排除模式
        for pattern in exclude_patterns:
            cmd.extend(['-xr!' + pattern])
        
        # 添加输出文件和源目录
        cmd.extend([str(output_path), str(venv_path)])
        
        print(f"使用7-Zip压缩（推荐）...")
        print(f"执行命令: {' '.join(cmd)}")
        print("这可能需要10-30分钟，请耐心等待...")
        
        try:
            result = subprocess.run(cmd, check=True, text=True, capture_output=True)
            print(f"✓ 7z压缩完成: {output_path}")
            
            # 显示文件大小
            if os.path.exists(output_path):
                size = os.path.getsize(output_path)
                size_gb = size / (1024 * 1024 * 1024)
                print(f"压缩包大小: {size_gb:.2f} GB")
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"警告: 7z压缩失败: {e}")
            print("尝试使用Python压缩（备用方案）...")
            # 继续使用Python方案
        except FileNotFoundError:
            print("7z命令不可用，使用Python压缩（备用方案）...")
            # 继续使用Python方案
    
    # 备用方案：使用Python的zipfile（较慢但无需额外工具）
    print()
    print("=" * 60)
    print("使用Python压缩（备用方案）")
    print("注意: 这比7z慢，但无需安装额外工具")
    print("=" * 60)
    print()
    
    # 如果输出是.7z，改为.zip
    if output_path.suffix == '.7z':
        output_path = output_path.with_suffix('.zip')
        print(f"输出格式改为: {output_path}")
    
    if compress_venv_with_python(venv_path, output_path):
        # 显示文件大小
        if os.path.exists(output_path):
            size = os.path.getsize(output_path)
            size_gb = size / (1024 * 1024 * 1024)
            print(f"压缩包大小: {size_gb:.2f} GB")
        return True
    
    return False

def main():
    """主函数"""
    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    venv_path = project_root / 'venv'
    
    # 输出路径
    output_dir = script_dir / 'environment'
    output_dir.mkdir(exist_ok=True)
    # 优先使用7z，如果没有7z则使用zip
    if check_7zip():
        output_path = output_dir / 'venv.7z'
    else:
        output_path = output_dir / 'venv.zip'
        print("注意: 未检测到7-Zip，将使用ZIP格式（体积可能稍大）")
    
    print("=" * 60)
    print("创建环境包")
    print("=" * 60)
    print()
    
    # 检查venv是否存在
    if not venv_path.exists():
        print(f"错误: venv不存在: {venv_path}")
        print("请先创建并配置venv环境")
        return 1
    
    # 检查7-Zip
    if not check_7zip():
        print("警告: 未检测到7-Zip")
        print("将尝试使用Python的zipfile模块（较慢）")
        # 可以添加使用zipfile的备用方案
        return 1
    
    # 如果输出文件已存在，询问是否覆盖
    if output_path.exists():
        response = input(f"输出文件已存在: {output_path}\n是否覆盖? (y/n): ")
        if response.lower() != 'y':
            print("已取消")
            return 0
        output_path.unlink()
    
    # 压缩venv
    if compress_venv(venv_path, output_path):
        print()
        print("=" * 60)
        print("✓ 环境包创建成功！")
        print("=" * 60)
        print(f"文件位置: {output_path}")
        print()
        print("下一步:")
        print("1. 将 environment/venv.7z 复制到打包输出目录")
        print("2. 修改应用启动逻辑，添加环境解压功能")
        return 0
    else:
        print()
        print("=" * 60)
        print("✗ 环境包创建失败")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    sys.exit(main())

