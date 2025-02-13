"""
TradingPal Main Application
---
Main entry point for the TradingPal application handling routing, 
authentication, and API endpoints.

Author: Trading Pal Team
Version: 1.0
"""

from datetime import datetime, timedelta
import threading
import time
from flask import (
    Flask, request, jsonify, render_template, redirect, 
    session, url_for, g
)
from flask_cors import CORS
import google.generativeai as genai
import configparser
import traceback
import os
import json
import logging
import broker_factory
from models import BrokerConfig, db, User, Conversation
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
from sqlalchemy import desc

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

# Load configuration
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
login_manager.login_view = 'auth.login_page'
login_manager.init_app(app)

# Initialize market data server
from data_server import MarketDataServer
market_data_server = None
market_data_lock = threading.Lock()

def get_market_data_server():
    """Get or initialize market data server with proper locking"""
    global market_data_server
    with market_data_lock:
        if market_data_server is None:
            try:
                api_key = config.get('API_KEYS', 'POLYGON_API_KEY')
                market_data_server = MarketDataServer(api_key, pairs=['EUR-USD'])
                
                # Start server in a background thread
                def run_server():
                    try:
                        market_data_server.start()
                    except Exception as e:
                        logger.error(f"Market data server error: {str(e)}")
                        
                server_thread = threading.Thread(target=run_server, daemon=True)
                server_thread.start()
                
                logger.info("Market data server initialized")
                
                # Wait for initial historical data
                retries = 0
                while retries < 5:
                    time.sleep(2)
                    if market_data_server.get_data('EUR-USD'):
                        logger.info("Historical data loaded")
                        break
                    retries += 1
                if retries == 5:
                    logger.warning("Timeout waiting for historical data")
                    
            except Exception as e:
                logger.error(f"Failed to initialize market data server: {str(e)}")
                market_data_server = None
                raise
                
    return market_data_server

# API and model configurations
genai.configure(api_key=config.get('API_KEYS', 'GEMINI_API_KEY'))
OANDA_API_KEY = config.get('API_KEYS', 'OANDA_API_KEY')
BASE_URL = "https://api-fxpractice.oanda.com"
ACCOUNT_ID = config.get('API_KEYS', 'OANDA_ACCOUNT_ID')
api = API(access_token=OANDA_API_KEY)

# Initialize tool registry
tool_registry = ToolRegistry()

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return db.session.get(User, int(user_id))

def get_account_details(broker_type=None):
    """Get account details from current or specified broker"""
    try:
        broker_type = broker_type or request.headers.get('X-Selected-Broker')
        if not broker_type:
            raise ValueError("No broker specified")
            
        broker = g.broker_factory.get_broker(broker_type)
        if not broker:
            raise ValueError(f"Broker {broker_type} not initialized")
            
        return broker.get_account_details()
    except Exception as e:
        logger.error(f"Tool execution error: {str(e)}")
        raise


def create_order(account_id=None, order_data=None):
    """Enhanced order creation with broker context"""
    try:
        broker = g.broker_factory.get_broker()
        order_response = broker.create_order(order_data)
        
        response_data = {
            "order": order_response,
            "broker_used": broker.name,
            "broker_status": g.broker_factory.get_broker_status(broker.name),
            "account_id": account_id
        }
        
        return response_data
        
    except Exception as err:
        logger.error(f"[create_order] ERROR: {str(err)}")
        raise

def detect_intent(user_message):
    """Detect which endpoint the user is trying to access based on their message"""
    user_message = user_message.lower()
    
    for endpoint, phrases in endpoint_phrases.items():
        if any(phrase.lower() in user_message for phrase in phrases):
            return endpoint
            
    return None

def get_broker_for_request(user_message=None):
    """Get appropriate broker based on user context and message"""
    try:
        if not current_user.is_authenticated:
            broker = broker_factory.get_broker(message=user_message)
        else:
            user_prefs = current_user.trading_preferences
            broker = broker_factory.get_broker(
                message=user_message,
                user_prefs=user_prefs
            )
            
        if not broker:
            raise ValueError("No available brokers configured")
            
        if not broker_factory.check_broker_status(broker.name):
            raise ValueError(f"Broker {broker.name} is not connected")
            
        return broker
        
    except Exception as e:
        logger.error(f"[get_broker_for_request] ERROR: {str(e)}")
        raise

