import time
import pandas as pd
import numpy as np
import os
from oandapyV20 import API
from oandapyV20.exceptions import V20Error
from oandapyV20.endpoints.pricing import PricingStream
from oandapyV20.endpoints.instruments import InstrumentsCandles

# Set the OANDA API key
OANDA_API_KEY = "33a9e22e79a6afe67da0e568b0cca830-cf5e494dfe461d8704057859e229b74e"
api = API(access_token=OANDA_API_KEY)

ACCOUNT_ID = "101-001-25836141-002"
INSTRUMENTS = ["GBP_USD"]  # Add more forex pairs as per your requirements
GRANULARITIES = ["D"]
directory = "streaming_data"
os.makedirs(directory, exist_ok=True)

INDICATORS_DIRECTORY = "indicators"
os.makedirs(INDICATORS_DIRECTORY, exist_ok=True)


def load_historical_data(instrument, granularity, count):
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
    df = calculate_indicators(df)
    processed_data = preprocess_data(df)
    save_to_csv(processed_data, instrument, granularity)
    save_indicators_to_csv(df, instrument)


def preprocess_data(df):
    # Select columns for preprocessing
    numeric_cols = ["close"]
    processed_data = df[numeric_cols]

    # Normalize the data
    processed_data = normalize_data(processed_data)

    # Convert DataFrame to numpy array
    processed_data = processed_data.values

    return processed_data


def normalize_data(df):
    return (df - df.mean()) / df.std()


def save_indicators_to_csv(df, instrument):
    indicators = ["RSI", "MACD", "Signal_Line", "Histogram", "BollingerBands_middle", "BollingerBands_std", "ATR",
                  "ADX", "OBV"]
    for indicator in indicators:
        indicator_df = df[["time", indicator]]
        filename = f"{INDICATORS_DIRECTORY}/{instrument}_{indicator}.csv"
        indicator_df.to_csv(filename, index=False)


def calculate_indicators(df):
    # Convert columns to numeric type
    numeric_cols = ["open", "high", "low", "close"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric)

    # Calculate indicators
    df["RSI"] = calculate_rsi(df["close"], window=14)
    df["MACD"], df["Signal_Line"], df["Histogram"] = calculate_macd(df["close"], window_fast=12, window_slow=26,
                                                                   window_signal=9)
    df["BollingerBands_middle"], df["BollingerBands_std"] = calculate_bollinger_bands(df["close"], window=20)
    df["ATR"] = calculate_atr(df["high"], df["low"], df["close"], window=14)
    df["ADX"] = calculate_adx(df["high"], df["low"], df["close"], window=14)
    df["OBV"] = calculate_obv(df["close"], df["volume"])

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


def save_to_csv(data, instrument, granularity):
    if data is not None and len(data) > 0:
        filename = os.path.join(directory, f"{instrument}_{granularity}.csv")
        if not os.path.isfile(filename):
            pd.DataFrame(data).to_csv(filename, index=False, header=False, mode="a")
        else:
            pd.DataFrame(data).to_csv(filename, index=False, header=False, mode="a")

if __name__ == "__main__":
    for instrument in INSTRUMENTS:
        for granularity in GRANULARITIES:
            load_historical_data(instrument, granularity, count=90 * 24)

  
