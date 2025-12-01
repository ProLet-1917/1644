# EU5 征召兵竞争机制详解

## 一、核心竞争原则

### 1. "第一个匹配"原则

**关键机制**：游戏使用**"第一个匹配"（First Match）**机制来决定使用哪个levy。

根据readme和代码注释：
```
# Picks first valid entry
# Otherwise, the game will just fill all the available levy picks 
# with the first levy it finds and move on.
```

**工作原理**：
1. 游戏按顺序检查所有levy定义
2. 找到**第一个完全匹配**的levy后立即使用
3. **不再检查后续levy**
4. 该pop的所有征召兵都使用这个匹配到的levy类型

### 2. 检查顺序（优先级）

游戏按以下顺序检查levy：

#### 第一优先级：文件加载顺序

文件按**文件名排序**加载：
- `00_xxx.txt` → 最先加载
- `01_xxx.txt` → 第二
- `02_xxx.txt` → 第三
- ...
- `10_xxx.txt` → 最后

**示例**：
```
00_revolutions_levies.txt      ← 最先检查
01_absolutism_levies.txt
02_reformation_levies.txt
03_discovery_levies.txt
04_renaissance_levies.txt
05_traditions_levies.txt
06_tribal_levies.txt
10_traditions_levies_navy.txt  ← 最后检查
```

#### 第二优先级：文件内顺序

在同一文件内，按**从上到下的顺序**检查：
- 文件第一行的levy → 最先检查
- 文件第二行的levy → 第二
- ...
- 文件最后一行的levy → 最后

## 二、匹配条件检查顺序

对于每个levy定义，游戏按以下顺序检查条件：

### 1. country_allow（国家层面）

```cpp
country_allow = {
    tag = QNG
}
```

如果国家条件不满足，**立即跳过**该levy，不检查后续条件。

### 2. allowed_pop_type（Pop类型）

```cpp
allowed_pop_type = nobles
allowed_pop_type = soldiers
```

如果pop类型不在允许列表中，**立即跳过**该levy。

### 3. allowed_culture（文化）

```cpp
allowed_culture = jurchen_culture
allowed_culture = manchu_culture
```

如果pop文化不在允许列表中，**立即跳过**该levy。

### 4. allow（Pop层面额外条件）

```cpp
allow = {
    owner = { tag = QNG }
    OR = {
        culture = jurchen_culture
        culture = manchu_culture
    }
}
```

如果pop层面条件不满足，**立即跳过**该levy。

### 5. allow_as_crew（船员条件，仅海军）

```cpp
allow_as_crew = {
    # 条件
}
```

## 三、竞争策略

### 策略1：条件严格性排序

**原则**：条件最严格的levy应该放在**最前面**。

**原因**：
- 如果通用levy在前面，会匹配所有符合条件的pop
- 特殊levy在后面，永远不会被匹配到

**示例**：

❌ **错误排序**：
```cpp
// 01_absolutism_levies.txt
levy_a_militiamen = {          // ← 通用，匹配所有peasants
    allowed_pop_type = peasants
    unit = a_militiamen
}

levy_a_scottish_highlander = { // ← 特殊，永远不会被匹配
    allowed_pop_type = peasants
    allowed_culture = highland
    unit = a_scottish_highlander
}
```

✅ **正确排序**：
```cpp
// 01_absolutism_levies.txt
levy_a_scottish_highlander = { // ← 特殊，先检查
    allowed_pop_type = peasants
    allowed_culture = highland
    unit = a_scottish_highlander
}

levy_a_militiamen = {          // ← 通用，后检查
    allowed_pop_type = peasants
    unit = a_militiamen
}
```

### 策略2：文件命名优先级

**原则**：最重要的levy应该放在**文件名最靠前**的文件中。

**示例**：

对于清朝八旗骑兵：
```
00_1644_banner_levies.txt      ← 八旗骑兵，最高优先级
01_absolutism_levies.txt       ← 原版通用levy
02_reformation_levies.txt
...
```

### 策略3：条件数量决定优先级

**原则**：条件数量越多，应该越靠前。

**条件严格性排序**（从严格到宽松）：

1. **最严格**：`country_allow` + `allowed_pop_type` + `allowed_culture` + `allow`
2. **较严格**：`country_allow` + `allowed_pop_type` + `allowed_culture`
3. **中等**：`allowed_pop_type` + `allowed_culture`
4. **较宽松**：`allowed_pop_type` + `allow`
5. **最宽松**：只有`allowed_pop_type`

## 四、实际竞争示例

### 示例1：苏格兰高地人 vs 普通民兵

**场景**：苏格兰的highland文化peasants

**文件顺序**：
```
01_absolutism_levies.txt
```

**文件内容**：
```cpp
// 正确排序
levy_a_scottish_highlander = {  // ← 先检查
    allowed_pop_type = peasants
    allowed_culture = highland
    unit = a_scottish_highlander
}

levy_a_militiamen = {            // ← 后检查
    allowed_pop_type = peasants
    unit = a_militiamen
}
```

**匹配过程**：
1. 检查`levy_a_scottish_highlander`：
   - ✅ `allowed_pop_type = peasants`（匹配）
   - ✅ `allowed_culture = highland`（匹配）
   - ✅ **使用此levy**

2. 不再检查`levy_a_militiamen`

**结果**：highland文化的peasants使用`a_scottish_highlander`

### 示例2：八旗骑兵 vs 通用骑兵

