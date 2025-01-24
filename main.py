from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai
import configparser
import traceback
import os
import json
import pandas as pd
from models import db, User, Conversation, Strategy, BacktestResult, Review, Comment
from datetime import datetime
import requests
from oandapyV20 import API
from oandapyV20.exceptions import V20Error
from oandapyV20.endpoints.instruments import InstrumentsCandles
from indicators import calculate_rsi, calculate_macd, calculate_bollinger_bands, calculate_atr, calculate_adx, calculate_obv
from words import endpoint_phrases, trading_keywords
from tools import ToolRegistry

config = configparser.ConfigParser()
config.read('config.ini')

# Initialize app configurations
app = Flask(__name__)
CORS(app, supports_credentials=True)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tradingpal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# API and model configurations
genai.configure(api_key=config.get('API_KEYS', 'GEMINI_API_KEY'))
OANDA_API_KEY = config.get('API_KEYS', 'OANDA_API_KEY')
BASE_URL = "https://api-fxpractice.oanda.com"
ACCOUNT_ID = config.get('API_KEYS', 'OANDA_ACCOUNT_ID', fallback="101-001-25836")
api = API(access_token=OANDA_API_KEY)

# Headers setup
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OANDA_API_KEY}",
    "Accept-Datetime-Format": "RFC3339"
}

database = []  # In-memory storage for strategies before db integration
INDICATORS_DIRECTORY = "indicators_directory"
# Function definitions
def get_account_details():
    """Get account details with enhanced error handling"""
    try:
        print(f"[get_account_details] Requesting account details for {ACCOUNT_ID}")
        url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/summary"  # Changed to summary endpoint
        print(f"[get_account_details] Request URL: {url}")
        
        response = requests.get(url, headers=headers)
        print(f"[get_account_details] Response status: {response.status_code}")
        
        if response.status_code != 200:
            error_msg = f"Failed to get account details. Status: {response.status_code}, Response: {response.text}"
            print(f"[get_account_details] ERROR: {error_msg}")
            return {"error": error_msg}
            
        data = response.json()
        print("[get_account_details] Successfully retrieved account data")
        return data
        
    except requests.exceptions.RequestException as err:
        error_msg = f"Network error getting account details: {str(err)}"
        print(f"[get_account_details] ERROR: {error_msg}")
        return {"error": error_msg}
    except Exception as err:
        error_msg = f"Unexpected error getting account details: {str(err)}"
        print(f"[get_account_details] ERROR: {error_msg}")
        return {"error": error_msg}

def create_order(account_id, order_data):
    try:
        url = f"{BASE_URL}/v3/accounts/{account_id}/orders"
        response = requests.post(url, headers=headers, json=order_data)
        response.raise_for_status()
        order_response = response.json()
        
        message = f"Successfully created order. Response from broker: {order_response}"
        messages = [
            {"role": "user", "content": "create order"},
            {"role": "assistant", "content": message}
        ]
        assistant_response = get_gemini_response(messages)
        return assistant_response, order_response
    except requests.exceptions.HTTPError as err:
        error_message = f"Failed to create order. Error: {err}"
        messages = [
            {"role": "user", "content": "create order"},
            {"role": "assistant", "content": error_message}
        ]
        assistant_response = get_gemini_response(messages)
        raise Exception(assistant_response) from err

def detect_intent(user_message):
    """Detect which endpoint the user is trying to access based on their message"""
    user_message = user_message.lower()
    
    # Check each endpoint's phrases
    for endpoint, phrases in endpoint_phrases.items():
        if any(phrase.lower() in user_message for phrase in phrases):
            return endpoint
            
    return None

