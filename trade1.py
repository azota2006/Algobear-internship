import backtrader as bt
import pandas as pd

class Strat1(bt.Strategy):
    params = dict(
        holding_period=5  # max holding period in days
    )

    def __init__(self):
        self.order = None
        self.entry_bar = None
        self.prev_close = self.datas[0].close(-1)
        self.prev_high = self.datas[0].high(-1)
        self.trading_stopped = False
        self.last_trade_log = None  # Store buy log until sell
        self.last_trade_size = 0    # Track last buy size

    def next(self):
        # Log position value and current price
        if self.position.size > 0:
            pos_value = self.position.size * self.data.close[0]
            # print(f"POSITION VALUE: {pos_value:.2f}, Current Price: {self.data.close[0]:.2f}, Size: {self.position.size}")
            # Force close if price drops to zero
            if self.data.close[0] <= 0:
                if self.last_trade_size > 0:
                    self.sell(size=self.last_trade_size)
                    print(f"FORCED SELL: Price dropped to zero at {self.data.datetime.date(0)}")
                    self.last_trade_size = 0
        # Stop trading if cash is 0
        if self.broker.get_cash() <= 0:
            self.trading_stopped = True
        if self.trading_stopped:
            return
        # Check if we are in the market
        if self.position.size == 0:
            # Entry condition: today's open < yesterday's close
            # Additional check: only buy if enough cash for at least 1 share and cash won't go negative
            cash = self.broker.get_cash()
            price = self.data.open[0]
            slippage_cost = price * 0.001  # SLIPPAGE_PCT
            total_price_per_share = price + slippage_cost
            max_cash = cash * 0.05  # MAX_TRADE_PCT
            size = int(max_cash // total_price_per_share)
            total_trade_cost = size * total_price_per_share
            if (
                self.data.open[0] < self.data.close[-1]
                and size >= 1
                and total_trade_cost <= cash
                and (cash - total_trade_cost) >= 0  # Hard cash floor
            ):
                self.order = self.buy(size=size)
                self.last_trade_size = size
                self.entry_bar = len(self)
                self.target_price = self.data.high[-1]  # previous day's high
                self.last_trade_log = (
                    f"BUY EXECUTED: Date: {self.data.datetime.date(0)}, Price: {price:.2f}, Size: {size}, Cash after: {cash - total_trade_cost:.2f}"
                )
        else:
            # Only allow sell if a position exists
            if self.position.size > 0 and self.last_trade_size > 0:
                # Exit condition 1: price hits previous day's high
                if self.data.high[0] >= self.target_price:
                    self.sell(size=self.last_trade_size)
                    self.order = None
                    self.entry_bar = None
                    sell_log = f"SELL EXECUTED: Date: {self.data.datetime.date(0)}, Price: {self.data.high[0]:.2f}, Size: {self.last_trade_size}, Cash after: {self.broker.get_cash():.2f}"
                    if self.last_trade_log:
                        print(self.last_trade_log)
                        print(sell_log)
                        self.last_trade_log = None
                    self.last_trade_size = 0
                # Exit condition 2: holding period exceeded
                elif self.entry_bar is not None and (len(self) - self.entry_bar) >= self.p.holding_period:
                    self.sell(size=self.last_trade_size)
                    self.order = None
                    self.entry_bar = None
                    sell_log = f"SELL EXECUTED: Date: {self.data.datetime.date(0)}, Price: {self.data.close[0]:.2f}, Size: {self.last_trade_size}, Cash after: {self.broker.get_cash():.2f}"
                    if self.last_trade_log:
                        print(self.last_trade_log)
                        print(sell_log)
                        self.last_trade_log = None
                    self.last_trade_size = 0

    def stop(self):
        # Force close any open position at the end of the backtest
        if self.position.size > 0 and self.last_trade_size > 0:
            self.sell(size=self.last_trade_size)
            sell_log = f"FORCED SELL AT END: Date: {self.data.datetime.date(0)}, Price: {self.data.close[0]:.2f}, Size: {self.last_trade_size}"
            if self.last_trade_log:
                print(self.last_trade_log)
                print(sell_log)
                self.last_trade_log = None
            self.last_trade_size = 0
