from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
import google.generativeai as genai
import configparser
import traceback
import os
import json
from models import BacktestResult, Strategy, db, User, Conversation, Review, Comment
from datetime import datetime
import requests
from oandapyV20 import API
from oandapyV20.exceptions import V20Error
from oandapyV20.endpoints.instruments import InstrumentsCandles
from indicators import calculate_rsi, calculate_macd, calculate_bollinger_bands, calculate_atr, calculate_adx, calculate_obv
from tools import ToolRegistry
from words import endpoint_phrases, trading_keywords
from oanda_broker import OandaBroker
from trading import load_historical_data, trading_bp
from broker_factory import BrokerFactory
from flask_login import login_required, current_user, LoginManager
from auth import auth_bp
from user_config import user_config_bp

config = configparser.ConfigParser()
config.read('config.ini')

# Initialize app configurations
app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')  # Change in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tradingpal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'auth.login_page'  # Update this line
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# API and model configurations
genai.configure(api_key=config.get('API_KEYS', 'GEMINI_API_KEY'))
OANDA_API_KEY = config.get('API_KEYS', 'OANDA_API_KEY')
BASE_URL = "https://api-fxpractice.oanda.com"
ACCOUNT_ID = config.get('API_KEYS', 'OANDA_ACCOUNT_ID', fallback="101-001-25836")
api = API(access_token=OANDA_API_KEY)

# Replace broker initialization with broker factory
broker_factory = BrokerFactory()

INDICATORS_DIRECTORY = "indicators_directory"

# Initialize strategy database
strategy_database = []

# Function definitions
def get_account_details(broker_name=None):
    """Get account details from specified or available broker"""
    if broker_name and broker_factory.is_broker_available(broker_name):
        broker, _ = broker_factory.get_broker()
    else:
        broker, broker_name = broker_factory.get_broker()
    return broker.get_account_details()

def create_order(account_id, order_data):
    try:
        broker, broker_name = get_broker_for_request()
        order_response = broker.create_order(order_data)
        message = f"Successfully created order. Response from broker: {order_response}"
        messages = [
            {"role": "user", "content": "create order"},
            {"role": "assistant", "content": message}
        ]
        assistant_response = get_gemini_response(messages)
        return assistant_response, order_response
    except Exception as err:
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

def get_broker_for_request(user_message=None):
    """Get appropriate broker based on user context and message"""
    try:
        if not current_user.is_authenticated:
            # Use default broker config if no user is logged in
            broker, broker_name = broker_factory.get_broker(message=user_message)
        else:
            # Get user's trading preferences
            user_prefs = current_user.trading_preferences
            broker, broker_name = broker_factory.get_broker(
                message=user_message,
                user_prefs=user_prefs
            )
            
        if not broker:
            raise ValueError("No available brokers configured")
            
        # Verify broker connection
        if not broker_factory.check_broker_status(broker_name):
            raise ValueError(f"Broker {broker_name} is not connected")
            
        return broker, broker_name
        
    except Exception as e:
        print(f"[get_broker_for_request] ERROR: {str(e)}")
        raise