def execute_endpoint_action(intent, user_message=None):
    """Execute the appropriate action and get AI response based on the data"""
    try:
        response_data = None
        
        if intent == "get_accounts":
            url = f"{BASE_URL}/v3/accounts"
            response = requests.get(url, headers=headers)
            response_data = response.json()
            
        elif intent == "get_account_details":
            response_data = get_account_details()
            
        elif intent == "create_order":
            return jsonify({"action": "create_order"})
            
        elif intent == "get_candlestick_data":
            instrument = extract_instrument(user_message)
            params = {"count": 100, "granularity": "M1"}
            r = InstrumentsCandles(instrument=instrument, params=params)
            api.request(r)
            response_data = r.response
            
        elif intent == "get_order_book":
            instrument = extract_instrument(user_message)
            url = f"{BASE_URL}/v3/instruments/{instrument}/orderBook"
            response = requests.get(url, headers=headers)
            response_data = response.json()
            
        elif intent == "get_position_book":
            instrument = extract_instrument(user_message)
            url = f"{BASE_URL}/v3/instruments/{instrument}/positionBook"
            response = requests.get(url, headers=headers)
            response_data = response.json()
            
        elif intent == "get_trades":
            url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/trades"
            response = requests.get(url, headers=headers)
            response_data = response.json()
            
        elif intent == "get_positions":
            url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/positions"
            response = requests.get(url, headers=headers)
            response_data = response.json()
            
        elif intent == "close_position":
            instrument = extract_instrument(user_message)
            url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/positions/{instrument}/close"
            response = requests.put(url, headers=headers)
            response_data = response.json()

        if response_data:
            # Format prompt for the AI with both intent and data
            prompt = f"""
            User Intent: {intent}
            User Message: {user_message}
            API Response Data: {json.dumps(response_data, indent=2)}
            
            Please provide a natural language response explaining this data to the user.
            Focus on the most important details and explain any technical terms.
            """
            
            messages = [
                {"role": "system", "content": "You are Trading Pal 1.0, a sophisticated AI trading assistant."},
                {"role": "user", "content": prompt}
            ]
            
            ai_response = get_gemini_response(messages)
            return jsonify({"response": ai_response, "data": response_data})
            
    except Exception as e:
        error_message = f"Failed to execute {intent}: {str(e)}"
        return jsonify({"error": error_message}), 500

def extract_order_details(message: str) -> dict:
    """Extract order details from user message and add smart defaults"""
    message = message.lower()
    
    # Default order structure matching OANDA's expected format
    order_data = {
        "order": {
            "type": "MARKET",
            "instrument": "USD_JPY",  # Will be overwritten if found in message
            "timeInForce": "FOK",
            "positionFill": "DEFAULT",
            "units": "100",  # Default position size
            "trailingStopLossOnFill": {
                "distance": "0.05",  # Default 5 pips trailing stop
                "timeInForce": "GTC"
            }
        }
    }
    
    # Extract currency pair with proper formatting
    pairs_map = {
        "usd/jpy": "USD_JPY",
        "eur/usd": "EUR_USD",
        "gbp/usd": "GBP_USD",
        "usd/chf": "USD_CHF",
        "aud/usd": "AUD_USD",
        "usd/cad": "USD_CAD"
    }
    
    # Find currency pair in message
    for pair_text, pair_code in pairs_map.items():
        if pair_text in message.replace(" ", ""):  # Remove spaces for matching
            order_data["order"]["instrument"] = pair_code
            break
    
    # Determine direction (buy/sell)
    if "buy" in message:
        order_data["order"]["units"] = "100"  # Positive for buy
    elif "sell" in message:
        order_data["order"]["units"] = "-100"  # Negative for sell
    
    # Extract specific units if provided
    import re
    units_match = re.search(r'(\d+)\s*(?:units?|lots?)', message)
    if units_match:
        units = int(units_match.group(1))
        order_data["order"]["units"] = str(units if "sell" not in message else -units)
    
    # Add trailing stop loss by default for protection
    pair = order_data["order"]["instrument"]
    volatility_map = {
        "USD_JPY": "0.200",    # 20 pips for JPY pairs
        "EUR_USD": "0.0020",   # 20 pips for EUR pairs
        "GBP_USD": "0.0025",   # 25 pips for GBP pairs
        "USD_CHF": "0.0020",   # 20 pips for CHF pairs
        "AUD_USD": "0.0015",   # 15 pips for AUD pairs
        "USD_CAD": "0.0020"    # 20 pips for CAD pairs
    }
    
    # Add trailing stop loss
    order_data["order"]["trailingStopLossOnFill"] = {
        "distance": volatility_map.get(pair, "0.0020"),
        "timeInForce": "GTC"
    }
    
    print(f"[extract_order_details] Generated order data: {json.dumps(order_data, indent=2)}")
    return order_data

