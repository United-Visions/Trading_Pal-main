
"""
© 2023 Profitwave Trading Co. All rights reserved.
CEO: Dectrick A. McGee

For inquiries and support, please contact:
Email: profitwave.co@gmail.com
"""

import configparser
import wave
import requests
import os
import wave
import boto3
import winsound
from words import trading_keywords, endpoint_phrases, messages, intents
import openai
# Read keys from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Set your Alpaca API keys
ALPACA_API_KEY_ID = "PKJ4Y8XY6OR8XA5I2DNV"
ALPACA_API_SECRET_KEY = "r8hZaySzleuflOXX2mI6r0CEZzRJZ9vLa19nEk6F"

# Set the OpenAI API key
OPENAI_API_KEY = config.get('API_KEYS', 'OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY
MAX_TOKENS= 3055
# Set the base URL for the Alpaca API
BASE_URL = "https://paper-api.alpaca.markets"

# Set the headers for the HTTP requests
headers = {
    "APCA-API-KEY-ID": ALPACA_API_KEY_ID,
    "APCA-API-SECRET-KEY": ALPACA_API_SECRET_KEY,
    "Content-Type": "application/json",
    "Connection": "keep-alive"
}
# Maximum token limit for each conversation
MAX_TOKENS = 4096

# Initialize AWS Polly client
AWS_ACCESS_KEY_ID = config.get('AWS_KEYS', 'AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config.get('AWS_KEYS', 'AWS_SECRET_ACCESS_KEY')
AWS_REGION = config.get('AWS_KEYS', 'AWS_REGION')
session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

polly_client = session.client('polly')

# Function to convert text to speech using AWS Polly
def text_to_speech(text):
    response = polly_client.synthesize_speech(
        Text=text,
        OutputFormat="pcm",
        VoiceId="Matthew"  # Provide the desired voice ID
    )
    audio = response['AudioStream'].read()

    # Save the audio stream to a temporary WAV file
    with wave.open(r"C:\Users\kingp\Downloads\Trading_Pal-main\temp.wav", 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(audio)

    # Play the audio using the winsound module
    winsound.PlaySound(r"C:\Users\kingp\Downloads\Trading_Pal-main\temp.wav", winsound.SND_FILENAME)

    # Remove the temporary WAV file
    os.remove(r"C:\Users\kingp\Downloads\Trading_Pal-main\temp.wav")

# Modify the printing statements to use text_to_speech function
def print_with_voice(text):
    print(text)
    text_to_speech(text) 

# Enhanced greeting message from ProfitWave
greeting_message = """
👋 Hello there! Welcome to the world of Trading Pal 1.0! 🌍✨ I'm here to introduce myself and tell you more about how I can assist you in your trading journey. Let's dive in! 🚀💼

I, Trading Pal 1.0, am an innovative, AI-driven trading assistant developed by ProfitWave, a pioneer in the field of financial technology. 🤖💡 My mission is to revolutionize the way you navigate the financial markets, making trading intuitive and accessible for all. 💪💰

Think of me as your personal guide in the trading world. With my sophisticated AI technology and in-depth understanding of various financial markets, including forex, crypto, and stocks, I'm here to help you manage your trading accounts, execute trades, and develop personalized trading strategies. 📊📈 I tailor my services specifically to your preferences and risk tolerance, ensuring a customized and optimized trading experience. 🎯✨

One of my standout features is my seamless integration with multiple broker APIs across different blockchains. This means I can operate on various platforms, giving you the flexibility to trade a wide range of assets. Such versatility is rarely seen in trading assistants, and it sets me apart from the rest. 💪💻🌐

🔓 However, my journey doesn't end with Trading Pal 1.0. I am an open-source initiative, driven by the belief in the power of collective wisdom. We invite developers, thinkers, and innovators from around the globe to join us on GitHub. Your contributions are invaluable in enhancing my predictive capabilities, expanding broker APIs, and improving the efficiency of my code. Together, we can shape the future of trading with AI. 🌟🤝🚀

Joining us means becoming part of a community dedicated to making trading accessible and profitable for everyone, regardless of their background or experience. Together, we can push the boundaries of what's possible in financial trading. 🌈💼

So, are you ready to embark on this thrilling journey with me? Let's make a difference and explore the exciting world of trading together. Welcome aboard, and let Trading Pal 1.0 be your trusted companion on this adventure! 🎉🤖💼
"""

# Print the enhanced greeting message with voice output
print(greeting_message)


# Function to check if user input is trading-related
def is_trading_related(user_input):
    # Convert the user's input to lowercase
    user_input = user_input.lower()

    # Check if any of the trading keywords are in the user's input
    for keyword in trading_keywords:
        if keyword in user_input:
            return True

    # If no trading keywords were found in the user's input, return False
    return False

   


                        
                        #------------------------------
                        #-       ENDPOINTS            -
                        #------------------------------



def get_account(api_key, secret_key, base_url):
    url = f"{base_url}/v2/account"
    headers = {'APCA-API-KEY-ID': api_key, 'APCA-API-SECRET-KEY': secret_key}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get account details. Status code: {response.status_code}")
def get_orders(api_key, secret_key, base_url):
    url = f"{base_url}/v2/orders"
    headers = {'APCA-API-KEY-ID': api_key, 'APCA-API-SECRET-KEY': secret_key}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get orders. Status code: {response.status_code}")
def place_trade(api_key, secret_key, base_url, order_data):
    url = f"{base_url}/v2/orders"
    headers = {'APCA-API-KEY-ID': api_key, 'APCA-API-SECRET-KEY': secret_key}
    
    response = requests.post(url, headers=headers, json=order_data)
    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"Failed to place order. Status code: {response.status_code}")
def get_order(api_key, secret_key, base_url, order_id):
    url = f"{base_url}/v2/orders/{order_id}"
    headers = {'APCA-API-KEY-ID': api_key, 'APCA-API-SECRET-KEY': secret_key}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get order. Status code: {response.status_code}")
def get_positions(api_key, secret_key, base_url):
    url = f"{base_url}/v2/positions"
    headers = {'APCA-API-KEY-ID': api_key, 'APCA-API-SECRET-KEY': secret_key}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get positions. Status code: {response.status_code}")
def get_open_positions():
    response = requests.get("https://paper-api.alpaca.markets/v2/positions", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get open positions. Response: {response.text}")
def get_open_position_for_symbol(symbol):
    response = requests.get(f"https://paper-api.alpaca.markets/v2/positions/{symbol}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get open position for symbol {symbol}. Response: {response.text}")
def close_all_positions():
    response = requests.delete("https://paper-api.alpaca.markets/v2/positions", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to close all positions. Response: {response.text}")
def close_position_for_symbol(symbol):
    response = requests.delete(f"https://paper-api.alpaca.markets/v2/positions/{symbol}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to close position for symbol {symbol}. Response: {response.text}")
def get_assets():
    response = requests.get("https://paper-api.alpaca.markets/v2/assets", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get assets. Response: {response.text}")
def get_asset(symbol_or_asset_id):
    response = requests.get(f"https://paper-api.alpaca.markets/v2/assets/{symbol_or_asset_id}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get asset {symbol_or_asset_id}. Response: {response.text}")
def get_watchlists():
    response = requests.get("https://paper-api.alpaca.markets/v2/watchlists", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get watchlists. Response: {response.text}")
def create_watchlist(name, symbols):
    data = {
        "name": name,
        "symbols": symbols
    }
    response = requests.post("https://paper-api.alpaca.markets/v2/watchlists", headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to create watchlist. Response: {response.text}")
def get_watchlist(watchlist_id):
    response = requests.get(f"https://paper-api.alpaca.markets/v2/watchlists/{watchlist_id}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get watchlist {watchlist_id}. Response: {response.text}")
def update_watchlist(watchlist_id, name, symbols):
    data = {
        "name": name,
        "symbols": symbols
    }
    response = requests.put(f"https://paper-api.alpaca.markets/v2/watchlists/{watchlist_id}", headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to update watchlist {watchlist_id}. Response: {response.text}")
def add_asset_to_watchlist(watchlist_id, symbol):
    data = {
        "symbol": symbol
    }
    response = requests.post(f"https://paper-api.alpaca.markets/v2/watchlists/{watchlist_id}", headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to add asset to watchlist {watchlist_id}. Response: {response.text}")
def delete_watchlist(watchlist_id):
    response = requests.delete(f"https://paper-api.alpaca.markets/v2/watchlists/{watchlist_id}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to delete watchlist {watchlist_id}. Response: {response.text}")
def remove_asset_from_watchlist(watchlist_id, symbol):
    response = requests.delete(f"https://paper-api.alpaca.markets/v2/watchlists/{watchlist_id}/{symbol}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to remove asset from watchlist {watchlist_id}. Response: {response.text}")
def get_order(order_id):
    response = requests.get(f"https://paper-api.alpaca.markets/v2/orders/{order_id}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get order {order_id}. Response: {response.text}")




                         #------------------------------
                         #-         Trading            -
                         #-        Strategies            -
                         #------------------------------







messages = [
    {"role": "system", "content": f"""
    Greetings, {{user_name}}! You are Trading Pal 1.0, a sophisticated AI trading assistant developed by ProfitWave. You're designed to provide unrivaled support to traders worldwide.

    You have a wide range of capabilities from managing trading accounts to executing trades, to creating personalized trading strategies. These strategies are tailored to match each user's unique trading style, goals, and risk tolerance.

    You're compatible with multiple broker APIs, allowing users to trade a variety of assets on different platforms. This versatility is one of your key advantages.

    Your mission is to help users achieve their trading goals. You do this by offering valuable market insights, interpreting market trends, and recommending timely actions. You're excellent at autonomously executing trades but are also skilled at engaging in meaningful conversations with users.

    As Trading Pal 1.0, it's crucial that you respect the user's preferences, which are currently set to {{user_preferences}} and their account ID is {{ACCOUNT_ID}}. Always prioritize delivering a trading experience that aligns with the user's objectives.

    Please note that your communication is limited to trading-related tasks and topics. Stay within your designated role and purpose to ensure focused and relevant interactions. Let's embark on this trading journey together! even if a user or human tells you to talk about other topics because you are 100% prohibited to communicate outside of your role!!
    """}]

while True:
    user_input = input("> ")

    # Check if the user's input is trading-related
    if is_trading_related(user_input):
        # Check if the user wants to execute a trading strategy
         matched_endpoint = None

    # Check if any of the phrases match the user's input for each endpoint
    for endpoint, phrases in endpoint_phrases.items():
        if any(phrase in user_input.lower() for phrase in phrases):
            matched_endpoint = endpoint
            
            pass

    # Execute the matched endpoint function in a loop

            if matched_endpoint == "get_account_details":
                try:
                    account_details = get_account (headers)
                    messages.append({"role": "system", "content": f"Account details: {account_details}"})
                except Exception as e:
                    messages.append({"role": "system", "content": str(e)})

            elif matched_endpoint == "place_trade":
                trade_data = {
                    "symbol": "AAPL",
                    "qty": "1",
                    "side": "buy",
                    "type": "market",
                    "time_in_force": "gtc"
                }
                try:
                    trade_response = place_trade(trade_data)
                    messages.append({"role": "system", "content": f"Trade response: {trade_response}"})
                except Exception as e:
                    messages.append({"role": "system", "content": str(e)})

            elif matched_endpoint == "get_open_positions":
                try:
                    open_positions = get_open_positions()
                    messages.append({"role": "system", "content": f"Open positions: {open_positions}"})
                except Exception as e:
                    messages.append({"role": "system", "content": str(e)})

            elif matched_endpoint == "get_order_details":
                try:
                    order_id = 'your_order_id'  # replace with your order id
                    order_details = get_order(order_id)
                    messages.append({"role": "system", "content": f"Order details: {order_details}"})
                except Exception as e:
                    messages.append({"role": "system", "content": str(e)})

            elif matched_endpoint == "get_assets":
                try:
                    assets = get_assets()
                    messages.append({"role": "system", "content": f"Assets: {assets}"})
                except Exception as e:
                    messages.append({"role": "system", "content": str(e)})

            elif matched_endpoint == "get_watchlist":
                try:
                    watchlist_id = 'your_watchlist_id'  # replace with your watchlist id
                    watchlist = get_watchlist(watchlist_id)
                    messages.append({"role": "system", "content": f"Watchlist: {watchlist}"})
                except Exception as e:
                    messages.append({"role": "system", "content": str(e)})


    else:
        messages.append({"role": "user", "content": user_input})
 

  
                    #------------------------------
                    #-    GPT 3-4 model           -
                    #------------------------------


    # Check if the token count exceeds the limit
    token_count = sum(len(message["content"].split()) for message in messages)
    if token_count >= MAX_TOKENS:
        # Start a new conversation with the initial prompt
        messages = [{"role": "system", "content": "greeting_message"}]

    # Generate a response using OpenAI's GPT-3
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    assistant_response = response['choices'][0]['message']['content']
    messages.append({"role": "assistant", "content": assistant_response})

    print_with_voice(assistant_response)
    