import pandas as pd
import json

# Our final one-shot script. This grabs the metaImage.csv output by imageGetter.py and sticks the image URLs into tableData.json

meta_df = pd.read_csv('metaImage.csv')

meta_df['symbol'] = meta_df['symbol'].str.lower().str.strip()
meta_df['id'] = meta_df['id'].str.strip()
meta_df['thumb'] = meta_df['thumb'].str.strip()

with open('tableData.json', 'r') as f:
    graph_data = json.load(f)

for symbol_key, data in graph_data.items():
    if not isinstance(data, dict):
        print(f"Skipping '{symbol_key} - not a dict: {type(data)}")
        continue

    match = meta_df[meta_df['symbol'] == symbol_key.lower()]

    if not match.empty:
        row = match.iloc[0]
        if pd.notna(row['symbol']) and pd.notna(row['id']) and pd.notna(row['thumb']):
            graph_data[symbol_key]['symbol'] = row['symbol']
            graph_data[symbol_key]['id'] = row['name']
            graph_data[symbol_key]['thumb'] = row['thumb']
            print(f"Updated '{symbol_key}' successfully!")
        else:
            print(f"Match found for '{symbol_key}'but contains NaNs. Skipping.")
    else:
        print(f"No match found for symbol '{symbol_key}' in metaImage.csv.")

with open('tableData.json', 'w') as f:
    json.dump(graph_data, f, indent=2)

    print("✅ tableData.json fully updated successfully!")
