import sqlite3

def check_database(db_file):
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables in the database:", tables)

        # Check table structure
        if tables:
            table_name = tables[0][0]  # Get the first table name
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            print(f"Columns in {table_name}:", columns)

            # Check data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 10;")
            data = cursor.fetchall()
            print(f"First 10 rows of {table_name}:", data)

    except sqlite3.Error as e:
        print("SQLite error:", e)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    db_file = 'osrs_market_data.db'  # Ensure the correct path
    check_database(db_file)
