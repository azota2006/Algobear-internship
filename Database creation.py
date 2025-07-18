
import psycopg2
import csv
import os

# Path to your CSV file
CSV_FILE = r'C:\Users\azota\Documents\Data_engine\nifty50_symbols.csv'

# PostgreSQL connection details (update these with your actual credentials)
DB_HOST = 'localhost'
DB_NAME = 'Stock_Summer_2025'
DB_USER = 'postgres'
DB_PASSWORD = 'Ansh2006**'
DB_PORT = 5432  # Default PostgreSQL port

# Connect to PostgreSQL database
conn = psycopg2.connect(
    host=DB_HOST,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    port=DB_PORT
)
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS master_symbol (
    symbol_id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    company_name VARCHAR(100) NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    sector VARCHAR(50),
    isin VARCHAR(20) UNIQUE
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS day_ohlcv (
    day_id SERIAL PRIMARY KEY,
    symbol_id INTEGER NOT NULL,
    trade_date DATE NOT NULL,
    open NUMERIC(12,2),
    high NUMERIC(12,2),
    low NUMERIC(12,2),
    close NUMERIC(12,2),
    volume BIGINT,
    FOREIGN KEY (symbol_id) REFERENCES master_symbol(symbol_id),
    UNIQUE(symbol_id, trade_date)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS minute_price (
    minute_id SERIAL PRIMARY KEY,
    symbol_id INTEGER NOT NULL,
    trade_datetime TIMESTAMP NOT NULL,
    price NUMERIC(12,2),
    FOREIGN KEY (symbol_id) REFERENCES master_symbol(symbol_id),
    UNIQUE(symbol_id, trade_datetime)
)
''')

# Read CSV and insert into master_symbol
with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        cursor.execute('''
            INSERT INTO master_symbol (symbol, company_name, exchange, sector, isin)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (symbol) DO NOTHING
        ''', (
            row['symbol'],
            row['company_name'],
            row['exchange'],
            row['sector'],
            row['isin']
        ))

# Commit and close
conn.commit()
cursor.close()
conn.close()

print("Database and tables created, master_symbol table populated from CSV.")