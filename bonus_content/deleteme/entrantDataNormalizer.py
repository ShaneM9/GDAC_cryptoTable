import pandas as pd

def main():

    # ------------------------------------------------------------------
    # Step 0: Open files in requested modes and load into DataFrames
    # ------------------------------------------------------------------
    print("Importing entrants data")
    with open("GDAC Crypto game entrants.csv", "r+", encoding="utf-8") as entrants_file:
        entrants_df = pd.read_csv(entrants_file)

        print("Importing cryptoList")
        with open("cryptoList.csv", "r", encoding="utf-8") as crypto_file:
            crypto_df = pd.read_csv(crypto_file)

            # --- NEW: normalize headers (fixes 'Date ' / 'Time ' etc.) ---
            entrants_df.columns = entrants_df.columns.astype(str).str.strip()
            crypto_df.columns = crypto_df.columns.astype(str).str.strip()

            # Ensure expected columns exist
            required_entrants_cols = ["Name", "Date", "Time", "Coin"]
            for col in required_entrants_cols:
                if col not in entrants_df.columns:
                    entrants_df[col] = pd.NA

            for col in ["id", "symbol", "name"]:
                if col not in crypto_df.columns:
                    raise ValueError("cryptoList.csv must contain 'id', 'symbol', and 'name' columns")

            # --- NEW: trim cell whitespace in key columns ---
            for c in ["Name", "Date", "Time", "Coin"]:
                entrants_df[c] = entrants_df[c].astype(str).str.strip()

            crypto_df["id"] = crypto_df["id"].astype(str).str.strip()
            crypto_df["name"] = crypto_df["name"].astype(str).str.strip()
            crypto_df["symbol"] = crypto_df["symbol"].astype(str).str.strip()

            # Normalize helper series
            crypto_ids_lower = crypto_df["id"].str.lower()
            crypto_names_lower = crypto_df["name"].str.lower()
            crypto_symbols_exact = crypto_df["symbol"]
            crypto_symbols_lower = crypto_symbols_exact.str.lower()

            # Prepare entrants 'Coin'
            entrants_df["Coin"] = entrants_df["Coin"].astype(str)
            coin_lower_series = entrants_df["Coin"].str.lower()

            # ------------------------------------------------------------------
            # Step 1.1: Re-write full names (matched against crpytoList.id) to tickers (equivalent cryptoList.symbol)
            # ------------------------------------------------------------------
            print("Normalizing id values to symbols")
            id_symbol_pairs = list(zip(crypto_ids_lower, crypto_symbols_exact))

            new_coins = []
            for idx, coin_lower in coin_lower_series.items():
                original_coin_display = entrants_df.at[idx, "Coin"]
                replaced_value = original_coin_display  # default unchanged

                for id_lower, symbol_exact in id_symbol_pairs:
                    if isinstance(coin_lower, str) and id_lower in coin_lower:
                        if original_coin_display != symbol_exact:
                            print(f"Anomaly: '{original_coin_display}' being replaced with '{symbol_exact}'")
                        replaced_value = symbol_exact
                        break  # first match wins

                new_coins.append(replaced_value)

            entrants_df["Coin"] = pd.Series(new_coins, index=entrants_df.index)

            # Refresh the lowercase series after 1.1
            coin_lower_series = entrants_df["Coin"].astype(str).str.lower()

            # ------------------------------------------------------------------
            # Step 1.2: Re-write full names (matched against cryptoList.name) to tickers (equivalent cryptoList.symbol)
            # ------------------------------------------------------------------
            print("Normalizing id values to names")
            name_symbol_name_triples = list(zip(crypto_names_lower, crypto_symbols_exact, crypto_df["name"]))

            new_coins = []
            for idx, coin_lower in coin_lower_series.items():
                original_coin_display = entrants_df.at[idx, "Coin"]
                replaced_value = original_coin_display  # default unchanged

                for name_lower, symbol_exact, name_exact in name_symbol_name_triples:
                    if isinstance(coin_lower, str) and name_lower in coin_lower:
                        # Exact requested wording
                        print(f"Anomaly: {original_coin_display} being replaced with {name_exact}")
                        replaced_value = symbol_exact
                        break  # first match wins

                new_coins.append(replaced_value)

            entrants_df["Coin"] = pd.Series(new_coins, index=entrants_df.index)

            # ------------------------------------------------------------------
            # Step 1.3: Filter out Party/Virtual ticket types
            # ------------------------------------------------------------------
            print("Filtering out entrants with Ticket Type 'Party' or 'Virtual'")

            if "Ticket Type" in entrants_df.columns:
                # Trim and normalize for reliable matching
                tt_raw = entrants_df["Ticket Type"].astype(str).str.strip()
                tt_norm = tt_raw.str.lower()

                # Substring match per your spec ("contains" Party/Virtual)
                drop_mask = tt_norm.str.contains("party", na=False) | tt_norm.str.contains("virtual", na=False)

                if drop_mask.any():
                    for _, row in entrants_df.loc[drop_mask, ["Name", "Ticket Type"]].iterrows():
                        print(f"Entry for '{row['Name']}' discounted for ticket type: '{row['Ticket Type']}'")
                    entrants_df = entrants_df.loc[~drop_mask].reset_index(drop=True)
            else:
                print("Warning: 'Ticket Type' column not found; Step 1.3 skipped")

            # ------------------------------------------------------------------
            # Step 2: Convert entrants column 'Coin' tolower
            # ------------------------------------------------------------------
            print("Converting all values tolower")
            entrants_df["Coin"] = entrants_df["Coin"].astype(str).str.lower()

            # ------------------------------------------------------------------
            # Step 3: Convert data in date column to format 'dd-MMM-yyyy'
            # (supports input in BOTH dd/MM/yy and dd/MM/yyyy)
            # ------------------------------------------------------------------
            print("Converting all dates to format 'dd-MMM-yyyy'")
            date_str = entrants_df["Date"].astype(str).str.strip()

            # Detect 4-digit and 2-digit year patterns
            mask_yyyy = date_str.str.match(r"^\d{1,2}/\d{1,2}/\d{4}$", na=False)
            mask_yy   = date_str.str.match(r"^\d{1,2}/\d{1,2}/\d{2}$",  na=False)

            parsed = pd.Series(pd.NaT, index=entrants_df.index, dtype="datetime64[ns]")
            # Parse explicit formats
            parsed.loc[mask_yyyy] = pd.to_datetime(date_str.loc[mask_yyyy], format="%d/%m/%Y", errors="coerce")
            parsed.loc[mask_yy]   = pd.to_datetime(date_str.loc[mask_yy],   format="%d/%m/%y", errors="coerce")

            # Fallback for any oddballs: general parser with dayfirst
            need_fallback = parsed.isna()
            if need_fallback.any():
                parsed.loc[need_fallback] = pd.to_datetime(date_str.loc[need_fallback], dayfirst=True, errors="coerce")

            # Write formatted string; if still NaT, keep original trimmed value
            entrants_df["Date"] = parsed.dt.strftime("%d-%b-%Y").where(parsed.notna(), date_str)

            # Normalize Time -> keep as HH:mm (with safe fallback)
            time_str = entrants_df["Time"].astype(str).str.strip()
            times_parsed = pd.to_datetime(time_str, format="%H:%M", errors="coerce")
            entrants_df["Time"] = times_parsed.dt.strftime("%H:%M").where(times_parsed.notna(), time_str)

            # ------------------------------------------------------------------
            # Step 4: Delete rows where entrants Coin not in cryptoList symbols
            # ------------------------------------------------------------------
            symbols_set = set(crypto_symbols_lower.tolist())
            to_drop_indices = []
            for idx, coin_val in entrants_df["Coin"].items():
                if pd.isna(coin_val) or coin_val not in symbols_set:
                    name_val = entrants_df.at[idx, "Name"]
                    coin_display = entrants_df.at[idx, "Coin"]
                    print(f"Entry for '{name_val}' discounted for data mismatch: '{coin_display}' not present in cryptoList")
                    to_drop_indices.append(idx)

            if to_drop_indices:
                entrants_df = entrants_df.drop(index=to_drop_indices).reset_index(drop=True)

            # ------------------------------------------------------------------
            # Step 5: Delete all columns except 'Name', 'Date', 'Time', 'Coin'
            # ------------------------------------------------------------------
            print("Removing all non-relevant columns")
            keep_cols = ["Name", "Date", "Time", "Coin"]
            for col in keep_cols:
                if col not in entrants_df.columns:
                    entrants_df[col] = pd.NA
            entrants_df = entrants_df[keep_cols]

            # Step 6: Rename columns
            print("Renaming columns")
            entrants_df = entrants_df.rename(
                columns={
                    "Name": "attendeeName",
                    "Date": "signUpDate",
                    "Time": "signUpTime",
                    "Coin": "cryptoSymbol",
                }
            )

            # ------------------------------------------------------------------
            # Step 7 — Cap to first five entries per cryptoSymbol by date-time
            # ------------------------------------------------------------------
            print("Capping entries to first five per cryptoSymbol (by date-time)")

            # Build a sort key from signUpDate + signUpTime; put unparsable values last
            dt = pd.to_datetime(
                entrants_df["signUpDate"].astype(str).str.strip() + " " +
                entrants_df["signUpTime"].astype(str).str.strip(),
                format="%d-%b-%Y %H:%M",
                errors="coerce"
            )
            # Keep a stable tie-breaker
            entrants_df["_orig_idx"] = range(len(entrants_df))
            entrants_df["_dt_sort"] = dt.fillna(pd.Timestamp.max)

            # Sort then mark rows beyond the first 5 per symbol
            entrants_df = entrants_df.sort_values(["cryptoSymbol", "_dt_sort", "_orig_idx"]).reset_index(drop=True)
            excess_mask = entrants_df.groupby("cryptoSymbol").cumcount() >= 5
            if excess_mask.any():
                # Print one line per removed row for traceability
                for i, row in entrants_df.loc[excess_mask].iterrows():
                    print(
                        f"Entry for '{row['attendeeName']}' on '{row['signUpDate']} {row['signUpTime']}' "
                        f"removed due to >5 cap for '{row['cryptoSymbol']}'"
                    )
                entrants_df = entrants_df.loc[~excess_mask].reset_index(drop=True)

            # Clean temp columns
            entrants_df = entrants_df.drop(columns=["_orig_idx", "_dt_sort"], errors="ignore")

            # Step 8: Save entrants to attendeeList.csv
            print("Saving data to 'attendeeList.csv'")
            entrants_df.to_csv("attendeeList.csv", index=False)

        # Step 9: Close entrants, close cryptoList (handled by context managers)

if __name__ == "__main__":
    main()
