import requests
import pandas as pd

def fetch_item_data(item_id):
    # Define the URL for the time-series data
    url = f"https://prices.runescape.wiki/api/v1/osrs/timeseries?id={item_id}&timestep=1h"
    
    # Set a User-Agent to identify the request
    headers = {
        "User-Agent": "OSRS Market Predictor - @Based_ on Discord"
    }
    
    # Make the API request
    response = requests.get(url, headers=headers)
    
    # Check for a successful response
    if response.status_code == 200:
        data = response.json()
        print(data)  # Print the raw API response for inspection
        
        # Ensure to adjust this depending on the actual structure of the returned data
        # Assuming 'data' contains a dictionary with timestamps as keys and price details as values
        return pd.DataFrame(data['data']).T.reset_index()  # Transpose and reset index for better structure
    else:
        print(f"Error fetching data: {response.status_code}")
        return None

# Example usage
if __name__ == "__main__":
    item_id = 4151  # Abyssal Whip
    item_data = fetch_item_data(item_id)
    if item_data is not None:
        print(item_data)
