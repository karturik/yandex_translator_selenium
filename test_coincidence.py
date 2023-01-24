import pandas as pd

file = ''

excel = pd.read_excel(f'excel/{file.replace(".tsv", ".xlsx")}', sheet_name='Sheet1')
excel_col = excel['INPUT:originalText']
src_df = pd.read_csv(f'docs_to_tansl/{file}', sep='\t')
src_df_col = src_df['INPUT:text']

for i in range(1, len(excel_col)+1):
    if excel_col[i-1] != src_df_col[i-1]:
        print(file, ': ', excel_col[i-1], ', ', src_df_col[i-1])

print()