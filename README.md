# 🪙 GDAC Crypto Table

This repo powers the **live cryptocurrency table** on the [GDAC website](https://digitalconferenceguernsey.gg/crypto-game), showing real-time gain/loss stats for tracked tokens since the start of the GDAC 2025 crypto challenge.

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

---

## 🛠 How It Works

- The core logic is in `cryptoTable.py`
- It is automatically run every hour using **GitHub Actions**
- Results are committed back to the repo by the GitHub Actions bot

---

## 📁 Repo Structure

├── cryptoList.csv         # List of tracked cryptocurrencies (id, symbol, name)
├── cryptoTable.py         # Main script for fetching, calculating, and updating
├── tableData.json         # Output file used by the website
└── .github/workflows/
    └── update_crypto_table.yml  # GitHub Actions workflow (runs hourly)

---

## ⚙️ Automation (GitHub Actions)

This repo uses a [GitHub Actions workflow](.github/workflows/update_crypto_table.yml) that runs the script every hour:

- Installs required Python packages
- Runs `cryptoTable.py`
- Commits updated `tableData.json` to `main` branch

You can also manually trigger the workflow from the **Actions** tab in GitHub.

---

## 🔐 API Info

- Data is pulled from CoinGecko’s free API.
- No API key required, but the script handles rate limits (HTTP 429) gracefully.

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

---

## 🧪 Manual Test

To test locally:

```bash
pip install pandas requests
python cryptoTable.py
```

Ensure that cryptoList.csv and tableData.json are in the same directory.

---

## 🤝 Contributing

This is a public project for GDAC 2025. Feel free to fork or suggest improvements via pull request or issue.

---

## 🐶 About the Dev

This is a project from RocketPug - [RocketPug.dev](https://www.rocketpug.dev)
