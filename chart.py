from flask import Flask, render_template, jsonify
import pandas as pd
try:
    import pandas_ta as ta
except ImportError:
    print("pandas_ta not found. Installing...")
    import subprocess
    subprocess.check_call(["pip", "install", "pandas_ta"])
import numpy as np
import websockets
import asyncio
import json
import oandapyV20
import oandapyV20.endpoints.instruments as instruments
from datetime import datetime, timedelta
import pytz
import os
import threading

app = Flask(__name__, template_folder=os.path.abspath('templates'))

class EnhancedDataManager:
    def __init__(self):
        self.data = {}
        self.timeframes = ["M1", "M5", "M15", "H1"]
        self.websocket_clients = set()
        try:
            self.oanda_api = oandapyV20.API(access_token=os.getenv('OANDA_API_KEY', 'your-api-key'))
        except Exception as e:
            print(f"Failed to initialize OANDA API: {e}")
            self.oanda_api = None
        
    async def initialize_data(self, instrument="EUR_USD"):
        end = datetime.now(pytz.UTC)
        start = end - timedelta(days=30)  # Get last 30 days
        
        for tf in self.timeframes:
            self.data[tf] = await self.fetch_historical_data(instrument, tf, start, end)
            self.calculate_advanced_indicators(tf)

    async def fetch_historical_data(self, instrument, granularity, start, end):
        params = {
            "granularity": granularity,
            "from": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "to": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "price": "M"
        }
        
        try:
            r = instruments.InstrumentsCandles(instrument=instrument, params=params)
            await self.oanda_api.request(r)
            
            df = pd.DataFrame([{
                'timestamp': pd.to_datetime(c['time']),
                'open': float(c['mid']['o']),
                'high': float(c['mid']['h']),
                'low': float(c['mid']['l']),
                'close': float(c['mid']['c']),
                'volume': int(c['volume'])
            } for c in r.response['candles'] if c['complete']])
            
            return df.set_index('timestamp')
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            return pd.DataFrame()

    def calculate_advanced_indicators(self, timeframe):
        df = self.data[timeframe]
        if len(df) == 0:
            return

        try:
            # Calculate basic indicators
            df['SMA_20'] = ta.sma(df['close'], length=20)
            df['SMA_50'] = ta.sma(df['close'], length=50)
            df['RSI_14'] = ta.rsi(df['close'], length=14)
            
            # Calculate Bollinger Bands
            bollinger = ta.bbands(df['close'], length=20)
            df = pd.concat([df, bollinger], axis=1)
            
            # Calculate MACD
            macd = ta.macd(df['close'])
            df = pd.concat([df, macd], axis=1)
            
            # Calculate Volume Weighted Average Price
            if 'volume' in df.columns:
                df['VWAP'] = ta.vwap(df['high'], df['low'], df['close'], df['volume'])
                
        except Exception as e:
            print(f"Error calculating indicators for {timeframe}: {e}")
            # Initialize empty indicators if calculation fails
            df['SMA_20'] = pd.NA
            df['SMA_50'] = pd.NA
            df['RSI_14'] = pd.NA
        
        self.data[timeframe] = df

    async def stream_data(self, websocket, path):
        self.websocket_clients.add(websocket)
        try:
            while True:
                for tf in self.timeframes:
                    if len(self.data[tf]) > 0:
                        latest_data = self.data[tf].tail(100)
                        await websocket.send(json.dumps({
                            'timeframe': tf,
                            'data': {
                                'candles': latest_data.reset_index().to_dict('records'),
                                'indicators': {
                                    col: latest_data[col].tolist() 
                                    for col in latest_data.columns 
                                    if col not in ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                                }
                            }
                        }))
                await asyncio.sleep(1)
        finally:
            self.websocket_clients.remove(websocket)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/initial_data/<timeframe>')
def get_initial_data(timeframe):
    if timeframe not in data_manager.timeframes:
        return jsonify({'error': 'Invalid timeframe'}), 400
    
    df = data_manager.data[timeframe].tail(100)
    return jsonify({
        'candles': df.reset_index().to_dict('records'),
        'indicators': {
            col: df[col].tolist() 
            for col in df.columns 
            if col not in ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        }
    })

if __name__ == '__main__':
    data_manager = EnhancedDataManager()
    
    # Run WebSocket server in a separate thread
    async def start_websocket():
        async with websockets.serve(data_manager.stream_data, "localhost", 8765):
            await asyncio.Future()  # run forever
    
    # Initialize data and start WebSocket server
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(data_manager.initialize_data())
    
    websocket_thread = threading.Thread(
        target=lambda: asyncio.new_event_loop().run_until_complete(start_websocket())
    )
    websocket_thread.daemon = True
    websocket_thread.start()
    
    app.run(debug=True)
