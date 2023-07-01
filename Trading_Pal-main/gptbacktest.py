import pandas as pd
import numpy as np
import os
import openai
from oandapyV20 import API
from oandapyV20.exceptions import V20Error
from oandapyV20.endpoints.instruments import InstrumentsCandles
from indicators import calculate_rsi, calculate_macd, calculate_bollinger_bands, calculate_atr, calculate_adx, calculate_obv

OANDA_API_KEY = "ba62e5ad63f2f3ce2"
api = API(access_token=OANDA_API_KEY)

ACCOUNT_ID = "101-002"
INSTRUMENTS = ["GBP_USD"]
GRANULARITIES = [ "D"]

INDICATORS_DIRECTORY = "indicators"
os.makedirs(INDICATORS_DIRECTORY, exist_ok=True)


class Strategies:
    def __init__(self, df):
        self.df = df

    
        #--------------------------#
        #                          #
        #    Strategies List       #
        #                          #
        #--------------------------#


    #TODO Add an exaustive list of Strategies, Indicators, trading robots!
    #TODO ALLOW USERS TO INPUT THE STARTING BALANCE, instrument, risk parameters
    #TODO For Contributors recognition add Strategy  Arthur name & Description will add new feature to search strategies by authors.
    #TODO adding more results for example add drawdown, winning trdes & loss trades, etc.
    #TODO SEARCH by user prefrences by adding each strategy based on tHe users risk tolorances, trading styles and tradi v
    def RSI_and_MACD_Crossover_Strategy(self):
        self.author = "ProfitWave Trading Co."
        self.description = "This strategy combines RSI and MACD crossover signals."

        balance = 10000                 
        position = 0
        buy_price, sell_price = 0, 0
        stop_loss, take_profit = 0, 0
        profit, losses = 0, 0
        entry_prices, exit_prices = [], []

        # Additional parameters
        max_balance, drawdown = balance, 0
        num_trades, num_wins, num_losses = 0, 0, 0
        trailing_stop = 0

        for i in range(len(self.df)):
            current_price = self.df["close"][i]
            current_rsi = self.df["RSI"][i]
            current_macd = self.df["MACD"][i]
            current_signal_line = self.df["Signal_Line"][i]
            current_atr = self.df["ATR"][i]

            # Check if we're not in a position
            if position == 0:
                # Check entry conditions
                if current_rsi > 30 and current_macd > current_signal_line:
                    # Enter a long position
                    position = 1
                    buy_price = current_price
                    stop_loss = buy_price - 2 * current_atr
                    take_profit = buy_price + 2 * current_atr
                elif current_rsi < 70 and current_macd < current_signal_line:
                    # Enter a short position
                    position = -1
                    sell_price = current_price
                    stop_loss = sell_price + 2 * current_atr
                    take_profit = sell_price - 2 * current_atr
            elif position == 1:
                # Update trailing stop loss for long position
                trailing_stop = max(trailing_stop, current_price - 2 * current_atr)
                # We're in a long position, check exit conditions
                if current_rsi > 70 or current_macd < current_signal_line or current_price <= trailing_stop or current_price >= take_profit:
                    # Close the position
                    position = 0
                    profit += current_price - buy_price
                    entry_prices.append(buy_price)
                    exit_prices.append(current_price)
            else:
                # Update trailing stop loss for short position
                trailing_stop = min(trailing_stop, current_price + 2 * current_atr)
                # We're in a short position, check exit conditions
                if current_rsi < 30 or current_macd > current_signal_line or current_price >= trailing_stop or current_price <= take_profit:
                    # Close the position
                    position = 0
                    profit += sell_price - current_price
                    entry_prices.append(sell_price)
                    exit_prices.append(current_price)

            # Update maximum balance and drawdown
            max_balance = max(max_balance, balance)
            drawdown = max(drawdown, max_balance - balance)

            # Update number of trades and number of winning/losing trades
            if position == 0:
                num_trades += 1
                if profit > 0:
                    num_wins += 1
                elif profit < 0:
                    num_losses += 1

        # Calculate performance metrics
        total_return = profit / balance
        win_rate = num_wins / num_trades
        loss_rate = num_losses / num_trades

        print(f"Total return: {total_return * 100}%")
        print(f"Win rate: {win_rate * 100}%")
        print(f"Loss rate: {loss_rate * 100}%")
        print(f"Drawdown: {drawdown / balance * 100}%")
        print(f"Number of trades: {num_trades}")
        print(f"Number of winning trades: {num_wins}")
        print(f"Number of losing trades: {num_losses}")


    def Three_MA_Crossover_Strategy(self):
        self.author = "ProfitWave Trading Co."
        self.description = "This strategy uses a three MA crossover approach."
        balance = 10000
        position = 0
        buy_price, sell_price = 0, 0
        stop_loss, take_profit = 0, 0
        profit, losses = 0, 0
        entry_prices, exit_prices = [], []

        # Additional parameters
        max_balance, drawdown = balance, 0
        num_trades, num_wins, num_losses = 0, 0, 0
        trailing_stop = 0

        # Calculate moving averages
        self.df["MA1"] = self.df["close"].rolling(window=10).mean()
        self.df["MA2"] = self.df["close"].rolling(window=20).mean()
        self.df["MA3"] = self.df["close"].rolling(window=50).mean()

        for i in range(len(self.df)):
            current_price = self.df["close"][i]
            ma1 = self.df["MA1"][i]
            ma2 = self.df["MA2"][i]
            ma3 = self.df["MA3"][i]

            # Check if we're not in a position
            if position == 0:
                # Check entry conditions
                if ma1 > ma2 > ma3:
                    # Enter a long position
                    position = 1
                    buy_price = current_price
                    stop_loss = buy_price - 0.002
                    take_profit = buy_price + 0.003
                elif ma1 < ma2 < ma3:
                    # Enter a short position
                    position = -1
                    sell_price = current_price
                    stop_loss = sell_price + 0.002
                    take_profit = sell_price - 0.003
            elif position == 1:
                # Update trailing stop loss for long position
                trailing_stop = max(trailing_stop, current_price - 0.001)
                # We're in a long position, check exit conditions
                if current_price <= trailing_stop or current_price >= take_profit:
                    # Close the position
                    position = 0
                    profit += current_price - buy_price
                    entry_prices.append(buy_price)
                    exit_prices.append(current_price)
            else:
                # Update trailing stop loss for short position
                trailing_stop = min(trailing_stop, current_price + 0.001)
                # We're in a short position, check exit conditions
                if current_price >= trailing_stop or current_price <= take_profit:
                    # Close the position
                    position = 0
                    profit += sell_price - current_price
                    entry_prices.append(sell_price)
                    exit_prices.append(current_price)

            # Update maximum balance and drawdown
            max_balance = max(max_balance, balance)
            drawdown = max(drawdown, max_balance - balance)

            # Update number of trades and number of winning/losing trades
            if position == 0:
                num_trades += 1
                if profit > 0:
                    num_wins += 1
                elif profit < 0:
                    num_losses += 1

        # Calculate performance metrics
        total_return = profit / balance
        win_rate = num_wins / num_trades
        loss_rate = num_losses / num_trades

        print(f"Total return: {total_return * 100}%")
        print(f"Win rate: {win_rate * 100}%")
        print(f"Loss rate: {loss_rate * 100}%")
        print(f"Drawdown: {drawdown / balance * 100}%")
        print(f"Number of trades: {num_trades}")
        print(f"Number of winning trades: {num_wins}")
        print(f"Number of losing trades: {num_losses}")

        #--------------------------#
        # Add New Strategies Here  #
        #--------------------------#

    def One_Day_Reversal_Strategy(self):
        self.author = "Your Name"
        self.description = "This strategy identifies a reversal pattern on a daily candlestick chart."

        balance = 10000                 
        position = 0
        buy_price, sell_price = 0, 0
        stop_loss, take_profit = 0, 0
        profit, losses = 0, 0
        entry_prices, exit_prices = [], []

        for i in range(2, len(self.df["close"])): 
            # Assuming self.df["close"] is the closing prices of the daily candles

            # Enter a long position when a candle closes above the previous one after a series of down candles
            if self.df["close"][i] > self.df["close"][i-1] and self.df["close"][i-1] < self.df["close"][i-2]:
                if position != 0:
                    # Close previous position
                    if position == 1:
                        profit += self.df["close"][i] - buy_price
                    else:
                        profit += sell_price - self.df["close"][i]
                    entry_prices.append(buy_price if position == 1 else sell_price)
                    exit_prices.append(self.df["close"][i])

                # Enter a long position
                position = 1
                buy_price = self.df["close"][i]
                stop_loss = buy_price - self.df["close"][i-1]  # Stop loss at previous candle's closing price
                take_profit = buy_price + self.df["close"][i-1]  # Take profit at twice the previous candle's closing price

            # Enter a short position when a candle closes below the previous one after a series of up candles
            elif self.df["close"][i] < self.df["close"][i-1] and self.df["close"][i-1] > self.df["close"][i-2]:
                if position != 0:
                    # Close previous position
                    if position == 1:
                        profit += self.df["close"][i] - buy_price
                    else:
                        profit += sell_price - self.df["close"][i]
                    entry_prices.append(buy_price if position == 1 else sell_price)
                    exit_prices.append(self.df["close"][i])

                # Enter a short position
                position = -1
                sell_price = self.df["close"][i]
                stop_loss = sell_price + self.df["close"][i-1]  # Stop loss at previous candle's closing price
                take_profit = sell_price - self.df["close"][i-1]  # Take profit at twice the previous candle's closing price

        print(f"Profit: {profit}")

    

    strategies = {
        "RSI_and_MACD_Crossover_Strategy": {
            "author": "ProfitWave Trading Co.",
            "func": RSI_and_MACD_Crossover_Strategy
        },
        "Three_MA_Crossover_Strategy": {
            "author": "ProfitWave Trading Co.",
            "func": Three_MA_Crossover_Strategy
        },
         "One_Day_Reversal_Strategy": {
            "author": "Your Name",
            "func": One_Day_Reversal_Strategy
        }
        # Add more strategies here...
    }

    def search_and_backtest_by_strategy(self, strategy_name):
        strategy = self.strategies.get(strategy_name)
        if strategy is not None:
            print(f"Backtesting strategy: {strategy_name} by {strategy['author']}")
            strategy["func"](self)
        else:
            print("Strategy not found.")

    def get_strategies_by_author(self, author_name):
        strategies_by_author = [strategy for strategy, details in self.strategies.items() if details["author"] == author_name]
        if strategies_by_author:
            print(f"Found {len(strategies_by_author)} strategies by {author_name}.")
            return strategies_by_author
        else:
            print("No strategies found by the specified author.")
            return []





