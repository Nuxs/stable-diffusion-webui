#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复测试脚本中的 Unicode 字符
将特殊字符替换为 ASCII 等效字符
"""

from pathlib import Path


def fix_unicode_in_file(file_path: Path):
    """修复文件中的 Unicode 字符"""
    replacements = {
        '✓': '[OK]',
        '✗': '[X]',
        '⚠': '[!]',
    }
    
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        for unicode_char, ascii_char in replacements.items():
            content = content.replace(unicode_char, ascii_char)
        
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            print(f"[OK] 已修复: {file_path.name}")
            return True
        else:
            print(f"[--] 无需修复: {file_path.name}")
            return False
            
    except Exception as e:
        print(f"[X] 修复失败 {file_path.name}: {e}")
        return False


def main():
    """主函数"""
    print("修复测试脚本中的 Unicode 字符\n")
    
    # 要修复的文件
    files_to_fix = [
        "fix_pyqt6_env.py",
        "test_modules.py",
        "diagnose_pyqt6.py",
    ]
    
    base_dir = Path(__file__).parent
    fixed_count = 0
    
    for filename in files_to_fix:
        file_path = base_dir / filename
        if file_path.exists():
            if fix_unicode_in_file(file_path):
                fixed_count += 1
        else:
            print(f"[!] 文件不存在: {filename}")
    
    print(f"\n总计: 修复了 {fixed_count} 个文件")


if __name__ == "__main__":
    main()

