import json
import websocket
import threading
import time
import requests
from datetime import datetime, timedelta
import logging
from collections import deque
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('market_feed.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MarketDataServer:
    def __init__(self, api_key, pairs=None):
        self.api_key = api_key
        self.pairs = pairs or ['EUR-USD']  # Default to EUR-USD if no pairs specified
        self.ws = None
        self.is_running = False
        self.data_buffer = {}  # Buffer for each pair
        self.buffer_size = 1000  # Keep last 1000 data points per pair
        self.last_historical_update = {}
        self.historical_update_interval = 3600  # Update historical data every hour
        self.ws_lock = threading.Lock()  # Lock for WebSocket operations
        self.reconnect_delay = 5  # Initial reconnect delay
        self.max_reconnect_delay = 60  # Maximum reconnect delay
        
        # Initialize buffers for each pair
        for pair in self.pairs:
            self.data_buffer[pair] = deque(maxlen=self.buffer_size)
            self.last_historical_update[pair] = 0
            
        # Ensure data directory exists
        os.makedirs('feeds/forex', exist_ok=True)

    def fetch_historical_data(self, pair):
        """Fetch historical data from Polygon REST API"""
        try:
            # Get data for the last 24 hours
            end = datetime.now()
            start = end - timedelta(days=1)
            
            url = f"https://api.polygon.io/v2/aggs/ticker/C:{pair}/range/1/minute/{start.strftime('%Y-%m-%d')}/{end.strftime('%Y-%m-%d')}?adjusted=true&sort=asc&limit=50000&apiKey={self.api_key}"
            
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data['resultsCount'] > 0:
                    formatted_data = []
                    for result in data['results']:
                        entry = {
                            'type': 'per-minute',
                            'pair': pair.replace('-', '/'),
                            'HH': result['h'],
                            'HL': result['l'],
                            'LH': result['h'],
                            'LL': result['l'],
                            'timestamp': result['t']
                        }
                        formatted_data.append(entry)
                        self.data_buffer[pair].append(entry)
                    
                    # Save to file
                    self.save_to_json(formatted_data, pair)
                    logger.info(f"Historical data fetched for {pair}: {len(formatted_data)} entries")
                    
                    self.last_historical_update[pair] = time.time()
                    return True
            
            logger.error(f"Failed to fetch historical data for {pair}: {response.status_code}")
            return False
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {pair}: {str(e)}")
            return False

    def save_to_json(self, data, pair):
        """Save data to JSON file with proper formatting"""
        filename = f'feeds/forex/{pair}.json'
        try:
            # If file exists, read existing data
            existing_data = []
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    for line in f:
                        try:
                            existing_data.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue

            # Combine existing data with new data and sort by timestamp
            all_data = existing_data + (data if isinstance(data, list) else [data])
            all_data.sort(key=lambda x: x['timestamp'])
            
            # Keep only the most recent data points
            if len(all_data) > self.buffer_size:
                all_data = all_data[-self.buffer_size:]
            
            # Write back to file
            with open(filename, 'w') as f:
                for entry in all_data:
                    json.dump(entry, f)
                    f.write('\n')
                    
        except Exception as e:
            logger.error(f"Error saving data to {filename}: {str(e)}")

    def on_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            if not isinstance(data, list) or len(data) == 0:
                return
                
            for entry in data:
                output_data = None
                
                if entry.get('ev') == 'CA':  # Per-minute data
                    output_data = {
                        'type': 'per-minute',
                        'pair': entry['pair'],
                        'HH': entry['h'],
                        'HL': entry['l'],
                        'LH': entry['h'],
                        'LL': entry['l'],
                        'timestamp': entry['s']
                    }
                elif entry.get('ev') == 'CAS':  # Per-second data
                    output_data = {
                        'type': 'per-second',
                        'pair': entry['pair'],
                        'HH': entry['h'],
                        'HL': entry['l'],
                        'LH': entry['h'],
                        'LL': entry['l'],
                        'timestamp': entry['s']
                    }
                elif entry.get('ev') == 'C':  # Quote data
                    output_data = {
                        'type': 'quote',
                        'pair': entry['p'],
                        'bid': entry['b'],
                        'ask': entry['a'],
                        'timestamp': entry['t']
                    }
                
                if output_data:
                    pair = output_data['pair'].replace('/', '-')
                    if pair in self.pairs:
                        self.data_buffer[pair].append(output_data)
                        self.save_to_json(output_data, pair)
                        
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")

    def on_error(self, ws, error):
        """Handle WebSocket errors"""
        logger.error(f"WebSocket error: {str(error)}")
        self.schedule_reconnect()

    def on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket connection close"""
        logger.info(f"WebSocket connection closed: {close_status_code} - {close_msg}")
        self.schedule_reconnect()

    def on_open(self, ws):
        """Handle WebSocket connection open"""
        try:
            logger.info("WebSocket connected")
            
            # Reset reconnect delay on successful connection
            self.reconnect_delay = 5
            
            # Authenticate
            auth_data = {"action":"auth","params": self.api_key}
            ws.send(json.dumps(auth_data))
            logger.info("Authentication sent")
            
            # Subscribe to data streams for each pair
            subscriptions = []
            for pair in self.pairs:
                subscriptions.extend([
                    f"CA.C:{pair}",  # Per-minute aggregates
                    f"CAS.C:{pair}", # Per-second aggregates
                    f"C.C:{pair}"    # Quotes
                ])
            
            subscribe_data = {"action":"subscribe", "params":",".join(subscriptions)}
            ws.send(json.dumps(subscribe_data))
            logger.info(f"Subscribed to {len(self.pairs)} pairs")
            
        except Exception as e:
            logger.error(f"Error in on_open: {str(e)}")
            self.schedule_reconnect()

    def schedule_reconnect(self):
        """Schedule a reconnection attempt with exponential backoff"""
        if self.is_running:
            logger.info(f"Scheduling reconnect in {self.reconnect_delay} seconds")
            threading.Timer(self.reconnect_delay, self.connect_websocket).start()
            # Increase delay for next attempt
            self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)

    def connect_websocket(self):
        """Establish WebSocket connection with proper error handling"""
        if not self.is_running:
            return
            
        with self.ws_lock:
            try:
                if self.ws:
                    self.ws.close()
                    self.ws = None
                
                self.ws = websocket.WebSocketApp(
                    "wss://socket.polygon.io/forex",
                    on_open=self.on_open,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close
                )
                
                # Start WebSocket connection in a new thread
                ws_thread = threading.Thread(
                    target=lambda: self.ws.run_forever(
                        ping_interval=30,
                        ping_timeout=10,
                        ping_payload='{"action":"ping"}'
                    )
                )
                ws_thread.daemon = True
                ws_thread.start()
                
            except Exception as e:
                logger.error(f"Error connecting to WebSocket: {str(e)}")
                self.schedule_reconnect()

    def start(self):
        """Start the market data server"""
        if self.is_running:
            return
            
        self.is_running = True
        
        # Start historical data update thread
        threading.Thread(target=self._historical_update_loop, daemon=True).start()
        
        # Initial historical data fetch
        for pair in self.pairs:
            self.fetch_historical_data(pair)
        
        # Start WebSocket connection
        self.connect_websocket()

    def stop(self):
        """Stop the market data server"""
        self.is_running = False
        with self.ws_lock:
            if self.ws:
                self.ws.close()
                self.ws = None

    def _historical_update_loop(self):
        """Background thread to periodically update historical data"""
        while self.is_running:
            current_time = time.time()
            for pair in self.pairs:
                # Update if more than update_interval has passed
                if current_time - self.last_historical_update.get(pair, 0) > self.historical_update_interval:
                    self.fetch_historical_data(pair)
            time.sleep(60)  # Check every minute

    def get_data(self, pair, limit=None):
        """Get the latest data for a pair"""
        pair = pair.replace('/', '-')
        if pair not in self.data_buffer:
            return []
            
        data = list(self.data_buffer[pair])
        if limit:
            data = data[-limit:]
        return data

if __name__ == "__main__":
    # Load API key from config
    import configparser
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_key = config.get('API_KEYS', 'POLYGON_API_KEY')
    
    # Enable debug logging for websocket-client
    websocket.enableTrace(True)
    
    # Start server with EUR/USD pair
    server = MarketDataServer(api_key, pairs=['EUR-USD'])
    try:
        server.start()
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
