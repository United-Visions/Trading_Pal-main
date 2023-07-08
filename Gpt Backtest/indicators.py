import pandas as pd
import numpy as np
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
