import backtrader as bt
import pandas as pd

class Trade2(bt.Strategy):
    params = dict(
        fast_period=5,
        slow_period=20,
        size_per_trade=0.05  # Use 1.0 for all-in, or set to a fraction for partial
    )

    def __init__(self):
        self.fast_ma = []
        self.slow_ma = []
        self.crossover = []
        for data in self.datas:
            self.fast_ma.append(bt.indicators.SimpleMovingAverage(data, period=self.p.fast_period))
            self.slow_ma.append(bt.indicators.SimpleMovingAverage(data, period=self.p.slow_period))
            self.crossover.append(bt.indicators.CrossOver(self.fast_ma[-1], self.slow_ma[-1]))
        self.order = None
        self.last_trade_log = None
        self.last_trade_size = 0

    def next(self):
        for i, data in enumerate(self.datas):
            if len(data) < self.p.slow_period:
                continue
            position = self.getposition(data)
            cash = self.broker.get_cash()
            price = data.close[0]
            size = int(cash // price)
            if not position:
                if self.crossover[i][0] > 0 and size > 0:
                    self.buy(data=data, size=size)
            else:
                if self.crossover[i][0] < 0:
                    self.close(data=data, size=size)