def get_ai_response(user_message: str, available_data: dict = None) -> str:
    """Get AI response with tool awareness"""
    system_prompt = f"""You are Trading Pal 1.0, a sophisticated AI trading assistant.
    You have access to the following tools:
    
    {tool_registry.get_tool_descriptions()}
    
    When a user asks to place an order:
    1. If only a currency pair is mentioned, create a market order with smart defaults including trailing stop loss
    2. Call the create_order tool with: <tool>create_order|account_id={ACCOUNT_ID}|data=ORDER_DETAILS</tool>
    3. Wait for the order response
    4. Explain to the user:
       - The order details
       - That a trailing stop loss was added for protection
       - How the trailing stop loss works
       - That the position size was set to a conservative default
    
    For other requests requiring tools:
    1. Identify which tool is needed
    2. Call the tool using: <tool>tool_name</tool>
    3. Wait for the tool's response
    4. Provide a natural language response explaining the data
    """
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    
    if available_data:
        messages.append({
            "role": "assistant", 
            "content": f"I have retrieved the following data: {json.dumps(available_data, indent=2)}"
        })
    
    return get_gemini_response(messages)

def extract_instrument(message):
    """Extract instrument name from user message"""
    # Add common currency pairs
    pairs = ["EUR_USD", "USD_JPY", "GBP_USD", "USD_CHF", "AUD_USD", "USD_CAD"]
    for pair in pairs:
        if pair.lower() in message.lower():
            return pair
    return None

def standardize_currency_pair(pair):
    """Standardize currency pair format for OANDA API"""
    print(f"[standardize_currency_pair] Input pair: {pair}")
    
    # Remove any spaces and convert to uppercase
    pair = pair.strip().upper().replace(" ", "")
    
    # Handle common separators
    for sep in ['/', '_', '-', '.']:
        if sep in pair:
            parts = pair.split(sep)
            if len(parts) == 2:
                return f"{parts[0]}_{parts[1]}"
    
    # If no separator found but length is 6, assume it's a direct currency pair
    if len(pair) == 6:
        return f"{pair[:3]}_{pair[3:]}"
        
    print(f"[standardize_currency_pair] Could not standardize pair: {pair}")
    return None

def validate_timeframe(timeframe):
    """Validate and standardize timeframe format"""
    print(f"[validate_timeframe] Input timeframe: {timeframe}")
    
    # Map common timeframe formats to OANDA format
    timeframe_map = {
        '1h': 'H1', 'h1': 'H1', 'hour': 'H1', '1hour': 'H1',
        '4h': 'H4', 'h4': 'H4',
        '1d': 'D', 'd1': 'D', 'day': 'D', '1day': 'D',
        '1m': 'M1', 'm1': 'M1', 'minute': 'M1',
        '30m': 'M30', 'm30': 'M30'
    }
    
    timeframe = timeframe.lower()
    if timeframe in timeframe_map:
        return timeframe_map[timeframe]
    
    print(f"[validate_timeframe] Invalid timeframe format: {timeframe}")
    return None

def load_historical_data(instrument, granularity, count):
    """Load historical data with improved error handling and validation"""
    print(f"[load_historical_data] Loading data for {instrument} with granularity {granularity} and count {count}")
    
    # Validate and standardize inputs
    std_instrument = standardize_currency_pair(instrument)
    if not std_instrument:
        raise ValueError(f"Invalid currency pair format: {instrument}")
    
    std_granularity = validate_timeframe(granularity)
    if not std_granularity:
        raise ValueError(f"Invalid timeframe format: {granularity}")
    
    params = {"granularity": std_granularity, "count": count}
    print(f"[load_historical_data] Requesting data for {std_instrument} with params {params}")
    
    r = InstrumentsCandles(instrument=std_instrument, params=params)
    
    try:
        api.request(r)
        print(f"[load_historical_data] Successfully loaded data for {std_instrument}")
    except V20Error as e:
        print(f"[load_historical_data] OANDA API Error: {e}")
        raise ValueError(f"Failed to fetch data: {str(e)}")
    except Exception as e:
        print(f"[load_historical_data] Unexpected error: {e}")
        raise

    # Process candle data
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

    print(f"[load_historical_data] Processed {len(records)} candles")
    df = pd.DataFrame(records)
    df["time"] = pd.to_datetime(df["time"])
    df = calculate_indicators(df)
    save_to_csv(df, std_instrument, std_granularity)
    return df

