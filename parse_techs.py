#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析legacy科技文件，按依赖树组织科技
"""
import re
import os
from collections import defaultdict, deque

# 文件列表
LEGACY_FILES = [
    'in_game/common/advances_legacy/0_age_of_traditions.txt',
    'in_game/common/advances_legacy/0_age_of_renaissance.txt',
    'in_game/common/advances_legacy/0_age_of_discovery.txt',
    'in_game/common/advances_legacy/0_age_of_reformation.txt',
    'in_game/common/advances_legacy/1_building_unlocks.txt',
    'in_game/common/advances_legacy/2_army_unlocks.txt',
    'in_game/common/advances_legacy/2_ship_unlocks.txt',
    'in_game/common/advances_legacy/3_cabinet_actions_unlocks.txt',
    'in_game/common/advances_legacy/3_fort_level.txt',
    'in_game/common/advances_legacy/3_production_method_unlocks.txt',
    'in_game/common/advances_legacy/3_reform_unlocks.txt',
    'in_game/common/advances_legacy/3_road_unlocks.txt',
    'in_game/common/advances_legacy/3_supply_limit.txt',
]

# 只处理前4个时代的科技
AGE_FILTER = ['age_1_traditions', 'age_2_renaissance', 'age_3_discovery', 'age_4_reformation']

def parse_tech_file(filepath):
    """解析科技文件，返回科技字典"""
    techs = {}
    current_tech = None
    current_lines = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            # 检测科技定义开始
            match = re.match(r'^([a-z_][a-z0-9_]*)\s*=\s*\{', line)
            if match:
                # 保存之前的科技
                if current_tech:
                    techs[current_tech] = ''.join(current_lines)
                current_tech = match.group(1)
                current_lines = [line]
            elif current_tech:
                current_lines.append(line)
                # 检测科技定义结束
                if line.strip() == '}':
                    techs[current_tech] = ''.join(current_lines)
                    current_tech = None
                    current_lines = []
    
    # 保存最后一个科技
    if current_tech:
        techs[current_tech] = ''.join(current_lines)
    
    return techs

def extract_tech_info(tech_name, tech_content):
    """提取科技信息"""
    info = {
        'name': tech_name,
        'age': None,
        'requires': None,
        'depth': None,
        'unlocks': {
            'building': [],
            'levy': [],
            'law': [],
            'subject_type': [],
            'government_reform': [],
            'country_interaction': [],
            'unit': [],
            'road_type': [],
            'production_method': [],
            'casus_belli': [],
            'diplomacy': [],
            'ability': [],
            'cabinet_action': [],
        }
    }
    
    # 提取age
    age_match = re.search(r'age\s*=\s*([a-z0-9_]+)', tech_content)
    if age_match:
        info['age'] = age_match.group(1)
    
    # 提取requires
    requires_match = re.search(r'requires\s*=\s*([a-z_][a-z0-9_]*)', tech_content)
    if requires_match:
        info['requires'] = requires_match.group(1)
    
    # 提取depth
    depth_match = re.search(r'depth\s*=\s*(\d+)', tech_content)
    if depth_match:
        info['depth'] = int(depth_match.group(1))
    
    # 提取unlock语句
    unlock_patterns = {
        'building': r'unlock_building\s*=\s*([a-z_][a-z0-9_]*)',
        'levy': r'unlock_levy\s*=\s*([a-z_][a-z0-9_]*)',
        'law': r'unlock_law\s*=\s*([a-z_][a-z0-9_]*)',
        'subject_type': r'unlock_subject_type\s*=\s*([a-z_][a-z0-9_]*)',
        'government_reform': r'unlock_government_reform\s*=\s*([a-z_][a-z0-9_]*)',
        'country_interaction': r'unlock_country_interaction\s*=\s*([a-z_][a-z0-9_]*)',
        'unit': r'unlock_unit\s*=\s*([a-z_][a-z0-9_]*)',
        'road_type': r'unlock_road_type\s*=\s*([a-z_][a-z0-9_]*)',
        'production_method': r'unlock_production_method\s*=\s*([a-z_][a-z0-9_]*)',
        'casus_belli': r'unlock_casus_belli\s*=\s*([a-z_][a-z0-9_]*)',
        'diplomacy': r'unlock_diplomacy\s*=\s*\{[^}]*supportrebels[^}]*\}',
        'ability': r'unlock_ability\s*=\s*([a-z_][a-z0-9_]*)',
        'cabinet_action': r'unlock_cabinet_action\s*=\s*([a-z_][a-z0-9_]*)',
    }
    
    for unlock_type, pattern in unlock_patterns.items():
        matches = re.findall(pattern, tech_content)
        if matches:
            if unlock_type == 'diplomacy':
                info['unlocks'][unlock_type] = ['supportrebels']
            else:
                info['unlocks'][unlock_type].extend(matches)
    
    return info

def build_dependency_tree(techs_info):
    """构建依赖树"""
    # 找出根节点（depth=0或没有requires）
    root_nodes = []
    children = defaultdict(list)
    
    for tech_name, info in techs_info.items():
        if info['depth'] == 0 or not info['requires']:
            root_nodes.append(tech_name)
        else:
            children[info['requires']].append(tech_name)
    
    return root_nodes, children

def topological_sort(root_nodes, children, techs_info):
    """拓扑排序，按依赖顺序组织科技"""
    result = []
    visited = set()
    
    def dfs(tech_name, depth=0):
        if tech_name in visited or tech_name not in techs_info:
            return
        visited.add(tech_name)
        result.append((tech_name, depth))
        # 递归处理子节点
        for child in sorted(children[tech_name]):
            dfs(child, depth + 1)
    
    # 从每个根节点开始DFS
    for root in sorted(root_nodes):
        dfs(root)
    
    return result

def generate_script(techs_info, root_nodes, sorted_techs):
    """生成脚本内容"""
    lines = []
    
    # 按时代分组
    age_groups = defaultdict(list)
    for tech_name, depth in sorted_techs:
        if tech_name in techs_info:
            age = techs_info[tech_name]['age']
            if age and age in AGE_FILTER:
                age_groups[age].append((tech_name, depth))
    
    # 生成每个时代的脚本
    age_names = {
        'age_1_traditions': '研究时代1的所有科技（按依赖树组织）',
        'age_2_renaissance': '研究时代2的所有科技（按依赖树组织）',
        'age_3_discovery': '研究时代3的所有科技（按依赖树组织）',
        'age_4_reformation': '研究时代4的所有科技（按依赖树组织）',
    }
    
    for age in AGE_FILTER:
        if age not in age_groups:
            continue
        
        lines.append(f'# {age_names[age]}')
        lines.append(f'research_{age.replace("age_", "age_").replace("_", "_")}_advances = {{')
        
        current_root = None
        for tech_name, depth in age_groups[age]:
            info = techs_info[tech_name]
            
            # 如果是根节点，添加分隔注释
            if depth == 0:
                if current_root is not None:
                    lines.append('')
                current_root = tech_name
                # 获取科技的中文名称（如果有注释）
                comment = f'# 根节点：{tech_name}'
                lines.append(f'\t# ========================================')
                lines.append(f'\t{comment}')
                lines.append(f'\t# ========================================')
            
            # 添加unlock和research
            lines.append(f'\tunlock_advance_effect = {{ type = {tech_name} }}')
            lines.append(f'\tresearch_advance = advance_type:{tech_name}')
            
            # 添加unlock效果
            for unlock_type, items in info['unlocks'].items():
                if items:
                    for item in items:
                        if unlock_type == 'building':
                            lines.append(f'\tunlock_building_effect = {{ type = {item} }}')
                        elif unlock_type == 'levy':
                            lines.append(f'\tunlock_levy_effect = {{ type = {item} }}')
                        elif unlock_type == 'law':
                            lines.append(f'\tunlock_law_effect = {{ type = {item} }}')
                        elif unlock_type == 'government_reform':
                            lines.append(f'\tunlock_government_reform_effect = {{ type = {item} }}')
                        elif unlock_type == 'country_interaction':
                            lines.append(f'\tunlock_country_interaction_effect = {{ type = {item} }}')
                        elif unlock_type == 'cabinet_action':
                            lines.append(f'\tunlock_cabinet_action_effect = {{ type = {item} }}')
                        # 注意：subject_type, unit等可能需要特殊处理
            
            # 添加依赖关系注释
            if info['requires']:
                lines.append(f'\t# {info["requires"]} -> {tech_name}')
            lines.append('')
        
        lines.append('}')
        lines.append('')
    
    return '\n'.join(lines)

def main():
    """主函数"""
    base_dir = 'C:/Users/qiush/Documents/Paradox Interactive/Europa Universalis V/mod/1644'
    os.chdir(base_dir)
    
    # 解析所有文件
    all_techs = {}
    for filepath in LEGACY_FILES:
        full_path = os.path.join(base_dir, filepath)
        if os.path.exists(full_path):
            techs = parse_tech_file(full_path)
            all_techs.update(techs)
    
    # 提取科技信息
    techs_info = {}
    for tech_name, tech_content in all_techs.items():
        info = extract_tech_info(tech_name, tech_content)
        # 只保留前4个时代的科技
        if info['age'] and info['age'] in AGE_FILTER:
            techs_info[tech_name] = info
    
    # 构建依赖树
    root_nodes, children = build_dependency_tree(techs_info)
    
    # 拓扑排序
    sorted_techs = topological_sort(root_nodes, children, techs_info)
    
    # 生成脚本
    script_content = generate_script(techs_info, root_nodes, sorted_techs)
    
    # 输出到文件
    output_file = 'in_game/common/scripted_effects/zzz_1644_starting_tech_generated.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f'Generated script with {len(sorted_techs)} technologies')
    print(f'Root nodes: {len(root_nodes)}')
    print(f'Output saved to: {output_file}')

if __name__ == '__main__':
    main()


