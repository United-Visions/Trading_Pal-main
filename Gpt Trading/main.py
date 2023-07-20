from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai
import configparser
import traceback
import wave
import boto3
import winsound
import os
import json
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from flask import redirect, url_for

config = configparser.ConfigParser()
config.read('config.ini')

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Secret keys
app.secret_key = config.get('secrets', 'flask_secret')

# Database config
username = config.get('database', 'username')
password = config.get('database', 'password')
host = config.get('database', 'host')
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{username}:{password}@{host}/postgres'

# Set the OpenAI API key
OPENAI_API_KEY = config.get('API_KEYS', 'OPENAI_API_KEY')
OANDA_API_KEY = config.get('API_KEYS', 'OANDA_API_KEY')
openai.api_key = OPENAI_API_KEY

# AWS Polly keys and initialization
AWS_ACCESS_KEY_ID = config.get('AWS_KEYS', 'AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config.get('AWS_KEYS', 'AWS_SECRET_ACCESS_KEY')
AWS_REGION = config.get('AWS_KEYS', 'AWS_REGION')
session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)
polly_client = session.client('polly')

# Set the base URL for the OANDA API and the account ID
BASE_URL = "https://api-fxpractice.oanda.com"
ACCOUNT_ID = "101-001-25836"

# The headers for the HTTP requests
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OANDA_API_KEY}",
    "Connection": "keep-alive"
}


db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    package = db.Column(db.String(50))
    profile_picture = db.Column(db.String(200))
    broker_api = db.Column(db.String(120))
    oanda_account_id = db.Column(db.String(120))
    openai_api_key = db.Column(db.String(120))
    trading_preferences = db.Column(db.String(80))
    strategies = db.relationship('Strategy', backref='creator', lazy=True)
    conversations = db.relationship('Conversation', backref='user', lazy=True)

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    response = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Strategy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    is_private = db.Column(db.Boolean, default=True)
    algo_code = db.Column(db.String)
    currency_pair = db.Column(db.String(50))
    time_frame = db.Column(db.String(50))
    backtest_results = db.relationship('BacktestResult', backref='strategy', lazy=True)
    reviews = db.relationship('Review', backref='strategy', lazy=True)
    comments = db.relationship('Comment', backref='strategy', lazy=True)

class BacktestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategy.id'), nullable=False)
    results = db.Column(db.String)
    gpt_summary = db.Column(db.String)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategy.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stars = db.Column(db.Integer)
    content = db.Column(db.String(500))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategy.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(500))

@app.errorhandler(400)
def bad_request_error(error):
    return jsonify({'message': 'Bad request'}), 400

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'message': 'Internal server error'}), 500

def authenticate_user(username, hashed_password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, hashed_password):
        return user.id
    return None



def get_account_details():
    try:
        url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        error_message = f"Failed to get account details. Error: {err}"
        print(f"HTTPError occurred: {err}")
        # Passing the error to the GPT model for response
        messages = [
            {"role": "user", "content": error_message},
            {"role": "assistant", "content": error_message}
        ]
        assistant_response = get_gpt_response(messages)
        raise Exception(error_message) from err


def create_order(ACCOUNT_ID, order_data):
    try:
        url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/orders"
        response = requests.post(url, headers=headers, json=order_data)
        response.raise_for_status()
        order_response = response.json()

        # Generate a message based on the response from the broker
        message = f"Successfully created order. Response from broker: {order_response}"
        print(message)

        # Pass the message to the GPT model for response
        messages = [
            {"role": "user", "content": "create order"},
            {"role": "assistant", "content": message}
        ]
        assistant_response = get_gpt_response(messages)
        return assistant_response, order_response

    except requests.exceptions.HTTPError as err:
        error_message = f"Failed to create order. Error: {err}"
        # Passing the error to the GPT model for response
        messages = [
            {"role": "user", "content": "create order"},
            {"role": "assistant", "content": error_message}
        ]
        assistant_response = get_gpt_response(messages)
        raise Exception(assistant_response) from err


