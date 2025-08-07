from datetime import datetime, timedelta, timezone
from dateutil import parser
import pandas as pd
import requests
import time

# Initial config step for constants
START_DATE = datetime(2025, 7, 14).date()
END_DATE = datetime.today().date()
API_HEADER = {"User-Agent": "Mozilla/5.0 (CryptoGameDataFetcher/1.1)"}  # Apparently including a header helps prioritise your API call... probably witchcraft or some old-wives-tale, but who really knows...
API_URL = "https://api.coingecko.com/api/v3/coins/{}/market_chart"
TIEBREAKER_URL = "https://api.coingecko.com/api/v3/coins/{}/market_chart/range"
CURRENCY = "usd"


# This is the function that calls the coinGecko API and obtains values for all relevant symbols as decided per the get_data() function later
# We call this function in get_data(), hence defining it here ahead of time.
def api_call(symbol, coin_id):
    params = {
        "vs_currency": CURRENCY,
        "days": (END_DATE - START_DATE).days + 1,
        "interval": "daily"
    }

    for attempt in range(3):
        response = requests.get(API_URL.format(coin_id), headers=API_HEADER, params=params)
        if response.status_code == 200:
            data = response.json()
            prices = {datetime.fromtimestamp(p[0] / 1000, tz=timezone.utc).date(): p[1] for p in data ["prices"]}
            return prices
        elif response.status_code == 429:
            print(f"Rate limited for {coin_id}. Trying again in 1 minute", end="", flush=True)
            for _ in range(65):
                time.sleep(1)
                print(".", end="", flush=True)
            print(f"\nRequesting: {symbol} ({coin_id})")
            print()
        else:
            print(f"Error fetching {coin_id}: {response.status_code}")
            return None
    return None

# Predefining our tiebreaker logic. This will call the CoinGecko API in the event of a tie at the top, and will
# download the data for the coin in question for the signUpDate. We will use the time of sign-up to see which attendee
# picked the coin whilst it was at the lower price (or near as damnit)
def tiebreaker(top_results, attendee_df, symbol_to_id):
    print("\nTiebreaker check in progress...")

    first_symbol = top_results.iloc[0]['cryptoSymbol']
    coin_id = symbol_to_id.get(first_symbol)

    signup_date_str = attendee_df.loc[
        attendee_df['cryptoSymbol'] == first_symbol, 'signUpDate'
    ].values[0]
    sign_up_date = parser.parse(signup_date_str).date()

    start_ts = int(datetime.combine(sign_up_date, datetime.min.time()).replace(tzinfo=timezone.utc).timestamp())
    end_ts = int(datetime.combine(sign_up_date + timedelta(days=1), datetime.min.time()).replace(tzinfo=timezone.utc).timestamp())

    url = TIEBREAKER_URL.format(coin_id)
    params = {
        "vs_currency": CURRENCY,
        "from": start_ts,
        "to": end_ts
    }

    print(f"Fetching intraday data for symbol {first_symbol} on {sign_up_date}...")
    response = requests.get(url, headers=API_HEADER, params=params)
    tie_data = []

    if response.status_code == 200:
        data = response.json()
        prices = data.get("prices", [])
        for price_entry in prices:
            timestamp = datetime.fromtimestamp(price_entry[0] / 1000, tz=timezone.utc)
            price = price_entry[1]
            tie_data.append({
                "cryptoSymbol": first_symbol,
                "signUpDate": sign_up_date,
                "timestampUTC": timestamp,
                "price": price
            })
    else:
        print(f"Failed to fetch intraday data for {first_symbol} on {sign_up_date}. Error code: {response.status_code}")
    
    if tie_data:
        pd.DataFrame(tie_data).to_csv("tiebreakerData.csv", index=False)
        print("Tiebreaker data written to tiebreakerData.csv!")
    else:
        print("No tiebreaker data was available to write to file. Please check prices manually via CoinGecko.com")

