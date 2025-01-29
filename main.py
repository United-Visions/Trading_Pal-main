import datetime
from flask import Flask, request, jsonify, render_template, redirect, session, url_for
from flask_cors import CORS
import google.generativeai as genai
import configparser
import traceback
import os
import json
import logging
from models import  BrokerConfig, db, User, Conversation
import requests
from oandapyV20 import API
from oandapyV20.exceptions import V20Error
from oandapyV20.endpoints.instruments import InstrumentsCandles
from tools import ToolRegistry
from words import endpoint_phrases, trading_keywords
from oanda_broker import OandaBroker
from trading import load_historical_data
from broker_factory import BrokerFactory
from flask_login import login_required, current_user, LoginManager
from auth import auth_bp
from user_config import user_config_bp
from utils import get_gemini_response

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('main.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
    return db.session.get(User, int(user_id))

# API and model configurations
genai.configure(api_key=config.get('API_KEYS', 'GEMINI_API_KEY'))
OANDA_API_KEY = config.get('API_KEYS', 'OANDA_API_KEY')
BASE_URL = "https://api-fxpractice.oanda.com"
ACCOUNT_ID = config.get('API_KEYS', 'OANDA_ACCOUNT_ID', fallback="101-001-25836")
api = API(access_token=OANDA_API_KEY)

# Replace broker initialization with broker factory
broker_factory = BrokerFactory()



# Function definitions
def get_account_details(broker_name=None):
    """Get account details from specified or available broker"""
    if broker_name and broker_factory.is_broker_available(broker_name):
        broker, _ = broker_factory.get_broker()
    else:
        broker, broker_name = broker_factory.get_broker()
    return broker.get_account_details()

def create_order(account_id=None, order_data=None):
    """Enhanced order creation with broker context"""
    try:
        broker = g.broker_factory.get_broker()
        order_response = broker.create_order(order_data)
        
        # Include broker context in response
        response_data = {
            "order": order_response,
            "broker_used": broker.name,
            "broker_status": g.broker_factory.get_broker_status(broker.name),
            "account_id": account_id
        }
        
        return response_data
        
    except Exception as err:
        print(f"[create_order] ERROR: {str(err)}")
        raise

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



def get_gemini_response(messages, model="gemini-pro"):
    # Add model parameter with default value
    try:
        response = model.generate_content(messages)
        return response.text
    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        return "Sorry, I encountered an error processing your request."

def get_ai_response(user_message: str, available_data: dict = None, conversation_history: list = None) -> str:
    system_prompt = f"""You are Trading Pal 1.0, a sophisticated AI trading assistant.
    You have access to the following tools and context:
    
    {tool_registry.get_tool_descriptions()}
    Current Broker: {g.get('broker_factory').current_broker if hasattr(g, 'broker_factory') else 'Not set'}
    
    You can:
    1. Get account details and status
    2. Provide market analysis
    3. Explain trading concepts
    4. Show historical data
    
    You CANNOT:
    1. Place trades or create orders
    2. Modify existing positions
    3. Give specific trading advice
    
    Focus on providing information and analysis while directing users to their broker's platform for actual trading.
    """
    # Include conversation history for context
    messages = [{"role": "system", "content": system_prompt}]
    if conversation_history:
        messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_message})
    
    if available_data:
        messages.append({
            "role": "assistant", 
            "content": f"Retrieved data: {json.dumps(available_data, indent=2)}"
        })
    
    return get_gemini_response(messages, model="gemini-pro") # Pass model parameter

def extract_instrument(message):
    """Extract instrument name from user message"""
    # Add common currency pairs
    pairs = ["EUR_USD"]
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
    get_account_details  # No parameters needed as broker is handled internally
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