def calculate_indicators(df):
    print("[calculate_indicators] Calculating indicators...")
    numeric_cols = ["open", "high", "low", "close"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric)

    df["RSI"] = calculate_rsi(df["close"], window=14)
    df["MACD"], df["Signal_Line"], df["Histogram"] = calculate_macd(df["close"], window_fast=12, window_slow=26, window_signal=9)
    df["BollingerBands_middle"], df["BollingerBands_std"] = calculate_bollinger_bands(df["close"], window=20)
    df["ATR"] = calculate_atr(df["high"], df["low"], df["close"], window=14)
    df["ADX"] = calculate_adx(df["high"], df["low"], df["close"], window=14)
    df["OBV"] = calculate_obv(df["close"], df["volume"])

    print("[calculate_indicators] Indicators calculated.")
    return df

def save_to_csv(df, instrument, granularity):
    print(f"[save_to_csv] Saving historical data to CSV for {instrument} at {granularity} granularity.")
    filename = f"{INDICATORS_DIRECTORY}/{instrument}_{granularity}.csv"
    df.to_csv(filename, index=False)
    
    # Save individual indicators
    indicators = ["RSI", "MACD", "Signal_Line", "Histogram", "BollingerBands_middle", "BollingerBands_std", "ATR",
                 "ADX", "OBV"]
    for indicator in indicators:
        indicator_df = df[["time", indicator]]
        filename = f"{INDICATORS_DIRECTORY}/{instrument}_{indicator}.csv"
        indicator_df.to_csv(filename, index=False)
    print("[save_to_csv] Data and indicators saved to CSV.")

# Initialize tool registry after function definitions
tool_registry = ToolRegistry()

# Register tools after they are defined
tool_registry.register(
    "get_account_details",
    "Fetch current account details including balance, margin, positions, etc.",
    get_account_details
)

tool_registry.register(
    "create_order",
    "Create a new trading order",
    create_order,
    ["account_id", "order_data"]
)

# Gemini model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

@app.route('/')
def index():
    return render_template('main.html')

def get_gemini_response(messages):
    chat = model.start_chat()
    
    # Convert message format to Gemini format
    for msg in messages:
        if msg["role"] == "system":
            chat.send_message(msg["content"])
        else:
            chat.send_message(msg["content"])
    
    return chat.last.text

@app.route('/api/v1/query', methods=['POST'])
def query():
    """Enhanced query route with tool calling"""
    print("[query] Received new query request")
    user_message = request.json.get('message')
    
    if not user_message:
        return jsonify({"error": "Message not provided"}), 400

    print(f"[query] Processing message: {user_message}")

    try:
        # Get initial AI response to identify needed tool
        response = get_ai_response(user_message)
        
        # Check for tool calls in response
        if "<tool>" in response and "</tool>" in response:
            tool_call = response.split("<tool>")[1].split("</tool>")[0]
            
            # Parse tool call with parameters
            if "|" in tool_call:
                parts = tool_call.split("|")
                tool_name = parts[0]
                params = dict(p.split("=") for p in parts[1:])
            else:
                tool_name = tool_call
                params = {}
            
            tool = tool_registry.get_tool(tool_name)
            
            if tool:
                if tool_name == "create_order":
                    # Extract order details from user message
                    order_data = extract_order_details(user_message)
                    # Execute create order with parameters
                    tool_response = tool.function(
                        account_id=params.get('account_id', ACCOUNT_ID),
                        order_data=order_data
                    )
                else:
                    # Execute other tools
                    tool_response = tool.function()
                
                # Get final AI response with tool data
                final_response = get_ai_response(user_message, tool_response)
                
                # Save conversation
                save_conversation_to_db(user_message, final_response)
                
                return jsonify({"response": final_response, "data": tool_response})
            
        # No tool needed, return direct AI response
        save_conversation_to_db(user_message, response)
        return jsonify({"response": response})
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"[query] ERROR: {str(e)}")
        print(f"[query] Traceback:\n{error_trace}")
        return jsonify({
            "error": str(e),
            "traceback": error_trace
        }), 500

