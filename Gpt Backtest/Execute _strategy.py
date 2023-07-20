
from oanda_bot import Bot

class MyBot(Bot):
    def strategy(self):
        fast_ma = self.sma(period=5)
        slow_ma = self.sma(period=25)
        
        # golden cross
        self.sell_exit = self.buy_entry = (fast_ma > slow_ma) & (fast_ma.shift() <= slow_ma.shift())
        
        # dead cross
        self.buy_exit = self.sell_entry = (fast_ma < slow_ma) & (fast_ma.shift() >= slow_ma.shift())

# For backtesting
MyBot(
    account_id='101-001-25836141-002',
    access_token='f7501c9e6231ab183360c4eb468eee7d-6530b7bf8b31cd881e2d17ba449a9590',
).backtest()

# For live trading
MyBot(
    account_id='101-001-25836141-002',
    access_token='ba62e5ad63f2a8759ee31761ba01e196-fb6f30ba3b58d44a94152fa5cd4f3ce2',
).run()