def execute_endpoint_action(intent, user_message=None):
    """Execute the appropriate action and get AI response based on the data"""
    try:
        broker = get_broker_for_request(user_message)
        
        if not broker_factory.check_broker_status(broker.name):
            return jsonify({
                "error": f"Broker {broker.name} is not connected. Please check your configuration."
            }), 503

        response_data = None
        if intent == "get_accounts":
            response_data = broker.get_account_details()
        elif intent == "get_account_details":
            response_data = broker.get_account_details()
        elif intent == "create_order":
            return jsonify({"action": "create_order", "broker": broker.name})
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
            response_data.update({
                "broker_used": broker.name,
                "broker_status": broker_factory.get_broker_status(broker.name),
                "available_brokers": broker_factory.get_available_brokers()
            })
            
            prompt = f"""
            User Intent: {intent}
            Broker Used: {broker.name}
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

def extract_instrument(message):
    """Extract instrument name from user message"""
    pairs = ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD"]
    for pair in pairs:
        if pair.lower() in message.lower():
            return pair
    return None

# Register tool
tool_registry.register(
    "get_account_details",
    "Fetch current account details including balance, margin, positions, etc.",
    get_account_details
)

# Routes
@app.route('/')
def landing():
    """Landing page route"""
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    return redirect(url_for('auth.login_page'))

@app.route('/main')
@login_required
def main():
    """Main application page"""
    return render_template('main.html')

@app.route('/api/v1/query', methods=['POST'])
@login_required
def query():
    """Handle chat queries with tool selection logging"""
    logger.info("[query] Received new query request")
    
    try:
        data = request.json
        user_message = data.get('message')
        conversation_history = data.get('conversation_history', [])
        
        if not user_message:
            return jsonify({"error": "Message not provided"}), 400

        logger.info(f"[query] Processing message: {user_message}")
        current_broker = request.headers.get('X-Selected-Broker') or 'oanda'
        logger.info(f"[query] Using broker: {current_broker}")
        
        # Get broker instance from g context
        if not hasattr(g, 'broker_factory'):
            g.broker_factory = BrokerFactory()
            
        # Available tools prompt
        tools_desc = tool_registry.get_tool_descriptions()
        logger.info(f"[query] Available tools: {tools_desc}")

        # Format system prompt with tools context
        system_prompt = f"""You are Trading Pal 1.0, a sophisticated AI trading assistant.
        Currently using {current_broker.upper()} broker.
        
        Available tools:
        {tools_desc}
        
        If the user asks about account details, use the get_account_details tool.
        Respond with "EXECUTE_TOOL:get_account_details" if you determine this tool should be used.
        Otherwise respond naturally to the query.
        """

        messages = [{
            "role": "system",
            "content": system_prompt
        }]
        
        messages.extend(conversation_history)
        messages.append({
            "role": "user",
            "content": user_message
        })

        # Get initial response to check if tool needed
        response = get_gemini_response(messages)
        logger.info(f"[query] Initial response: {response}")

        # Check if response indicates tool usage
        if "EXECUTE_TOOL:" in response:
            tool_name = response.split("EXECUTE_TOOL:")[1].strip()
            logger.info(f"[query] Tool selected: {tool_name}")
            
            # Get tool from registry
            tool = tool_registry.get_tool(tool_name)
            if not tool:
                logger.error(f"[query] Tool {tool_name} not found")
                return jsonify({"error": f"Tool {tool_name} not available"}), 500
                
            # Execute tool with broker context
            try:
                account_data = tool.execute(broker=g.broker_factory.brokers[current_broker])
                logger.info(f"[query] Tool execution result: {account_data}")
                
                # Get final response with real data
                data_prompt = f"""The {tool_name} tool returned this data:
                {json.dumps(account_data, indent=2)}
                
                Please provide a natural language summary of this account information."""
                
                messages.append({
                    "role": "assistant",
                    "content": data_prompt
                })
                
                response = get_gemini_response(messages)
            except Exception as e:
                logger.error(f"[query] Tool execution error: {str(e)}")
                return jsonify({"error": f"Failed to execute tool: {str(e)}"}), 500
                
        # Save conversation
        conversation = save_conversation_to_db(user_message, response, current_broker)

        return jsonify({
            "response": response,
            "conversation_id": conversation.id if conversation else None
        })

    except Exception as e:
        logger.error(f"[query] ERROR: {str(e)}")
        logger.error(f"[query] Traceback:\n{traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/conversation_history', methods=['GET'])
@login_required
def get_conversation_history():
    """Get user's conversation history"""
    try:
        thirty_days_ago = datetime.now() - timedelta(days=30)
        conversations = Conversation.query.filter(
            Conversation.user_id == current_user.id,
            Conversation.timestamp >= thirty_days_ago
        ).order_by(desc(Conversation.timestamp)).all()
        
        history = []
        for conv in conversations:
            history.append({
                'id': conv.id,
                'message': conv.message,
                'response': conv.response,
                'broker_context': conv.broker_context,
                'timestamp': conv.timestamp.isoformat() if conv.timestamp else None
            })
            
        return jsonify({
            'conversations': history,
            'count': len(history)
        })
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': 'Failed to retrieve conversation history',
            'details': str(e)
        }), 500

