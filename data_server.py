import os
import logging
import websocket
import json
import time
from datetime import datetime
from flask import Flask, jsonify
import feedgenerator
import configparser
import requests
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('polygon_feed.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('polygon_feed')

# Load config
config = configparser.ConfigParser()
config.read('config.ini')
POLYGON_API_KEY = config.get('API_KEYS', 'POLYGON_API_KEY')

# Initialize Flask app
app = Flask(__name__)

# Create feeds directory if it doesn't exist
FEEDS_DIR = Path('feeds')
FEEDS_DIR.mkdir(exist_ok=True)

class PolygonFeedHandler:
    def __init__(self):
        self.ws = None
        self.pairs = {
            'forex': ['EUR-USD'],
            'crypto': ['BTC-USD']
        }
        self.feeds = {}
        self.retry_count = 0
        self.max_retries = 5
        self.retry_delay = 5
        self.initialize_feed_files()
        
    def initialize_feed_files(self):
        """Initialize JSON files for each pair"""
        try:
            for market, pairs in self.pairs.items():
                market_dir = FEEDS_DIR / market
                market_dir.mkdir(exist_ok=True)
                
                for pair in pairs:
                    feed_file = market_dir / f"{pair}.json"
                    if not feed_file.exists() or feed_file.stat().st_size == 0:
                        initial_data = []
                        feed_file.write_text(json.dumps(initial_data))
                    self.feeds[f"{market}_{pair}"] = []
                    
                    # Load existing data
                    try:
                        with feed_file.open('r') as f:
                            self.feeds[f"{market}_{pair}"] = json.loads(f.read())
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON in {feed_file}, initializing empty")
                        self.feeds[f"{market}_{pair}"] = []
                        feed_file.write_text(json.dumps([]))
                        
        except Exception as e:
            logger.error(f"Error initializing feed files: {e}")
            raise

    def save_feed_data(self, market, pair, data):
        """Save feed data to JSON file with proper error handling"""
        feed_key = f"{market}_{pair}"
        feed_file = FEEDS_DIR / market / f"{pair}.json"
        
        try:
            # Update memory cache
            if feed_key not in self.feeds:
                self.feeds[feed_key] = []
                
            self.feeds[feed_key].append(data)
            
            # Trim to last 1000 points
            if len(self.feeds[feed_key]) > 1000:
                self.feeds[feed_key] = self.feeds[feed_key][-1000:]
            
            # Save to file
            with feed_file.open('w') as f:
                json.dump(self.feeds[feed_key], f, indent=2)
                
            logger.debug(f"Saved data for {feed_key}: {data}")
            
        except Exception as e:
            logger.error(f"Error saving feed data for {feed_key}: {e}")
            
    def connect_websocket(self):
        """Initialize WebSocket connection with retry logic"""
        while self.retry_count < self.max_retries:
            try:
                ws_url = "wss://socket.polygon.io/forex"
                
                def on_message(ws, message):
                    try:
                        data = json.loads(message)
                        logger.debug(f"Received message: {data}")
                        
                        if isinstance(data, list):
                            for event in data:
                                self.process_event(event)
                        else:
                            self.process_event(data)
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON message: {e}")
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")

                def on_error(ws, error):
                    logger.error(f"WebSocket error: {error}")
                    self.retry_count += 1
                    if self.retry_count >= self.max_retries:
                        logger.error("Max retries reached, stopping reconnection attempts")
                    else:
                        time.sleep(self.retry_delay)

                def on_close(ws, close_status_code, close_msg):
                    logger.info(f"WebSocket closed: {close_status_code} - {close_msg}")
                    if close_status_code == 1008:  # Policy violation
                        logger.error("Authentication failed")
                        self.retry_count = self.max_retries  # Stop retrying
                    elif self.retry_count < self.max_retries:
                        time.sleep(self.retry_delay)
                        self.connect_websocket()

                def on_open(ws):
                    logger.info("WebSocket connection established")
                    # Reset retry count on successful connection
                    self.retry_count = 0
                    
                    # Authenticate
                    auth_data = {
                        "action": "auth",
                        "params": POLYGON_API_KEY
                    }
                    ws.send(json.dumps(auth_data))
                    
                    # Subscribe after brief delay to ensure auth is processed
                    time.sleep(1)
                    
                    # Subscribe to feeds
                    for market, pairs in self.pairs.items():
                        prefix = 'C' if market == 'forex' else 'XT'
                        for pair in pairs:
                            sub_data = {
                                "action": "subscribe",
                                "params": f"{prefix}.{pair}"
                            }
                            ws.send(json.dumps(sub_data))
                            logger.info(f"Subscribed to {market} {pair}")

                self.ws = websocket.WebSocketApp(
                    ws_url,
                    on_message=on_message,
                    on_error=on_error,
                    on_close=on_close,
                    on_open=on_open
                )
                
                self.ws.run_forever()
                
            except Exception as e:
                logger.error(f"Connection error: {e}")
                self.retry_count += 1
                if self.retry_count < self.max_retries:
                    time.sleep(self.retry_delay)
                else:
                    logger.error("Max retries reached, stopping connection attempts")
                    break

    def process_event(self, event):
        """Process incoming WebSocket events"""
        ev_type = event.get('ev')
        if ev_type == 'C':  # Forex quote
            market = 'forex'
            pair = event['p'].replace('/', '-')
        elif ev_type == 'XT':  # Crypto trade
            market = 'crypto'
            pair = event['pair']
        else:
            return

        data = {
            'timestamp': datetime.fromtimestamp(event['t']/1000).isoformat(),
            'price': float(event['p']) if ev_type == 'XT' else (float(event['a']) + float(event['b']))/2,
            'volume': float(event.get('s', 1))
        }
        
        self.save_feed_data(market, pair, data)
        logger.debug(f"Processed {market} {pair} event")

feed_handler = PolygonFeedHandler()

# Flask routes
@app.route('/api/feed/<market>/<pair>', methods=['GET'])
def get_market_feed(market, pair):
    """Get market data feed for specific pair"""
    try:
        feed_key = f"{market}_{pair}"
        if feed_key not in feed_handler.feeds:
            return jsonify({"error": "Invalid market or pair"}), 404
            
        return jsonify(feed_handler.feeds[feed_key])
    except Exception as e:
        logger.error(f"Error serving feed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/rss/<market>/<pair>', methods=['GET'])
def get_rss_feed(market, pair):
    """Get RSS feed for specific market pair"""
    try:
        feed_key = f"{market}_{pair}"
        if feed_key not in feed_handler.feeds:
            return "Invalid market or pair", 404
            
        fg = feedgenerator.Rss201rev2Feed(
            title=f'{market.upper()} - {pair} Feed',
            link=f'http://localhost:4000/rss/{market}/{pair}',
            description=f'Live {market} data feed for {pair}'
        )
        
        for item in feed_handler.feeds[feed_key][-100:]:
            fg.add_item(
                title=f'{pair}: {item["price"]}',
                link=f'http://localhost:4000/rss/{market}/{pair}',
                description=json.dumps(item),
                pubdate=datetime.fromisoformat(item['timestamp'])
            )
        
        return fg.writeString('utf-8'), 200, {'Content-Type': 'application/rss+xml'}
    except Exception as e:
        logger.error(f"Error serving RSS: {e}")
        return str(e), 500

if __name__ == '__main__':
    # Start WebSocket connection in background
    import threading
    ws_thread = threading.Thread(target=feed_handler.connect_websocket)
    ws_thread.daemon = True
    ws_thread.start()
    
    app.run(debug=True, port=4000)