@app.route('/api/v1/query', methods=['POST'])
@login_required
def query():
    print("[query] Received new query request")
    
    try:
        data = request.json
        user_message = data.get('message')
        conversation_history = data.get('conversation_history', [])
        
        if not user_message:
            return jsonify({"error": "Message not provided"}), 400

        print(f"[query] Processing message: {user_message}")
        current_broker = request.headers.get('X-Selected-Broker') or 'oanda'
        print(f"[query] Using broker: {current_broker}")

        # Get broker configuration
        broker_config = BrokerConfig.query.filter_by(
            user_id=current_user.id,
            broker_type=current_broker,
            is_active=True
        ).first()

        # Format messages for Gemini
        messages = [{
            "role": "system",
            "content": "You are Trading Pal 1.0, a sophisticated AI trading assistant. "
                      f"Currently using {current_broker.upper()} broker."
        }]
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add current message
        messages.append({
            "role": "user",
            "content": user_message
        })

        # Get AI response
        response = get_gemini_response(messages)
        
        # Save conversation if successful
        if response:
            save_conversation_to_db(user_message, response, current_broker)
            return jsonify({"response": response})
        else:
            return jsonify({"error": "Failed to get AI response"}), 500

    except Exception as e:
        logger.error(f"[query] ERROR: {str(e)}")
        logger.error(f"[query] Traceback:\n{traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

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

from flask import g

@app.before_request
def initialize_user_brokers():
    """Initialize broker factory before each request if user is authenticated"""
    if current_user.is_authenticated:
        # Store broker factory in Flask's g object to persist during request
        if not hasattr(g, 'broker_factory'):
            g.broker_factory = BrokerFactory()
        # Initialize brokers if not already done
        if hasattr(g, 'broker_factory') and not g.broker_factory.brokers:
            active_configs = BrokerConfig.query.filter_by(
                user_id=current_user.id,
                is_active=True
            ).all()
            
            if active_configs:
                g.broker_factory.initialize_user_brokers(current_user)

@app.teardown_appcontext
def teardown_broker_factory(exception):
    """Clean up broker factory at end of request"""
    broker_factory = g.pop('broker_factory', None)

    
@app.route('/charts')
@login_required
def charts_view():
    """Render charts view template with RSS feed integration"""
    
    # Check if data server is running
    try:
        response = requests.get('http://localhost:4000/api/feed/forex/EUR-USD')
        if (response.status_code != 200):
            logger.warning("Data server not responding properly")
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to data server")
        
    return render_template(
        'charts_components/charts_container.html',
        data_server_url='http://localhost:4000'
    )

@app.route('/api/v1/account_details', methods=['GET'])
@login_required
def account_details():
    try:
        broker_type = request.args.get('broker')
        if not broker_type:
            return jsonify({"error": "Broker type not specified"}), 400
            
        broker_config = BrokerConfig.query.filter_by(
            user_id=current_user.id,
            broker_type=broker_type,
            is_active=True
        ).first()
        
        if not broker_config:
            return jsonify({
                "error": "Broker not configured",
                "need_configuration": True
            }), 400
            
        # Initialize the specific broker
        broker_factory = BrokerFactory()
        success = broker_factory.add_broker(
            broker_type=broker_config.broker_type,
            api_key=broker_config.api_key,
            api_secret=broker_config.api_secret,
            account_id=broker_config.account_id
        )
        
        if not success:
            return jsonify({
                "error": f"Failed to initialize {broker_type} broker",
                "need_configuration": True
            }), 400
            
        broker = broker_factory.get_broker(broker_type)
        details = broker.get_account_details()
        
        if "error" in details:
            return jsonify({"error": details["error"]}), 400
            
        return jsonify({
            "account": details,
            "broker": broker_type,
            "status": "connected"
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "need_configuration": "configure broker credentials" in str(e).lower()
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

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

@app.route('/api/v1/store_conversation', methods=['POST'])
def store_conversation():
    """Store conversation endpoint with detailed logging"""
    print("[store_conversation] Received new conversation storage request")
    try:
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
    app.register_blueprint(user_config_bp)    
    app.run(port=5000, debug=True)