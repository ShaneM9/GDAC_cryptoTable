# 🪙 GDAC Crypto Table

![Build Status](https://github.com/ShaneM9/GDAC_cryptoTable/actions/workflows/update_crypto_table.yml/badge.svg)
![Last Commit](https://img.shields.io/github/last-commit/ShaneM9/GDAC_cryptoTable)
[![GDAC Website](https://img.shields.io/badge/Visit%20GDAC%20Site-Click%20Here-blue)](https://digitalconferenceguernsey.gg/crypto-game)

This repo powers the **live cryptocurrency table** on the [Guernsey Digital Assets Conference 2025 website](https://digitalconferenceguernsey.gg/crypto-game), showing real-time gain/loss stats for tracked tokens since the start of the GDAC 2025 "Crypto Game".

## 📚 Table of Contents

- [What It Does](#-what-it-does)
- [How It Works](#-how-it-works)
- [Repo Structure](#-repo-structure)
- [Automation (GitHub Actions)](#-automation-github-actions)
- [API Info](#-api-info)
- [Example Output](#-example-output)
- [Manual Test](#-manual-test)
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

## 🧪 Manual Test

To test locally:

```bash
pip install pandas requests
python cryptoTable.py
```

Ensure that `cryptoList.csv` and `tableData.json` are in the same directory.

---

## 🤝 Contributing

This is a public project for GDAC 2025. Feel free to fork or suggest improvements via pull request or issue.

---

## 🐶 About the Dev

This is a project from RocketPug - [RocketPug.dev](https://www.rocketpug.dev)
