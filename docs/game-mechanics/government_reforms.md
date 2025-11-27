# 政府改革系统

## 概述
政府改革是EU5中定义国家政治体制的核心系统。

## 基本结构

```
reform_name = {
    # 改革的图标
    icon = "reform_icon"
    
    # 改革所属的改革层级
    reform_level = 1
    
    # 改革提供的修正
    modifiers = {
        global_tax_modifier = 0.10
        production_efficiency = 0.10
    }
    
    # 改革的触发条件
    trigger = {
        has_reform = previous_reform
    }
}
```

## 常用字段

- `icon`: 改革图标
- `reform_level`: 改革层级（1-5）
- `modifiers`: 提供的修正器
- `trigger`: 触发条件
- `removed_effect`: 移除时的效果
- `custom_attributes`: 自定义属性

## 示例

参见游戏文件: `common/government_reforms/`