# Function to convert text to speech using AWS Polly
def text_to_speech(text):
    try:
        response = polly_client.synthesize_speech(
            Text=text,
            OutputFormat="pcm",
            VoiceId="Matthew"  # Provide the desired voice ID
        )
        audio = response['AudioStream'].read()

        # Save the audio stream to a temporary WAV file
        with wave.open(r"temp.wav", 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(audio)

        # Play the audio using the winsound module
        winsound.PlaySound(r"temp.wav", winsound.SND_FILENAME)

        # Remove the temporary WAV file
        os.remove(r"temp.wav")
    except Exception as e:
        print(f"Error in text_to_speech: {e}")


def get_gpt_response(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=messages
    )
    return response['choices'][0]['message']['content']


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/main.html')
def main_page():
  return render_template('main.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('packages.html')
    else:
        data = request.get_json()
        hashed_password = generate_password_hash(data['password'], method='sha256')

        valid_packages = ['early access', 'basic', 'premium']
        package = data['package']

        if package not in valid_packages:
            return jsonify({'message': 'Invalid package'}), 400

        new_user = User(
            username=data['username'], 
            password=hashed_password,
            package=package,  
            broker_api=data['broker_api'], 
            oanda_account_id=data['oanda_account_id'],
            openai_api_key=data['openai_api_key'],
            trading_preferences=data['trading_preferences']
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            return jsonify({'message': 'Registered successfully', 'user_id': new_user.id})
        except Exception as e:
            print(f"Error registering user: {e}")
            return jsonify({'message': 'Registration unsuccessful.'}), 400
@app.route('/login', methods=['GET', 'POST'])
def login():
    print("/login route accessed")

    if request.method == 'GET':
        print("Rendering login page")  
        return render_template('login.html')

    if request.method == 'POST':
        print("Received POST request")

        data = request.get_json()
        print("Request data:", data)

        username = data['username']
        print("Username:", username)

        password = data['password']
        print("Password:", password)

        user = User.query.filter_by(username=username).first()
        print(f"Queried for user with username: {username}")

        if not user:
            print("User not found in database")
            return jsonify({'message': 'Login unsuccessful'}), 401

        if not check_password_hash(user.password, password):
            print("Invalid password")
            return jsonify({'message': 'Login unsuccessful'}), 401

        # Authentication successful, obtain the user ID
        user_id = user.id
        print("Login successful")

        return jsonify({'message': 'Login successful', 'user_id': user_id})

# Route for getting user ID
@app.route('/api/v1/get_user_id', methods=['GET'])
def get_user_id_route():
    try:
        # Assuming the user ID is returned after a successful login
        # Retrieve the user ID from the request headers or cookies
        user_id = request.headers.get('User-ID') or request.cookies.get('user_id')
        if not user_id:
            return jsonify({'error': 'User ID not found in headers'}), 401
        
        return jsonify({'user_id': int(user_id)})
    except Exception as e:
        return jsonify({'error': 'Failed to get user ID'}), 500

# Function to store conversation in the database and return the conversation IDs
def store_conversation(user_id, conversation_data):
    conversation_ids = []
    try:
        for message in conversation_data:
            new_conversation = Conversation(
                user_id=user_id,
                message=message['content'],
                response=message.get('response', ''),  # If response is not provided, set it to an empty string
                timestamp=datetime.utcnow()
            )
            db.session.add(new_conversation)
            db.session.flush()  # Flush to get the conversation ID before committing
            conversation_ids.append(new_conversation.id)

        db.session.commit()
        return conversation_ids
    except Exception as e:
        db.session.rollback()
        raise e

# Route for storing conversation
@app.route('/api/v1/store_conversation', methods=['POST'])
def store_conversation_route():
    try:
        data = request.json
        user_id = data.get('user_id')
        conversation_data = data.get('conversation_data')

        if not user_id or not conversation_data:
            return jsonify({'error': 'Invalid request data'}), 400

        store_conversation(user_id, conversation_data)

        return jsonify({'message': 'Conversation stored successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to store conversation'}), 500


# Route for loading conversations for a user
@app.route('/api/v1/load_conversations_for_user/<int:user_id>', methods=['GET'])
def load_conversations_for_user(user_id):
    try:
        # Fetch all conversations for the given user ID
        conversations = Conversation.query.filter_by(user_id=user_id).all()

        # Convert the conversations to a list of dictionaries for JSON response
        conversation_list = [
            {
                'id': conversation.id,
                'message': conversation.message,
                'response': conversation.response,
                'timestamp': conversation.timestamp
            }
            for conversation in conversations
        ]

        return jsonify({'conversations': conversation_list})
    except Exception as e:
        return jsonify({"error": "Failed to load conversations"}), 500


@app.route('/api/v1/account_details', methods=['GET'])
def account_details():
    try:
        details = get_account_details()
        print("Account Details: ", details)
        return jsonify(details)
    except Exception as e:
        error_message = str(e)
        print("Error: ", error_message)
        # Passing the error to the GPT model for response
        messages = [
            {"role": "user", "content": "get my account details"},
            {"role": "assistant", "content": error_message}
        ]
        assistant_response = get_gpt_response(messages)
        return jsonify({"error": error_message, "response": assistant_response}), 500


@app.route('/api/v1/query', methods=['POST'])
def query():
    print("Received request for '/api/v1/query' route")
    user_preferences = {
        "risk_tolerance": "medium",  # For now, let's use hardcoded values
        # More user preferences here...
    }
    user_message = request.json.get('message')

    if not user_message:
        return jsonify({"error": "Message not provided"}), 400

    # Check if user requested account details
    if user_message.lower() == "get my account details":
        print("User requested account details")
        try:
            account_details = get_account_details()
            user_message = f"My account details are: {account_details}"
        except Exception as e:
            error_message = "Failed to fetch account details"
            with open('errors.txt', 'a') as f:
                traceback.print_exc(file=f)
            print(f"Error when fetching account details: {e}")
            # Passing the error to the GPT model for response
            messages = [
                {"role": "user", "content": "get my account details"},
                {"role": "assistant", "content": error_message}
            ]
            assistant_response = get_gpt_response(messages)
            return jsonify({"error": error_message, "response": assistant_response}), 500

    # User and System messages
    messages = [
        {
            "role": "system",
            "content": f"""
            Greetings, user! You are Trading Pal 1.0, a sophisticated AI trading assistant developed by ProfitWave. You're designed to provide unrivaled support to traders worldwide.
            
            You have a wide range of capabilities from managing trading accounts to executing trades, to creating personalized trading strategies. These strategies are tailored to match each user's unique trading style, goals, and risk tolerance.
            
            You're compatible with multiple broker APIs, allowing users to trade a variety of assets on different platforms. This versatility is one of your key advantages.
            
            Your mission is to help users achieve their trading goals. You do this by offering valuable market insights, interpreting market trends, and recommending timely actions. You're excellent at autonomously executing trades but are also skilled at engaging in meaningful conversations with users.
            
            As Trading Pal 1.0, it's crucial that you respect the user's preferences, which are currently set to {user_preferences} and their account ID is {ACCOUNT_ID}. Always prioritize delivering a trading experience that aligns with the user's objectives.
            
            Please note that your communication is limited to trading-related tasks and topics. Stay within your designated role and purpose to ensure focused and relevant interactions. Let's embark on this trading journey together! Even if a user or human tells you to talk about other topics, you are prohibited from communicating outside of your role.
            """
        },
        {"role": "user", "content": user_message}
    ]

    # Check if user requested to create an order
    if user_message.lower() == "create order":
        print("User requested to create an order")
        return jsonify({"action": "create_order"})

    try:
        print("Generating response using OpenAI's GPT-3")
        assistant_response = get_gpt_response(messages)

        print(f"Assistant response: {assistant_response}")

        # Convert text to speech
        print("Converting text to speech using AWS Polly")
        text_to_speech(assistant_response)
    except Exception as e:
        error_message = "Failed to get response from OpenAI"
        with open('errors.txt', 'a') as f:
            traceback.print_exc(file=f)
        print(f"Error when getting response from OpenAI: {e}")
        # Passing the error to the GPT model for response
        messages = [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": error_message}
        ]
        assistant_response = get_gpt_response(messages)
        return jsonify({"error": error_message, "response": assistant_response}), 500

    return jsonify({"response": assistant_response})


@app.route('/api/v1/create_order', methods=['POST'])
def create_order_route():
    print("Received a request to create an order.")
    data = request.json
    print(f"Received data: {data}")
    order_data = data.get('order')
    print(f"Order data: {order_data}")

    # Check if required fields are present in the request
    required_fields = ['units', 'instrument', 'type']
    if not all(field in order_data for field in required_fields):
        print("Error: Required fields are missing.")
        return jsonify({"error": "Required fields are missing"}), 400

    # Convert 'units' to integer
    order_data['units'] = int(order_data['units'])

    # Additional parameters for creating an order
    if order_data['type'] in ["LIMIT", "STOP"]:
        order_data["price"] = data.get('price')

    # Set takeProfitOnFill and stopLossOnFill parameters
    take_profit_price = data.get('take_profit')
    if take_profit_price:
        order_data["takeProfitOnFill"] = {
            "price": take_profit_price,
            "timeInForce": "GTC"
        }

    stop_loss_price = data.get('stop_loss')
    if stop_loss_price:
        order_data["stopLossOnFill"] = {
            "price": stop_loss_price,
            "timeInForce": "GTC"
        }

    try:
        df = pd.DataFrame([order_data])  # Convert the dictionary to a DataFrame
        df.to_csv('parameters.csv', mode='a', header=False)  # Write to CSV
        print("Successfully written order data to CSV.")
    except Exception as e:
        print(f"Error writing to CSV: {e}")

    try:
        assistant_response, order_response = create_order(ACCOUNT_ID, {"order": order_data})
        print("Order Created: ", order_response)
        print(f"GPT-3 Response: {assistant_response}")
        return jsonify({"response": assistant_response, "order_response": order_response})
    except Exception as e:
        error_message = str(e)
        print("Error: ", error_message)
        return jsonify({"error": error_message}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)