@app.route('/api/v1/create_order', methods=['POST'])
def create_order_route():
    print("Received a request to create an order.")
    data = request.json
    print(f"Received data: {data}")
    order_data = data.get('order')
    print(f"Order data: {order_data}")

    required_fields = ['units', 'instrument', 'type']
    if not all(field in order_data for field in required_fields):
        print("Error: Required fields are missing.")
        return jsonify({"error": "Required fields are missing"}), 400

    order_data['units'] = int(order_data['units'])

    # Add additional parameters
    if order_data['type'] in ["LIMIT", "STOP"]:
        order_data["price"] = data.get('price')

    # Handle take profit
    take_profit_price = data.get('take_profit')
    if take_profit_price:
        order_data["takeProfitOnFill"] = {
            "price": take_profit_price,
            "timeInForce": "GTC"
        }

    # Handle stop loss
    stop_loss_price = data.get('stop_loss')
    if stop_loss_price:
        order_data["stopLossOnFill"] = {
            "price": stop_loss_price,
            "timeInForce": "GTC"
        }

    # Handle trailing stop
    trailing_stop = data.get('trailing_stop_loss_distance')
    if trailing_stop:
        order_data["trailingStopLossOnFill"] = {
            "distance": trailing_stop
        }

    # Handle guaranteed stop
    guaranteed_stop = data.get('guaranteed_stop_loss_price')
    if guaranteed_stop:
        order_data["guaranteedStopLossOnFill"] = {
            "price": guaranteed_stop,
            "timeInForce": "GTC"
        }

    try:
        # Save order parameters to CSV
        df = pd.DataFrame([order_data])
        df.to_csv('parameters.csv', mode='a', header=False)
        print("Successfully written order data to CSV.")

        # Create the order
        assistant_response, order_response = create_order(ACCOUNT_ID, {"order": order_data})
        print("Order Created: ", order_response)
        print(f"Assistant Response: {assistant_response}")
        
        return jsonify({
            "response": assistant_response, 
            "order_response": order_response
        })

    except Exception as e:
        error_message = str(e)
        print("Error: ", error_message)
        return jsonify({"error": error_message}), 500

@app.route('/save_strategy', methods=['POST'])
def save_strategy():
    data = request.get_json()
    print(f"[save_strategy] Received data to save strategy: {data}")
    database.append(data)
    print("[save_strategy] Strategy saved successfully.")
    return jsonify(success=True)


@app.route('/search_strategies', methods=['POST'])
def search_strategies():
    search = request.get_json().get('search')
    print(f"[search_strategies] Searching strategies with term: {search}")
    result = [s for s in database if search in s['strategyName'] or search in s['authorName']]
    print(f"[search_strategies] Found {len(result)} strategies matching search term.")
    return jsonify(result)

