#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EU5 人口文化宗教更改工具
功能：按百分比更改指定area/region/location的人口文化和宗教
"""

import re
import os
import sys
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

# 路径配置
# 自动获取脚本所在目录，向上一级到mod根目录（1644文件夹）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MOD_PATH = os.path.dirname(SCRIPT_DIR)
GAME_PATH = r"D:\SteamLibrary\steamapps\common\Europa Universalis V\game"
DEFINITIONS_FILE = os.path.join(GAME_PATH, "in_game", "map_data", "definitions.txt")
POPS_FILE = os.path.join(MOD_PATH, "main_menu", "setup", "start", "06_pops.txt")


class PopCultureReligionChanger:
    def __init__(self, definitions_file: str, pops_file: str):
        self.definitions_file = definitions_file
        self.pops_file = pops_file
        self.areas = {}
        self.populations = {}
        
    def parse_populations(self) -> Dict[str, List[Dict]]:
        """解析06_pops.txt，提取所有location的人口数据"""
        print(f"正在解析 {self.pops_file}...")
        
        populations = {}
        current_location = None
        current_pops = []
        
        with open(self.pops_file, 'r', encoding='utf-8') as f:
            for line in f:
                stripped = line.strip()
                if not stripped:
                    continue
                
                # 跳过文件开头的 "locations = {" 或 "locations={"
                if stripped == 'locations = {' or stripped == 'locations={':
                    continue
                
                # 匹配 location_name = { (可能前面有制表符)
                # 排除 "locations" 和 "define_pop" 等关键字
                location_match = re.match(r'^[\t\s]*([a-z_][a-z0-9_]*)\s*=\s*\{$', stripped)
                if location_match:
                    loc_name = location_match.group(1)
                    # 排除关键字
                    if loc_name in ['locations', 'define_pop']:
                        continue
                    
                    # 保存上一个location的数据
                    if current_location and current_pops:
                        populations[current_location] = current_pops
                    
                    current_location = loc_name
                    current_pops = []
                    continue
                
                # 匹配单行格式：define_pop = { type = ... size = ... culture = ... religion = ... }
                # 注意：数据中使用制表符分隔，行首可能有制表符
                if stripped and 'define_pop' in stripped:
                    pop_match = re.search(
                        r'define_pop\s*=\s*\{.*?type\s*=\s*(\w+).*?size\s*=\s*([\d.]+).*?culture\s*=\s*(\w+).*?religion\s*=\s*(\w+)',
                        stripped
                    )
                    if pop_match:
                        pop_data = {
                            'type': pop_match.group(1),
                            'size': float(pop_match.group(2)),
                            'culture': pop_match.group(3),
                            'religion': pop_match.group(4),
                            'original_line': line  # 保留原始行，用于格式化
                        }
                        current_pops.append(pop_data)
                        continue
                
                # 匹配location结束大括号
                if stripped == '}' and current_location:
                    if current_pops:
                        populations[current_location] = current_pops
                    current_location = None
                    current_pops = []
        
        # 处理最后一个location
        if current_location and current_pops:
            populations[current_location] = current_pops
        
        print(f"  解析了 {len(populations)} 个 locations 的人口数据")
        self.populations = populations
        return populations
    
    def parse_definitions(self) -> Dict[str, List[str]]:
        """解析definitions.txt，提取所有area及其包含的locations"""
        if self.areas:
            return self.areas
        
        print(f"正在解析 {self.definitions_file}...")
        
        with open(self.definitions_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        areas = {}
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # 匹配 area_name = {
            area_match = re.match(r'(\w+_area)\s*=\s*\{', line)
            if area_match:
                area_name = area_match.group(1)
                locations = []
                
                # 解析area内容，直到找到匹配的结束大括号
                i += 1
                brace_count = 1
                area_content = []
                
                while i < len(lines) and brace_count > 0:
                    current_line = lines[i]
                    area_content.append(current_line)
                    
                    # 计算大括号
                    brace_count += current_line.count('{') - current_line.count('}')
                    i += 1
                
                # 从area内容中提取locations
                content_text = ''.join(area_content)
                # 匹配 province_name = { location1 location2 ... }
                province_pattern = r'\w+_province\s*=\s*\{([^}]+)\}'
                for prov_match in re.finditer(province_pattern, content_text):
                    prov_locations = prov_match.group(1).strip().split()
                    locations.extend([loc.strip() for loc in prov_locations if loc.strip()])
                
                if locations:
                    areas[area_name] = locations
                
                continue
            
            i += 1
        
        self.areas = areas
        return areas
    
    def get_area_locations(self, area_name: str) -> Optional[List[str]]:
        """获取指定area的所有locations"""
        if not self.areas:
            self.parse_definitions()
        
        # 支持完整名称或部分匹配
        if area_name in self.areas:
            return self.areas[area_name]
        
        # 尝试部分匹配
        for key, locations in self.areas.items():
            if area_name.lower() in key.lower() or key.lower() in area_name.lower():
                return locations
        
        return None
    
    def get_region_areas(self, region_name: str) -> List[str]:
        """获取指定region下的所有area名称"""
        if not self.areas:
            self.parse_definitions()
        
        # 从definitions.txt解析region结构
        with open(self.definitions_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        region_areas = []
        i = 0
        in_target_region = False
        region_indent_level = 0
        
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # 计算缩进级别（制表符数量）
            indent_level = len(line) - len(line.lstrip('\t'))
            
            # 匹配 region_name = {
            if re.match(rf'{region_name}\s*=\s*{{', stripped):
                in_target_region = True
                region_indent_level = indent_level
                i += 1
                continue
            
            # 如果在目标region内
            if in_target_region:
                # 如果遇到同级别或更高级别的结束大括号，说明离开了region
                if stripped == '}' and indent_level <= region_indent_level:
                    break
                
                # 匹配 area_name = { (必须在region内，且缩进级别大于region)
                area_match = re.match(r'(\w+_area)\s*=\s*\{', stripped)
                if area_match and indent_level > region_indent_level:
                    area_name = area_match.group(1)
                    if area_name in self.areas:
                        region_areas.append(area_name)
            
            i += 1
        
        return region_areas
    
    def get_region_locations(self, region_name: str) -> List[str]:
        """获取指定region下的所有locations"""
        areas = self.get_region_areas(region_name)
        all_locations = []
        
        for area_name in areas:
            locations = self.get_area_locations(area_name)
            if locations:
                all_locations.extend(locations)
        
        return all_locations
    
    def change_culture_religion(
        self,
        location: str,
        source_culture: Optional[str] = None,
        source_religion: Optional[str] = None,
        target_culture: Optional[str] = None,
        target_religion: Optional[str] = None,
        percentage: float = 100.0,
        pop_type: Optional[str] = None
    ) -> Dict[str, List[Dict]]:
        """
        按百分比更改人口的文化和宗教
        
        参数:
        - location: location名称
        - source_culture: 源文化（None表示所有文化）
        - source_religion: 源宗教（None表示所有宗教）
        - target_culture: 目标文化（None表示不更改）
        - target_religion: 目标宗教（None表示不更改）
        - percentage: 转换百分比（0-100）
        - pop_type: 人口类型（None表示所有类型）
        """
        if not self.populations:
            self.parse_populations()
        
        if location not in self.populations:
            raise ValueError(f"未找到 location: {location}")
        
        # 筛选匹配的人口
        matched_pops = []
        unmatched_pops = []
        
        for pop in self.populations[location]:
            match = True
            
            if pop_type and pop['type'] != pop_type:
                match = False
            
            if source_culture and pop['culture'] != source_culture:
                match = False
            
            if source_religion and pop['religion'] != source_religion:
                match = False
            
            if match:
                matched_pops.append(pop)
            else:
                unmatched_pops.append(pop)
        
        if not matched_pops:
            raise ValueError(f"未找到匹配的人口")
        
        # 计算总人口
        total_matched_size = sum(pop['size'] for pop in matched_pops)
        
        # 计算要转换的人口数量
        convert_size = total_matched_size * (percentage / 100.0)
        
        # 按比例转换每个人口组
        new_pops = []
        
        for pop in matched_pops:
            pop_convert_size = pop['size'] * (percentage / 100.0)
            
            # 转换的人口
            converted_pop = pop.copy()
            converted_pop['size'] = pop_convert_size
            if target_culture:
                converted_pop['culture'] = target_culture
            if target_religion:
                converted_pop['religion'] = target_religion
            # 只有当转换后的人口数量大于阈值时才添加
            if converted_pop['size'] > 0.0001:
                new_pops.append(converted_pop)
            
            # 未转换的人口（保持原文化和宗教）
            remaining_pop = pop.copy()
            remaining_pop['size'] = pop['size'] - pop_convert_size
            if remaining_pop['size'] > 0.0001:  # 避免过小的人口
                new_pops.append(remaining_pop)
        
        # 添加未匹配的人口
        new_pops.extend(unmatched_pops)
        
        # 验证总人口
        original_total = sum(pop['size'] for pop in self.populations[location])
        new_total = sum(pop['size'] for pop in new_pops)
        
        # 只显示简要信息
        print(f"  {location}: 转换 {convert_size:.1f} 千人口 (匹配: {total_matched_size:.1f} 千)")
        
        # 创建结果字典
        result = {location: new_pops}
        return result
    
    def change_multiple_locations(
        self,
        locations: List[str],
        source_culture: Optional[str] = None,
        source_religion: Optional[str] = None,
        target_culture: Optional[str] = None,
        target_religion: Optional[str] = None,
        percentage: float = 100.0,
        pop_type: Optional[str] = None
    ) -> Dict[str, List[Dict]]:
        """批量更改多个location的人口文化和宗教"""
        result = {}
        skipped_locations = []
        
        for location in locations:
            try:
                changed = self.change_culture_religion(
                    location=location,
                    source_culture=source_culture,
                    source_religion=source_religion,
                    target_culture=target_culture,
                    target_religion=target_religion,
                    percentage=percentage,
                    pop_type=pop_type
                )
                result.update(changed)
            except ValueError:
                # 静默跳过未找到匹配人口的location（可能是无法通行的地区或没有匹配人口）
                skipped_locations.append(location)
                continue
            except KeyError:
                # 静默跳过未找到的location（无法通行的地区）
                skipped_locations.append(location)
                continue
        
        # 只在最后显示汇总信息
        if skipped_locations:
            print(f"\n  跳过 {len(skipped_locations)} 个 locations（无匹配人口或无法通行地区）")
        
        return result
    
    def format_output(self, changed_populations: Dict[str, List[Dict]]) -> str:
        """格式化输出为EU5脚本格式"""
        output_lines = ["locations = {"]
        
        for loc_name in sorted(changed_populations.keys()):
            output_lines.append(f"\t{loc_name} = {{")
            for pop in changed_populations[loc_name]:
                output_lines.append(
                    f"\t\tdefine_pop = {{\ttype = {pop['type']}\tsize = {pop['size']:.3f}\tculture = {pop['culture']}\treligion = {pop['religion']} }}"
                )
            output_lines.append("\t}")
        
        output_lines.append("}")
        return "\n".join(output_lines)
    
    def update_pops_file(
        self,
        changed_populations: Dict[str, List[Dict]],
        comment: str = "",
        backup: bool = True
    ) -> str:
        """更新原pops文件，替换指定locations的人口数据"""
        # 创建备份
        if backup:
            backup_file = self.pops_file + ".backup"
            import shutil
            shutil.copy2(self.pops_file, backup_file)
            print(f"\n已创建备份文件: {backup_file}")
        
        # 读取原文件
        with open(self.pops_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 找到第一个要被替换的location在文件中的位置
        first_location_index = None
        for i, line in enumerate(lines):
            stripped = line.strip()
            location_match = re.match(r'^[\t\s]*([a-z_][a-z0-9_]*)\s*=\s*\{$', stripped)
            if location_match:
                loc_name = location_match.group(1)
                if loc_name not in ['locations', 'define_pop'] and loc_name in changed_populations:
                    first_location_index = i
                    break
        
        # 构建新的文件内容
        new_lines = []
        i = 0
        skip_location = False
        brace_count = 0
        
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            original_line = line  # 保留原始行（包括换行符）
            
            # 如果在跳过location块中
            if skip_location:
                # 计算大括号（只计算当前行的，不匹配其他location）
                brace_count += line.count('{') - line.count('}')
                if brace_count == 0:
                    # location块结束
                    skip_location = False
                    # 不添加原结束大括号，因为我们已经在前面添加了新的
                i += 1
                continue
            
            # 匹配 location_name = {
            location_match = re.match(r'^[\t\s]*([a-z_][a-z0-9_]*)\s*=\s*\{$', stripped)
            if location_match:
                loc_name = location_match.group(1)
                # 排除关键字
                if loc_name in ['locations', 'define_pop']:
                    new_lines.append(original_line)
                    i += 1
                    continue
                
                # 检查是否需要替换这个location
                if loc_name in changed_populations:
                    # 添加注释（只在第一个被替换的location之前添加一次）
                    if i == first_location_index and comment:
                        new_lines.append(f"\t# {comment}\n")
                    
                    # 添加location定义
                    new_lines.append(f"\t{loc_name} = " + "{\n")
                    
                    # 添加更改后的人口数据
                    for pop in changed_populations[loc_name]:
                        new_lines.append(
                            f"\t\tdefine_pop = " + "{" + f"\ttype = {pop['type']}\tsize = {pop['size']:.3f}\tculture = {pop['culture']}\treligion = {pop['religion']} " + "}\n"
                        )
                    
                    # 添加结束大括号
                    new_lines.append("\t}\n")
                    
                    # 开始跳过原location块
                    skip_location = True
                    brace_count = 1  # 已经有一个开始大括号
                    i += 1
                    continue
            
            # 正常添加其他行
            new_lines.append(original_line)
            i += 1
        
        # 写入新文件
        with open(self.pops_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        return self.pops_file


def main():
    """主函数：按百分比更改人口文化和宗教"""
    print("=" * 60)
    print("EU5 人口文化宗教更改工具")
    print("=" * 60)
    
    # 从命令行参数获取配置
    if len(sys.argv) < 3:
        print("\n用法:")
        print("  python change_pop_culture_religion.py <target> <percentage> [选项] [--area|--region]")
        print("\n参数:")
        print("  target            - area/region/location名称（支持多个，用逗号分隔）")
        print("  percentage        - 转换百分比（0-100）")
        print("\n选项:")
        print("  -sc, --source-culture <文化>    - 源文化（可选，默认所有文化）")
        print("  -sr, --source-religion <宗教>   - 源宗教（可选，默认所有宗教）")
        print("  -tc, --target-culture <文化>    - 目标文化（可选，不指定则不更改）")
        print("  -tr, --target-religion <宗教>   - 目标宗教（可选，不指定则不更改）")
        print("  -pt, --pop-type <类型>          - 只转换指定阶层的人口（可选，默认所有阶层）")
        print("                                    可选值: nobles, clergy, burghers, peasants, laborers, soldiers, slaves")
        print("  -a, --area                      - 指定target为area名称")
        print("  -r, --region                    - 指定target为region名称")
        print("  -l, --location                  - 指定target为location名称（默认）")
        print("\n示例:")
        print("  # 将area的所有人口100%转换为han文化和confucian宗教")
        print("  python change-pops.py ile_de_france_area 100 -tc han -tr confucian -a")
        print("\n  # 将region的所有人口50%转换为han文化")
        print("  python change-pops.py france_region 50 -tc han -r")
        print("\n  # 将location的swedish文化人口50%转换为han文化")
        print("  python change-pops.py stockholm 50 -sc swedish -tc han")
        print("\n  # 将多个area的lutheran宗教人口30%转换为confucian宗教")
        print("  python change-pops.py ile_de_france_area,paris_area 30 -sr lutheran -tr confucian -a")
        print("\n  # 【阶层转换】只转换peasants阶层的人口")
        print("  python change-pops.py france_region 100 -tc han -tr confucian -pt peasants -r")
        print("\n  # 【阶层转换】将巴尔干region所有士兵阶层的人口文化改为土耳其")
        print("  python change-pops.py balkans_region 100 -pt soldiers -tc turkish_culture -r")
        print("\n  # 【阶层转换】将巴尔干region希腊文化的所有阶层人口转换为土耳其文化")
        print("  python change-pops.py balkans_region 100 -sc greek_culture -tc turkish_culture -r")
        print("\n  # 【组合筛选】只转换希腊文化的士兵阶层")
        print("  python change-pops.py balkans_region 100 -sc greek_culture -pt soldiers -tc turkish_culture -r")
        sys.exit(1)
    
    target_str = sys.argv[1]
    percentage = float(sys.argv[2])
    
    if percentage < 0 or percentage > 100:
        print("错误: 百分比必须在0-100之间")
        sys.exit(1)
    
    # 解析target列表
    targets = [t.strip() for t in target_str.split(',')]
    
    # 解析选项
    source_culture = None
    source_religion = None
    target_culture = None
    target_religion = None
    pop_type = None
    target_type = 'location'  # 默认是location
    
    i = 3
    while i < len(sys.argv):
        arg = sys.argv[i]
        # 支持长参数和短参数
        if (arg == '--source-culture' or arg == '-sc') and i + 1 < len(sys.argv):
            source_culture = sys.argv[i + 1]
            i += 2
        elif (arg == '--source-religion' or arg == '-sr') and i + 1 < len(sys.argv):
            source_religion = sys.argv[i + 1]
            i += 2
        elif (arg == '--target-culture' or arg == '-tc') and i + 1 < len(sys.argv):
            target_culture = sys.argv[i + 1]
            i += 2
        elif (arg == '--target-religion' or arg == '-tr') and i + 1 < len(sys.argv):
            target_religion = sys.argv[i + 1]
            i += 2
        elif (arg == '--pop-type' or arg == '-pt') and i + 1 < len(sys.argv):
            pop_type = sys.argv[i + 1]
            i += 2
        elif arg == '--area' or arg == '-a':
            target_type = 'area'
            i += 1
        elif arg == '--region' or arg == '-r':
            target_type = 'region'
            i += 1
        elif arg == '--location' or arg == '-l':
            target_type = 'location'
            i += 1
        else:
            print(f"错误: 未知选项 {sys.argv[i]}")
            sys.exit(1)
    
    # 验证至少指定了目标文化或目标宗教
    if not target_culture and not target_religion:
        print("错误: 必须至少指定 --target-culture 或 --target-religion 之一")
        sys.exit(1)
    
    changer = PopCultureReligionChanger(DEFINITIONS_FILE, POPS_FILE)
    
    try:
        # 根据target_type获取所有locations
        all_locations = []
        
        if target_type == 'region':
            print(f"\n处理 {len(targets)} 个 regions...")
            for region_name in targets:
                locations = changer.get_region_locations(region_name)
                if locations:
                    print(f"  {region_name}: 找到 {len(locations)} 个 locations")
                    all_locations.extend(locations)
        
        elif target_type == 'area':
            print(f"\n处理 {len(targets)} 个 areas...")
            for area_name in targets:
                locations = changer.get_area_locations(area_name)
                if locations:
                    print(f"  {area_name}: 找到 {len(locations)} 个 locations")
                    all_locations.extend(locations)
        
        else:  # location
            all_locations = targets
        
        if not all_locations:
            print("错误: 未找到任何 locations")
            sys.exit(1)
        
        # 去重
        all_locations = list(set(all_locations))
        print(f"\n总共将处理 {len(all_locations)} 个 locations")
        print("正在处理...")
        
        # 批量更改人口
        if len(all_locations) == 1:
            changed_pops = changer.change_culture_religion(
                location=all_locations[0],
                source_culture=source_culture,
                source_religion=source_religion,
                target_culture=target_culture,
                target_religion=target_religion,
                percentage=percentage,
                pop_type=pop_type
            )
        else:
            changed_pops = changer.change_multiple_locations(
                locations=all_locations,
                source_culture=source_culture,
                source_religion=source_religion,
                target_culture=target_culture,
                target_religion=target_religion,
                percentage=percentage,
                pop_type=pop_type
            )
        
        # 生成注释
        comment_parts = []
        if target_type == 'region':
            comment_parts.append(f"Region:{','.join(targets)}")
        elif target_type == 'area':
            comment_parts.append(f"Area:{','.join(targets)}")
        else:
            comment_parts.append(f"Location:{','.join(targets)}")
        if source_culture:
            comment_parts.append(f"源文化:{source_culture}")
        if source_religion:
            comment_parts.append(f"源宗教:{source_religion}")
        if pop_type:
            comment_parts.append(f"类型:{pop_type}")
        if target_culture:
            comment_parts.append(f"→文化:{target_culture}")
        if target_religion:
            comment_parts.append(f"→宗教:{target_religion}")
        comment_parts.append(f"{percentage}%")
        comment = " ".join(comment_parts)
        
        # 更新原pops文件
        print("\n" + "=" * 60)
        print("正在更新原pops文件...")
        print("=" * 60)
        
        updated_file = changer.update_pops_file(changed_pops, comment, backup=True)
        
        # 计算总转换人口
        total_converted = 0
        for loc_pops in changed_pops.values():
            for pop in loc_pops:
                # 检查是否是转换后的人口（匹配目标文化和宗教）
                is_converted = True
                if source_culture and pop.get('culture') == source_culture:
                    is_converted = False
                if source_religion and pop.get('religion') == source_religion:
                    is_converted = False
                if target_culture and pop.get('culture') == target_culture:
                    is_converted = True
                if target_religion and pop.get('religion') == target_religion:
                    is_converted = True
                # 简化：只统计匹配目标的人口
                if target_culture and pop.get('culture') == target_culture:
                    total_converted += pop['size']
                elif target_religion and pop.get('religion') == target_religion:
                    total_converted += pop['size']
        
        print(f"\n[成功] 已更新文件: {updated_file}")
        print(f"[成功] 共处理 {len(changed_pops)} 个 locations")
        if total_converted > 0:
            print(f"[成功] 总计转换约 {total_converted:.1f} 千人口")
        print(f"[成功] 已创建备份文件: {updated_file}.backup")
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