def execute_endpoint_action(intent, user_message=None):
    """Execute the appropriate action and get AI response based on the data"""
    try:
        broker, broker_name = get_broker_for_request(user_message)
        
        if not broker_factory.check_broker_status(broker_name):
            return jsonify({
                "error": f"Broker {broker_name} is not connected. Please check your configuration."
            }), 503

        response_data = None
        if intent == "get_accounts":
            response_data = broker.get_account_details()
        elif intent == "get_account_details":
            response_data = broker.get_account_details()
        elif intent == "create_order":
            return jsonify({"action": "create_order", "broker": broker_name})
        elif intent == "get_candlestick_data":
            instrument = extract_instrument(user_message)
            response_data = broker.get_candlestick_data(instrument)
        elif intent == "get_trades":
            response_data = broker.get_trades()
        elif intent == "get_positions":
            response_data = broker.get_positions()
        elif intent == "close_position":
            instrument = extract_instrument(user_message)
            response_data = broker.close_position(instrument)

        if response_data:
            # Add enhanced broker information
            response_data.update({
                "broker_used": broker_name,
                "broker_status": broker_factory.get_broker_status(broker_name),
                "available_brokers": broker_factory.get_available_brokers()
            })
            
            prompt = f"""
            User Intent: {intent}
            Broker Used: {broker_name}
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
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    return redirect(url_for('auth.login_page'))

@app.route('/main')
@login_required
def main():
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
@login_required
def create_order_route():
    """Enhanced order creation with broker selection"""
    try:
        data = request.json
        
        # Get appropriate broker using user preferences
        broker, broker_name = get_broker_for_request(data.get('message'))
        
        # Process order based on broker type
        processed_order = broker.process_order_request(data)
        
        # Create the order
        assistant_response, order_response = create_order(
            account_id=broker.account_id,
            order_data=processed_order
        )
        
        return jsonify({
            "response": assistant_response,
            "order_response": order_response,
            "broker_used": broker_name,
            "broker_status": broker_factory.get_broker_status(broker_name)
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"[create_order_route] ERROR: {error_msg}")
        return jsonify({"error": error_msg}), 500

@app.route('/api/v1/broker/status', methods=['GET'])
@login_required
def get_broker_status():
    """Get status of all configured brokers"""
    try:
        available_brokers = broker_factory.get_available_brokers()
        status = {
            broker: broker_factory.get_broker_status(broker)
            for broker in available_brokers
        }
        
        # Get user's trading preferences
        user_prefs = current_user.trading_preferences
        preferred_markets = user_prefs.preferred_markets if user_prefs else []
        
        return jsonify({
            "active_brokers": available_brokers,
            "status": status,
            "preferred_markets": preferred_markets,
            "default_broker": next(iter(available_brokers), None)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.before_request
def initialize_user_brokers():
    if current_user.is_authenticated and not broker_factory.brokers:
        broker_factory.initialize_user_brokers(current_user)

@app.route('/save_strategy', methods=['POST'])
def save_strategy():
    data = request.get_json()
    print(f"[save_strategy] Received data to save strategy: {data}")
    strategy_database.append(data)
    print("[save_strategy] Strategy saved successfully.")
    return jsonify(success=True)


@app.route('/search_strategies', methods=['POST'])
def search_strategies():
    search = request.get_json().get('search')
    print(f"[search_strategies] Searching strategies with term: {search}")
    result = [s for s in strategy_database if search in s['strategyName'] or search in s['authorName']]
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

@app.route('/backtest')
def backtest_page():
    return render_template('backtest.html')

@app.route('/api/v1/account_details', methods=['GET'])
@login_required
def account_details():
    """Get account details from selected broker"""
    try:
        # Get broker based on user preferences
        broker, broker_name = get_broker_for_request()
        
        details = broker.get_account_details()
        if "error" in details:
            return jsonify({"error": details["error"]}), 400
            
        # Add broker information to response
        details["broker_used"] = broker_name
        details["broker_status"] = broker_factory.get_broker_status(broker_name)
        
        return jsonify(details)
        
    except Exception as e:
        error_msg = f"Failed to get account details: {str(e)}"
        print(f"[account_details] ERROR: {error_msg}")
        return jsonify({"error": error_msg}), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'error': 'Internal server error'}), 500



# Add these database helper functions after the configurations
def save_conversation_to_db(user_message, assistant_response, broker_name=None):
    """Save conversation to database with error logging"""
    print("[save_conversation_to_db] Saving new conversation")
    try:
        conversation = Conversation(
            user_id=current_user.id if current_user.is_authenticated else 1,
            message=user_message,
            response=assistant_response,
            broker_context=broker_name,
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
    app.register_blueprint(auth_bp)
    app.register_blueprint(trading_bp)
    app.register_blueprint(user_config_bp)  # Add this line
    app.run(port=5000, debug=True)