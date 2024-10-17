import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

def load_data(db_file, item_id):
    conn = sqlite3.connect(db_file)
    query = f"SELECT * FROM osrs_market_data WHERE item_id = {item_id}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def main():
    db_file = 'osrs_market_data.db'
    item_id = input("Enter item ID to visualize (or press Enter to show default item ID 4151): ")

    if not item_id.strip():
        item_id = '4151'  # Default item ID if none provided
    
    df = load_data(db_file, item_id)
    
    if df.empty:
        print("No data available for analysis.")
        return

    print("Basic Statistics:")
    print(df.describe())
    
    # Print the raw DataFrame to inspect its contents
    print("DataFrame Loaded:")
    print(df.head())  # Display the first few rows

    # Check for bytes and decode if necessary
    for col in ['high_price', 'low_price']:
        if df[col].dtype == 'object':
            df[col] = df[col].apply(lambda x: x.decode() if isinstance(x, bytes) else x)
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df.sort_values('timestamp', inplace=True)

    # Drop rows with NaN values in the price columns after conversion
    df.dropna(subset=['high_price', 'low_price', 'timestamp'], inplace=True)

    # Print the DataFrame after cleaning
    print("Cleaned DataFrame:")
    print(df.head())  # Display the first few rows after cleaning
    print("Data Types:")
    print(df.dtypes)  # Display data types of the columns

    # Check if there's data to plot
    if df.empty:
        print("No valid data available for plotting.")
        return

    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(df['timestamp'], df['high_price'], label='High Price', color='g')
    plt.plot(df['timestamp'], df['low_price'], label='Low Price', color='r')
    plt.title(f'Price History for Item ID {item_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Price')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
