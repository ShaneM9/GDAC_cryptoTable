# 🪙 GDAC Crypto Table

![Build Status](https://github.com/ShaneM9/GDAC_cryptoTable/actions/workflows/update_crypto_table.yml/badge.svg)
![Last Commit](https://img.shields.io/github/last-commit/ShaneM9/GDAC_cryptoTable)
[![GDAC Website](https://img.shields.io/badge/Visit%20GDAC%20Site-Click%20Here-blue)](https://digitalconferenceguernsey.gg/crypto-game)

This repo powers the **live cryptocurrency table** on the [Guernsey Digital Assets Conference 2025 website](https://digitalconferenceguernsey.gg/crypto-game), showing real-time gain/loss stats for tracked tokens since the start of the GDAC 2025 "Crypto Game". Gain/loss figures are updated hourly (or near-as, whenever GitHub decides to run the Action).

## 📚 Table of Contents

- [What It Does](#-what-it-does)
- [How It Works](#-how-it-works)
- [Repo Structure](#-repo-structure)
- [Automation (GitHub Actions)](#-automation-github-actions)
- [API Info](#-api-info)
- [Example Output](#-example-output)
- [Initial Setup](#-initial-setup)
- [Manual Test](#-manual-test)
- [Crypto Game](#-crypto-game)
- [Contributing](#-contributing)
- [About the Dev](#-about-the-dev)

---

## 📌 What It Does

- Reads a list of tracked cryptocurrencies from `cryptoList.csv`
- Fetches up-to-date USD prices from the [CoinGecko API](https://www.coingecko.com/en/api)
- Calculates percent change since **14 July 2025**
- Updates `tableData.json`, which is read by the GDAC website to display price movement

Note: The rationale behind using a separate `cryptoList.csv` is that the list can be updated by staff locally more easily than the .json file. Transposing the .csv to .json can be done very simply with a single-use script whenever needed.

---

## 🛠 How It Works

- The core logic is in `cryptoTable.py`:
    - `cryptoList.csv` is opened and the symbols are recorded
    - A request is built consisting of all symbols + a currency code
    - `GET` request to **CoinGecko** API for today's prices for each of symbol
    - Percentage change between 14 July 2025 and today is calculated
    - Today's date, today's price and percentage change are all updated in `tableData.json`
- The script is automatically run every hour, on the hour, using **GitHub Actions**
- Results are committed back to the repo by the **GitHub Actions** bot

Note: The date of 14 July 2025 is the agreed start date for the competition, hence hard-coded as a constant.

---

## 📁 Repo Structure

```.
├── cryptoList.csv         # List of tracked cryptocurrencies (id, symbol, name)
├── cryptoTable.py         # Main script for fetching, calculating, and updating
├── tableData.json         # Output file used by the website
└── .github/workflows/
    └── update_crypto_table.yml  # GitHub Actions workflow (runs hourly)
└── bonus_content
    └── cryptoTable_Local.py
    └── metaImage.py
    └── metaWriter.py
    └── startDataGetter.py
    └── table.html
└── crypto_game
    └── cryptoGame.py
```

---

## ⚙️ Automation (GitHub Actions)

This repo uses a [GitHub Actions workflow](.github/workflows/update_crypto_table.yml) that runs the script every hour, on the hour:

- Installs required Python packages
- Runs `cryptoTable.py`
- Commits updated `tableData.json` to `main` branch

It can also be triggered manually via GitHub's **Actions** tab.

---

## 🔐 API Info

- Data is pulled from CoinGecko’s free API.
- No API key required, but consideration should be given to rate limits if additional calls are to be made.
- Whilst this script only makes use of `GET` for today's prices, it is worth noting that one-off calls were made to CoinGecko ahead of implementing this repository in order to build the .json and .csv files that this script runs from/outputs to. These included requests for initial coin prices as at 14 July 2025, as well as ticker data such as id, symbol, name, and image URLs for thumbnails to be used on the GDAC website.

---

## 📊 Example Output

Each entry in `tableData.json` looks like:

```json
"btc": {
  "symbol": "btc",
  "id": "Bitcoin",
  "thumb": "https://coin-images.coingecko.com/coins/images/1/small/bitcoin.png",
  "start_date": "2025-07-14",
  "start_price": 119117.55,
  "todays_date": "2025-08-06",
  "todays_price": 113950,
  "percent_change": -4.34
}
```

Values are maintained for `start_date`, `start_price`, `todays_date` and `todays_price` for manual validation purposes and transparency as part of the competition and reporting.

---

## 🤖 Initial Setup

**!IMPORTANT**

Note that cryptoList.csv was decided ahead of this project being comissioned, and thus the `cryptoList.csv` had already been decided upon and manually set up. I'm sure there's a way you could automate this using CoinGecko and market cap data as at a date - but I didn't need to do it, so there is no script for that here.

I have, however, included the scripts I used to populate `tableData.json` with various metadata. The setup was split into two scripts purely because they utilise two separate API URLs, and we didn't want to re-run both in the event that we had to re-run one of them. Note there is also not a script to generate the initial template for `tableData.json` - we just hit CTRL+V a bunch of times and manually added all 100 names and symbols because I wasn't thinking straight (actually that's a lie - I used the find+replace function in VS Code within the .csv, and put some random tags around each bit of data I wanted to keep - eg. "---Bitcoin+++", "---Ethereum+++", "---Dogecoin+++" - then find+replace could search for "---" and replace it with `"id": "` and search for "+++" and replace with `","thumb": "","start_date": "","start_price": 0.0,"todays_date": "","todays_price": 0.0,"percent_change": 0.0},"`... then just save-out as .json and prettify it. Talk about jank, but it works - jsut remember to tidy up the start and end of the file by removing any extra commas or adding any extra curly braces.

Anyway, in this repo you will see the following additional scripts in the `/bonus_content/` folder:

`startDataGetter.py`
- Run this first. Obtains start-date data and populates `tableData.json` with the price in USD as at competition start-date
- You can adjust const `TARGET_DATE` to change the start date, but note you will have to manually adjust this date for entry "start_date" in `tableData.json` for each crypto, since this functionality was not in scope for me.

`imageGetter.py`
- Run this next. It will grab the image URL for use in the table that we use on GDAC's website.
- Note that we experienced one crypto that had de-listed between project start and implementing images into the web app - since it was only one, and since we only planned on running this script once, we managed to manually add the URL from historic data.
- Note also that this outputs to `metaImage.csv` rather than writing to `tableData.json` immediately. This is because initially we had grabbed the URLs for use in a flat HTML `<table>` within a script, and a .csv was quicker for a human to parse... but when we moved to JavaScript and automating table generation it turned out .json was preferable... hence we built `tableData.json` and populated that instead. Honestly should have used JS from the beginning. Rookie error

`metaWriter.py`
- Originally intended as something grander, this script ended-up being a means of adding the image URLs to `tableData.json` and that was it.
- Run this after getting the image URLs from `metaImage.py` - or if you're feeling really smart, forego this entirely and just adapt the function in `metaImage.py` to write to `tableData.json` instead. These are all single-use throwaway scripts for me, so I'm not too fussed about optimising them... consider them 'bonus content' that I'm giving you for ease of setup - you might have your own way of doing this.

`table.html`
- This contains the HTML code snippet for use in the web application/code block on the website.
- Put very simply it grabs the data from within `tableData.json` and generates a CSS-styled table in the format:
    - `"thumb"`
    - `"id" ("symbol")`
    - `"percent_change"`
- Note that `"percent_change"` is coloured according to gain (green), loss (red) or black (no change)
- The block is mobile-friendly, and will scale down from 5 columns (desktop) to 3 columns (mobile)

---

## 🧪 Manual Test

To test locally please use `cryptoTable_Local.py` (found in the `/bonus_content/` folder of this repo) and link this to your own GitHub repo as stated within the comments of that file. Then run:

```bash
pip install pandas requests
python cryptoTable.py
```

Ensure that `cryptoList.csv` and `tableData.json` are in the same directory, or that you adjust the locations within the script.

---

## 🎮 Crypto Game

In the folder `/crypto_game/` you'll find 'entrantDataNormalizer.py' and 'cryptoGame.py' - another Brucie Bonus. This repo isn't specifically about the crypto game itself, but rather I have included this for future use at other events if needed. The comments in the file should be relatively self-explanatory, but to summarise here:

### `entrantDataNormalizer.py`
- Opens the files we will use to create our final list of entrants - `GDAC Crypto game entrants.csv` and `cryptoList.csv`
- Step 1: We begin by replacing user's choices with the correct symbol. This is because the website sign-up used a free-text field for choices, thus we have to account for extra random words, letters, or for example "Bitcoin" instead of the requested "BTC" or "btc". We cannot handle every potential scenario (it is a free-text field, of course) but the below goes some way to hunt-out the choice in any given string of potential text and replace with the correct symbol.
    - Step 1.1: Begins by comparing `GDAC Crypto game entrants.csv` column 'Coin' to `cryptoList.csv` column 'id' - if the value in 'id' is located within the string that exists in 'Coin' then replace the entire string in 'Coin' with the value in `cryptoList.csv` column 'symbol'
    - Step 1.2: Repeat the same thing, but using `cryptoList.csv` column 'name' and, where a match is found, replace values in 'Coin' with those in 'symbol'.
    - Step 1.3: We then filter out entrants with 'Party' or 'Virtual' ticket types, this at the request of the organizer. Only in-person attendees are eligible for prizes.
- Step 2: We convert the 'Coin' column of `GDAC Crypto game entrants.csv` 'tolower' to ensure a perfect fit with CoinGecko API data.
- Step 3: 'Date' column in `GDAC Crypto game entrants.csv` is converted to a standard 'dd-MMM-yyyy' format to play nicely with `cryptoGame.py`. There are two formats present in the dataset - 'dd-MM-yy' and 'dd-MM-yyyy' so the scrript handles both.
- Step 4: Matching against `cryptoList.csv`, we delete any rows where user selection does not match a value in `cryptoList.csv` (think "spoiled ballots"!).
- Step 5: All unneccessary columns are deleted, leaving only 'Name', 'Date', 'Time' and 'Coin'.
- Step 6: Columns are renamed to fit with those expected in `cryptoGame.py`
- Step 7: We limit the entrants to the first 5 individuals to have chosen the coin in question - only a max of 5 can choose any single coin, first-come first-served.
- Step 8: The final output is saved as `attendeeList.csv` in the same location as `cryptoGame.py`
- Step 9: Closure of component .csv files is handled by context managers - no need for extra script here.
- We can now run `cryptoGame.py` and it will pick up our formatted `attendeeList.csv` and work with it as expected!

### `cryptoGame.py`
- Extracts unique "cryptoSymbol" data from `attendeeList.csv`
- Matches these against the values in `cryptoList.csv` to check they exist in the CoinGecko API
- Fetches historical data from CoinGecko for each crypto from 14 July 2025 to today and outputs `coinGeckoData.csv`
- Works out a winner using "signUpDate" and "cryptoSymbol" values from `attendeeList.csv`:
    - Find price data on "signUpDate" for "cryptoSymbol"
    - Find price data for today for "cryptoSymbol"
    - Work out percentage gain/loss for each attendee
    - Outputs results to `cryptoGameResults.csv` in order from highest gain to biggest loss
- As well as outputting a full results .csv, the program also outputs a top-10 to the console CLI.
- In the event of a tiebreak there is further logic to:
    - Get the crypto that the tiebreaker attendees chose, and the date they chose it
    - Contact the CoinGecko API and retireve hourly (or near-as-dammit) values for that crypto on that day
    - Output to `tiebreakerData.csv` for manual review
    - Given more time I would like to have added automation for the tiebreaker also, given we have a 'Time' column in the original entrants dataset, but for now users can manually review the hourly data and see which attendee chose the particular coin when it was at the lower value (eg. John chose PugCoin at $420.69 and Jane chose it at $420.42, and the coin is now worth $694.20, Jane wins because hers gained a few extra cents, and thus a slightly higher percentage). I may update this if I ever update the script, but for now you get the manual version... Likewise incorporating `entrantData Normalizer.py` would have been nice... time is always against us!

A quick note on the structure of `attendeeList.csv` since this is not included in this repo for Data Protection reasons - the structure is assumed to be as follows, (we expect the date-time structure to change):

```
attendeeName,signUpDate,signUpTime,cryptoSymbol
John Smith,14-Jul-2025,10:00,btc
```

Note also that `cryptoList.csv` is the same that is used by `cryptoTable.py`.

---

## 🤝 Contributing

This is a public project for GDAC 2025. Feel free to fork or suggest improvements via pull request or issue.

---

## 🐶 About the Dev

This is a project from RocketPug - [RocketPug.dev](https://www.rocketpug.dev)
