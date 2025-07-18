import backtrader as bt
import pandas as pd
import numpy as np
from data_retrieve import df_day
from trade1 import Strat1
from trade2 import Trade2

# === Backtest Configuration ===
INITIAL_CAPITAL = 1000000  # Set your initial capital here
SLIPPAGE_PCT = 0.001  # 0.1% slippage
MAX_TRADE_PCT = 0.05  # Max 5% of current capital per trade

class TradeSizer(bt.Sizer):
    def _getsizing(self, comminfo, cash, data, isbuy):
        # Use up to 5% of current cash for each trade
        max_cash = cash * MAX_TRADE_PCT
        price = data.close[0]
        # Estimate cost per share including slippage
        slippage_cost = price * SLIPPAGE_PCT
        total_price_per_share = price 
        if total_price_per_share <= 0:
            return 0
        size = int(max_cash // total_price_per_share)
        # Ensure we have enough cash for at least 1 share
        if size < 1 or (size * total_price_per_share) > cash:
            return 0
        return size

# Prepare data for Backtrader
# Ensure df_day has a datetime index for Backtrader
if 'trade_date' in df_day.columns:
    df_day['trade_date'] = pd.to_datetime(df_day['trade_date'])
    df_day = df_day.set_index('trade_date')

# Set up Cerebro
cerebro = bt.Cerebro()
cerebro.broker.setcash(INITIAL_CAPITAL)
cerebro.broker.set_slippage_perc(SLIPPAGE_PCT)
cerebro.broker.setcommission(commission=0.0, leverage=1.0)  # No margin, no commission
# Prevent shorting if supported
if hasattr(cerebro.broker, 'set_shortcash'):
    cerebro.broker.set_shortcash(True)
cerebro.addsizer(TradeSizer)

# Add a data feed for each symbol_id
symbol_col = 'symbol_id'
unique_symbols = df_day[symbol_col].unique()
for symbol in unique_symbols:
    symbol_df = df_day[df_day[symbol_col] == symbol].copy()
    symbol_df = symbol_df.drop(columns=[symbol_col])
    data = bt.feeds.PandasData(dataname=symbol_df)
    cerebro.adddata(data, name=str(symbol))
    print(f"Added data feed for symbol_id: {symbol}, Rows: {len(symbol_df)}")

cerebro.addstrategy(Strat1)

# Add analyzers
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='tradeanalyzer')

# Run backtest
results = cerebro.run()
strat = results[0]

# Output results
print(f"Final Portfolio Value: {cerebro.broker.getvalue():.2f}")
print(f"Final Cash Remaining: {cerebro.broker.get_cash():.2f}")
print(f"Sharpe Ratio: {strat.analyzers.sharpe.get_analysis()}")
returns = strat.analyzers.returns.get_analysis()
if 'rnorm100' in returns:
    print(f"Annualized Return (IRR): {returns['rnorm100']:.2f}%")
else:
    print("IRR not available.")

# After running the backtest, print the total number of closed trades
trade_analysis = strat.analyzers.tradeanalyzer.get_analysis()
num_trades = trade_analysis.get('total', {}).get('closed', 0)
print(f"Total Trades Executed: {num_trades}")

# Print trade log with buy date, sell date, size, PnL, and symbol id if available
if 'closed' in trade_analysis:
    print("\nTRADE LOG:")
    closed_trades = trade_analysis['closed']
    for trade in closed_trades:
        # TradeAnalyzer does not provide symbol id directly, so this is a placeholder
        print(f"Buy Date: {trade['open_datetime']}, Sell Date: {trade['close_datetime']}, Size: {trade['size']}, PnL: {trade['pnl']:.2f}, Symbol: N/A")
else:
    print("No closed trades to log.")
