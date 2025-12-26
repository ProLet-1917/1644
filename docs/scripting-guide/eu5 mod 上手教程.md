# 贡献指南

感谢您对1644 EU5模组的贡献兴趣！本指南将一步步教您如何快速添加一个新国家，并立即在游戏中看到成果。

## 目录

1. [快速开始：添加一个新国家](#快速开始添加一个新国家)
2. [如何编辑人物](#如何编辑人物)
3. [进阶：使用Git提交更改（可选）](#进阶使用git提交更改可选)

---

## 快速开始：添加一个新国家

我们的目标是：**在5分钟内创建一个新国家，并在游戏中看到它！**

### 步骤 1：下载项目文件（最简单方式）

您有两种方式获取项目文件：

#### 方式 1：直接下载ZIP（推荐新手）

1. 打开浏览器，访问：https://github.com/ProLet-1917/1644
2. 点击绿色的 **"Code"** 按钮
3. 选择 **"Download ZIP"**
4. 解压下载的ZIP文件到任意位置（如桌面）
5. 进入解压后的 `1644` 文件夹

**就这么简单！** 您已经获得了所有项目文件。

#### 方式 2：使用Git（如果您熟悉Git）

```bash
git clone https://github.com/ProLet-1917/1644.git
cd 1644
```

### 步骤 2：找到模组安装位置

EU5模组需要放在特定文件夹中才能被游戏识别。找到您的模组文件夹：

- **Windows**: `C:\Users\您的用户名\Documents\Paradox Interactive\Europa Universalis V\mod\`
- **Mac**: `~/Documents/Paradox Interactive/Europa Universalis V/mod/`

**操作：**
1. 将 `1644` 文件夹**复制**或**移动**到上述模组文件夹中
2. 最终路径应该是：`...Europa Universalis V\mod\1644\`

### 步骤 3：编辑国家定义文件

现在开始创建您的国家！需要修改**两个文件**：

#### 文件 1：国家基本信息

**文件位置：** `1644\in_game\setup\countries\xxx.txt`
创建一个文本文件，就命名为 （你的名字）.txt

用记事本打开这个文件，添加您的国家：

```txt
# 这是我的新国家 - 示例
MYN = {
	color = rgb { 200 50 100 }  # 地图上的颜色（红=200，绿=50，蓝=100）
	color2 = rgb { 150 30 80 }  # 次要颜色
	culture_definition = han_culture  # 文化：汉族
	religion_definition = sanjiao  # 宗教：三教
}
```

**参数说明：**
- `MYN`：国家代码（必须3个大写字母，且不能和已有的重复）
- `color`：地图显示颜色，格式 `rgb { 红 绿 蓝 }`，每个数字0-255
  - 例如：`rgb { 255 0 0 }` = 红色，`rgb { 0 255 0 }` = 绿色
- `culture_definition`：文化类型
  - `han_culture`（汉族）、`jurchen_culture`（女真）、`korean_culture`（朝鲜）等
- `religion_definition`：宗教类型
  - `sanjiao`（三教）、`mahayana`（大乘佛教）、`shinto`（神道）等

**参考现有国家的格式：**

MNG = {	#Míng
	color = map_MNG
	color2 = rgb { 179 128 104 }
	culture_definition = han_culture
	religion_definition = sanjiao
	#Released during the Crisis events
}
```

#### 文件 2：开局状态

**文件位置：** `1644\main_menu\setup\start\10_countries.txt`

这个文件定义开局时国家的状态。打开文件，找到 `countries = {` 这一行，在这个大括号内（建议放在文件末尾附近），添加：

```txt
# 我的新国家开局设置
MYN = {
	own_control_core = {
		beijing  # 开局控制的省份（必须是游戏中的location名称）
	}
	capital = beijing  # 首都
	starting_technology_level = 4  # 起始科技等级（1-8）
	country_rank = rank_kingdom  # 国家等级
}
```

**参数说明：**
- `own_control_core`：开局拥有的省份列表（每个省份占一行）
  - 常用省份名：`beijing`（北京）、`nanjing`（南京）、`shenyang`（沈阳）等
- `capital`：首都位置（必须是上面列出的省份之一）
- `starting_technology_level`：起始科技等级，建议4-5
- `country_rank`：国家等级
  - `rank_county`（伯爵领）、`rank_duchy`（公爵领）、`rank_kingdom`（王国）、`rank_empire`（帝国）

**完整示例：**
```txt
MYN = {
	own_control_core = {
		beijing
		nanjing
		tianjin
	}
	capital = beijing
	starting_technology_level = 4
	country_rank = rank_kingdom
}
```

### 步骤 4：保存文件

保存您修改的两个文件：
- `in_game\setup\countries\xxx.txt`
- `main_menu\setup\start\10_countries.txt`

按 `Ctrl+S` 保存。

### 步骤 5：在游戏中测试（最重要！）

现在是最激动人心的时刻——在游戏中看到您的国家！

1. **启动游戏**：打开 Europa Universalis V

2. **启用模组**：
   - 在主菜单，找到 **"Mods"** 或 **"模组"** 选项
   - 确保 **"1644"** 模组已勾选
   - 点击 **"Play"** 或 **"开始游戏"**


3. **找到您的国家**：
   - 在地图上找到您设定的省份位置
   - **您应该能看到您创建的国家！** 🎉

4. **验证设置**：
   - 点击您的国家，查看颜色是否正确
   - 检查拥有的省份是否正确
   - 查看文化、宗教等是否匹配

**成功了吗？** 恭喜！您已经成功创建了自己的国家！

**遇到问题？** 检查以下几点：
- 文件是否保存成功？
- 大括号 `{}` 是否配对？
- 国家代码是否与其他国家重复？
- 省份名称是否正确（区分大小写）？

### 步骤 6：查看错误日志（如果有问题）

如果游戏崩溃或国家没有出现，查看错误日志：

1. 打开文件夹：`C:\Users\您的用户名\Documents\Paradox Interactive\Europa Universalis V\logs\`
2. 用记事本打开 `error.log`
3. 查看文件末尾最近的错误信息
4. 根据错误信息修正文件中的问题

常见错误：
- **语法错误**：检查括号、逗号是否配对
- **未定义的省份**：确保省份名称正确
- **重复的国家代码**：更改您的国家代码

---

## 如何编辑人物

添加人物和添加国家的流程类似，但需要了解人物数据结构。

### 文件位置

**人物数据文件：** `1644\main_menu\setup\start\zzz_05_characters.txt`

### 人物结构示例

每个人物的格式如下：

```4:21:main_menu/setup/start/zzz_05_characters.txt
# 朱元璋
chi_zhu_yuanzhang = {
	first_name = {
		name = name_yaun2.name_zhang12
	}
	dynasty = rtr_ming_zhu_dynasty
	culture = jianghuai_culture
	religion = sanjiao
	adm = 95
	dip = 95
	mil = 95
	birth_date = 1328.10.21
	birth = zhongli
	death_date = 1398.6.24
	tag = MNG
	# 法治者
	ruler_trait = lawgiver
}
```

### 添加人物的步骤

1. **打开人物文件**：`main_menu\setup\start\zzz_05_characters.txt`

2. **找到文件开头的 `character_db = {`**，在这个大括号内添加人物

3. **在文件末尾添加您的人物**（建议放在已有的人物后面）：

```txt
# 张三
chi_zhang_san = {
	first_name = {
		name = Zhang_San
	}
	dynasty = example_dynasty
	culture = han_culture
	religion = sanjiao
	adm = 75
	dip = 80
	mil = 70
	birth_date = 1600.1.1
	birth = beijing
	death_date = 1650.1.1
	tag = MYN  # 所属国家（您的国家代码）
	ruler_trait = expansionist
}
```

4. **保存文件**

5. **在游戏中测试**：启动游戏，选择您的国家，检查人物是否出现在统治者或将领列表中

### 常用字段说明

- **人物ID**（如 `chi_zhang_san`）：唯一标识符，建议格式 `chi_姓_名`
- `first_name`：名字（引用本地化文件，或直接用英文）
- `dynasty`：王朝名称
- `culture`：人物文化
- `religion`：人物宗教
- `adm`：行政能力（0-100）
- `dip`：外交能力（0-100）
- `mil`：军事能力（0-100）
- `birth_date`：出生日期（格式：`YYYY.M.D`，如 `1600.1.1`）
- `death_date`：死亡日期
- `birth`：出生地点（location名称）
- `tag`：所属国家代码（必须与您的国家代码匹配）
- `ruler_trait`：统治者特质
  - `lawgiver`（法治者）、`conqueror`（征服者）、`tactical_genius`（战术天才）、`expansionist`（开疆扩土）等

### ⚠️ 重要规则：家族顺序

**子女必须定义在父母之后！** 否则游戏可能崩溃。

✅ **正确顺序：**
```txt
chi_parent = {
	# 父辈定义
}

chi_child = {
	father = chi_parent
	# 子女定义
}
```

❌ **错误顺序（会导致崩溃）：**
```txt
chi_child = {
	father = chi_parent  # 错误：父辈还没定义！
}

chi_parent = {
	# 父辈定义
}
```

---

## 进阶：使用Git提交更改（可选）

如果您想将您的更改分享给其他玩家，可以学习使用Git。这部分是可选的，如果您只是想自己使用，可以跳过。

### 为什么要使用Git？

- 备份您的更改
- 与其他贡献者协作
- 将您的贡献合并到主项目中

### 快速Git指南

#### 1. 安装Git

- 下载：https://git-scm.com/download/win（Windows）或 https://git-scm.com/download/mac（Mac）
- 安装：使用默认设置即可

#### 2. 在项目文件夹中初始化Git

打开命令提示符/终端，进入您的模组文件夹：

```bash
cd "C:\Users\您的用户名\Documents\Paradox Interactive\Europa Universalis V\mod\1644"
git init
git remote add origin https://github.com/ProLet-1917/1644.git
git pull origin main
```

#### 3. 提交您的更改

```bash
# 查看您修改了哪些文件
git status

# 添加修改的文件
git add in_game/setup/countries/east_asia.txt
git add main_menu/setup/start/10_countries.txt

# 提交更改
git commit -m "添加新国家 MYN"

# 推送到GitHub（需要先fork项目）
git push
```

#### 4. 创建Pull Request

1. 访问：https://github.com/ProLet-1917/1644
2. 点击 "Fork" 创建您的副本
3. 推送您的更改到您的fork
4. 点击 "New Pull Request"
5. 填写描述，等待审核

**提示：** 完整的Git工作流程比较复杂，如果您遇到困难，可以：
- 在GitHub上创建Issue询问
- 查看现有的Git教程
- 或者先自己使用，之后再学习Git

---

## 常见问题

### 我的国家没有出现在游戏中

- 检查文件是否保存
- 确认国家代码唯一（没有与其他国家重复）
- 检查语法错误（括号配对）
- 查看错误日志

### 省份显示不正确

- 确认省份名称正确（区分大小写）
- 检查省份是否在游戏中存在

### 游戏崩溃

- 查看错误日志
- 检查语法错误
- 确认人物定义顺序正确（子女在父母后）

### 如何修改已有国家？

找到对应的国家代码（如 `MNG`），直接修改属性即可。记得保存文件并在游戏中测试。

---

## 需要帮助？

- **遇到问题？** 在GitHub创建Issue：https://github.com/ProLet-1917/1644/issues
- **不确定怎么做？** 查看项目中现有的国家和人物定义作为参考
- **想要更多功能？** 查看EU5模组开发文档：https://eu5.paradoxwikis.com/

**祝您模组制作愉快！** 🎮
