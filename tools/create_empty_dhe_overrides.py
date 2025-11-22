#!/usr/bin/env python3
"""
为包含已删除国家标签的DHE文件创建空覆盖文件
"""

import re
from pathlib import Path

# 已删除的国家标签列表
DELETED_COUNTRIES = ['CHI', 'SPA', 'GBR']

# 游戏目录
GAME_DIR = Path(r"E:\SteamLibrary\steamapps\common\Europa Universalis V\game")
MOD_DIR = Path(__file__).parent.parent

def find_event_files_with_deleted_countries(game_dir: Path, deleted_tags: list):
    """
    查找包含已删除国家标签的所有事件文件
    """
    event_files = []
    events_dir = game_dir / "in_game" / "events"
    
    if not events_dir.exists():
        print(f"事件目录不存在: {events_dir}")
        return event_files
    
    # 递归查找所有事件文件
    for event_file in events_dir.rglob("*.txt"):
        try:
            with open(event_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()
                
            # 检查是否包含dynamic_historical_event和已删除的国家标签
            if 'dynamic_historical_event' in content:
                for tag in deleted_tags:
                    if f'tag = {tag}' in content or f'tag={tag}' in content:
                        event_files.append(event_file)
                        break
        except Exception as e:
            print(f"无法读取文件 {event_file}: {e}")
            continue
    
    return event_files

def create_empty_override(file_path: Path):
    """
    创建空文件覆盖
    """
    try:
        # 计算相对于game/in_game目录的路径
        # file_path应该是类似 E:\...\game\in_game\events\DHE\flavor_ARA.txt
        # 我们需要提取 events\DHE\flavor_ARA.txt 部分
        parts = list(file_path.parts)
        try:
            in_game_idx = parts.index('in_game')
            # 取in_game之后的所有部分
            relative_parts = parts[in_game_idx + 1:]
            relative_path = Path(*relative_parts)
        except ValueError:
            # 如果找不到in_game，尝试使用relative_to
            try:
                relative_path = file_path.relative_to(GAME_DIR / "in_game")
            except ValueError:
                relative_path = file_path.relative_to(GAME_DIR)
        
        target_path = MOD_DIR / "in_game" / relative_path.parent
        target_path.mkdir(parents=True, exist_ok=True)
        
        target_file = MOD_DIR / "in_game" / relative_path
        
        # 创建空文件（只包含注释说明）
        namespace_match = re.search(r'namespace\s*=\s*(\w+)', file_path.read_text(encoding='utf-8-sig'))
        namespace = namespace_match.group(1) if namespace_match else "unknown"
        
        empty_content = f"# Empty override file\n# Original file: {relative_path}\n# This file disables all events from the original file\n\nnamespace = {namespace}\n"
        
        with open(target_file, 'w', encoding='utf-8-sig') as f:
            f.write(empty_content)
        
        print(f"已创建空覆盖: {relative_path}")
        return True
    except Exception as e:
        print(f"无法创建文件 {target_file}: {e}")
        return False

def main():
    print("开始查找包含已删除国家标签的事件文件...")
    
    event_files = find_event_files_with_deleted_countries(GAME_DIR, DELETED_COUNTRIES)
    
    print(f"找到 {len(event_files)} 个需要创建空覆盖的文件")
    
    processed = 0
    for event_file in event_files:
        if create_empty_override(event_file):
            processed += 1
    
    print(f"\n处理完成！共创建了 {processed} 个空覆盖文件")
    print(f"文件已保存到模组目录: {MOD_DIR / 'in_game'}")

if __name__ == "__main__":
    main()

