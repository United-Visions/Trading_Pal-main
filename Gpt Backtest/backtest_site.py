from flask import Flask, request, jsonify, render_template
import pandas as pd
import os
import openai
from oandapyV20 import API
from oandapyV20.exceptions import V20Error
from oandapyV20.endpoints.instruments import InstrumentsCandles
from indicators import calculate_rsi, calculate_macd, calculate_bollinger_bands, calculate_atr, calculate_adx, calculate_obv
import traceback
import requests

app = Flask(__name__)
OANDA_API_KEY = ""
OPENAI_API_KEY = "sk-"
api = API(access_token=OANDA_API_KEY)
openai.api_key = OPENAI_API_KEY
INDICATORS_DIRECTORY = "indicators"
os.makedirs(INDICATORS_DIRECTORY, exist_ok=True)
database = []


@app.route('/save_strategy', methods=['POST'])
def save_strategy():
    data = request.get_json()
    print(f"[save_strategy] Received data to save strategy: {data}")
    database.append(data)
    print("[save_strategy] Strategy saved successfully.")
    return jsonify(success=True)


@app.route('/get_strategies', methods=['GET'])
def get_strategies():
    print("[get_strategies] Fetching all strategies...")
    return jsonify(database)


@app.route('/search_strategies', methods=['POST'])
def search_strategies():
    search = request.get_json().get('search')
    print(f"[search_strategies] Searching strategies with term: {search}")
    result = [s for s in database if search in s['strategyName'] or search in s['authorName']]
    print(f"[search_strategies] Found {len(result)} strategies matching search term.")
    return jsonify(result)


def load_historical_data(instrument, granularity, count):
    print("[load_historical_data] Loading historical data...")
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
    print("[load_historical_data] Historical data loaded.")
    print("[load_historical_data] Calculating indicators...")
    df = calculate_indicators(df)
    if df is None:
        print("[load_historical_data] Failed to calculate indicators.")
    else:
        print(f"[load_historical_data] DataFrame size: {df.shape}")
    save_to_csv(df, instrument, granularity)
    save_indicators_to_csv(df, instrument)
    print("[load_historical_data] Historical data loaded and processed.")
    return df


def save_to_csv(df, instrument, granularity):
    print(f"[save_to_csv] Saving historical data to CSV for {instrument} at {granularity} granularity.")
    filename = f"{INDICATORS_DIRECTORY}/{instrument}_{granularity}.csv"
    df.to_csv(filename, index=False)
    print("[save_to_csv] Data saved to CSV.")


def calculate_indicators(df):
    print("[calculate_indicators] Calculating indicators...")
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

    print("[calculate_indicators] Indicators calculated.")
    return df


def save_indicators_to_csv(df, instrument):
    print("[save_indicators_to_csv] Saving indicators to CSV...")
    indicators = ["RSI", "MACD", "Signal_Line", "Histogram", "BollingerBands_middle", "BollingerBands_std", "ATR",
                  "ADX", "OBV"]
    for indicator in indicators:
        indicator_df = df[["time", indicator]]
        filename = f"{INDICATORS_DIRECTORY}/{instrument}_{indicator}.csv"
        indicator_df.to_csv(filename, index=False)
    print("[save_indicators_to_csv] Indicators saved to CSV.")


@app.route("/")
def index():
    return render_template("backtest.html")


@app.route("/backtest_strategy", methods=["POST"])
def backtest_strategy():
    data = request.get_json()
    print(f"[backtest_strategy] Received backtest request: {data}")
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
    print(f"[backtest_strategy] Saving strategy before backtesting: {save_strategy_data}")
    database.append(save_strategy_data)  # Save strategy to the database
    print("[backtest_strategy] Strategy saved.")

    try:
        df = load_historical_data(currency_pair, time_frame, 5000)
        globals_dict = {"df": df}
        exec(strategy_code, globals_dict)

        backtest_results = globals_dict.get("backtestResults", {})
        backtest_results_str = "\n".join(f"{k}: {v}" for k, v in backtest_results.items())
        result_dict = {"backtestResults": backtest_results_str, "error": None}

        # Prepare the message to the GPT model
        gpt_message = f"Here are the backtest results for a trading strategy named '{strategy_name}' by '{author_name}' for the currency pair '{currency_pair}' on the '{time_frame}' timeframe. The strategy code was: \n\n{strategy_code}\n\nThe backtest results are:\n{backtest_results_str}"
        print(f"[backtest_strategy] Preparing to send the following message to GPT: {gpt_message}")

        # Send the message to the GPT model
        gpt_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "system", "content": "You are a backtest_gpt that generates responses based on trading strategy backtest results. please include a full overview and summary of the author behind the strategy, and the parameters used for this particular strategy include the name of the strategy an include the functions of the strategy code"},
                {"role": "user", "content": gpt_message}
            ]
        )
        gpt_response_message = gpt_response.choices[0].message['content']
        print(f"[backtest_strategy] Received GPT response: {gpt_response_message}")

        result_dict['gptResponse'] = gpt_response_message
        print(f"[backtest_strategy] Backtest completed. Results: {result_dict}")

        return jsonify(result_dict)
    except Exception as e:
        traceback_string = traceback.format_exc()
        print(traceback_string)
        return jsonify({"error": traceback_string, "backtestResults": None, "gptResponse": None}), 500

# ...

if __name__ == "__main__":
    print("Starting server...")
    app.run(port=5001, debug=True, use_reloader=True)
 