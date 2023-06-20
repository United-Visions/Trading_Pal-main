import time
import pandas as pd
import numpy as np
from oandapyV20 import API
from oandapyV20.contrib.requests import MarketOrderRequest
from oandapyV20.endpoints.orders import OrderCreate
from oandapyV20.endpoints.pricing import PricingStream

OANDA_API_KEY = "33a9e22e79a6afe67da0e568b0cca830-cf5e494dfe461d8704057859e229b74e"
api = API(access_token=OANDA_API_KEY)
ACCOUNT_ID = "101-001-25836141-002"

class Strategies:
    def __init__(self):
        # initialize data
        self.df = pd.DataFrame()

        # trading states
        self.position = 0  # 1 for long position, -1 for short position, 0 for no position
        self.buy_price, self.sell_price = 0, 0
        self.stop_loss, self.take_profit = 0, 0
        self.balance = 10000

    def update_data(self, df_new):
        self.df = self.df.append(df_new, ignore_index=True)
        self.df = self.calculate_indicators(self.df)
        self.df.dropna(inplace=True)

    def RSI_and_MACD_Crossover_Strategy(self, data):
        # replace for loop with the last row of data
        i = -1
        current_price = data["close"]
        current_rsi = data["RSI"]
        current_macd = data["MACD"]
        current_signal_line = data["Signal_Line"]
        current_atr = data["ATR"]

        if self.position == 0:
            if current_rsi > 30 and current_macd > current_signal_line:
                self.position = 1
                self.buy_price = current_price
                self.stop_loss = self.buy_price - 2 * current_atr
                self.take_profit = self.buy_price + 2 * current_atr
                units = self.balance / current_price
                order_data = MarketOrderRequest(instrument='GBP_USD', units=units)
                r = OrderCreate(ACCOUNT_ID, data=order_data.data)
                api.request(r)
            elif current_rsi < 70 and current_macd < current_signal_line:
                self.position = -1
                self.sell_price = current_price
                self.stop_loss = self.sell_price + 2 * current_atr
                self.take_profit = self.sell_price - 2 * current_atr
                units = -self.balance / current_price
                order_data = MarketOrderRequest(instrument='GBP_USD', units=units)
                r = OrderCreate(ACCOUNT_ID, data=order_data.data)
                api.request(r)
        elif self.position == 1:
            if current_rsi > 70 or current_macd < current_signal_line or current_price <= self.stop_loss or current_price >= self.take_profit:
                self.position = 0
                units = -self.balance / current_price
                order_data = MarketOrderRequest(instrument='GBP_USD', units=units)
                r = OrderCreate(ACCOUNT_ID, data=order_data.data)
                api.request(r)
        else:
            if current_rsi < 30 or current_macd > current_signal_line or current_price >= self.stop_loss or current_price <= self.take_profit:
                self.position = 0
                units = self.balance / current_price
                order_data = MarketOrderRequest(instrument='GBP_USD', units=units)
                r = OrderCreate(ACCOUNT_ID, data=order_data.data)
                api.request(r)


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

def streaming_data():
    r = PricingStream(accountID=ACCOUNT_ID, params={"instruments": "GBP_USD"})
    rv = api.request(r)
    return rv

def main():
    strategies = Strategies()

    for tick in streaming_data():
        if tick["type"] != "PRICE":
            continue
        high_bid = float(tick["bids"][0]["price"])
        low_ask = float(tick["asks"][0]["price"])
        df_new = pd.DataFrame({
            "close": [tick["closeoutBid"]],
            "high": [high_bid],
            "low": [low_ask],
            "volume": [tick["volume"]],
            "time": [tick["time"]]
        })
        strategies.update_data(df_new)
        strategies.RSI_and_MACD_Crossover_Strategy(strategies.df.iloc[-1])


if __name__ == "__main__":
    main()
