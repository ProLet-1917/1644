# 国家科技与军事体系概览

本节汇总 EU5 原版与本模组在“国家科技（Advances）”及“军事体系”方面的核心脚本结构，便于快速查阅和扩展。

## 科技（Advances）

- **定义位置**
  - 原版：`game/in_game/common/advances/`
  - 模组覆盖/新增：建议放在 `in_game/common/advances/`（当前为空，可按需复制原版模板）
- **组织方式**
  - 以 Age 为核心划分（如 `0_age_of_traditions.txt`、`0_age_of_reformation.txt`），对应国家在该时代可研究的基础科技线。
  - 进阶内容（解锁建筑、军队、内阁、改革等）独立拆分在 `1_*.txt`、`2_*.txt`、`3_*.txt` 文件中，通过 `requires` 字段串联研究顺序。
  - 针对文化、地区、国家、宗教等的专属科技位于 `country_*.txt`、`culture_*.txt` 等文件；模组定制时可针对 TAG 或文化组单独维护。
- **常用字段（参见 `advances/readme.txt`）**
  - `age`：所属时代；控制科技出现的时代。
  - `requires`：前置科技；决定解锁顺序。
  - `for = adm/dip/mil`：限制于行政/外交/军事三专精；与时代选择的专精呼应。
  - `allow` / `potential`：触发条件（是否可研究/是否显示）。注意 `potential` 不会追溯检查，必须在时代开始前满足。
  - 解锁相关：`unlock_unit`、`unlock_ability`、`unlock_building`、`unlock_law`、`unlock_levy` 等。
  - `modifier_while_progressing`：研究过程中授予的临时修正，可用于体现研发投入。
- **实务建议**
  1. 复制 `_advances_template.txt` 建立新条目，确保字段齐全。
  2. 自定义国家线可仿照原版 `country_MNG.txt` 等文件，命名约定为 `country_<TAG>.txt`。
  3. 若需全局调整科技节奏，优先修改时代文件（`0_*`）或相关 `choices_*` 文件，避免直接改动大量国家专属科技。

### 示例：指定国家开局科技

在 `main_menu/setup/start` 的国家设定中加入 `starting_technology_level` 字段即可定义初始科技等级。例如，原版瑞典的配置如下：

```64:75:game/main_menu/setup/start/10_countries.txt
        include = "expl_scandinavia"
        include = "catholic_monarchy"

        country_rank = rank_kingdom

        starting_technology_level = 3
        government = {
            type = monarchy
            heir_selection = cognatic_primogeniture

            ruler = swe_magnus_eriksson
            consort = swe_blanka
```

若要在模组中为大顺开局设定科技等级，可在 `main_menu/setup/start/99_1644_10_countries.txt` 的 `CSH` 条目中插入 `starting_technology_level = 2`（或其它需要的数值）；本工程已加入示例，可直接参考：

```150:158:main_menu/setup/start/99_1644_10_countries.txt
        include = "expl_silk_road_east"

        # 示例：为大顺设定开局科技等级
        starting_technology_level = 2

        government = {
            type = monarchy
            ruler = chi_li_zicheng
```

## 军事体系

### 单位类型（Unit Types）

- **定义位置**
  - 原版：`game/in_game/common/unit_types/`
  - 模组覆盖：`in_game/common/unit_types/`（目前未覆写，可按需增补）
- **核心字段（见 `unit_types/readme.txt`）**
  - 基础属性：`age`、`build_time`、`buildable`、`levy`、`category` 等。
  - 部署限制：`location_trigger` / `location_potential`、`country_potential`。
  - 经济：`construction_demand`、`maintenance_demand`、`mercenaries_per_location`。
  - 战斗属性：`morale_damage_done/taken`、`strength_damage_done/taken`、`combat_speed`、`initiative`、`flanking_ability` 等。
  - 地形修正：`combat {}` 与 `impact {}` 分别影响输出与承伤。
  - 其它：`assault`、`bombard`、`auxiliary`、`copy_from`、`gfx_tags`。
- **模板划分**
  - `00_age_templates_land.txt` / `00_age_templates_navy.txt` 提供时代基准模板。
  - `1_*.txt` 与 `3_*.txt` 系列为特定时代或文化的独特兵种（如 `3_janissaries.txt`、`3_elephant_units.txt`）。
  - `2_unlocked_through_tech.txt` 追踪由科技解锁的单位，确保与 `advances` 衔接。
