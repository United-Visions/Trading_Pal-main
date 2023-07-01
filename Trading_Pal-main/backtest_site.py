from flask import Flask, request, render_template, jsonify
import pandas as pd
import os
from oandapyV20 import API
from oandapyV20.exceptions import V20Error
from oandapyV20.endpoints.instruments import InstrumentsCandles
from indicators import calculate_rsi, calculate_macd, calculate_bollinger_bands, calculate_atr, calculate_adx, calculate_obv
import traceback

app = Flask(__name__)

OANDA_API_KEY = "ba62e5"
api = API(access_token=OANDA_API_KEY)

INDICATORS_DIRECTORY = "indicators"
os.makedirs(INDICATORS_DIRECTORY, exist_ok=True)

# Replace with your actual database
database = []

@app.route('/save_strategy', methods=['POST'])
def save_strategy():
    data = request.get_json()
    database.append(data)
    return jsonify(success=True)

@app.route('/get_strategies', methods=['GET'])
def get_strategies():
    return jsonify(database)

@app.route('/search_strategies', methods=['POST'])
def search_strategies():
    search = request.get_json().get('search')
    result = [s for s in database if search in s['strategyName'] or search in s['authorName']]
    return jsonify(result)

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

@app.route("/")
def index():
    return render_template("backtest.html")
@app.route("/backtest", methods=["POST"])
def backtest_strategy():
    data = request.get_json()
    strategy_name = data["strategyName"]
    author_name = data["authorName"]
    strategy_code = data["strategyCode"]
    currency_pair = data["currencyPair"]
    time_frame = data["timeFrame"]

    # Save the strategy before backtesting
    save_strategy_data = {
        "strategyName": strategy_name,
        "authorName": author_name,
        "strategyCode": strategy_code,
        "currencyPair": currency_pair,
        "timeFrame": time_frame
    }
    save_strategy()  # Call the save_strategy function with the save_strategy_data

    try:
        df = load_historical_data(currency_pair, time_frame, 5000)
        globals_dict = {"df": df}
        exec(strategy_code, globals_dict)

        backtest_results = globals_dict.get("backtestResults", "")
        result_dict = {"backtestResults": backtest_results}

        return jsonify(result_dict)
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}, 500
if __name__ == "__main__":
    app.run()
