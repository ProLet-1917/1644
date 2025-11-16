#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析EU5原版通用科技文件，提取所有数值效果并计算累加值
"""

import re
import csv
from pathlib import Path
from collections import defaultdict

# 原版游戏路径
GAME_PATH = Path(r"E:\SteamLibrary\steamapps\common\Europa Universalis V\game")
ADVANCES_PATH = GAME_PATH / "in_game" / "common" / "advances"

# 要解析的文件
FILES = [
    ("Age 1", "0_age_of_traditions.txt"),
    ("Age 2", "0_age_of_renaissance.txt"),
    ("Age 3", "0_age_of_discovery.txt"),
    ("Age 4", "0_age_of_reformation.txt"),
]

# 数值效果模式（匹配 key = value 格式）
MODIFIER_PATTERN = re.compile(r'^\s*([a-z_][a-z0-9_]*)\s*=\s*([-+]?\d*\.?\d+|[a-z_][a-z0-9_]*)\s*$', re.IGNORECASE)

def parse_advance_file(file_path):
    """解析单个科技文件"""
    advances = []
    current_advance = None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # 跳过注释和空行
            if not line or line.startswith('#'):
                continue
            
            # 检测科技定义开始
            if '=' in line and '{' in line:
                # 提取科技ID
                match = re.match(r'^([a-z_][a-z0-9_]*)\s*=\s*\{', line, re.IGNORECASE)
                if match:
                    if current_advance:
                        advances.append(current_advance)
                    current_advance = {
                        'id': match.group(1),
                        'age': None,
                        'modifiers': {},
                        'unlocks': {
                            'unit': None,
                            'building': None,
                            'law': None,
                            'reform': None,
                            'other': []
                        }
                    }
            
            # 检测age字段
            if current_advance and line.startswith('age = '):
                match = re.search(r'age\s*=\s*([a-z0-9_]+)', line, re.IGNORECASE)
                if match:
                    current_advance['age'] = match.group(1)
            
            # 检测数值效果
            if current_advance:
                match = MODIFIER_PATTERN.match(line)
                if match:
                    key = match.group(1)
                    value = match.group(2)
                    
                    # 跳过非数值效果的关键字
                    skip_keys = {'requires', 'icon', 'research_cost', 'depth', 'starting_technology_level', 
                                'allow', 'potential', 'ai_weight', 'ai_preference_tags', 'for'}
                    if key.lower() in skip_keys:
                        continue
                    
                    # 检查是否是解锁类
                    if key.startswith('unlock_'):
                        unlock_type = key.replace('unlock_', '')
                        if unlock_type == 'unit':
                            current_advance['unlocks']['unit'] = value
                        elif unlock_type == 'building':
                            current_advance['unlocks']['building'] = value
                        elif unlock_type == 'law':
                            current_advance['unlocks']['law'] = value
                        elif unlock_type == 'government_reform':
                            current_advance['unlocks']['reform'] = value
                        else:
                            current_advance['unlocks']['other'].append(f"{key}={value}")
                    else:
                        # 尝试转换为数值
                        try:
                            num_value = float(value)
                            current_advance['modifiers'][key] = num_value
                        except ValueError:
                            # 非数值（如small_tax_income_efficiency_bonus）
                            current_advance['modifiers'][key] = value
        
        # 添加最后一个科技
        if current_advance:
            advances.append(current_advance)
    
    return advances

def main():
    all_advances = []
    modifier_totals = defaultdict(float)
    modifier_counts = defaultdict(int)
    
    # 解析所有文件
    for age_name, filename in FILES:
        file_path = ADVANCES_PATH / filename
        if not file_path.exists():
            print(f"警告: 文件不存在 {file_path}")
            continue
        
        print(f"正在解析 {age_name}: {filename}")
        advances = parse_advance_file(file_path)
        
        for adv in advances:
            adv['age_name'] = age_name
            all_advances.append(adv)
            
            # 累加数值效果
            for key, value in adv['modifiers'].items():
                if isinstance(value, (int, float)):
                    modifier_totals[key] += value
                    modifier_counts[key] += 1
    
    # 输出详细CSV
    output_dir = Path(__file__).parent.parent / "in_game" / "common" / "advances"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 详细列表
    with open(output_dir / "原版通用科技详细列表.csv", 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['时代', '科技ID', 'age字段', '效果键', '效果值', '解锁单位', '解锁建筑', '解锁法律', '解锁改革'])
        
        for adv in all_advances:
            if not adv['modifiers']:
                # 没有数值效果的科技也要记录（可能有解锁）
                unlocks = []
                if adv['unlocks']['unit']:
                    unlocks.append(f"单位:{adv['unlocks']['unit']}")
                if adv['unlocks']['building']:
                    unlocks.append(f"建筑:{adv['unlocks']['building']}")
                if adv['unlocks']['law']:
                    unlocks.append(f"法律:{adv['unlocks']['law']}")
                if adv['unlocks']['reform']:
                    unlocks.append(f"改革:{adv['unlocks']['reform']}")
                unlocks.extend(adv['unlocks']['other'])
                
                writer.writerow([
                    adv['age_name'],
                    adv['id'],
                    adv['age'] or '',
                    '无数值效果',
                    '',
                    adv['unlocks']['unit'] or '',
                    adv['unlocks']['building'] or '',
                    adv['unlocks']['law'] or '',
                    adv['unlocks']['reform'] or ''
                ])
            else:
                # 有数值效果的科技
                first_row = True
                for key, value in adv['modifiers'].items():
                    unlocks = []
                    if first_row:
                        if adv['unlocks']['unit']:
                            unlocks.append(f"单位:{adv['unlocks']['unit']}")
                        if adv['unlocks']['building']:
                            unlocks.append(f"建筑:{adv['unlocks']['building']}")
                        if adv['unlocks']['law']:
                            unlocks.append(f"法律:{adv['unlocks']['law']}")
                        if adv['unlocks']['reform']:
                            unlocks.append(f"改革:{adv['unlocks']['reform']}")
                        unlocks.extend(adv['unlocks']['other'])
                    
                    writer.writerow([
                        adv['age_name'] if first_row else '',
                        adv['id'] if first_row else '',
                        adv['age'] or '' if first_row else '',
                        key,
                        value,
                        adv['unlocks']['unit'] or '' if first_row else '',
                        adv['unlocks']['building'] or '' if first_row else '',
                        adv['unlocks']['law'] or '' if first_row else '',
                        adv['unlocks']['reform'] or '' if first_row else ''
                    ])
                    first_row = False
    
    # 累加统计
    with open(output_dir / "原版通用科技累加统计.csv", 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['效果键', '累加值', '出现次数', '平均値', '说明'])
        
        # 按累加值排序
        sorted_modifiers = sorted(modifier_totals.items(), key=lambda x: abs(x[1]), reverse=True)
        
        for key, total in sorted_modifiers:
            count = modifier_counts[key]
            avg = total / count if count > 0 else 0
            writer.writerow([key, total, count, f"{avg:.4f}", f"前四个时代累加值"])
    
    print(f"\n完成！")
    print(f"- 共解析 {len(all_advances)} 个科技")
    print(f"- 共发现 {len(modifier_totals)} 种不同的效果")
    print(f"- 详细列表: {output_dir / '原版通用科技详细列表.csv'}")
    print(f"- 累加统计: {output_dir / '原版通用科技累加统计.csv'}")

if __name__ == '__main__':
    main()








