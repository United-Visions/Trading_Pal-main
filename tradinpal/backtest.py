import pandas as pd
import numpy as np
import os
from oandapyV20 import API
from oandapyV20.exceptions import V20Error
from oandapyV20.endpoints.instruments import InstrumentsCandles

OANDA_API_KEY = "33a9e22e79a6afe67da0e568b0cca830-cf5e494dfe461d8704057859e229b74e"
api = API(access_token=OANDA_API_KEY)

ACCOUNT_ID = "101-001-25836141-002"
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


def calculate_rsi(series, window):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(series, window_fast, window_slow, window_signal):
    ema_fast = series.ewm(span=window_fast, adjust=False).mean()
    ema_slow = series.ewm(span=window_slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=window_signal, adjust=False).mean()
    histogram = macd - signal_line
    return macd, signal_line, histogram

def calculate_bollinger_bands(series, window):
    middle_band = series.rolling(window=window).mean()
    std = series.rolling(window=window).std()
    return middle_band, std

def calculate_atr(high, low, close, window):
    tr = np.maximum(high - low, np.abs(high - close.shift()), np.abs(low - close.shift()))
    atr = tr.rolling(window=window).mean()
    return atr

def calculate_adx(high, low, close, window):
    tr = np.maximum(high - low, np.abs(high - close.shift()), np.abs(low - close.shift()))
    atr = calculate_atr(high, low, close, window)  # Calculate ATR using the separate function
    plus_dm = np.where((high - high.shift()) > (low.shift() - low), high - high.shift(), 0)
    minus_dm = np.where((low.shift() - low) > (high - high.shift()), low.shift() - low, 0)
    plus_di = 100 * (pd.Series(plus_dm).rolling(window=window).mean() / pd.Series(atr).rolling(window=window).mean())
    minus_di = 100 * (pd.Series(minus_dm).rolling(window=window).mean() / pd.Series(atr).rolling(window=window).mean())
    dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = dx.rolling(window=window).mean()
    return adx

def calculate_obv(close, volume):
    obv = np.where(close > close.shift(), volume, -volume).cumsum()
    return obv




        #--------------------------#
        # Calculate New Indicators #
        #--------------------------#





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
    print("Starting main function...")
    dataframes = load_all_timeframes('GBP_USD', 90*24)
    strategies = {timeframe: Strategies(df) for timeframe, df in dataframes.items()}
    print("Created strategies for all timeframes.")

    strategy_name = input("Enter the strategy to backtest: ")

    for timeframe, strategy in strategies.items():
        print(f"\nBacktesting {strategy_name} on {timeframe} data...")
        if strategy_name == "RSI and MACD Crossover Strategy":
            strategy.RSI_and_MACD_Crossover_Strategy()
        elif strategy_name == "Three MA Crossover Strategy":
            strategy.Three_MA_Crossover_Strategy()
        else:
            print("Invalid strategy name!")
    print("Finished backtesting.")

if __name__ == "__main__":
    print("Starting script...")
    main()
    print("Script finished.")