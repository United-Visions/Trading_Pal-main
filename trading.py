from flask import Blueprint, request, jsonify
from oandapyV20.exceptions import V20Error
from oandapyV20.endpoints.instruments import InstrumentsCandles
from oandapyV20 import API
import configparser
import pandas as pd
from flask_login import login_required

trading_bp = Blueprint('trading', __name__)

# Initialize OANDA API
config = configparser.ConfigParser()
config.read('config.ini')
api = API(access_token=config.get('API_KEYS', 'OANDA_API_KEY'))

# Keep only these utility functions:
def standardize_currency_pair(pair):
    pair = pair.strip().upper().replace(" ", "")
    for sep in ['/', '_', '-', '.']:
        if sep in pair:
            parts = pair.split(sep)
            if len(parts) == 2:
                return f"{parts[0]}_{parts[1]}"
    if len(pair) == 6:
        return f"{pair[:3]}_{pair[3:]}"
    return None

def validate_timeframe(timeframe):
    timeframe_map = {
        '1h': 'H1', 'h1': 'H1', 'hour': 'H1', '1hour': 'H1',
        '4h': 'H4', 'h4': 'H4',
        '1d': 'D', 'd1': 'D', 'day': 'D', '1day': 'D',
        '1m': 'M1', 'm1': 'M1', 'minute': 'M1',
        '30m': 'M30', 'm30': 'M30'
    }
    
    timeframe = timeframe.lower()
    return timeframe_map.get(timeframe)

def load_historical_data(instrument, granularity, count):
    std_instrument = standardize_currency_pair(instrument)
    if not std_instrument:
        raise ValueError(f"Invalid currency pair format: {instrument}")
    
    std_granularity = validate_timeframe(granularity)
    if not std_granularity:
        raise ValueError(f"Invalid timeframe format: {granularity}")
    
    params = {"granularity": std_granularity, "count": count}
    
    r = InstrumentsCandles(instrument=std_instrument, params=params)
    
    try:
        api.request(r)
    except V20Error as e:
        raise ValueError(f"Failed to fetch data: {str(e)}")

    records = []
    for candle in r.response["candles"]:
        record = {
            "time": candle["time"],
            "volume": candle["volume"],
            "open": float(candle["mid"]["o"]),
            "high": float(candle["mid"]["h"]),
            "low": float(candle["mid"]["l"]),
            "close": float(candle["mid"]["c"]),
            "instrument": std_instrument,
            "granularity": std_granularity
        }
        records.append(record)

    df = pd.DataFrame(records)
    df["time"] = pd.to_datetime(df["time"])
    return df

@trading_bp.route('/api/v1/candlestick_data', methods=['GET'])
def get_candlestick_data():
    try:
        instrument = request.args.get('instrument')
        granularity = request.args.get('granularity')
        count = request.args.get('count', 100)
        
        df = load_historical_data(instrument, granularity, count)
        return jsonify(df.to_dict('records'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