@app.route('/api/v1/backtest_strategy', methods=['POST'])
def backtest_strategy():
    """Enhanced backtest route with database integration and detailed logging"""
    print("[backtest_strategy] Received new backtest request")
    data = request.get_json()
    print(f"[backtest_strategy] Request data: {json.dumps(data, indent=2)}")

    try:
        # Save strategy first
        strategy = save_strategy_to_db(data)
        print(f"[backtest_strategy] Strategy saved with ID: {strategy.id}")

        # Load historical data and calculate indicators
        print(f"[backtest_strategy] Loading historical data for {data['currencyPair']}")
        df = load_historical_data(data['currencyPair'], data['timeFrame'], 5000)
        print(f"[backtest_strategy] Loaded {len(df)} candles of historical data")

        # Execute strategy code
        print("[backtest_strategy] Executing strategy code")
        globals_dict = {"df": df}
        exec(data['strategyCode'], globals_dict)

        backtest_results = globals_dict.get("backtestResults", {})
        backtest_results_str = "\n".join(f"{k}: {v}" for k, v in backtest_results.items())
        print(f"[backtest_strategy] Strategy execution completed. Results:\n{backtest_results_str}")

        # Get AI analysis
        analysis_prompt = f"""Analyze this trading strategy:
        Strategy Details:
        Name: {data['strategyName']}
        Author: {data['authorName']}
        Pair: {data['currencyPair']}
        Timeframe: {data['timeFrame']}
        
        Code: {data['strategyCode']}
        
        Results: {backtest_results_str}
        
        Provide a comprehensive analysis including:
        1. Strategy overview and approach
        2. Performance metrics analysis
        3. Risk assessment
        4. Potential improvements
        5. Market conditions suitability
        """

        print("[backtest_strategy] Requesting AI analysis")
        messages = [
            {"role": "system", "content": "You are an expert trading strategy analyst."},
            {"role": "user", "content": analysis_prompt}
        ]
        analysis = get_gemini_response(messages)
        print(f"[backtest_strategy] Received AI analysis of length: {len(analysis)}")

        # Save backtest results
        backtest_result = save_backtest_result_to_db(strategy.id, backtest_results_str, analysis)
        print(f"[backtest_strategy] Saved backtest results with ID: {backtest_result.id}")

        return jsonify({
            "strategy_id": strategy.id,
            "backtestResults": backtest_results_str,
            "analysis": analysis,
            "error": None
        })

    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"[backtest_strategy] ERROR: {str(e)}")
        print(f"[backtest_strategy] Traceback:\n{error_trace}")
        return jsonify({
            "error": str(e),
            "traceback": error_trace,
            "backtestResults": None,
            "analysis": None
        }), 500