def load_historical_data(instrument, granularity, count):
    print("Loading historical data...")
    params = {"granularity": granularity, "count": count}
    r = InstrumentsCandles(instrument=instrument, params=params)
    api.request(r)

    records = []
    for candle in r.response["candles"]:
        record = {
            "time": candle["time"],
            "volume": candle["volume"],
            "open": candle["mid"]["o"],
            "high": candle["mid"]["h"],
            "low": candle["mid"]["l"],
            "close": candle["mid"]["c"],
            "instrument": instrument,
            "granularity": granularity
        }
        records.append(record)

    df = pd.DataFrame(records)
    df["time"] = pd.to_datetime(df["time"])
    print("Calculating indicators...")
    df = calculate_indicators(df) 
    if df is None:
        print("Failed to calculate indicators.")
    else:
        print(f"DataFrame size: {df.shape}")
    save_to_csv(df, instrument, granularity)
    save_indicators_to_csv(df, instrument)
    print("Historical data loaded and processed.")
    return df

def save_to_csv(df, instrument, granularity):
    filename = f"{INDICATORS_DIRECTORY}/{instrument}_{granularity}.csv"
    df.to_csv(filename, index=False)






        #--------------------------#
        #                          #
        #   define and calculate   #
        #      indictors           #
        #                          #
        #--------------------------#
 

