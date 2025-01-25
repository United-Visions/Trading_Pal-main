from flask import Blueprint, request, jsonify
from models import db, Strategy, BacktestResult
import pandas as pd
from datetime import datetime
import traceback
import json
from oandapyV20.exceptions import V20Error
from oandapyV20.endpoints.instruments import InstrumentsCandles
from oandapyV20 import API
import configparser

trading_bp = Blueprint('trading', __name__)

# Initialize OANDA API
config = configparser.ConfigParser()
config.read('config.ini')
api = API(access_token=config.get('API_KEYS', 'OANDA_API_KEY'))

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

@trading_bp.route('/api/v1/strategies', methods=['GET'])
def get_strategies():
    try:
        strategies = Strategy.query.all()
        return jsonify([{
            'id': s.id,
            'name': s.name,
            'description': s.description,
            'currency_pair': s.currency_pair,
            'time_frame': s.time_frame,
            'user_id': s.user_id,
            'algo_code': s.algo_code
        } for s in strategies])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@trading_bp.route('/api/v1/strategy/<int:strategy_id>', methods=['GET'])
def get_strategy(strategy_id):
    try:
        strategy = Strategy.query.get_or_404(strategy_id)
        return jsonify({
            'id': strategy.id,
            'name': strategy.name,
            'description': strategy.description,
            'algo_code': strategy.algo_code,
            'currency_pair': strategy.currency_pair,
            'time_frame': strategy.time_frame,
            'user_id': strategy.user_id
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@trading_bp.route('/api/v1/strategy', methods=['POST'])
def create_strategy():
    try:
        data = request.get_json()
        strategy = Strategy(
            name=data['name'],
            description=data.get('description', ''),
            algo_code=data['algo_code'],
            currency_pair=data['currency_pair'],
            time_frame=data['time_frame'],
            user_id=data['user_id']
        )
        db.session.add(strategy)
        db.session.commit()
        return jsonify({
            'message': 'Strategy created successfully',
            'strategy_id': strategy.id
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@trading_bp.route('/api/v1/strategy/<int:strategy_id>', methods=['PUT', 'DELETE'])
def manage_strategy(strategy_id):
    try:
        strategy = Strategy.query.get_or_404(strategy_id)
        
        if request.method == 'DELETE':
            db.session.delete(strategy)
            db.session.commit()
            return jsonify({'message': 'Strategy deleted successfully'})
            
        data = request.get_json()
        strategy.name = data.get('name', strategy.name)
        strategy.description = data.get('description', strategy.description)
        strategy.algo_code = data.get('algo_code', strategy.algo_code)
        strategy.currency_pair = data.get('currency_pair', strategy.currency_pair)
        strategy.time_frame = data.get('time_frame', strategy.time_frame)
        
        db.session.commit()
        return jsonify({'message': 'Strategy updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

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
