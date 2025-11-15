# 移除已删除国家的动态历史事件标记

## 问题描述

当你删除了某些国家（如CHI、SPA、GBR等）后，原版游戏的事件文件中仍然包含这些国家的`dynamic_historical_event`标记，导致游戏加载时出现大量错误：

```
Event flavor_ara.7 is tagged as an dynamic historical event, but it is for the unknown 'SPA' country.
```

## 解决方案

使用 `remove_deleted_country_events.py` 脚本自动处理这些错误。

## 使用方法

1. **编辑脚本配置**（如果需要）：
   - 打开 `tools/remove_deleted_country_events.py`
   - 修改 `DELETED_COUNTRIES` 列表，添加你删除的国家标签
   - 确认 `GAME_DIR` 路径正确

2. **运行脚本**：
   ```bash
   cd tools
   python remove_deleted_country_events.py
   ```

3. **脚本会**：
   - 扫描原版游戏目录中的所有事件文件
   - 查找包含已删除国家标签的`dynamic_historical_event`块
   - 从块中删除已删除国家的`tag`行
   - 如果块中没有任何tag了，注释掉整个块
   - 将处理后的文件保存到模组的`in_game`目录

## 处理逻辑

- **保留其他tag**：如果`dynamic_historical_event`块中还有其他国家的tag（如ARA），只删除已删除国家的tag行
- **注释空块**：如果块中只剩下已删除国家的tag，注释掉整个块
- **保持结构**：保留文件的原始格式和缩进

## 注意事项

- 脚本会创建模组覆盖文件，不会修改原版游戏文件
- 建议在运行前备份你的模组
- 如果还有其他已删除的国家，请添加到`DELETED_COUNTRIES`列表中

## 示例

处理前：
```txt
dynamic_historical_event = {
    tag = ARA
    tag = SPA
    from = 1640.1.1
    to = 1658.1.1
    monthly_chance = 10
}
```

处理后（如果SPA在删除列表中）：
```txt
dynamic_historical_event = {
    tag = ARA
    from = 1640.1.1
    to = 1658.1.1
    monthly_chance = 10
}
```

如果块中只有已删除的tag：
```txt
# REMOVED: dynamic_historical_event = {
# REMOVED:     tag = SPA
# REMOVED:     from = 1640.1.1
# REMOVED:     to = 1658.1.1
# REMOVED:     monthly_chance = 10
# REMOVED: }
```


