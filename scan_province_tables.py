import pandas as pd
import re

file_path = 'docs/ming_pops.xlsx'

try:
    df = pd.read_excel(file_path, sheet_name='Sheet1', header=None)
    
    provinces = ['北平', '京师', '南直隶', '北直隶', '山东', '山西', '河南', '陕西', '四川', '江西', '湖广', '浙江', '福建', '广东', '广西', '云南', '贵州']
    
    # Heuristic: Look for rows that contain "表" AND Province AND ("分府" or "各府")
    # AND NOT ("城市" or "市镇" or "分县" or "密度")
    
    print("Scanning for potential Province Tables...")
    
    for index, row in df.iterrows():
        val = str(row[0]).strip()
        if "表" in val:
            # Check province
            found_prov = None
            for p in provinces:
                if p in val:
                    found_prov = p
                    break
            
            if found_prov:
                if ("分府" in val or "各府" in val or "八路" in val) and not any(x in val for x in ["城市", "市镇", "分县", "密度", "育子", "死亡", "职业"]):
                    print(f"[{index}] {found_prov}: {val}")

except Exception as e:
    print(f"Error: {e}")

