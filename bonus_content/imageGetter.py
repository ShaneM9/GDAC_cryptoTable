import pandas as pd
import requests
import time

# Another one-shot, throwaway script for grabbing image URLs and outputting. This goes to a CSV, but would probably
# be better outputting straight to the JSON... but we decided to use JSON after running this, so instead we just used
# another script to pull from the CSV into the new JSON format... Including in this repo since it might be useful to someone...

crypto_df = pd.read_csv('cryptoList.csv')

image_data = []

for _, row in crypto_df.iterrows():
    coin_id = row['id']
    symbol = row['symbol']
    name = row['name']

    try:
        response = requests.get(f'https://api.coingecko.com/api/v3/coins/{coin_id}')
        if response.status_code == 200:
            print(f"Fetching image data for: {coin_id}", end="", flush=True)
            data = response.json()
            image = data.get('image', {})
            image_data.append({
                'id': coin_id,
                'symbol': symbol,
                'name': name,
                'thumb': image.get('thumb')
            })
            for _ in range(12): # Being kind to the API... only roughly 5-6 calls possible per minute before limits kick in
                time.sleep(1)
                print(".", end="", flush=True)
            print()
        else:
            print(f"Failed to retrieve metadata for {coin_id}: {response.status_code}")
    except Exception as e:
        print(f"Error fetching image for {coin_id}: {e}")

df_images = pd.DataFrame(image_data)
df_images.to_csv('metaImage.csv', index=False)
print("Saved metadata to metaImage.csv!")
