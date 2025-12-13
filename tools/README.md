# 人口缩放脚本使用说明

## 功能
按比例缩放EU5中指定region或area的人口数据，自动更新mod文件夹中的`06_pops.txt`文件。

## 使用方法
```bash
python scale_pops.py <region/area名称> <目标人口> [region/area]
```

## 示例
- 缩放region：`python scale_pops.py france_region 20000.0 region`
- 缩放area：`python scale_pops.py ile_de_france_area 150.0 area`

## 说明
目标人口单位为"千"。脚本会自动创建备份文件，仅修改mod文件夹中的文件，不影响原版游戏。
