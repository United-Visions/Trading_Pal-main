
import json
import oandapyV20
from oandapyV20 import API
import oandapyV20.endpoints.instruments as instruments
import csv
import time
import configparser

# Read keys from config.ini
config = configparser.ConfigParser()
config.read('config.ini')


# Set the base URL for the OANDA API
BASE_URL = "https://api-fxpractice.oanda.com"
ACCOUNT_ID  = "101-001-25836141-002"

# The headers for the HTTP requests
OANDA_API_KEY = config.get('API_KEYS', 'OANDA_API_KEY')
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OANDA_API_KEY}",
    "Connection": "keep-alive"
}
api = API(access_token=OANDA_API_KEY, environment="practice")

while True:
    with open("order_book.csv", "a") as csvfile:
        fieldnames = ["time", "price", "longCountPercent", "shortCountPercent"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        r = instruments.InstrumentsOrderBook(instrument="GBP_USD")
        rv = api.request(r)
        data = rv["orderBook"]
        for bucket in data["buckets"]:
            writer.writerow({"time": data["time"], "price": bucket["price"], "longCountPercent": bucket["longCountPercent"], "shortCountPercent": bucket["shortCountPercent"]})
    time.sleep(60)


    import csv
import json
from oandapyV20 import API
from oandapyV20.endpoints.instruments import InstrumentsPositionBook

client = API(access_token='33a9e22e79a6afe67da0e568b0cca830-cf5e494dfe461d8704057859e229b74e')

r = InstrumentsPositionBook(instrument="GBP_USD")
client.request(r)
position_book = r.response

with open('positions_book.csv', 'w') as f:
    writer = csv.writer(f)
    # Write header row
    writer.writerow(['time', 'price', 'longCountPercent', 'shortCountPercent'])
    # Write data rows
    for bucket in position_book['positionBook']['buckets']:
        writer.writerow([
            position_book['positionBook']['time'],
            bucket['price'],
            bucket['longCountPercent'],
            bucket['shortCountPercent']
        ])



    import pandas as pd
import os
import time
from oandapyV20 import API
from oandapyV20.exceptions import V20Error
from oandapyV20.endpoints.pricing import PricingStream
from oandapyV20.endpoints.instruments import InstrumentsCandles

# Set the OANDA API key
OANDA_API_KEY = "33a9e22e79a6afe67da0e568b0cca830-cf5e494dfe461d8704057859e229b74e"
api = API(access_token=OANDA_API_KEY)

ACCOUNT_ID = "101-001-25836141-002"
INSTRUMENTS = [ "GBP_USD"]  # Add more forex pairs as per your requirements
GRANULARITIES = ["H4", "D"]

# Create directory if not exists
directory = "streaming_data"
if not os.path.exists(directory):
    os.makedirs(directory)

def stream_data(account_id, instruments):
    try:
        r = PricingStream(accountID=account_id, params={"instruments": ",".join(instruments)})
        for R in api.request(r):
            for instrument in instruments:
                if R['type'] == 'PRICE' and R['instrument'] == instrument:
                    process_data(R, instrument)
    except V20Error as e:
        print(f"Error: {e}")

def process_data(data, instrument):
    for granularity in GRANULARITIES:
        r = InstrumentsCandles(instrument=instrument, params={"granularity": granularity, "count": 1})
        api.request(r)
        
        for candle in r.response["candles"]:
            # extract the data you need
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
            save_to_csv(record, instrument, granularity)

def save_to_csv(data, instrument, granularity):
    filename = os.path.join(directory, f"{instrument}_{granularity}.csv")
    df = pd.DataFrame([data])
    df.to_csv(filename, mode='a', index=False)  # mode='a' to append data to existing file

if __name__ == "__main__":
    stream_data(ACCOUNT_ID, INSTRUMENTS)
    