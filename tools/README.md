# 人口工具使用说明

## 1. 人口缩放脚本 (scale_pops.py)

### 功能
按比例缩放EU5中指定region或area的人口数据，自动更新mod文件夹中的`06_pops.txt`文件。

### 使用方法
```bash
python scale_pops.py <region/area名称> <目标人口> [region/area]
```

### 示例
- 缩放region：`python scale_pops.py france_region 20000.0 region`
- 缩放area：`python scale_pops.py ile_de_france_area 150.0 area`

### 说明
目标人口单位为"千"。脚本会自动创建备份文件，仅修改mod文件夹中的文件，不影响原版游戏。

---

## 2. 人口文化宗教更改工具 (change_pop_culture_religion.py)

### 功能
按百分比更改指定area/region/location的人口文化和宗教，自动更新mod文件夹中的`06_pops.txt`文件。

### 使用方法
```bash
python change_pop_culture_religion.py <target> <percentage> [选项] [--area|--region|--location]
```

### 参数
- `target` - area/region/location名称（支持多个，用逗号分隔）
- `percentage` - 转换百分比（0-100）

### 选项
- `--source-culture <文化>` - 源文化（可选，默认所有文化）
- `--source-religion <宗教>` - 源宗教（可选，默认所有宗教）
- `--target-culture <文化>` - 目标文化（可选，不指定则不更改）
- `--target-religion <宗教>` - 目标宗教（可选，不指定则不更改）
- `--pop-type <类型>` - 人口类型（可选，默认所有类型）
- `--area` - 指定target为area名称
- `--region` - 指定target为region名称
- `--location` - 指定target为location名称（默认）

### 示例

#### Region级别处理

**将region的所有人口100%转换为指定文化和宗教**
```bash
python change_pop_culture_religion.py france_region 100 --target-culture han --target-religion confucian --region
```

**将region的指定文化人口50%转换为目标文化**
```bash
python change_pop_culture_religion.py france_region 50 --source-culture french --target-culture han --region
```

**将region的指定宗教人口30%转换为目标宗教**
```bash
python change_pop_culture_religion.py france_region 30 --source-religion catholic --target-religion confucian --region
```

**批量处理多个regions**
```bash
python change_pop_culture_religion.py france_region,iberia_region 30 --source-religion catholic --target-religion confucian --region
```

#### Area级别处理

**将area的所有人口100%转换为指定文化和宗教**
```bash
python change_pop_culture_religion.py ile_de_france_area 100 --target-culture han --target-religion confucian --area
```

**将area的指定文化人口50%转换为目标文化**
```bash
python change_pop_culture_religion.py ile_de_france_area 50 --source-culture french --target-culture han --area
```

**批量处理多个areas**
```bash
python change_pop_culture_religion.py ile_de_france_area,paris_area 30 --source-religion catholic --target-religion confucian --area
```

#### Location级别处理

**将location的所有人口100%转换为指定文化和宗教**
```bash
python change_pop_culture_religion.py stockholm 100 --target-culture han --target-religion confucian
```

**将指定文化的人口50%转换为目标文化**
```bash
python change_pop_culture_religion.py stockholm 50 --source-culture swedish --target-culture han
```

**将指定宗教的人口30%转换为目标宗教**
```bash
python change_pop_culture_religion.py stockholm 30 --source-religion lutheran --target-religion confucian
```

**批量处理多个locations**
```bash
python change_pop_culture_religion.py stockholm,norrtalje,uppsala 30 --source-religion lutheran --target-religion confucian
```

#### 其他示例

**只更改特定阶层的人口**
```bash
# 只转换peasants阶层
python change-pops.py france_region 100 -tc han -tr confucian -pt peasants -r

# 将巴尔干region所有士兵阶层的人口文化改为土耳其
python change-pops.py balkans_region 100 -pt soldiers -tc turkish_culture -r

# 将巴尔干region希腊文化的所有阶层人口转换为土耳其文化
python change-pops.py balkans_region 100 -sc greek_culture -tc turkish_culture -r

# 组合筛选：只转换希腊文化的士兵阶层
python change-pops.py balkans_region 100 -sc greek_culture -pt soldiers -tc turkish_culture -r
```

**同时更改文化和宗教**
```bash
python change-pops.py france_region 75 -sc french -sr catholic -tc han -tr confucian -r
```

**阶层类型说明**
- `nobles` - 贵族
- `clergy` - 教士
- `burghers` - 市民
- `peasants` - 农民
- `laborers` - 劳工
- `soldiers` - 士兵
- `slaves` - 奴隶

### 说明
- 脚本会自动创建备份文件（`.backup`），仅修改mod文件夹中的文件，不影响原版游戏
- 转换会保持总人口数不变，只是改变文化和宗教的分布
- 支持按百分比部分转换，未转换的人口保持原样
- 可以同时指定源文化和源宗教进行精确筛选
- 支持region、area、location三个级别，会自动处理包含的所有locations
- 使用`--region`或`--area`时，脚本会自动从definitions.txt读取相关locations

---

## 3. 人口清理工具 (remove_zero_pops.py)

### 功能
移除所有 `size = 0.000` 的人口条目，清理无效数据。

### 使用方法
```bash
python remove_zero_pops.py [选项]
```

### 选项
- `--no-backup` - 不创建备份文件（默认会创建备份）
- `--file <路径>` - 指定要处理的文件路径（默认：`main_menu/setup/start/06_pops.txt`）

### 示例
```bash
# 默认使用（会创建备份）
python remove_zero_pops.py

# 不创建备份
python remove_zero_pops.py --no-backup

# 指定文件路径
python remove_zero_pops.py --file path/to/pops.txt
```

### 说明
- 脚本会自动识别并移除所有 `size = 0.000`、`size = 0.0` 等零值人口条目
- 默认会创建备份文件，确保数据安全
- 会显示详细的处理统计信息（移除数量、保留数量等）
