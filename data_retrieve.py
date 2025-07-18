import psycopg2
import pandas as pd

# PostgreSQL connection details
DB_HOST = 'localhost'
DB_NAME = 'Stock_Summer_2025'
DB_USER = 'postgres'
DB_PASSWORD = 'Ansh2006**'
DB_PORT = 5432

# Connect to PostgreSQL database
conn = psycopg2.connect(
    host='localhost',
    dbname='Stock_Summer_2025',
    user='postgres',
    password='Ansh2006**',
    port=5432
)

# Query to retrieve all data from day_ohlcv
df_day = pd.read_sql_query('SELECT * FROM day_ohlcv ORDER BY symbol_id ASC, trade_date DESC', conn)
df_minute = pd.read_sql_query('SELECT * FROM minute_price ORDER BY symbol_id ASC, trade_datetime DESC', conn)
# Close the connection
conn.close()

# The DataFrame 'df_day' now contains your day_ohlcv table data and can be used in other scripts
# Example: print(df_day.head())

# The DataFrame 'df_minute' now contains your minute_price table data and can be used in other scripts
# Example: print(df_minute.head())
print(df_day.head(10))
#print(df_minute.head(10))