#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EU5 人口清理工具
功能：移除所有 size = 0.000 的人口条目
"""

import re
import os
import sys

# 路径配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MOD_PATH = os.path.dirname(SCRIPT_DIR)
POPS_FILE = os.path.join(MOD_PATH, "main_menu", "setup", "start", "06_pops.txt")


def remove_zero_pops(pops_file: str, backup: bool = True):
    """移除所有 size = 0.000 的人口条目"""
    print("=" * 60)
    print("EU5 人口清理工具 - 移除 size = 0.000 的条目")
    print("=" * 60)
    
    # 创建备份
    if backup:
        backup_file = pops_file + ".backup"
        import shutil
        shutil.copy2(pops_file, backup_file)
        print(f"\n已创建备份文件: {backup_file}")
    
    # 读取文件
    print(f"\n正在读取文件: {pops_file}")
    with open(pops_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 统计信息
    total_lines = len(lines)
    removed_count = 0
    kept_count = 0
    
    # 处理每一行
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # 检查是否包含 define_pop 且 size = 0.000
        if 'define_pop' in line:
            # 匹配 size = 0.000 或 size = 0.0 等（允许小数点后任意位数）
            # 匹配 size = 0.000 或 size=0.000（可能有制表符）
            zero_match = re.search(r'size\s*=\s*0\.0+', line)
            
            if zero_match:
                # 跳过这一行（移除）
                removed_count += 1
                i += 1
                continue
            else:
                # 保留这一行
                kept_count += 1
                new_lines.append(line)
                i += 1
        else:
            # 非人口定义行，直接保留
            new_lines.append(line)
            i += 1
    
    # 写入新文件
    print(f"\n处理完成:")
    print(f"  总行数: {total_lines}")
    print(f"  移除的条目: {removed_count}")
    print(f"  保留的条目: {kept_count}")
    print(f"  新文件行数: {len(new_lines)}")
    
    # 写入文件
    print(f"\n正在写入文件...")
    with open(pops_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"\n[成功] 已更新文件: {pops_file}")
    print(f"[成功] 移除了 {removed_count} 个 size = 0.000 的条目")
    if backup:
        print(f"[成功] 备份文件: {backup_file}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='移除所有 size = 0.000 的人口条目')
    parser.add_argument('--no-backup', action='store_true', help='不创建备份文件')
    parser.add_argument('--file', type=str, default=POPS_FILE, help='要处理的文件路径')
    
    args = parser.parse_args()
    
    try:
        remove_zero_pops(args.file, backup=not args.no_backup)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()