- **自定义流程**
  1. 依据需求复制最接近的模板文件，修改 `category` 与战斗数值。
  2. 如需与科技联动，在对应 `advances` 中添加 `unlock_unit = <unit_id>`。
  3. 若单位需作为徭役/征召，记得设置 `levy = yes` 并在征召表中挂接。

#### 示例：定义科技解锁的单位

下列原版条目展示了名为 `a_footmen` 的步兵单位，它通过科技树解锁；本模组在 `in_game/common/unit_types/1644_sample_units.txt` 中也提供了示例 `csh_banner_guard` 与配套科技 `csh_banner_doctrine` 可供对照：

```5:24:game/in_game/common/unit_types/2_unlocked_through_tech.txt
a_footmen = {
    category = army_infantry
    default = yes
    copy_from = a_age_1_traditions_infantry
    strength_damage_taken = -0.05

    country_potential = { 
        government_type != government_type:steppe_horde
    }

    mercenaries_per_location = {
        pop_type = burghers
        multiply = 0.1
    }

    upgrades_to = a_men_at_arms
```

如果希望新单位在某个科技完成后解锁，只需在相应 `advances` 条目中添加 `unlock_unit = my_new_unit`，保证 ID 与这里定义的单位名一致即可。

```1:18:in_game/common/unit_types/1644_sample_units.txt
csh_banner_guard = {
    category = army_infantry
    copy_from = a_age_4_reformation_infantry

    # 仅大顺可招募
    country_potential = { tag = CSH }

    buildable = yes
    maintenance_demand = early_heavy_infantry_maintenance
    construction_demand = early_heavy_infantry_construction

    morale_damage_done = 0.05
    strength_damage_done = 0.05
    morale_damage_taken = -0.05

    gfx_tags = { medium_tag }
}
```

```1:11:in_game/common/advances/1644_sample_advances.txt
csh_banner_doctrine = {
    age = age_4_reformation
    research_cost = 1.0

    # 仅大顺可见，并可在完成后解锁示例单位
    allow = { tag = CSH }
    unlock_unit = csh_banner_guard
}
```

### 征召体系（Levies）

- **定义位置**：`game/in_game/common/levies/`
- **关键字段（见 `levies/readme.txt`）**
  - `unit`：调用的单位类型。
  - `size`：每次征召的单位规模。
  - `country_allow`：国家层面限制（Scope: country）。
  - `allow`：人口层面限制（Scope: pops），可精确到阶层、财富、忠诚等。
  - `allow_as_crew`：用于海军编制的额外限制。
  - `allowed_pop_type` / `allowed_culture`：限定可提供征召的族群。
- **排序原则**：条件越苛刻的征召条目必须置于文件顶部，避免被通用条目抢占。

### 编制方式（Recruitment Method）

- **定义位置**：`game/in_game/common/recruitment_method/`
- **字段说明**
  - `strength`、`experience`：初始兵力与经验值。
  - `build_time`：训练耗时。
  - `army`：是否适用于陆军（海军则置为 `no`）。
  - `default`：该类别的默认编制方式。
- **扩展建议**：用于区分正规军、地方军、雇佣军等不同编制体系，让同一兵种在不同国家间表现差异化。

### 相关联要素

- **单位能力**：`game/in_game/common/unit_abilities/` 定义特殊战场动作，可与科技或独特单位绑定。
- **兵种分类**：`game/in_game/common/unit_categories/` 指定单位所属类别，影响编制、供应线与部分脚本判定。
- **科技联动**：`advances` 的 `unlock_levy`、`unlock_unit`、`unlock_ability` 等字段是建立科技—军事关联的核心手段。

## 模组整合建议

1. **建立自有科技线**：将原版相关 `advances` 文件复制至 `in_game/common/advances/`，按 1644 年代背景重写时代、解锁和条件。
2. **同步军事内容**：若引入新兵种或征召方式，需同时更新 `unit_types`、`levies`、`recruitment_method`，并在科技树中挂接解锁。
3. **本地化支持**：所有新增条目需在 `main_menu/localization/simp_chinese/` 对应文件中补充条目，避免游戏内出现未翻译键。
4. **测试流程**：通过游戏内控制台或日志 (`logs/error.log`) 检查科技树与单位解锁是否报错，确保触发条件与时代专精设置合理。

> 若需进一步扩展，请参考原版目录下每个 `readme.txt` 中的字段注释，保持结构一致可以显著减少错误。***

