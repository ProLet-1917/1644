#!/usr/bin/env python3
"""
移除已删除国家的dynamic_historical_event标记
用于修复因删除国家导致的动态历史事件错误
"""

import re
import os
from pathlib import Path

# 已删除的国家标签列表
DELETED_COUNTRIES = ['CHI', 'SPA', 'GBR']

# 游戏目录
GAME_DIR = Path(r"E:\SteamLibrary\steamapps\common\Europa Universalis V\game")
MOD_DIR = Path(__file__).parent.parent

def remove_deleted_tags_from_blocks(file_path: Path, deleted_tags: list):
    """
    从dynamic_historical_event块中移除已删除国家的tag行
    """
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    except Exception as e:
        print(f"无法读取文件 {file_path}: {e}")
        return False
    
    original_content = content
    lines = content.split('\n')
    modified = False
    in_dynamic_block = False
    block_start = -1
    brace_count = 0
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # 检测dynamic_historical_event块开始
        if 'dynamic_historical_event' in line and '{' in line:
            in_dynamic_block = True
            block_start = i
            brace_count = line.count('{') - line.count('}')
        
        # 如果在块内
        elif in_dynamic_block:
            # 更新大括号计数
            brace_count += line.count('{') - line.count('}')
            
            # 检查是否是已删除的tag行
            for tag in deleted_tags:
                if re.search(rf'^\s*tag\s*=\s*{tag}\s*$', line):
                    # 删除这一行
                    lines.pop(i)
                    modified = True
                    i -= 1  # 调整索引
                    break
            
            # 检测块结束（大括号平衡）
            if brace_count <= 0 and '}' in line:
                # 检查块中是否还有其他tag（非已删除的）
                block_lines = lines[block_start:i+1] if i < len(lines) else lines[block_start:]
                has_other_tags = False
                for bl in block_lines:
                    tag_match = re.search(r'^\s*tag\s*=\s*(\w+)\s*$', bl)
                    if tag_match and tag_match.group(1) not in deleted_tags:
                        has_other_tags = True
                        break
                
                # 如果块中没有任何tag了，注释掉整个块
                if not has_other_tags and block_start >= 0:
                    # 找到块的缩进
                    indent_str = ''
                    if block_start < len(lines):
                        indent_len = len(lines[block_start]) - len(lines[block_start].lstrip())
                        indent_str = ' ' * indent_len
                    
                    # 注释掉整个块
                    end_idx = min(i + 1, len(lines))
                    for j in range(block_start, end_idx):
                        if j < len(lines) and lines[j].strip() and not lines[j].strip().startswith('#'):
                            lines[j] = indent_str + '# REMOVED: ' + lines[j].lstrip()
                    modified = True
                
                in_dynamic_block = False
                block_start = -1
                brace_count = 0
        
        i += 1
    
    if modified:
        try:
            # 创建目标目录
            # 计算相对于game目录的路径
            if 'game' in str(file_path):
                # 如果路径包含game，需要去掉game部分
                parts = file_path.parts
                try:
                    game_idx = parts.index('game')
                    relative_path = Path(*parts[game_idx+1:])
                except ValueError:
                    relative_path = file_path.relative_to(GAME_DIR)
            else:
                relative_path = file_path.relative_to(GAME_DIR)
            
            target_path = MOD_DIR / "in_game" / relative_path.parent
            target_path.mkdir(parents=True, exist_ok=True)
            
            target_file = MOD_DIR / "in_game" / relative_path
            with open(target_file, 'w', encoding='utf-8-sig') as f:
                f.write('\n'.join(lines))
            print(f"已处理: {relative_path}")
            return True
        except Exception as e:
            print(f"无法写入文件 {target_file}: {e}")
            return False
    
    return False

def find_event_files_with_deleted_countries(game_dir: Path, deleted_tags: list):
    """
    查找包含已删除国家标签的事件文件
    """
    event_files = []
    
    # 搜索事件文件
    for event_file in game_dir.rglob("*.txt"):
        if "events" not in str(event_file):
            continue
        
        try:
            with open(event_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()
                
            # 检查是否包含dynamic_historical_event和已删除的国家标签
            if 'dynamic_historical_event' in content:
                for tag in deleted_tags:
                    if f'tag = {tag}' in content or f'tag={tag}' in content:
                        event_files.append(event_file)
                        break
        except Exception:
            continue
    
    return event_files

def main():
    print("开始查找包含已删除国家标签的事件文件...")
    
    event_files = find_event_files_with_deleted_countries(GAME_DIR, DELETED_COUNTRIES)
    
    print(f"找到 {len(event_files)} 个需要处理的文件")
    
    processed = 0
    for event_file in event_files:
        if remove_deleted_tags_from_blocks(event_file, DELETED_COUNTRIES):
            processed += 1
    
    print(f"\n处理完成！共处理了 {processed} 个文件")
    print(f"文件已保存到模组目录: {MOD_DIR / 'in_game'}")

if __name__ == "__main__":
    main()

