import csv
import json
import requests
import time

# Intended for one-time-use, throwaway script. Use at your peril!

CSV_FILE = 'cryptoList.csv'
JSON_FILE = 'tableData.json'
TARGET_DATE = '14-07-2025'  # Adjust if start date of competition is different, obviously
COINGECKO_API = 'https://api.coingecko.com/api/v3/coins/{id}/history?date={date}'

with open(JSON_FILE, 'r') as f:
    table_data = json.load(f)
    with open(CSV_FILE, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            symbol = row['symbol']
            coingeck_id = row['id']

            if symbol not in table_data:
                continue

            url = COINGECKO_API.format(id=coingeck_id, date=TARGET_DATE)
            try:
                response = requests.get(url)
                data = response.json()

                market_data = data.get('market_data', {})
                current_price = market_data.get('current_price', {})
                usd_price = current_price.get('usd')

                if usd_price is not None:
                    print(f"Data obtained for {symbol}")
                    table_data[symbol]['start_price'] = usd_price
                    time.sleep(12) #respect the API calls @ 5/6 per minute
                else:
                    print(f"Warning: USD price not found for {symbol} on {TARGET_DATE}")
            
            except Exception as e:
                print(f"Error: Failed to fetch data for {symbol}: {e}")

with open(JSON_FILE, 'w') as f:
    json.dump(table_data, f, indent=2)

print("✅ start_price values in tableData.json updated successfully!")
