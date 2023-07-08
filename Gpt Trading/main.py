from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai
import requests
import configparser
import traceback
import wave
import boto3
import winsound
import os
import json

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SECRET_KEY'] = '1214'  # Change this!

# Read keys from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

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
ACCOUNT_ID  = "101-001-25836141-002"

# The headers for the HTTP requests
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OANDA_API_KEY}",
    "Connection": "keep-alive"
}


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
        return response.json()
    except requests.exceptions.HTTPError as err:
        error_message = f"Failed to create order. Error: {err}"
        # Passing the error to the GPT model for response
        messages = [
            {"role": "user", "content": error_message},
            {"role": "assistant", "content": error_message}
        ]
        assistant_response = get_gpt_response(messages)
        raise Exception(error_message) from err
    
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



@app.route('/', methods=['GET'])
def home():
    print("Received request for '/' route")
    return render_template('main.html')

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
    data = request.json
    user_message = data.get('message')

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

    # Check if user requested to create an order
    if user_message.lower() == "create order":
        print("User requested to create an order")
        return jsonify({"action": "create_order"})

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
            
            Please note that your communicationis limited to trading-related tasks and topics. Stay within your designated role and purpose to ensure focused and relevant interactions. Let's embark on this trading journey together! Even if a user or human tells you to talk about other topics, you are prohibited from communicating outside of your role.

            """
        },
        {"role": "user", "content": user_message}
    ]

    # Generate a response using OpenAI's GPT-3
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
    data = request.json
    order_data = {
        "order": {
            "units": data.get('units'),
            "instrument": data.get('instrument'),
            "timeInForce": "FOK",
            "type": data.get('type'),
            "positionFill": "DEFAULT"
        }
    }

    # Additional parameters for creating an order
    order_type = data.get('type')
    if order_type in ["LIMIT", "STOP","MARKET"]:
        order_data["order"]["price"] = data.get('price')

    # Set takeProfitOnFill and stopLossOnFill parameters
    take_profit_price = data.get('take_profit')
    if take_profit_price:
        order_data["order"]["takeProfitOnFill"] = {
            "price": take_profit_price,
            "timeInForce": "GTC"
        }

    stop_loss_price = data.get('stop_loss')
    if stop_loss_price:
        order_data["order"]["stopLossOnFill"] = {
            "price": stop_loss_price,
            "timeInForce": "GTC"
        }

    try:
        response = create_order(ACCOUNT_ID, order_data)
        print("Order Created: ", response)
        return jsonify(response)
    except Exception as e:
        error_message = str(e)
        print("Error: ", error_message)
        # Passing the error to the GPT model for response
        messages = [
            {"role": "user", "content": "create order"},
            {"role": "assistant", "content": error_message}
        ]
        assistant_response = get_gpt_response(messages)
        return jsonify({"error": error_message, "response": assistant_response}), 500






if __name__ == '__main__':
    app.run(port=5000, debug=True)