**场景**：清朝的满族nobles

**文件顺序**：
```
00_1644_banner_levies.txt      ← 先检查
01_absolutism_levies.txt
02_reformation_levies.txt
```

**文件内容**：

`00_1644_banner_levies.txt`：
```cpp
levy_a_banner_cavalry = {
    country_allow = { tag = QNG }
    allowed_pop_type = nobles
    allowed_culture = jurchen_culture
    allowed_culture = manchu_culture
    allow = {
        owner = { tag = QNG }
    }
    unit = a_banner_cavalry
}
```

`01_absolutism_levies.txt`：
```cpp
levy_provincial_cavalry = {
    allowed_pop_type = nobles
    unit = a_provincial_cavalry
}
```

**匹配过程**：
1. 检查`00_1644_banner_levies.txt`中的`levy_a_banner_cavalry`：
   - ✅ `country_allow = { tag = QNG }`（匹配）
   - ✅ `allowed_pop_type = nobles`（匹配）
   - ✅ `allowed_culture = jurchen_culture`（匹配）
   - ✅ `allow = { owner = { tag = QNG } }`（匹配）
   - ✅ **使用此levy**

2. 不再检查后续文件中的`levy_provincial_cavalry`

**结果**：清朝的满族nobles使用`a_banner_cavalry`，而不是`a_provincial_cavalry`

### 示例3：多个条件竞争的复杂情况

**场景**：有tribes特权的非游牧国家的tribesmen（在有马匹的location）

**文件顺序**：
```
06_tribal_levies.txt
```

**文件内容**：
```cpp
levy_tribal_cavalry = {          // ← 先检查
    allowed_pop_type = tribesmen
    allow = {
        location = {
            market = {
                OR = {
                    is_produced_in_market = goods:horses
                    is_traded_in_market = goods:horses
                }
            }
        }
    }
    country_allow = {
        has_estate_privilege = estate_privilege:tribes_tribal_levies
        NOT = { government_type = government_type:steppe_horde }
    }
    unit = a_tribal_cavalry
}

levy_tribesmen = {               // ← 后检查（默认）
    allowed_pop_type = peasants
    allowed_pop_type = tribesmen
    unit = a_tribesmen
}
```

**匹配过程**：
1. 检查`levy_tribal_cavalry`：
   - ✅ `allowed_pop_type = tribesmen`（匹配）
   - ✅ `allow`条件（location有马匹）（匹配）
   - ✅ `country_allow`条件（有特权且非游牧）（匹配）
   - ✅ **使用此levy**

2. 不再检查`levy_tribesmen`

**结果**：符合条件的tribesmen使用`a_tribal_cavalry`

## 五、常见竞争问题

### 问题1：特殊levy没有被使用

**原因**：通用levy在文件中的位置更靠前

**解决方案**：
1. 将特殊levy移到文件顶部
2. 或将特殊levy移到文件名更靠前的文件中

### 问题2：多个特殊levy竞争

**场景**：一个pop可以匹配多个特殊levy

**解决方案**：
1. 按条件严格性排序（最严格的在前）
2. 使用文件命名优先级（最重要的在00开头文件）

### 问题3：原版levy覆盖了自定义levy

**原因**：原版文件加载顺序更靠前

**解决方案**：
1. 自定义levy文件使用`00_`开头
2. 确保自定义levy条件更严格

## 六、最佳实践

### 1. 文件命名策略

```
00_<mod_name>_special_levies.txt    ← 最特殊的levy
01_<mod_name>_general_levies.txt    ← 通用levy
```

### 2. 文件内排序策略

```cpp
// 文件顶部：最特殊的levy
levy_most_specific = {
    country_allow = { ... }
    allowed_pop_type = ...
    allowed_culture = ...
    allow = { ... }
}

// 文件中部：中等特殊的levy
levy_moderately_specific = {
    allowed_pop_type = ...
    allowed_culture = ...
}

// 文件底部：通用levy
levy_generic = {
    allowed_pop_type = ...
}
```

### 3. 条件设计策略

**原则**：特殊levy应该包含尽可能多的限制条件

**示例**：
```cpp
// 八旗骑兵：4个条件
levy_a_banner_cavalry = {
    country_allow = { tag = QNG }           // 条件1：国家
    allowed_pop_type = nobles               // 条件2：Pop类型
    allowed_culture = jurchen_culture       // 条件3：文化
    allow = { owner = { tag = QNG } }       // 条件4：Pop层面
}
```

## 七、调试技巧

### 1. 检查文件加载顺序

确认自定义levy文件是否在`00_`开头，优先于原版文件。

### 2. 检查文件内顺序

确认特殊levy是否在文件顶部，通用levy在底部。

### 3. 检查条件严格性

确认特殊levy的条件是否比通用levy更严格。

### 4. 测试匹配逻辑

创建一个测试pop，手动检查会匹配哪个levy：
1. 检查`country_allow`
2. 检查`allowed_pop_type`
3. 检查`allowed_culture`
4. 检查`allow`条件

## 八、总结

**核心机制**：
- ✅ 第一个匹配的levy会被使用
- ✅ 一旦匹配，不再检查后续levy
- ✅ 文件加载顺序决定优先级
- ✅ 文件内顺序决定优先级

**关键原则**：
- ✅ 条件最严格的levy应该在最前面
- ✅ 特殊levy应该优先于通用levy
- ✅ 使用文件命名和文件内排序来控制优先级