@app.route('/api/v1/store_conversation', methods=['POST'])
@login_required
def store_conversation():
    """Store new conversation or update existing one"""
    try:
        data = request.json.get('conversation_data', {})
        messages = data.get('messages', [])
        
        conversation_id = data.get('id')
        if conversation_id:
            conversation = Conversation.query.get(conversation_id)
            if not conversation or conversation.user_id != current_user.id:
                return jsonify({'error': 'Conversation not found'}), 404
        else:
            conversation = None
            
        for msg in messages:
            if conversation:
                conversation.message = msg.get('content', '')
                conversation.response = msg.get('response', '')
                conversation.timestamp = datetime.now()
            else:
                conversation = Conversation(
                    user_id=current_user.id,
                    message=msg.get('content', ''),
                    response=msg.get('response', ''),
                    broker_context=session.get('selected_broker'),
                    timestamp=datetime.now()
                )
                db.session.add(conversation)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'id': conversation.id,
            'timestamp': conversation.timestamp.isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error storing conversation: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': 'Failed to store conversation',
            'details': str(e)
        }), 500

@app.route('/api/v1/delete_conversation/<int:conversation_id>', methods=['DELETE'])
@login_required
def delete_conversation(conversation_id):
    """Delete a specific conversation"""
    try:
        conversation = Conversation.query.get(conversation_id)
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
            
        if conversation.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
            
        db.session.delete(conversation)
        db.session.commit()
         
        return jsonify({
            'success': True,
            'message': 'Conversation deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting conversation: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': 'Failed to delete conversation',
            'details': str(e)
        }), 500

@app.route('/api/v1/update_conversation/<int:conversation_id>', methods=['PUT'])
@login_required
def update_conversation(conversation_id):
    """Update conversation title or content"""
    try:
        conversation = Conversation.query.get(conversation_id)
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
            
        if conversation.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
            
        data = request.json
        if 'title' in data:
            conversation.title = data['title']
        if 'message' in data:
            conversation.message = data['message']
        if 'response' in data:
            conversation.response = data['response']
            
        conversation.updated_at = datetime.now()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'conversation': {
                'id': conversation.id,
                'title': conversation.title,
                'message': conversation.message,
                'response': conversation.response,
                'timestamp': conversation.timestamp.isoformat(),
                'updated_at': conversation.updated_at.isoformat()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating conversation: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': 'Failed to update conversation',
            'details': str(e)
        }), 500

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
        logger.error(f"Error getting broker status: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/account_details', methods=['GET'])
@login_required
def account_details():
    """Get account details for specified broker"""
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

@app.before_request
def initialize_user_brokers():
    """Initialize broker factory before each request if user is authenticated"""
    if current_user.is_authenticated:
        if not hasattr(g, 'broker_factory'):
            g.broker_factory = BrokerFactory()
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
    """Render charts view template"""
    return render_template('charts_components/charts_container.html')

@app.route('/api/chart_data/<pair>', methods=['GET'])
@login_required
def get_chart_data(pair):
    """Get chart data for the specified pair"""
    try:
        # Get market data server
        server = get_market_data_server()
        if server is None:
            return jsonify({"error": "Market data server not available"}), 500
            
        # Get data from market data server
        data = server.get_data(pair)
        if not data:
            return jsonify({"error": "No data available for pair"}), 404
            
        # Convert data to chart format
        formatted_data = []
        for entry in data:
            if entry['type'] in ['per-minute', 'per-second']:
                formatted_data.append({
                    'timestamp': entry['timestamp'],
                    'price': (entry['HH'] + entry['LL']) / 2,  # Use mid-price
                    'high': entry['HH'],
                    'low': entry['LL'],
                    'open': entry['LH'],
                    'close': entry['HL']
                })
                
        if not formatted_data:
            return jsonify({"error": "No formatted data available"}), 404
            
        # Sort by timestamp
        formatted_data.sort(key=lambda x: x['timestamp'])
        
        # Add metadata
        response = {
            'data': formatted_data,
            'metadata': {
                'pair': pair,
                'last_update': int(time.time() * 1000),
                'count': len(formatted_data),
                'type': 'real-time'
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error getting chart data: {str(e)}")
        return jsonify({"error": "Failed to process chart data"}), 500

@app.teardown_appcontext
def teardown_market_data(exception):
    """Clean up market data server at end of app context"""
    global market_data_server
    if market_data_server:
        market_data_server.stop()
        market_data_server = None
        
def save_conversation_to_db(user_message, assistant_response, broker_name=None):
    """Save conversation to database with error logging"""
    logger.info("[save_conversation_to_db] Saving new conversation")
    try:
        conversation = Conversation(
            user_id=current_user.id if current_user.is_authenticated else 1,
            message=user_message,
            response=assistant_response,
            broker_context=broker_name,
            timestamp=datetime.now()
        )
        db.session.add(conversation)
        db.session.commit()
        logger.info(f"[save_conversation_to_db] Successfully saved conversation ID: {conversation.id}")
        return conversation
    except Exception as e:
        db.session.rollback()
        logger.error(f"[save_conversation_to_db] ERROR: Failed to save conversation: {str(e)}")
        logger.error(f"[save_conversation_to_db] Traceback: {traceback.format_exc()}")
        raise

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_server_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(user_config_bp)

# Main entry point
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5000, debug=True)
