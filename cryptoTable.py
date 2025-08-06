from datetime import datetime
import base64
import json
import os
import pandas as pd
import requests
import time

# Pseudocode for this script:
#   Parse cryptoList.csv
#   Contact CoinGecko API to obtain today's coin price
#   Work out % gain/loss between 14 July 2025 (competition start date) and today
#   Update tableData.json todays_date, todays_price, percent_change
#   Upload tableData.json to ShaneM9's GitHub repo (note that the token expires 11 Sept 2025)
#   EXTERNAL TO THIS SCRIPT: tableData.json is used to display current crypto gain/loss data in a code block on the GDAC website

# --- CoinGecko CONFIG ---
START_DATE = datetime(2025, 7, 14).date()
TODAY_DATE = datetime.today().date()
API_HEADER = {"user-agent": "Mozilla/5.0 (CryptoTableDataFetcher/1.0)"}
API_URL = "https://api.coingecko.com/api/v3/simple/price"
CURRENCY = "usd"
LOCAL_FILE_PATH = "tableData.json"

# Call API for daily prices
def fetch_todays_prices(coin_ids):
    url = API_URL
    params = {
        "ids": ",".join(coin_ids),
        "vs_currencies": CURRENCY
    }

    print(f"→ Fetching today's prices for {len(coin_ids)} coins...")

    response = requests.get(url, headers=API_HEADER, params=params)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        print("⚠️ Rate limited. Waiting 12s to retry...")
        time.sleep(12)
        return fetch_todays_prices(coin_ids)  # Retry
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
        return None

def main():
    # Load cryptoList.csv, normalise symbols (covering-off manual updates where a capital letter might accidentally be used)
    try:
        crypto_df = pd.read_csv("cryptoList.csv")
    except Exception as e:
        print(f"❌ Failed to read cryptoList.csv: {e}")
        return
    crypto_df['symbol'] = crypto_df['symbol'].str.lower()
    symbol_to_id = dict(zip(crypto_df['symbol'], crypto_df['id']))

    if os.path.exists(LOCAL_FILE_PATH):
        with open(LOCAL_FILE_PATH, "r") as f:
            table_data = json.load(f)
    else:
        print(f"⚠️ {LOCAL_FILE_PATH} not found.")
        return

    # Bunch all coin ids from cryptoList.csv
    all_coin_ids = list(symbol_to_id.values())
    price_data = fetch_todays_prices(all_coin_ids)
    if price_data is None:
        print("❌ Failed to fetch price data.")
        return

    for symbol, coin_id in symbol_to_id.items():
        print(f"Processing {symbol} ({coin_id})")
        todays_price = price_data.get(coin_id, {}).get(CURRENCY)
        if todays_price is None:
            todays_price = 0.00
            print(f"❌ Missing price for {symbol} ({coin_id}) in API response.")
            continue

        if symbol not in table_data or 'start_price' not in table_data[symbol]:
            print(f"⚠️ Missing \"start_price\" in 'tableData.json' for {symbol}, skipping.")
            continue

        start_price = table_data[symbol]["start_price"]

        try:
            percent_change = ((todays_price - start_price) / start_price) * 100
        except ZeroDivisionError:
            percent_change = 0.0
        
        table_data[symbol].update({
            "todays_date": TODAY_DATE.isoformat(),
            "todays_price": todays_price,
            "percent_change":round(percent_change, 2)
        })

    # Write to tableData.json
    with open(LOCAL_FILE_PATH, "w") as f:
        json.dump(table_data, f, indent=2)
    print(f"✅ Updated {LOCAL_FILE_PATH}")

    print("✅ Script completed - GitHub Actions will handle the commit.")

if __name__ == "__main__":
    main()