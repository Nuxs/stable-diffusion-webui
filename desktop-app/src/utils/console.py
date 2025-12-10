#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
控制台输出辅助工具
处理 Windows 控制台编码问题
"""

import sys
import locale


def setup_console_encoding():
    """设置控制台编码为 UTF-8"""
    try:
        # Windows 控制台编码设置
        if sys.platform == 'win32':
            # 尝试设置控制台代码页为 UTF-8
            import subprocess
            try:
                subprocess.run(['chcp', '65001'], shell=True, capture_output=True)
            except:
                pass
            
            # 重新配置 stdout 和 stderr 的编码
            if hasattr(sys.stdout, 'reconfigure'):
                try:
                    sys.stdout.reconfigure(encoding='utf-8')
                    sys.stderr.reconfigure(encoding='utf-8')
                except:
                    pass
    except Exception:
        pass


def safe_print(*args, **kwargs):
    """
    安全的打印函数，自动处理编码问题
    将 Unicode 符号替换为 ASCII 等效字符
    """
    # Unicode 符号映射
    replacements = {
        '✓': '[OK]',
        '✗': '[X]',
        '⚠': '[!]',
        '→': '->',
        '←': '<-',
        '↑': '^',
        '↓': 'v',
        '━': '-',
        '│': '|',
        '┌': '+',
        '┐': '+',
        '└': '+',
        '┘': '+',
        '├': '+',
        '┤': '+',
        '┬': '+',
        '┴': '+',
        '┼': '+',
        '•': '*',
        '●': '*',
        '○': 'o',
        '◆': '*',
        '◇': 'o',
        '■': '#',
        '□': '[]',
        '★': '*',
        '☆': '*',
        '♦': '*',
        '♣': '*',
        '♠': '*',
        '♥': '*',
    }
    
    # 处理参数
    new_args = []
    for arg in args:
        if isinstance(arg, str):
            # 替换 Unicode 符号
            for unicode_char, ascii_char in replacements.items():
                arg = arg.replace(unicode_char, ascii_char)
        new_args.append(arg)
    
    # 打印
    try:
        print(*new_args, **kwargs)
    except UnicodeEncodeError:
        # 如果仍然失败，尝试使用 ASCII 编码
        try:
            ascii_args = [str(arg).encode('ascii', 'replace').decode('ascii') for arg in new_args]
            print(*ascii_args, **kwargs)
        except:
            # 最后的备用方案
            print("[编码错误：无法显示某些字符]")


# 导出别名
sprint = safe_print


if __name__ == "__main__":
    # 测试
    setup_console_encoding()
    
    safe_print("测试安全打印:")
    safe_print("✓ 成功")
    safe_print("✗ 失败")
    safe_print("⚠ 警告")
    safe_print("→ 箭头")
    safe_print("━━━━━━")

