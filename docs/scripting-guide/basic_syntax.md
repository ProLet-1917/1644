# EU5脚本基础语法

## 基本结构

EU5使用类似于PDX脚本的语法：

```
key = value
key = { ... }  # 代码块
```

## 数据类型

1. **字符串**: `name = "China"`
2. **数字**: `value = 100`
3. **布尔值**: `enabled = yes` 或 `enabled = no`
4. **列表**: `tags = { CHI JAP KOR }`

## 触发器 (Triggers)

触发器用于检查条件：

```
trigger = {
    tag = CHI
    has_reform = monarchy
    num_of_cities = 10
}
```

## 效果 (Effects)

效果用于执行操作：

```
effect = {
    add_country_modifier = {
        name = centralization
        duration = 3650
    }
    add_treasury = 1000
}
```

## 作用域 (Scopes)

- `ROOT`: 当前作用域
- `FROM`: 事件发送者
- `THIS`: 当前国家
- `PREV`: 上一个作用域

## 最佳实践

1. 使用缩进增加可读性
2. 添加注释说明复杂逻辑
3. 使用本地化键而非硬编码文本
4. 测试所有触发条件
