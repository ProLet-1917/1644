#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EU5 Area Population Scaling Script
功能：输入一个area和area总人口，从相关definition里读取area的所有地块，
按比例缩放人口，得到新人口数据。
"""

import re
import os
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

# 路径配置
# 自动获取脚本所在目录，向上一级到mod根目录（1644文件夹）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MOD_PATH = os.path.dirname(SCRIPT_DIR)
GAME_PATH = r"E:\SteamLibrary\steamapps\common\Europa Universalis V\game"
DEFINITIONS_FILE = os.path.join(GAME_PATH, "in_game", "map_data", "definitions.txt")
POPS_FILE = os.path.join(MOD_PATH, "main_menu", "setup", "start", "06_pops.txt")


class AreaPopulationScaler:
    def __init__(self, definitions_file: str, pops_file: str):
        self.definitions_file = definitions_file
        self.pops_file = pops_file
        self.areas = {}
        self.populations = {}
        
    def parse_definitions(self) -> Dict[str, List[str]]:
        """解析definitions.txt，提取所有area及其包含的locations"""
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
                    # 不输出所有area的日志，只在需要时输出
                
                continue
            
            i += 1
        
        self.areas = areas
        return areas
    
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
                
                # 跳过文件开头的 "locations = {"
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
                            'religion': pop_match.group(4)
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
    
    def calculate_total_population(self, locations: List[str]) -> float:
        """计算指定locations的总人口"""
        if not self.populations:
            self.parse_populations()
        
        total = 0.0
        found_locations = []
        missing_locations = []
        
        for loc in locations:
            if loc in self.populations:
                loc_total = sum(pop['size'] for pop in self.populations[loc])
                total += loc_total
                found_locations.append((loc, loc_total))
            else:
                missing_locations.append(loc)
        
        return total, found_locations, missing_locations
    
    def scale_multiple_areas(self, area_names: List[str], target_total: float) -> Dict[str, List[Dict]]:
        """按比例缩放多个area的人口数据"""
        all_locations = []
        area_location_map = {}  # 记录每个location属于哪个area
        
        # 收集所有locations
        for area_name in area_names:
            locations = self.get_area_locations(area_name)
            if locations:
                all_locations.extend(locations)
                for loc in locations:
                    area_location_map[loc] = area_name
        
        if not all_locations:
            raise ValueError(f"未找到任何area的locations")
        
        print(f"\n处理 {len(area_names)} 个 areas")
        print(f"包含 {len(all_locations)} 个 locations")
        
        # 计算当前总人口
        current_total, found_locations, missing_locations = self.calculate_total_population(all_locations)
        
        if current_total == 0:
            raise ValueError(f"当前总人口为0，无法缩放")
        
        print(f"\n当前总人口: {current_total:.3f}")
        print(f"目标总人口: {target_total:.3f}")
        print(f"缩放比例: {target_total / current_total:.6f}")
        
        if missing_locations:
            print(f"\n警告：以下 {len(missing_locations)} 个 locations 没有人口数据:")
            for loc in missing_locations[:10]:
                print(f"  - {loc}")
            if len(missing_locations) > 10:
                print(f"  ... 还有 {len(missing_locations) - 10} 个")
        
        # 计算缩放比例
        scale_factor = target_total / current_total
        
        # 缩放每个location的人口
        scaled_populations = {}
        for loc in found_locations:
            loc_name, loc_total = loc
            scaled_pops = []
            
            for pop in self.populations[loc_name]:
                scaled_pop = pop.copy()
                scaled_pop['size'] = pop['size'] * scale_factor
                scaled_pops.append(scaled_pop)
            
            scaled_populations[loc_name] = scaled_pops
        
        # 验证总人口
        new_total = sum(
            sum(pop['size'] for pop in pops)
            for pops in scaled_populations.values()
        )
        print(f"\n缩放后总人口: {new_total:.3f} (目标: {target_total:.3f}, 误差: {abs(new_total - target_total):.6f})")
        
        return scaled_populations
    
    def scale_population(self, area_name: str, target_total: float) -> Dict[str, List[Dict]]:
        """按比例缩放area的人口数据"""
        # 获取area的所有locations
        locations = self.get_area_locations(area_name)
        if not locations:
            raise ValueError(f"未找到 area: {area_name}")
        
        print(f"\n处理 area: {area_name}")
        print(f"包含 {len(locations)} 个 locations")
        
        # 计算当前总人口
        current_total, found_locations, missing_locations = self.calculate_total_population(locations)
        
        if current_total == 0:
            raise ValueError(f"area {area_name} 的当前总人口为0，无法缩放")
        
        print(f"\n当前总人口: {current_total:.3f}")
        print(f"目标总人口: {target_total:.3f}")
        print(f"缩放比例: {target_total / current_total:.6f}")
        
        if missing_locations:
            print(f"\n警告：以下 {len(missing_locations)} 个 locations 没有人口数据:")
            for loc in missing_locations[:10]:  # 只显示前10个
                print(f"  - {loc}")
            if len(missing_locations) > 10:
                print(f"  ... 还有 {len(missing_locations) - 10} 个")
        
        # 计算缩放比例
        scale_factor = target_total / current_total
        
        # 缩放每个location的人口
        scaled_populations = {}
        for loc in found_locations:
            loc_name, loc_total = loc
            scaled_pops = []
            
            for pop in self.populations[loc_name]:
                scaled_pop = pop.copy()
                scaled_pop['size'] = pop['size'] * scale_factor
                scaled_pops.append(scaled_pop)
            
            scaled_populations[loc_name] = scaled_pops
        
        # 验证总人口
        new_total = sum(
            sum(pop['size'] for pop in pops)
            for pops in scaled_populations.values()
        )
        print(f"\n缩放后总人口: {new_total:.3f} (目标: {target_total:.3f}, 误差: {abs(new_total - target_total):.6f})")
        
        return scaled_populations
    
    def format_output(self, scaled_populations: Dict[str, List[Dict]], comment: str = "") -> str:
        """格式化输出为EU5脚本格式"""
        output_lines = ["locations = {"]
        
        # 添加注释
        if comment:
            output_lines.append(f"\t# {comment}")
            output_lines.append("")
        
        for loc_name in sorted(scaled_populations.keys()):
            output_lines.append(f"\t{loc_name} = {{")
            for pop in scaled_populations[loc_name]:
                output_lines.append(
                    f"\t\tdefine_pop = {{\ttype = {pop['type']}\tsize = {pop['size']:.3f}\tculture = {pop['culture']}\treligion = {pop['religion']} }}"
                )
            output_lines.append("\t}")
        
        output_lines.append("}")
        return "\n".join(output_lines)
    
    def update_pops_file(self, scaled_populations: Dict[str, List[Dict]], comment: str = "", backup: bool = True) -> str:
        """更新原pops文件，替换指定locations的人口数据"""
        # 创建备份
        if backup:
            backup_file = self.pops_file + ".backup"
            import shutil
            shutil.copy2(self.pops_file, backup_file)
            print(f"已创建备份文件: {backup_file}")
        
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
                if loc_name not in ['locations', 'define_pop'] and loc_name in scaled_populations:
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
                if loc_name in scaled_populations:
                    # 添加注释（只在第一个被替换的location之前添加一次）
                    if i == first_location_index and comment:
                        new_lines.append(f"\t# {comment}\n")
                    
                    # 添加location定义
                    new_lines.append(f"\t{loc_name} = " + "{\n")
                    
                    # 添加缩放后的人口数据
                    for pop in scaled_populations[loc_name]:
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
    """主函数：按比例缩放region或area的人口数据"""
    import sys
    
    print("=" * 60)
    print("EU5 Area/Region Population Scaling Script")
    print("=" * 60)
    
    # 从命令行参数获取配置，或使用默认值
    if len(sys.argv) >= 3:
        target_name = sys.argv[1]  # region或area名称
        target_population = float(sys.argv[2])  # 目标人口
        is_region = len(sys.argv) > 3 and sys.argv[3].lower() == 'region'
    else:
        # 默认配置：法国region，2000万人口
        target_name = "france_region"
        target_population = 2000.0
        is_region = True
        print("\n使用默认配置（可通过命令行参数修改）:")
        print("  用法: python scale_pops.py <region/area名称> <目标人口> [region/area]")
        print("  示例: python scale_pops.py france_region 2000.0 region")
        print("  示例: python scale_pops.py ile_de_france_area 150.0 area")
    
    scaler = AreaPopulationScaler(DEFINITIONS_FILE, POPS_FILE)
    
    try:
        if is_region:
            # 处理region
            print(f"\n正在查找 {target_name} 下的所有 areas...")
            area_names = scaler.get_region_areas(target_name)
            
            if not area_names:
                raise ValueError(f"未找到 {target_name} 下的任何 area")
            
            print(f"找到 {len(area_names)} 个 areas:")
            for area in area_names[:10]:  # 只显示前10个
                print(f"  - {area}")
            if len(area_names) > 10:
                print(f"  ... 还有 {len(area_names) - 10} 个")
            
            # 缩放人口
            scaled_pops = scaler.scale_multiple_areas(area_names, target_population)
            
            # 生成注释
            comment = f"Scaled population for {target_name}: {target_population:.1f}千 (from {len(area_names)} areas)"
        else:
            # 处理单个area
            print(f"\n正在处理 area: {target_name}...")
            scaled_pops = scaler.scale_population(target_name, target_population)
            
            # 生成注释
            comment = f"Scaled population for {target_name}: {target_population:.1f}千"
        
        # 更新原pops文件
        print("\n" + "=" * 60)
        print("正在更新原pops文件...")
        print("=" * 60)
        
        updated_file = scaler.update_pops_file(scaled_pops, comment, backup=True)
        
        print(f"\n[成功] 已更新文件: {updated_file}")
        print(f"[成功] 共处理 {len(scaled_pops)} 个 locations")
        print(f"[成功] 已创建备份文件: {updated_file}.backup")
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

