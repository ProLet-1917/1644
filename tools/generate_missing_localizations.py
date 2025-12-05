#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成缺失的本地化文件
为所有中文本地化文件生成对应的英文版本，反之亦然
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Mod根目录
MOD_ROOT = Path(__file__).parent.parent

# 本地化目录
MAIN_MENU_CN = MOD_ROOT / "main_menu" / "localization" / "simp_chinese"
MAIN_MENU_EN = MOD_ROOT / "main_menu" / "localization" / "english"
IN_GAME_CN = MOD_ROOT / "in_game" / "localization" / "simp_chinese"
IN_GAME_EN = MOD_ROOT / "in_game" / "localization" / "english"

# 创建目录
IN_GAME_EN.mkdir(parents=True, exist_ok=True)
(MAIN_MENU_EN / "location_names").mkdir(parents=True, exist_ok=True)


def parse_localization_file(file_path: Path) -> Tuple[str, List[Tuple[str, str, str, str]]]:
    """
    解析本地化文件
    返回: (语言标识, [(完整行, key, version, value), ...])
    """
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    lines = content.split('\n')
    language = lines[0].strip() if lines else "l_english:"
    
    entries = []
    for line in lines[1:]:
        # 跳过空行和注释
        if not line.strip() or line.strip().startswith('#'):
            entries.append((line, None, None, None))
            continue
        
        # 匹配 key:version "value" 或 key: "value" (注意冒号后可能有空格)
        # key可以包含字母、数字、下划线、点号、中文
        match = re.match(r'^\s*([a-zA-Z0-9_.\u4e00-\u9fff]+)\s*:\s*(\d+)?\s*"(.+)"', line)
        if match:
            key = match.group(1)
            version = match.group(2) if match.group(2) else None
            value = match.group(3)
            entries.append((line, key, version, value))
        else:
            entries.append((line, None, None, None))
    
    return language, entries


def extract_name_from_key(key: str) -> str:
    """
    从key中提取人名
    - 如果包含中文，返回中文部分
    - 如果是英文名，提取name_后的部分并格式化（首字母大写，下划线转空格）
    """
    # 检查是否包含中文
    chinese_chars = re.findall(r'[\u4e00-\u9fff]+', key)
    if chinese_chars:
        return ''.join(chinese_chars)
    
    # 先去掉点号后的语言后缀
    # 例如: name_aaron.coptic_language -> name_aaron
    base_key = key.split('.')[0]
    
    # 处理英文名：提取 name_ 后的部分
    # 例如: name_aaron -> Aaron
    #      name_abd_al_qadir -> Abd Al Qadir
    match = re.match(r'^name_([a-z_]+)', base_key, re.IGNORECASE)
    if match:
        name_part = match.group(1)
        # 将下划线转为空格，并首字母大写
        name_words = name_part.split('_')
        formatted_name = ' '.join(word.capitalize() for word in name_words)
        return formatted_name
    
    # 处理其他带name的key（如 character_name_, dynasty_name_ 等）
    if '_name_' in base_key or base_key.startswith('name_') or base_key.endswith('_name'):
        # 尝试提取最有意义的部分
        parts = base_key.split('_')
        # 找到name后面的部分
        try:
            name_idx = parts.index('name')
            if name_idx + 1 < len(parts):
                name_part = parts[name_idx + 1]
                return name_part.capitalize()
        except ValueError:
            pass
    
    # 默认返回key本身
    return key


def is_name_key(key: str) -> bool:
    """
    判断是否是人名、地名相关的key
    """
    name_patterns = [
        r'^name_',
        r'^character_name_',
        r'^dynasty_name_',
        r'^noble_name_',
        r'^ruler_name_',
        r'_name$',
        r'^province_name_',
        r'^state_name_',
        r'^region_name_',
    ]
    for pattern in name_patterns:
        if re.search(pattern, key):
            return True
    return False


def generate_opposite_language_file(source_file: Path, target_file: Path, 
                                     source_lang: str, target_lang: str):
    """
    根据源语言文件生成目标语言文件
    """
    print(f"正在生成: {target_file.name}")
    
    language, entries = parse_localization_file(source_file)
    
    # 准备输出内容
    output_lines = [f"{target_lang}:\n"]
    
    for line, key, version, value in entries:
        if key is None:
            # 保留注释和空行
            output_lines.append(line + '\n')
        else:
            # 生成翻译值
            if target_lang == "l_english":
                # 中文 -> 英文
                if is_name_key(key):
                    # 人名地名：提取并格式化名字
                    trans_value = extract_name_from_key(key)
                else:
                    # 其他：使用key名
                    trans_value = key
            else:
                # 英文 -> 中文：直接使用英文原文
                trans_value = value
            
            # 构造输出行（保持原有缩进和版本号格式）
            if version is not None:
                # 有版本号格式
                output_lines.append(f' {key}:{version} "{trans_value}"\n')
            else:
                # 无版本号格式
                output_lines.append(f' {key}: "{trans_value}"\n')
    
    # 写入文件（带BOM）
    with open(target_file, 'w', encoding='utf-8-sig') as f:
        f.writelines(output_lines)
    
    print(f"  ✓ 已生成 {len([e for e in entries if e[1] is not None])} 个条目")


