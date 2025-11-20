import pandas as pd
file_path = 'docs/ming_pops.xlsx'
try:
    df = pd.read_excel(file_path, sheet_name='Sheet1', header=None)
    # Shaanxi approx 596
    print("Shaanxi rows 596-610:")
    for i in range(596, 610):
        if i < len(df):
            print(f"Row {i}: {df.iloc[i].tolist()}")
except Exception: pass

