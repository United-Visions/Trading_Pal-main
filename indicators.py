import pandas as pd
import numpy as np
from models import db, Indicator
import traceback

def calculate_rsi(series, window):
    """
    Calculates the Relative Strength Index (RSI) for a given series.

    Args:
        series (pd.Series): The input series.
        window (int): The lookback period for the RSI calculation.

    Returns:
        pd.Series: The calculated RSI values, or None if an error occurred.
    """
    try:
        delta = series.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=window).mean()
        avg_loss = loss.rolling(window=window).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    except Exception as e:
        print(f"[calculate_rsi] ERROR: {e}")
        print(f"[calculate_rsi] Traceback: {traceback.format_exc()}")
        return None

def calculate_macd(series, window_fast, window_slow, window_signal):
    """
    Calculates the Moving Average Convergence Divergence (MACD) for a given series.

    Args:
        series (pd.Series): The input series.
        window_fast (int): The lookback period for the fast EMA.
        window_slow (int): The lookback period for the slow EMA.
        window_signal (int): The lookback period for the signal line.

    Returns:
        tuple: A tuple containing the MACD line, signal line, and histogram, or (None, None, None) if an error occurred.
    """
    try:
        ema_fast = series.ewm(span=window_fast, adjust=False).mean()
        ema_slow = series.ewm(span=window_slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=window_signal, adjust=False).mean()
        histogram = macd - signal_line
        return macd, signal_line, histogram
    except Exception as e:
        print(f"[calculate_macd] ERROR: {e}")
        print(f"[calculate_macd] Traceback: {traceback.format_exc()}")
        return None, None, None

def calculate_bollinger_bands(series, window):
    """
    Calculates the Bollinger Bands for a given series.

    Args:
        series (pd.Series): The input series.
        window (int): The lookback period for the moving average and standard deviation.

    Returns:
        tuple: A tuple containing the middle band and standard deviation, or (None, None) if an error occurred.
    """
    try:
        middle_band = series.rolling(window=window).mean()
        std = series.rolling(window=window).std()
        return middle_band, std
    except Exception as e:
        print(f"[calculate_bollinger_bands] ERROR: {e}")
        print(f"[calculate_bollinger_bands] Traceback: {traceback.format_exc()}")
        return None, None

def calculate_atr(high, low, close, window):
    """
    Calculates the Average True Range (ATR) for a given series.

    Args:
        high (pd.Series): The high prices.
        low (pd.Series): The low prices.
        close (pd.Series): The closing prices.
        window (int): The lookback period for the ATR calculation.

    Returns:
        pd.Series: The calculated ATR values, or None if an error occurred.
    """
    try:
        tr = np.maximum(high - low, np.abs(high - close.shift()), np.abs(low - close.shift()))
        atr = tr.rolling(window=window).mean()
        return atr
    except Exception as e:
        print(f"[calculate_atr] ERROR: {e}")
        print(f"[calculate_atr] Traceback: {traceback.format_exc()}")
        return None

def calculate_adx(high, low, close, window):
    """
    Calculates the Average Directional Index (ADX) for a given series.

    Args:
        high (pd.Series): The high prices.
        low (pd.Series): The low prices.
        close (pd.Series): The closing prices.
        window (int): The lookback period for the ADX calculation.

    Returns:
        pd.Series: The calculated ADX values, or None if an error occurred.
    """
    try:
        tr = np.maximum(high - low, np.abs(high - close.shift()), np.abs(low - close.shift()))
        atr = calculate_atr(high, low, close, window)  # Calculate ATR using the separate function
        plus_dm = np.where((high - high.shift()) > (low.shift() - low), high - high.shift(), 0)
        minus_dm = np.where((low.shift() - low) > (high - high.shift()), low.shift() - low, 0)
        plus_di = 100 * (pd.Series(plus_dm).rolling(window=window).mean() / pd.Series(atr).rolling(window=window).mean())
        minus_di = 100 * (pd.Series(minus_dm).rolling(window=window).mean() / pd.Series(atr).rolling(window=window).mean())
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=window).mean()
        return adx
    except Exception as e:
        print(f"[calculate_adx] ERROR: {e}")
        print(f"[calculate_adx] Traceback: {traceback.format_exc()}")
        return None

def calculate_obv(close, volume):
    """
    Calculates the On-Balance Volume (OBV) for a given series.

    Args:
        close (pd.Series): The closing prices.
        volume (pd.Series): The volume data.

    Returns:
        pd.Series: The calculated OBV values, or None if an error occurred.
    """
    try:
        obv = np.where(close > close.shift(), volume, -volume).cumsum()
        return obv
    except Exception as e:
        print(f"[calculate_obv] ERROR: {e}")
        print(f"[calculate_obv] Traceback: {traceback.format_exc()}")
        return None

def load_all_indicators():
    """
    Load all indicators from the database and dynamically execute their calculation code.

    Returns:
        list: A list of dictionaries, each containing the indicator's name, description, and calculated values.
              Returns an empty list if no indicators are found or if an error occurs.
    """
    try:
        indicators = Indicator.query.all()
        if not indicators:
            print("[load_all_indicators] No indicators found in the database.")
            return []

        results = []
        for indicator in indicators:
            try:
                # Create a safe environment for executing the code
                safe_globals = {
                    "__builtins__": __builtins__,
                    "pd": pd,
                    "np": np,
                    "calculate_rsi": calculate_rsi,
                    "calculate_macd": calculate_macd,
                    "calculate_bollinger_bands": calculate_bollinger_bands,
                    "calculate_atr": calculate_atr,
                    "calculate_adx": calculate_adx,
                    "calculate_obv": calculate_obv
                }
                # Execute the calculation code
                exec(indicator.calculation_code, safe_globals)
                
                # Get the result
                result = safe_globals.get('result', None)
                
                if result is not None:
                    results.append({
                        "name": indicator.name,
                        "description": indicator.description,
                        "values": result
                    })
                else:
                    print(f"[load_all_indicators] Indicator '{indicator.name}' did not produce a result.")

            except Exception as e:
                print(f"[load_all_indicators] ERROR executing code for indicator '{indicator.name}': {e}")
                print(f"[load_all_indicators] Traceback: {traceback.format_exc()}")

        return results

    except Exception as e:
        print(f"[load_all_indicators] ERROR: {e}")
        print(f"[load_all_indicators] Traceback: {traceback.format_exc()}")
        return []

def save_indicator_to_db(name, description, calculation_code, parameters):
    """
    Save a new indicator to the database.

    Args:
        name (str): The name of the indicator.
        description (str): A description of the indicator.
        calculation_code (str): The Python code for calculating the indicator.
        parameters (dict): The parameters required for the indicator calculation.

    Returns:
        Indicator: The newly created Indicator object, or None if an error occurred.
    """
    try:
        # Check for duplicate indicator name
        existing_indicator = Indicator.query.filter_by(name=name).first()
        if existing_indicator:
            print(f"[save_indicator_to_db] ERROR: Indicator with name '{name}' already exists.")
            return None

        indicator = Indicator(
            name=name,
            description=description,
            calculation_code=calculation_code,
            parameters=parameters
        )
        db.session.add(indicator)
        db.session.commit()
        print(f"[save_indicator_to_db] Successfully saved indicator: {name}")
        return indicator
    except Exception as e:
        db.session.rollback()
        print(f"[save_indicator_to_db] ERROR: {e}")
        print(f"[save_indicator_to_db] Traceback: {traceback.format_exc()}")
        return None