# Our main function to gather data from the CSVs we have, confirm which specific symbols we need data for
# (instead of irresponsibly calling for all 100 - if attendees have only chosen 20 between them, we only make 20 calls)
# and subsequently trigger the api_call() function for each, generating coinGeckoList.csv for later use in function decide_winner()
def get_data():

    crypto_df = pd.read_csv("cryptoList.csv")       # Load our list of Top 100 cryptocurrencies by market cap at 14 July 2025
    attendee_df = pd.read_csv("attendeeList.csv")   # Load list of GDAC 2025 attendees, their date-of-purchase and symbol choice

    crypto_df['symbol'] = crypto_df['symbol'].str.lower()                   # Normalising to lower-case (safety net in case data is
    attendee_df['cryptoSymbol'] = attendee_df['cryptoSymbol'].str.lower()   # provided with erroneous formatting)

    # Phase 1: Work out unique symbol values in attendeeList.csv and download data for each, save-out a CSV with the data in it
    print("Extracting unique values from attendee list...")
    unique_symbols = attendee_df['cryptoSymbol'].unique()

    print("Matching unique symbols to CoinGecko API IDs...")
    symbol_to_id = crypto_df.set_index('symbol')['id'].to_dict()
    symbol_to_id = {sym: symbol_to_id.get(sym) for sym in unique_symbols if symbol_to_id.get(sym)}

    if len(symbol_to_id) < len(unique_symbols): # Catches any symbols that do not appear in BOTH cryptoList.csv and attendeeList.csv
        missing = set(unique_symbols) - set(symbol_to_id.keys())
        print(f"WARNING: No CoinGecko ID could be located for {', '.join(missing)}")
    
    date_range = [(START_DATE + timedelta(days=i)) for i in range((END_DATE - START_DATE).days + 1)]
    date_headers = [d.strftime("%d-%b-%Y") for d in date_range]

    all_prices = []

    print("Fetching historical prices from CoinGecko...")
    for symbol, coin_id in symbol_to_id.items():
        print(f"Requesting: {symbol} ({coin_id})", end="", flush=True)
        prices = api_call(symbol, coin_id)
        for _ in range(12): # Be kind to this free API... leave a little gap between calls. There is a throttle at more than 5-6 requests per minute. 10s + 2s buffer should keep us going without hitting the last-resort 1min+ hold we've built in api_call()
            time.sleep(1)
            print(".", end="", flush=True)
        print()
        if not prices:
            continue
        row = [symbol]
        for d in date_range:
            row.append(prices.get(d, None))
        all_prices.append(row)

    price_df = pd.DataFrame(all_prices, columns=["symbol"] + date_headers)
    price_df.to_csv("coinGeckoData.csv")
    print("Saved data to CoinGeckoData.csv")

def decide_winner():
    print("\nLoading CoinGecko price data for analysis...")
    price_df = pd.read_csv("coinGeckoData.csv")
    attendee_df = pd.read_csv("attendeeList.csv")
    crypto_df = pd.read_csv("cryptoList.csv")

    price_df['symbol'] = price_df['symbol'].str.lower() # Normalising again
    price_df.set_index('symbol', inplace=True)
    attendee_df['cryptoSymbol'] = attendee_df['cryptoSymbol'].str.lower()
    crypto_df['symbol'] = crypto_df['symbol'].str.lower()

    symbol_to_id = crypto_df.set_index('symbol')['id'].to_dict()

    results = []

    # Phase 2: Take signUpDate from attendee list and calculate gains/losses to date, decide a winner and print to console
    # along with a full csv, top-to-bottom, of all attendee results for review if need be
    print("Calculating gains/losses for each attendee...")
    for _, row in attendee_df.iterrows():
        attendee = row['attendeeName']
        symbol = row['cryptoSymbol']
        sign_up_date = parser.parse(row['signUpDate']).date()

        try:
            start_price = price_df.loc[symbol, sign_up_date.strftime("%d-%b-%Y")]
            end_price = price_df.loc[symbol, END_DATE.strftime("%d-%b-%Y")]
        except KeyError:
            print(f"Missing price data for {attendee} - {symbol} on required dates. Skipping...")
            continue

        if pd.isna(start_price) or pd.isna(end_price):
            print(f"Incomplete price data for {attendee} - {symbol}. Skipping...")
            continue

        percent_change = ((end_price - start_price) / start_price) * 100
        formatted = f"{'+' if percent_change >= 0 else '-'}{abs(percent_change):.2f}%"

        results.append({
            "attendeeName": attendee,
            "cryptoSymbol": symbol,
            "gainLoss": percent_change,
            "gainLossFormatted": formatted
        })

    # Outputting final results to CSV
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(by="gainLoss", ascending=False)
    results_df.to_csv("cryptoGameResults.csv", index=False)

    # Outputting Top 10 to Console
    print("\n:----------Top 10 Results:----------:")
    print(results_df[["attendeeName", "cryptoSymbol", "gainLossFormatted"]].head(10).to_string(index=False))

    # NEW tiebreaker logic - requires manual review at present, may add automation here depending on datetime data from SeatLab
    top_value = results_df.iloc[0]['gainLoss']
    top_results = results_df[results_df['gainLoss'] == top_value]
    if len(top_results) > 1:
        print("\nTIE! Initializing tiebreaker...")
        tiebreaker(top_results, attendee_df, symbol_to_id)
    else:
        print("No tiebreaker needed!")

if __name__ == "__main__":
    get_data()
    decide_winner()
