# 1644 科技拆分文件说明

本目录包含按根科技（level=0）拆分后的科技文件。每个文件包含一个根科技及其所有子科技。

## 文件结构

### Age 1 (时代1)
- `age_1_written_alphabet.txt` - 文字系统
- `age_1_agriculture_advance.txt` - 农业
- `age_1_mining_advance.txt` - 采矿
- `age_1_ship_building_advance.txt` - 造船
- `age_1_organized_religion.txt` - 有组织宗教
- `age_1_meritocracy_advance.txt` - 任人唯贤

### Age 2 (时代2 - 文艺复兴)
- `age_2_renaissance_advance.txt` - 文艺复兴
- `age_2_banking_advance.txt` - 银行业
- `age_2_professional_armies_advance.txt` - 职业军队
- `age_2_renaissance_development.txt` - 文艺复兴发展

### Age 3 (时代3 - 大发现)
- `age_3_new_world_advance.txt` - 新世界
- `age_3_printing_press_advance.txt` - 印刷术
- `age_3_pike_and_shot_advance.txt` - 长矛与火枪
- `age_3_trade_through_owned_disc_advance.txt` - 商旅之路（无依赖，level=0 根科技，包含 dry_dock_advance -> unlock_carrack_advance -> foreign_cultural_law_advance）

### Age 4 (时代4 - 宗教改革)
- `age_4_confessionalism_advance.txt` - 教派主义
- `age_4_global_trade_advance.txt` - 全球贸易（包含 customs_house_advance，在 development_of_maritime_law 下）
- `age_4_artillery_institution_advance.txt` - 炮兵机构（包含 shipyard_advance 在 cannon_workshop_advance 下，unlock_pinnace_advance 在 maurician_infantry 下）
- `age_4_unlock_war_galleon.txt` - 解锁战列舰（无依赖）

## 使用说明

这些文件是从 `zzz_1644_starting_tech.txt` 中拆分出来的，原文件保持不变。
每个文件包含一个根科技（level=0）及其所有直接和间接子科技。

## 注意事项

- 标记为"无依赖"的科技是独立的根科技，不依赖其他科技
- 每个文件中的科技树结构保持原样
- 原文件 `zzz_1644_starting_tech.txt` 保持不变，这些是额外的拆分文件
