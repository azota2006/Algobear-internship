import yfinance as yf
import pandas as pd
import psycopg2
import sys
from datetime import datetime, timedelta

def get_scalar(val):
    if isinstance(val, pd.Series):
        return val.iloc[0]
    return val

# Default values
update_mode = "both"
daily_start = (datetime.today() - timedelta(days=5*365)).strftime("%Y-%m-%d")
daily_end = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
daily_interval = "1d"
minute_start = (datetime.today() - timedelta(days=5*365)).strftime("%Y-%m-%d")
minute_end = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
minute_interval = "5m"

# Parse command-line arguments for custom ranges
#python Database_population.py --update day --daily_start 2024-05-01 --daily_end 2024-06-01
#python Database_population.py --update minute --minute_start 2024-06-10 --minute_end 2024-06-11
#python Database_population.py --update both --daily_start 2024-05-01 --daily_end 2024-06-01 --minute_start 2024-06-10 --minute_end 2024-06-11
args = sys.argv[1:]
if args:
    if "--update" in args:
        idx = args.index("--update")
        if idx + 1 < len(args):
            update_mode = args[idx + 1]
    if "--daily_start" in args:
        idx = args.index("--daily_start")
        if idx + 1 < len(args):
            daily_start = args[idx + 1]
    if "--daily_end" in args:
        idx = args.index("--daily_end")
        if idx + 1 < len(args):
            daily_end = args[idx + 1]
    if "--minute_start" in args:
        idx = args.index("--minute_start")
        if idx + 1 < len(args):
            minute_start = args[idx + 1]
    if "--minute_end" in args:
        idx = args.index("--minute_end")
        if idx + 1 < len(args):
            minute_end = args[idx + 1]

# Reconnect to DB if needed
conn = psycopg2.connect(
    host='localhost',
    dbname='Stock_Summer_2025',
    user='postgres',
    password='Ansh2006**',
    port=5432
)
cursor = conn.cursor()

# Get all symbols and their IDs
cursor.execute("SELECT symbol, symbol_id FROM master_symbol")
symbols = cursor.fetchall()

if update_mode in ("day", "both"):
    # Insert daily OHLCV data
    for symbol, symbol_id in symbols:
        df = yf.download(symbol + ".NS", start=daily_start, end=daily_end, interval=daily_interval)
        for date, row in df.iterrows():
            open_val = get_scalar(row['Open'])
            high_val = get_scalar(row['High'])
            low_val = get_scalar(row['Low'])
            close_val = get_scalar(row['Close'])
            volume_val = get_scalar(row['Volume'])
            cursor.execute('''
                INSERT INTO day_ohlcv (symbol_id, trade_date, open, high, low, close, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (symbol_id, trade_date) DO NOTHING
            ''', (
                int(symbol_id),
                date.date(),
                float(open_val) if pd.notnull(open_val) else None,
                float(high_val) if pd.notnull(high_val) else None,
                float(low_val) if pd.notnull(low_val) else None,
                float(close_val) if pd.notnull(close_val) else None,
                int(volume_val) if pd.notnull(volume_val) else None
            ))
        print(f"Inserted daily OHLCV for {symbol}")
    conn.commit()

if update_mode in ("minute", "both"):
    # Insert minute price data
    for symbol, symbol_id in symbols:
        df = yf.download(symbol + ".NS", start=minute_start, end=minute_end, interval=minute_interval)
        for dt, row in df.iterrows():
            close_val = get_scalar(row['Close'])
            cursor.execute('''
                INSERT INTO minute_price (symbol_id, trade_datetime, price)
                VALUES (%s, %s, %s)
                ON CONFLICT (symbol_id, trade_datetime) DO NOTHING
            ''', (
                int(symbol_id),
                dt.to_pydatetime(),
                float(close_val) if pd.notnull(close_val) else None
            ))
        print(f"Inserted minute price data for {symbol}")
    conn.commit()

# Physically reorder day_ohlcv by symbol_id ASC, trade_date DESC using CLUSTER
cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_day_ohlcv_symbol_date ON day_ohlcv(symbol_id ASC, trade_date DESC);
''')
cursor.execute('''
    CLUSTER day_ohlcv USING idx_day_ohlcv_symbol_date;
''')

# Physically reorder minute_price by symbol_id ASC, trade_datetime DESC using CLUSTER
cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_minute_price_symbol_datetime ON minute_price(symbol_id ASC, trade_datetime DESC);
''')
cursor.execute('''
    CLUSTER minute_price USING idx_minute_price_symbol_datetime;
''')

conn.commit()
cursor.close()
conn.close()