@app.route('/api/v1/strategies', methods=['GET'])
def get_strategies():
    """Get all strategies from database"""
    print("[get_strategies] Fetching all strategies")
    try:
        strategies = Strategy.query.all()
        print(f"[get_strategies] Found {len(strategies)} strategies")
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
        print(f"[get_strategies] ERROR: {str(e)}")
        print(f"[get_strategies] Traceback:\n{traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/strategy/<int:strategy_id>', methods=['GET'])
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

@app.route('/api/v1/strategy', methods=['POST'])
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

@app.route('/api/v1/strategy/<int:strategy_id>', methods=['PUT'])
def update_strategy(strategy_id):
    try:
        strategy = Strategy.query.get_or_404(strategy_id)
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

@app.route('/api/v1/strategy/<int:strategy_id>', methods=['DELETE'])
def delete_strategy(strategy_id):
    try:
        strategy = Strategy.query.get_or_404(strategy_id)
        db.session.delete(strategy)
        db.session.commit()
        return jsonify({'message': 'Strategy deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/backtest_results/<int:strategy_id>', methods=['GET'])
def get_backtest_results(strategy_id):
    try:
        results = BacktestResult.query.filter_by(strategy_id=strategy_id).order_by(BacktestResult.created_at.desc()).all()
        return jsonify([{
            'id': r.id,
            'results': r.results,
            'analysis': r.analysis,
            'created_at': r.created_at.isoformat()
        } for r in results])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/store_backtest_result', methods=['POST'])
def store_backtest_result():
    try:
        data = request.get_json()
        result = BacktestResult(
            strategy_id=data['strategy_id'],
            results=data['results'],
            analysis=data['analysis']
        )
        db.session.add(result)
        db.session.commit()
        return jsonify({'message': 'Backtest result stored successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/candlestick_data', methods=['GET'])
def get_candlestick_data():
    try:
        instrument = request.args.get('instrument')
        granularity = request.args.get('granularity')
        count = request.args.get('count', 100)
        
        df = load_historical_data(instrument, granularity, count)
        return jsonify(df.to_dict('records'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/backtest')
def backtest_page():
    return render_template('backtest.html')

@app.route('/api/v1/account_details', methods=['GET'])
def account_details():
    """Get account details endpoint with better error handling"""
    try:
        print("[account_details] Processing request")
        details = get_account_details()
        
        if "error" in details:
            print(f"[account_details] Returning error response: {details['error']}")
            return jsonify({"error": details["error"]}), 400
            
        account = details.get("account", {})
        
        response = {
            "account": {
                "balance": account.get("balance", "0"),
                "marginRate": account.get("marginRate", "0"),
                "openPositionCount": account.get("openPositionCount", 0),
                "openTradeCount": account.get("openTradeCount", 0),
                "marginAvailable": account.get("marginAvailable", "0"),
                "pl": account.get("pl", "0")
            }
        }
        
        print(f"[account_details] Returning successful response: {json.dumps(response, indent=2)}")
        return jsonify(response)
        
    except Exception as e:
        error_msg = f"Failed to process account details: {str(e)}"
        print(f"[account_details] ERROR: {error_msg}")
        print(f"[account_details] Traceback:\n{traceback.format_exc()}")
        return jsonify({"error": error_msg}), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'error': 'Internal server error'}), 500



# Add these database helper functions after the configurations
def save_conversation_to_db(user_message, assistant_response):
    """Save conversation to database with error logging"""
    print("[save_conversation_to_db] Saving new conversation")
    try:
        conversation = Conversation(
            user_id=1,  # TODO: Replace with actual user ID from session
            message=user_message,
            response=assistant_response,
            timestamp=datetime.utcnow()
        )
        db.session.add(conversation)
        db.session.commit()
        print(f"[save_conversation_to_db] Successfully saved conversation ID: {conversation.id}")
        return conversation
    except Exception as e:
        db.session.rollback()
        print(f"[save_conversation_to_db] ERROR: Failed to save conversation: {str(e)}")
        print(f"[save_conversation_to_db] Traceback: {traceback.format_exc()}")
        raise

def save_strategy_to_db(data):
    """Save strategy to database with error logging"""
    print(f"[save_strategy_to_db] Attempting to save strategy: {data['strategyName']}")
    try:
        strategy = Strategy(
            user_id=1,  # TODO: Replace with actual user ID from session
            name=data['strategyName'],
            description=f"Strategy created for {data['currencyPair']} on {data['timeFrame']} timeframe",
            algo_code=data['strategyCode'],
            currency_pair=data['currencyPair'],
            time_frame=data['timeFrame'],
            is_private=True
        )
        db.session.add(strategy)
        db.session.commit()
        print(f"[save_strategy_to_db] Successfully saved strategy ID: {strategy.id}")
        return strategy
    except Exception as e:
        db.session.rollback()
        print(f"[save_strategy_to_db] ERROR: Failed to save strategy: {str(e)}")
        print(f"[save_strategy_to_db] Traceback: {traceback.format_exc()}")
        raise

def save_backtest_result_to_db(strategy_id, results_str, analysis):
    """Save backtest results to database with error logging"""
    print(f"[save_backtest_result_to_db] Saving results for strategy ID: {strategy_id}")
    try:
        result = BacktestResult(
            strategy_id=strategy_id,
            results=results_str,
            analysis=analysis,
            created_at=datetime.utcnow()
        )
        db.session.add(result)
        db.session.commit()
        print(f"[save_backtest_result_to_db] Successfully saved backtest result ID: {result.id}")
        return result
    except Exception as e:
        db.session.rollback()
        print(f"[save_backtest_result_to_db] ERROR: Failed to save backtest result: {str(e)}")
        print(f"[save_backtest_result_to_db] Traceback: {traceback.format_exc()}")
        raise

@app.route('/api/v1/store_conversation', methods=['POST'])
def store_conversation():
    """Store conversation endpoint with detailed logging"""
    print("[store_conversation] Received new conversation storage request")
    try:
        data = request.get_json()
        print(f"[store_conversation] Received data: {json.dumps(data, indent=2)}")

        # Handle both single and batch conversation formats
        if 'conversation_data' in data:
            for conv in data['conversation_data']:
                save_conversation_to_db(conv['content'], conv['response'])
        else:
            save_conversation_to_db(data['message'], data['response'])

        print("[store_conversation] Successfully stored conversation")
        return jsonify({'success': True, 'message': 'Conversation stored successfully'})

    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"[store_conversation] ERROR: Failed to store conversation: {str(e)}")
        print(f"[store_conversation] Traceback:\n{error_trace}")
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': error_trace
        }), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5000, debug=True)