# -*- coding: utf-8 -*-
import pandas as pd
import re
import os

file_path = 'docs/ming_pops.xlsx'
output_dir = 'docs/ming_pops_by_province'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def clean_name(s):
    if pd.isna(s): return None
    s = str(s).strip()
    s = re.sub(r'[\[［\(（].*?[\]］\)）]', '', s)
    s = re.sub(r'\d+', '', s)
    s = re.sub(r'[^\u4e00-\u9fa5]', '', s)
    return s

def clean_number(s):
    if pd.isna(s): return None
    s = str(s).strip()
    # Remove spaces
    s = s.replace(' ', '')
    
    # Check for decimal
    if '.' in s:
        try:
            return float(s)
        except:
            pass
            
    match = re.match(r'([\d,]+)', s)
    if match:
        num_str = match.group(1).replace(',', '')
        if num_str:
            return float(num_str) # Return float to handle decimals
    return None

def parse_table(df, start_row, end_row, province, year, col_map, split_name=False, pop_multiplier=1):
    data = []
    print(f"Parsing {province} ({year}) from row {start_row} to {end_row}...")
    
    for i in range(start_row, end_row):
        if i >= len(df): break
        row = df.iloc[i]
        
        raw_name_col = col_map.get('name', 0)
        raw_h_col = col_map.get('house', 1)
        raw_p_col = col_map.get('pop', 2)
        
        name_val = row[raw_name_col] if len(row) > raw_name_col else None
        h_val = row[raw_h_col] if len(row) > raw_h_col else None
        p_val = row[raw_p_col] if len(row) > raw_p_col else None
        
        if split_name:
            part1 = row[0]
            part2 = row[1]
            if pd.isna(part1) or pd.isna(part2): continue
            s1 = str(part1).strip()
            s2 = str(part2).strip()
            if re.match(r'^\d', s2): continue
            name_str = s1 + s2
            h_val = row[col_map['house']]
            p_val = row[col_map['pop']]
        else:
            name_str = str(name_val) if pd.notna(name_val) else ""
            
        cleaned_name = clean_name(name_str)
        
        if not cleaned_name or len(cleaned_name) < 2: continue
        if '合计' in cleaned_name: continue
        
        h_num = clean_number(h_val)
        p_num = clean_number(p_val)
        
        if h_num is not None:
            h_num = int(h_num)
        else:
            h_num = 0
            
        if p_num is not None:
            p_num = p_num * pop_multiplier
            p_num = int(p_num)
        else:
            p_num = 0
            
        # Validation: Keep if either H or P is significant
        # For Shaanxi, H might be 0 but P is large
        if h_num > 1000 or p_num > 10000:
            if p_num < h_num and p_num < 1000: p_num = 0 # Page number check (only if P is small)
            
            data.append({
                'Province': province,
                'Prefecture': cleaned_name,
                'Households': h_num,
                'Population': p_num,
                'Year': year
            })
            
    if not data:
        return pd.DataFrame(columns=['Province', 'Prefecture', 'Households', 'Population', 'Year'])
    return pd.DataFrame(data)

def find_table_start(df, title_keyword, start_search_from=50):
    for i in range(start_search_from, len(df)):
        row_val = str(df.iloc[i, 0])
        if title_keyword in row_val:
            return i
    return -1

try:
    df = pd.read_excel(file_path, sheet_name='Sheet1', header=None)
    all_dfs = []
    
    # 1. Shanxi (Hongwu 24)
    sx_start = find_table_start(df, "表2-4 洪武二十四年山西分府户口")
    if sx_start != -1:
        all_dfs.append(parse_table(df, sx_start+2, sx_start+15, '山西', '1391', {'name': 0, 'house': 1, 'pop': 2}))
        
    # 2. Henan (Hongwu 24)
    hn_start = find_table_start(df, "表2-12 洪武二十四年河南分府户口")
    if hn_start != -1:
        all_dfs.append(parse_table(df, hn_start+2, hn_start+15, '河南', '1391', {'name': 0, 'house': 2, 'pop': 3}, split_name=True))

    # 3. Jiangxi (Hongwu 24)
    jx_start = find_table_start(df, "表2-13 洪武二十四年江西分府户口")
    if jx_start != -1:
        all_dfs.append(parse_table(df, jx_start+2, jx_start+20, '江西', '1391', {'name': 0, 'house': 1, 'pop': 2}))

    # 4. Guangdong (Hongwu 24)
    gd_start = find_table_start(df, "表4-15 洪武二十四年广东分府户口")
    if gd_start != -1:
        all_dfs.append(parse_table(df, gd_start+2, gd_start+15, '广东', '1391', {'name': 0, 'house': 1, 'pop': 2}))
        
    # 5. Nanzhili (Hongwu 26)
    nz_start = find_table_start(df, "表2-6 洪武二十六年京师地区分府")
    if nz_start != -1:
        all_dfs.append(parse_table(df, nz_start+2, nz_start+20, '南直隶', '1393', {'name': 0, 'house': 1, 'pop': 2}))

    # 6. Shandong (Jiajing 5)
    sd_start = find_table_start(df, "嘉靖五年山东分府户口")
    if sd_start != -1:
        all_dfs.append(parse_table(df, sd_start+2, sd_start+15, '山东', '1526', {'name': 0, 'house': 1, 'pop': 2}))

    # 7. Fujian (Yuan)
    fj_start = find_table_start(df, "表2-1 元代福建地区八路的户口", start_search_from=60) 
    if fj_start != -1:
        all_dfs.append(parse_table(df, fj_start+1, fj_start+15, '福建', 'Yuan', {'name': 0, 'house': 1, 'pop': 2}))
        
    # 8. Shaanxi (Hongwu 24 Estimate)
    # Table 4-5. Col 0 Name, Col 7 Pop (Actual Estimate in Wan). No Households.
    sn_start = find_table_start(df, "表4-5 洪武二十四年陕西分府人口估测")
    if sn_start != -1:
        all_dfs.append(parse_table(df, sn_start+2, sn_start+15, '陕西', '1391', {'name': 0, 'house': 99, 'pop': 7}, pop_multiplier=10000))

    # --- OUTPUT ---
    if all_dfs:
        final_df = pd.concat(all_dfs, ignore_index=True)
        
        if not final_df.empty and 'Province' in final_df.columns:
            for prov in final_df['Province'].unique():
                prov_df = final_df[final_df['Province'] == prov]
                p_file = os.path.join(output_dir, f"{prov}_pop.csv")
                prov_df.to_csv(p_file, index=False, encoding='utf-8-sig')
                print(f"Saved {prov} to {p_file} ({len(prov_df)} rows)")
                
            final_df.to_csv(os.path.join(output_dir, "ming_all_provinces_combined.csv"), index=False, encoding='utf-8-sig')
        else:
            print("Final DataFrame is empty or missing columns.")
    else:
        print("No tables extracted.")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
