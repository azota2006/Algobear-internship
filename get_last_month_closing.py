import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Prompt user for CSV file path
csv_path = input('Enter the path to the CSV file with ticker symbols: ')

# Read tickers from CSV (assume a column named 'Ticker')
tickers_df = pd.read_csv(csv_path)
tickers = tickers_df['Ticker']

# Calculate date range for the last month
end_date = datetime.today()
start_date = end_date - timedelta(days=30)

# Prepare a DataFrame to store results
results = pd.DataFrame()

for ticker in tickers:
    data = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
    if not data.empty:
        results[ticker] = data['Close']
    else:
        print(f'No data found for ticker {ticker} in the last month.')

if not results.empty:
    print('\nDaily closing prices for tickers (last month):')
    print(results)

    # Plotting
    plt.figure(figsize=(12, 6))
    for ticker in results.columns:
        plt.plot(results.index, results[ticker], label=ticker)
    plt.xlabel('Date')
    plt.ylabel('Closing Price')
    plt.title('Daily Closing Prices (Last Month)')
    plt.legend()
    plt.tight_layout()
    plt.show()
else:
    print('No price data found for any tickers.') 