def calculate_indicators(df):
    print("Calculating indicators...")
    # Convert columns to numeric type
    numeric_cols = ["open", "high", "low", "close"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric)

    # Calculate indicators
    df["RSI"] = calculate_rsi(df["close"], window=14)
    df["MACD"], df["Signal_Line"], df["Histogram"] = calculate_macd(df["close"], window_fast=12, window_slow=26, window_signal=9)
    df["BollingerBands_middle"], df["BollingerBands_std"] = calculate_bollinger_bands(df["close"], window=20)
    df["ATR"] = calculate_atr(df["high"], df["low"], df["close"], window=14)
    df["ADX"] = calculate_adx(df["high"], df["low"], df["close"], window=14)
    df["OBV"] = calculate_obv(df["close"], df["volume"])

    print("Indicators calculated.")
    return df
def save_indicators_to_csv(df, instrument):
    indicators = ["RSI", "MACD", "Signal_Line", "Histogram", "BollingerBands_middle", "BollingerBands_std", "ATR", "ADX", "OBV"]
    for indicator in indicators:
        indicator_df = df[["time", indicator]]
        filename = f"{INDICATORS_DIRECTORY}/{instrument}_{indicator}.csv"
        indicator_df.to_csv(filename, index=False)



# Create a list of timeframes
TIMEFRAMES = ["M1", "M15", "M30", "H1", "H4"]

# Load data for each timeframe
def load_all_timeframes(instrument, count):
    print("Starting to load data for all timeframes...")
    dataframes = {}
    for timeframe in TIMEFRAMES:
        print(f"\nLoading {timeframe} data...")
        df = load_historical_data(instrument, timeframe, count)
        if df is not None:
            print(f"Data for {timeframe} loaded successfully.")
            dataframes[timeframe] = df
        else:
            print(f"Failed to load data for {timeframe}.")
    print("Finished loading data for all timeframes.")
    return dataframes
def main():
    # Load historical data
    df = load_historical_data(INSTRUMENTS[0], GRANULARITIES[0], 5000)

    # Initialize strategies object
    strategies_obj = Strategies(df)

    # User input for search method
    search_method = input("Enter '1' to search by strategy or '2' to search by author: ")

    if search_method == '1':
        # Perform backtest by strategy name
        strategies_obj.search_and_backtest_by_strategy(input("Enter the strategy name: "))
    elif search_method == '2':
        author_name = input("Enter the author name: ")
        # Get strategies by author
        strategies = strategies_obj.get_strategies_by_author(author_name)
        if strategies:
            print(f"Found {len(strategies)} strategies by {author_name}:")
            for i, strategy in enumerate(strategies, 1):
                print(f"{i}. {strategy}")
            
            # User input to select strategy
            strategy_index = int(input("Enter the number of the strategy you want to backtest: ")) - 1
            if 0 <= strategy_index < len(strategies):
                # Perform backtest by selected strategy
                strategies_obj.search_and_backtest_by_strategy(strategies[strategy_index])
            else:
                print("Invalid strategy number.")
        else:
            print(f"No strategies found by {author_name}.")
    else:
        print("Invalid search method. Please enter either '1' or '2'.")

if __name__ == "__main__":
    main()
