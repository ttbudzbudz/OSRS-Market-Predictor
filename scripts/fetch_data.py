import aiohttp
import asyncio
import sqlite3

# Define the API endpoint to fetch all item IDs
ITEMS_URL = "https://prices.runescape.wiki/api/v1/osrs/mapping"

# User agent for requests
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
}

# Retry configuration
MAX_RETRIES = 5
RETRY_DELAY = 2  # seconds

async def fetch_all_item_ids():
    async with aiohttp.ClientSession() as session:
        async with session.get(ITEMS_URL, headers=HEADERS) as response:
            if response.status == 200:
                return await response.json()  # Return the JSON response
            return []

async def fetch_data(item_id, item_name, index, total_items, session):
    url = f"https://prices.runescape.wiki/api/v1/osrs/timeseries?timestep=5m&id={item_id}"

    retries = 0
    while retries < MAX_RETRIES:
        try:
            async with session.get(url, headers=HEADERS, timeout=10) as response:  # Timeout added
                if response.status == 200:
                    data = await response.json()

                    # Print the progress
                    print(f"{index}/{total_items} items processed: {item_name}")

                    # Check if the response contains valid data
                    if 'data' in data and isinstance(data['data'], dict) and len(data['data']) > 0:
                        timestamps = []
                        high_prices = []
                        low_prices = []
                        
                        # Iterate through the time series data
                        for timestamp, prices in data['data'].items():
                            avg_high_price = prices.get('avgHighPrice', 0) or 0
                            avg_low_price = prices.get('avgLowPrice', 0) or 0
                            
                            timestamps.append(timestamp)
                            high_prices.append(avg_high_price)
                            low_prices.append(avg_low_price)

                        return timestamps, high_prices, low_prices
                else:
                    print(f"Failed to fetch data for {item_name}. Status code: {response.status}")
                    
        except asyncio.TimeoutError:
            print(f"Timeout occurred for {item_name} (ID: {item_id}). Retrying...")
        except Exception as e:
            print(f"Error fetching data for {item_name} (ID: {item_id}): {str(e)}")
        
        # Increment retries and add delay
        retries += 1
        await asyncio.sleep(RETRY_DELAY * retries)

    print(f"Failed to fetch data for {item_name} after {MAX_RETRIES} attempts.")
    return None, None, None

def save_to_database(data):
    conn = sqlite3.connect('osrs_market_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS market_data (
        timestamp TEXT,
        item_id INTEGER,
        high_price INTEGER,
        low_price INTEGER
    )''')

    # Insert the fetched data into the database
    if data:
        cursor.executemany('INSERT INTO market_data (timestamp, item_id, high_price, low_price) VALUES (?, ?, ?, ?)', data)
    conn.commit()
    conn.close()

async def fetch_all_data():
    item_ids = await fetch_all_item_ids()
    all_data = []
    
    total_items = len(item_ids)
    
    async with aiohttp.ClientSession() as session:
        for index, item in enumerate(item_ids, start=1):  # Start counting from 1
            item_id = item['id']  # Adjust this depending on the structure of your item IDs list
            item_name = item['name']  # Assuming the item name is accessible here
            
            # Fetch the data for each item one by one
            timestamps, high_prices, low_prices = await fetch_data(item_id, item_name, index, total_items, session)

            if timestamps is not None:
                for j in range(len(timestamps)):
                    all_data.append((timestamps[j], item_id, high_prices[j], low_prices[j]))

    # Save all data once all items are processed
    save_to_database(all_data)
    print("All items processed and saved to database.")

if __name__ == "__main__":
    asyncio.run(fetch_all_data())