def main():
    """主函数"""
    print("=" * 60)
    print("开始生成缺失的本地化文件")
    print("=" * 60)
    
    generated_files = []
    
    # 1. 为中文文件生成英文版本
    print("\n[1/3] 为中文本地化生成英文版本...")
    
    # main_menu中文 -> 英文
    for cn_file in MAIN_MENU_CN.glob("*.yml"):
        en_filename = cn_file.name.replace("_simp_chinese", "_english")
        en_file = MAIN_MENU_EN / en_filename
        
        if not en_file.exists():
            generate_opposite_language_file(cn_file, en_file, "l_simp_chinese", "l_english")
            generated_files.append(str(en_file.relative_to(MOD_ROOT)))
    
    # main_menu/location_names中文 -> 英文
    location_names_cn = MAIN_MENU_CN / "location_names"
    if location_names_cn.exists():
        location_names_en = MAIN_MENU_EN / "location_names"
        for cn_file in location_names_cn.glob("*.yml"):
            en_filename = cn_file.name.replace("_simp_chinese", "_english")
            en_file = location_names_en / en_filename
            
            if not en_file.exists():
                generate_opposite_language_file(cn_file, en_file, "l_simp_chinese", "l_english")
                generated_files.append(str(en_file.relative_to(MOD_ROOT)))
    
    # in_game中文 -> 英文
    for cn_file in IN_GAME_CN.glob("*.yml"):
        en_filename = cn_file.name.replace("_simp_chinese", "_english")
        en_file = IN_GAME_EN / en_filename
        
        if not en_file.exists():
            generate_opposite_language_file(cn_file, en_file, "l_simp_chinese", "l_english")
            generated_files.append(str(en_file.relative_to(MOD_ROOT)))
    
    # 2. 为英文文件生成中文版本
    print("\n[2/3] 为英文本地化生成中文版本...")
    
    for en_file in MAIN_MENU_EN.glob("*.yml"):
        cn_filename = en_file.name.replace("_english", "_simp_chinese")
        cn_file = MAIN_MENU_CN / cn_filename
        
        if not cn_file.exists():
            generate_opposite_language_file(en_file, cn_file, "l_english", "l_simp_chinese")
            generated_files.append(str(cn_file.relative_to(MOD_ROOT)))
    
    # 3. 生成报告
    print("\n[3/3] 生成补全报告...")
    
    report_content = f"""# 本地化文件补全报告

## 执行时间
{os.popen('powershell Get-Date').read().strip()}

## 生成的文件

共生成 **{len(generated_files)}** 个本地化文件：

### 英文本地化文件
"""
    
    en_files = [f for f in generated_files if "_english" in f]
    for f in en_files:
        report_content += f"- `{f}`\n"
    
    report_content += "\n### 中文本地化文件\n"
    cn_files = [f for f in generated_files if "_simp_chinese" in f]
    for f in cn_files:
        report_content += f"- `{f}`\n"
    
    report_content += """

## 翻译策略

### 人名地名处理
- **Key模式**: `name_*`, `character_name_*`, `dynasty_name_*` 等
- **策略**: 提取key中的中文部分作为英文翻译
- **示例**: `name_李自成` → 英文翻译为 `"李自成"`

### 其他内容处理
- **策略**: 使用key名本身作为临时翻译
- **示例**: `ming_reform` → 翻译为 `"ming_reform"`

## 后续人工翻译优先级

建议按以下优先级进行人工翻译：

### 高优先级（玩家直接可见）
1. **事件文本**: `00_1644_events_l_english.yml`, `00_1644_wsg_events_l_english.yml`
2. **任务**: `00_1644_missions_l_english.yml`
3. **建筑**: `00_1644_buildings_l_english.yml`
4. **科技/进步**: `00_1644_advances_l_english.yml`

### 中优先级（游戏机制相关）
5. **法律政策**: `00_laws_and_policies_l_english.yml`
6. **政府改革**: `00_government_reforms_l_english.yml`
7. **国际组织状态**: `00_1644_io_statuses_l_english.yml`
8. **单位**: `00_units_l_english.yml`

### 低优先级（背景信息）
9. **人口**: `00_pops_l_english.yml`
10. **文化**: `00_cultures_l_english.yml`
11. **省份**: `00_province_l_english.yml`
12. **人名**: `00_character_names_dynamic_l_english.yml`（已使用中文）
13. **地名**: `location_names/00_province_l_english.yml`（已使用中文）

## 注意事项

- 所有文件均使用 **UTF-8 BOM** 编码
- Key名保持与源文件完全一致
- 版本号（如 `:0`）已保留
- 注释和空行已保留
- 人名地名已从key中提取中文，其他内容为占位符

## 下一步

1. 在游戏中测试，确保所有本地化条目正常加载
2. 按优先级逐步进行人工翻译
3. 建议使用版本控制，方便团队协作翻译
"""
    
    report_file = MOD_ROOT / "docs" / "localization_completion_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"  ✓ 报告已保存至: {report_file.relative_to(MOD_ROOT)}")
    
    print("\n" + "=" * 60)
    print(f"完成！共生成 {len(generated_files)} 个文件")
    print("=" * 60)


if __name__ == "__main__":
    main()

