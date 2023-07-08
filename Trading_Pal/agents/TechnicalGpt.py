import os
import pandas as pd
import openai
from oandapyV20 import API
from oandapyV20.exceptions import V20Error
from oandapyV20.endpoints.instruments import InstrumentsCandles
from indicators import calculate_rsi, calculate_macd, calculate_bollinger_bands, calculate_atr, calculate_adx, calculate_obv
import traceback
import requests

OANDA_API_KEY = "ba62e5ad63f2a8759ee31761ba01e196-fb6f30ba3b58d44a94152fa5cd4f3ce2"
OPENAI_API_KEY = "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"
api = API(access_token=OANDA_API_KEY)
openai.api_key = OPENAI_API_KEY
INDICATORS_DIRECTORY = "indicators"
os.makedirs(INDICATORS_DIRECTORY, exist_ok=True)

class TechnicalsAgent:
    def __init__(self, instrument, granularity, count):
        self.instrument = instrument
        self.granularity = granularity
        self.count = count

    def load_historical_data(self):
        params = {"granularity": self.granularity, "count": self.count}
        r = InstrumentsCandles(instrument=self.instrument, params=params)
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
                "instrument": self.instrument,
                "granularity": self.granularity
            }
            records.append(record)

        df = pd.DataFrame(records)
        df["time"] = pd.to_datetime(df["time"])
        return df

    def calculate_indicators(self, df):
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
        return df


    def run(self):
        df = self.load_historical_data()
        df = self.calculate_indicators(df)
        
               # Get the last row of indicators
        latest_indicators = df.iloc[-1]
        indicator_values = latest_indicators[["RSI", "MACD", "Signal_Line", "Histogram", "BollingerBands_middle", "BollingerBands_std", "ATR", "ADX", "OBV"]]

        # Prepare a message to send to GPT
        gpt_message = "The latest technical indicators for the instrument {} are:\n".format(self.instrument)
        for indicator, value in indicator_values.items():
            gpt_message += "- {}: {}\n".format(indicator, value)


        # Send the message to GPT
        gpt_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "system", "content": "You are a technical gpt an AI model trained to understand financial markets and technical analysis. Provide a detailed analysis and possible prediction based on the following technical indicators."},
                {"role": "user", "content": gpt_message}
            ]
        )

        # Extract GPT's message
        gpt_response_message = gpt_response.choices[0].message['content']

        print(f"GPT's market analysis: {gpt_response_message}")
        return df, gpt_response_message
if __name__ == "__main__":
    agent = TechnicalsAgent("USD_CAD", "S30", 5000)
    df, gpt_response_message = agent.run()
