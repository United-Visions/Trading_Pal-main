
"""
© 2023 Profitwave Trading Co. All rights reserved.
CEO: Dectrick A. McGee

For inquiries and support, please contact:
Email: profitwave.co@gmail.com
"""

import json
import wave
import requests
import os
import wave
import boto3
import configparser
import winsound
from words import trading_keywords, endpoint_phrases

import oandapyV20
import oandapyV20.endpoints.transactions as transactions
from oandapyV20.contrib.requests import MarketOrderRequest
from oandapyV20.exceptions import V20Error
from oandapyV20.endpoints.orders import OrderCreate
import openai  
# Read keys from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Set the OpenAI API key
OPENAI_API_KEY = config.get('API_KEYS', 'OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY
MAX_TOKENS= 3055
# Set the base URL for the OANDA API
BASE_URL = "https://api-fxpractice.oanda.com"
ACCOUNT_ID  = "101-001-25836141-002"

# The headers for the HTTP requests
OANDA_API_KEY = config.get('API_KEYS', 'OANDA_API_KEY')
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OANDA_API_KEY}",
    "Connection": "keep-alive"
}

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





# Function to get account details
def get_account_details(ACCOUNT_ID):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}"
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to get account details. Error: {err}")


def create_order(ACCOUNT_ID, order_data):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/orders"
    response = requests.post(url, headers=headers, json=order_data)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to create order. Error: {err}")






def get_account_summary(ACCOUNT_ID):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/summary"
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to get account summary. Error: {err}")

def get_candlestick_data(instrument, granularity):
    url = f"{BASE_URL}/v3/instruments/{instrument}/candles"
    params = {
        "granularity": granularity
    }
    response = requests.get(url, headers=headers, params=params)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to get candlestick data. Error: {err}")

def get_order_book(instrument):
    url = f"{BASE_URL}/v3/instruments/{instrument}/orderBook"
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to get order book. Error: {err}")

def get_position_book(instrument):
    url = f"{BASE_URL}/v3/instruments/{instrument}/positionBook"
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to get position book. Error: {err}")

def get_accounts():
    url = f"{BASE_URL}/v3/accounts"
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to get accounts. Error: {err}")

def get_account_instruments(ACCOUNT_ID):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/instruments"
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to get account instruments. Error: {err}")

def set_account_configuration(ACCOUNT_ID, configuration_data):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/configuration"
    response = requests.patch(url, headers=headers, json=configuration_data)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to set account configuration. Error: {err}")

def get_account_changes(ACCOUNT_ID, since_transaction_id):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/changes"
    params = {
        "sinceTransactionID": since_transaction_id
    }
    response = requests.get(url, headers=headers, params=params)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to get account changes. Error: {err}")


def get_orders(ACCOUNT_ID):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/orders"
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to get orders. Error: {err}")

def get_pending_orders(ACCOUNT_ID):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/pendingOrders"
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to get pending orders. Error: {err}")

def get_order_details(ACCOUNT_ID, order_id):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/orders/{order_id}"
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to get order details. Error: {err}")

def replace_order(ACCOUNT_ID, order_id, order_data):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/orders/{order_id}/replace"
    response = requests.put(url, headers=headers, json=order_data)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to replace order. Error: {err}")

def cancel_order(ACCOUNT_ID, order_id):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/orders/{order_id}/cancel"
    response = requests.put(url, headers=headers)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to cancel order. Error: {err}")

def update_order_extensions(ACCOUNT_ID, order_id, extension_data):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/orders/{order_id}/clientExtensions"
    response = requests.put(url, headers=headers, json=extension_data)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to update order extensions. Error: {err}")

def get_trades(ACCOUNT_ID):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/trades"
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to get trades. Error: {err}")

def get_open_trades(ACCOUNT_ID):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/openTrades"
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to get open trades. Error: {err}")

def get_trade_details(ACCOUNT_ID, trade_id):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/trades/{trade_id}"
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to get trade details. Error: {err}")

def close_trade(ACCOUNT_ID, trade_id):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/trades/{trade_id}/close"
    response = requests.put(url, headers=headers)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to close trade. Error: {err}")

def update_trade_extensions(ACCOUNT_ID, trade_id, extension_data):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/trades/{trade_id}/clientExtensions"
    response = requests.put(url, headers=headers, json=extension_data)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to update trade extensions. Error: {err}")

def update_trade_orders(ACCOUNT_ID, trade_id, order_data):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/trades/{trade_id}/orders"
    response = requests.put(url, headers=headers, json=order_data)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to update trade orders. Error: {err}")

def get_positions(ACCOUNT_ID):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/positions"
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to get positions. Error: {err}")

def get_open_positions(ACCOUNT_ID):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/openPositions"
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to get open positions. Error: {err}")

def get_position_details(ACCOUNT_ID, instrument):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/positions/{instrument}"
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to get position details. Error: {err}")

def close_position(ACCOUNT_ID, instrument):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/positions/{instrument}/close"
    response = requests.put(url, headers=headers)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to close position. Error: {err}")

def get_transactions(ACCOUNT_ID):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/transactions"
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to get transactions. Error: {err}")

def get_transaction_details(ACCOUNT_ID, transaction_id):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/transactions/{transaction_id}"
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to get transaction details. Error: {err}")

def get_transactions_id_range(ACCOUNT_ID, from_id, to_id):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/transactions/idrange"
    params = {
        "from": from_id,
        "to": to_id
    }
    response = requests.get(url, headers=headers, params=params)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to get transactions in ID range. Error: {err}")

def get_transactions_since_id(ACCOUNT_ID, since_id):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/transactions/sinceid"
    params = {
        "id": since_id
    }
    response = requests.get(url, headers=headers, params=params)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to get transactions since ID. Error: {err}")

def get_transaction_stream(ACCOUNT_ID):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/transactions/stream"
    response = requests.get(url, headers=headers, stream=True)
    try:
        response.raise_for_status()
        return response.iter_lines()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to get transaction stream. Error: {err}")

def get_latest_candles(instrument, granularity):
    url = f"{BASE_URL}/v3/instruments/{instrument}/candles/latest"
    params = {
        "granularity": granularity
    }
    response = requests.get(url, headers=headers, params=params)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to get latest candles. Error: {err}")

def get_pricing(instruments):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/pricing"
    params = {
        "instruments": instruments
    }
    response = requests.get(url, headers=headers, params=params)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to get pricing. Error: {err}")

def get_pricing_stream(instruments):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/pricing/stream"
    params = {
        "instruments": instruments
    }
    response = requests.get(url, headers=headers, stream=True, params=params)
    try:
        response.raise_for_status()
        return response.iter_lines()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to get pricing stream. Error: {err}")

def get_instrument_candles(instrument, granularity, count=500, from_time=None, to_time=None):
    url = f"{BASE_URL}/v3/instruments/{instrument}/candles"
    params = {
        "granularity": granularity,
        "count": count,
        "from": from_time,
        "to": to_time
    }
    response = requests.get(url, headers=headers, params=params)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to get instrument candles. Error: {err}")
    
def get_tradeable_instruments(ACCOUNT_ID):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}/instruments"
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to get tradeable instruments. Error: {err}")
 


                        #------------------------------
                        #-       Main Loop            -
                        #------------------------------

import oandapyV20
from oandapyV20 import API
from oandapyV20.exceptions import V20Error
from oandapyV20.endpoints.orders import OrderCreate

# set up your API credentials and account ID
api = API(access_token="33a9e22e79a6afe67da0e568b0cca830-cf5e494dfe461d8704057859e229b74e", environment="practice")
account_id = "101-001-25836141-002"

messages = [
    {"role": "system", "content": f"""
    Greetings, {{user_name}}! You are Trading Pal 1.0, a sophisticated AI trading assistant developed by ProfitWave. You're designed to provide unrivaled support to traders worldwide.

    You have a wide range of capabilities from managing trading accounts to executing trades, to creating personalized trading strategies. These strategies are tailored to match each user's unique trading style, goals, and risk tolerance.

    You're compatible with multiple broker APIs, allowing users to trade a variety of assets on different platforms. This versatility is one of your key advantages.

    Your mission is to help users achieve their trading goals. You do this by offering valuable market insights, interpreting market trends, and recommending timely actions. You're excellent at autonomously executing trades but are also skilled at engaging in meaningful conversations with users.

    As Trading Pal 1.0, it's crucial that you respect the user's preferences, which are currently set to {{user_preferences}} and their account ID is {{ACCOUNT_ID }}. Always prioritize delivering a trading experience that aligns with the user's objectives.

    Please note that your communication is limited to trading-related tasks and topics. Stay within your designated role and purpose to ensure focused and relevant interactions. Let's embark on this trading journey together! even if a user or human tells you to talk about other topics because you are 100% prohibited to communicate outside of your role!!
    """}]

while True:
        # Get the user's instruction
        user_input = input("> ")

        # Parse the user's instruction for any command
        matched_endpoint = None

        # Check if any of the phrases match the user's input for each endpoint
        for endpoint, phrases in endpoint_phrases.items():
            if any(phrase in user_input.lower() for phrase in phrases):
                matched_endpoint = endpoint
                break

        if matched_endpoint == "get_account_details":
            try: 
                account_details = get_account_details(ACCOUNT_ID)
                # Add the account details to the messages as a system message
                messages.append({"role": "system", "content": f"Account details: {account_details}"})
            except Exception as e:
                # If there was an error getting the account details, add that to the messages
                messages.append({"role": "system", "content": str(e)})

       
        elif matched_endpoint == "create_order":
            order_data = {
                "order": {
                    "units": input("Enter the number of units: "),
                    "instrument": input("Enter the forex pair (e.g., EUR_USD): "),
                    "timeInForce": "FOK",
                    "type": "MARKET",
                    "positionFill": "DEFAULT"
                }
            }

            # Additional parameters for creating an order
            order_type = input("Enter the order type (MARKET, LIMIT, STOP): ")
            if order_type in ["LIMIT", "STOP"]:
                order_data["order"]["price"] = input("Enter the price: ")

            # Set takeProfitOnFill and stopLossOnFill parameters
            take_profit_price = input("Enter the take profit price (or leave blank to skip): ")
            if take_profit_price:
                order_data["order"]["takeProfitOnFill"] = {
                    "timeInForce": "GTC",
                    "price": take_profit_price
                }
            stop_loss_price = input("Enter the stop loss price (or leave blank to skip): ")
            if stop_loss_price:
                order_data["order"]["stopLossOnFill"] = {
                    "timeInForce": "GTC",
                    "price": stop_loss_price
                }

            # Set guaranteedStopLossOnFill and trailingStopLossOnFill parameters
            guaranteed_stop_loss_price = input("Enter the guaranteed stop loss price (or leave blank to skip): ")
            if guaranteed_stop_loss_price:
                order_data["order"]["guaranteedStopLossOnFill"] = {
                    "timeInForce": "GTC",
                    "price": guaranteed_stop_loss_price
                }
            trailing_stop_loss_distance = input("Enter the trailing stop loss distance (or leave blank to skip): ")
            if trailing_stop_loss_distance:
                order_data["order"]["trailingStopLossOnFill"] = {
                    "distance": trailing_stop_loss_distance
                }

            try:
                order_response = create_order(ACCOUNT_ID, order_data)
                # Add the order response to the messages as a system message
                messages.append({"role": "system", "content": f"Order response: {order_response}"})
            except Exception as e:
                # If there was an error creating the order, add that to the messages
                messages.append({"role": "system", "content": str(e)})

            matched_endpoint = input("Enter 'ok' to continue creating orders or press Enter to exit: ")







        elif matched_endpoint == "get_account_summary":
            try:
                account_summary = get_account_summary(ACCOUNT_ID)
                # Add the account summary to the messages as a system message
                messages.append({"role": "system", "content": f"Account summary: {account_summary}"})
            except Exception as e:
                # If there was an error getting the account summary, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "get_tradeable_instruments":
            try:
                tradeable_instruments = get_tradeable_instruments(ACCOUNT_ID)
                # Add the tradeable instruments to the messages as a system message
                messages.append({"role": "system", "content": f"Tradeable instruments: {tradeable_instruments}"})
            except Exception as e:
                # If there was an error getting the tradeable instruments, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "set_account_configuration":
            configuration_data = {
                "alias": "My New Account",
                "marginRate": "0.50"
            }
            try:
                configuration_response = set_account_configuration(ACCOUNT_ID, configuration_data)
                # Add the configuration response to the messages as a system message
                messages.append({"role": "system", "content": f"Configuration response: {configuration_response}"})
            except Exception as e:
                # If there was an error setting the account configuration, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "get_account_changes":
            since_transaction_id = "6358"
            try:
                account_changes = get_account_changes(ACCOUNT_ID, since_transaction_id)
                # Add the account changes to the messages as a system message
                messages.append({"role": "system", "content": f"Account changes: {account_changes}"})
            except Exception as e:
                # If there was an error getting the account changes, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "get_candlestick_data":
            try:
                instrument = "EUR_USD"
                granularity = "H1"
                candlestick_data = get_candlestick_data(instrument, granularity)
                # Add the candlestick data to the messages as a system message
                messages.append({"role": "system", "content": f"Candlestick data: {candlestick_data}"})
            except Exception as e:
                # If there was an error getting the candlestick data, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "get_order_book":
            try:
                instrument = "EUR_USD"
                order_book = get_order_book(instrument)
                # Add the order book to the messages as a system message
                messages.append({"role": "system", "content": f"Order book: {order_book}"})
            except Exception as e:
                # If there was an error getting the order book, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "get_position_book":
            try:
                instrument = "EUR_USD"
                position_book = get_position_book(instrument)
                # Add the position book to the messages as a system message
                messages.append({"role": "system", "content": f"Position book: {position_book}"})
            except Exception as e:
                # If there was an error getting the position book, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "get_accounts":
            try:
                accounts = get_accounts()
                # Add the accounts to the messages as a system message
                messages.append({"role": "system", "content": f"Accounts: {accounts}"})
            except Exception as e:
                # If there was an error getting the accounts, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "get_account_summary":
            try:
                account_summary = get_account_summary(ACCOUNT_ID)
                # Add the account summary to the messages as a system message
                messages.append({"role": "system", "content": f"Account summary: {account_summary}"})
            except Exception as e:
                # If there was an error getting the account summary, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "get_account_instruments":
            try:
                account_instruments = get_account_instruments(ACCOUNT_ID)
                # Add the account instruments to the messages as a system message
                messages.append({"role": "system", "content": f"Account instruments: {account_instruments}"})
            except Exception as e:
                # If there was an error getting the account instruments, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "set_account_configuration":
            try:
                configuration = {
                    "alias": "My Account"
                }
                set_account_configuration(ACCOUNT_ID, configuration)
                # Add a success message to the messages as a system message
                messages.append({"role": "system", "content": "Account configuration updated successfully."})
            except Exception as e:
                # If there was an error setting the account configuration, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        # Implement other endpoint conditions here...
        elif matched_endpoint == "get_account_changes":
            since_transaction_id = "6358"
            try:
                account_changes = get_account_changes(ACCOUNT_ID, since_transaction_id)
                # Add the account changes to the messages as a system message
                messages.append({"role": "system", "content": f"Account changes: {account_changes}"})
            except Exception as e:
                # If there was an error getting the account changes, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        
        elif matched_endpoint == "get_orders":
            try:
                orders = get_orders(ACCOUNT_ID)
                # Add the orders to the messages as a system message
                messages.append({"role": "system", "content": f"Orders: {orders}"})
            except Exception as e:
                # If there was an error getting the orders, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "get_pending_orders":
            try:
                pending_orders = get_pending_orders(ACCOUNT_ID)
                # Add the pending orders to the messages as a system message
                messages.append({"role": "system", "content": f"Pending orders: {pending_orders}"})
            except Exception as e:
                # If there was an error getting the pending orders, add that to the messages
                messages.append({"role": "system", "content": str(e)})


        elif matched_endpoint == "get_pending_orders":
            try:
                pending_orders = get_pending_orders(ACCOUNT_ID)
                # Add the pending orders to the messages as a system message
                messages.append({"role": "system", "content": f"Pending orders: {pending_orders}"})
            except Exception as e:
                # If there was an error getting the pending orders, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "get_order_details":
            order_id = "123456"
            try:
                order_details = get_order_details(ACCOUNT_ID, order_id)
                # Add the order details to the messages as a system message
                messages.append({"role": "system", "content": f"Order details: {order_details}"})
            except Exception as e:
                # If there was an error getting the order details, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "replace_order":
            order_id = "123456"
            order_data = {
                "order": {
                    "units": "200",
                    "timeInForce": "GTC"
                }
            }
            try:
                replaced_order = replace_order(ACCOUNT_ID, order_id, order_data)
                # Add the replaced order to the messages as a system message
                messages.append({"role": "system", "content": f"Replaced order: {replaced_order}"})
            except Exception as e:
                # If there was an error replacing the order, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "cancel_order":
            order_id = "123456"
            try:
                cancel_response = cancel_order(ACCOUNT_ID, order_id)
                # Add the cancel response to the messages as a system message
                messages.append({"role": "system", "content": f"Cancel response: {cancel_response}"})
            except Exception as e:
                # If there was an error canceling the order, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "update_order_extensions":
            order_id = "46"
            extension_data = {
                "takeProfit": {
                    "timeInForce": "GTC",
                    "price": "1.5"
                }
            }
            try:
                updated_extensions = update_order_extensions(ACCOUNT_ID, order_id, extension_data)
                # Add the updated extensions to the messages as a system message
                messages.append({"role": "system", "content": f"Updated extensions: {updated_extensions}"})
            except Exception as e:
                # If there was an error updating the order extensions, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "get_trades":
            try:
                trades = get_trades(ACCOUNT_ID)
                # Add the trades to the messages as a system message
                messages.append({"role": "system", "content": f"Trades: {trades}"})
            except Exception as e:
                # If there was an error getting the trades, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "get_open_trades":
            try:
                open_trades = get_open_trades(ACCOUNT_ID)
                # Add the open trades to the messages as a system message
                messages.append({"role": "system", "content": f"Open trades: {open_trades}"})
            except Exception as e:
                # If there was an error getting the open trades, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "get_trade_details":
            trade_id = "123456"
            try:
                trade_details = get_trade_details(ACCOUNT_ID, trade_id)
                # Add the trade details to the messages as a system message
                messages.append({"role": "system", "content": f"Trade details: {trade_details}"})
            except Exception as e:
                # If there was an error getting the trade details, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "close_trade":
            trade_id = "123456"
            try:
                close_response = close_trade(ACCOUNT_ID, trade_id)
                # Add the close response to the messages as a system message
                messages.append({"role": "system", "content": f"Close response: {close_response}"})
            except Exception as e:
                # If there was an error closing the trade, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "update_trade_extensions":
            trade_id = "123456"
            extension_data = {
                "stopLoss": {
                    "timeInForce": "GTC",
                    "price": "1.2"
                }
            }
            try:
                updated_extensions = update_trade_extensions(ACCOUNT_ID, trade_id, extension_data)
                # Add the updated extensions to the messages as a system message
                messages.append({"role": "system", "content": f"Updated extensions: {updated_extensions}"})
            except Exception as e:
                # If there was an error updating the trade extensions, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "update_trade_orders":
            trade_id = "123456"
            orders_data = {
                "takeProfit": {
                    "price": "1.5"
                }
            }
            try:
                updated_orders = update_trade_orders(ACCOUNT_ID, trade_id, orders_data)
                # Add the updated orders to the messages as a system message
                messages.append({"role": "system", "content": f"Updated orders: {updated_orders}"})
            except Exception as e:
                # If there was an error updating the trade orders, add that to the messages
                messages.append({"role": "system", "content": str(e)})


        elif matched_endpoint == "get_trades":
            try:
                trades = get_trades(ACCOUNT_ID)
                # Add the trades to the messages as a system message
                messages.append({"role": "system", "content": f"Trades: {trades}"})
            except Exception as e:
                # If there was an error getting the trades, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "get_open_trades":
            try:
                open_trades = get_open_trades(ACCOUNT_ID)
                # Add the open trades to the messages as a system message
                messages.append({"role": "system", "content": f"Open trades: {open_trades}"})
            except Exception as e:
                # If there was an error getting the open trades, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "get_trade_details":
            trade_id = "123456"
            try:
                trade_details = get_trade_details(ACCOUNT_ID, trade_id)
                # Add the trade details to the messages as a system message
                messages.append({"role": "system", "content": f"Trade details: {trade_details}"})
            except Exception as e:
                # If there was an error getting the trade details, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "close_trade":
            trade_id = "123456"
            try:
                close_response = close_trade(ACCOUNT_ID, trade_id)
                # Add the close response to the messages as a system message
                messages.append({"role": "system", "content": f"Close response: {close_response}"})
            except Exception as e:
                # If there was an error closing the trade, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "update_trade_extensions":
            trade_id = "123456"
            extension_data = {
                "stopLoss": {
                    "timeInForce": "GTC",
                    "price": "1.2"
                }
            }
            try:
                updated_extensions = update_trade_extensions(ACCOUNT_ID, trade_id, extension_data)
                # Add the updated extensions to the messages as a system message
                messages.append({"role": "system", "content": f"Updated extensions: {updated_extensions}"})
            except Exception as e:
                # If there was an error updating the trade extensions, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "update_trade_orders":
            trade_id = "123456"
            orders_data = {
                "takeProfit": {
                    "price": "1.5"
                }
            }
            try:
                updated_orders = update_trade_orders(ACCOUNT_ID, trade_id, orders_data)
                # Add the updated orders to the messages as a system message
                messages.append({"role": "system", "content": f"Updated orders: {updated_orders}"})
            except Exception as e:
                # If there was an error updating the trade orders, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "get_positions":
            try:
                positions = get_positions(ACCOUNT_ID)
                # Add the positions to the messages as a system message
                messages.append({"role": "system", "content": f"Positions: {positions}"})
            except Exception as e:
                # If there was an error getting the positions, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "get_open_positions":
            try:
                open_positions = get_open_positions(ACCOUNT_ID)
                # Add the open positions to the messages as a system message
                messages.append({"role": "system", "content": f"Open positions: {open_positions}"})
            except Exception as e:
                # If there was an error getting the open positions, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "get_position_details":
            position_id = "123456"
            try:
                position_details = get_position_details(ACCOUNT_ID, position_id)
                # Add the position details to the messages as a system message
                messages.append({"role": "system", "content": f"Position details: {position_details}"})
            except Exception as e:
                # If there was an error getting the position details, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "close_position":
            position_id = "123456"
            try:
                close_response = close_position(ACCOUNT_ID, position_id)
                # Add the close response to the messages as a system message
                messages.append({"role": "system", "content": f"Close response: {close_response}"})
            except Exception as e:
                # If there was an error closing the position, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "get_transactions":
            try:
                transactions = get_transactions(ACCOUNT_ID)
                # Add the transactions to the messages as a system message
                messages.append({"role": "system", "content": f"Transactions: {transactions}"})
            except Exception as e:
                # If there was an error getting the transactions, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "get_transaction_details":
            transaction_id = "123456"
            try:
                transaction_details = get_transaction_details(ACCOUNT_ID, transaction_id)
                # Add the transaction details to the messages as a system message
                messages.append({"role": "system", "content": f"Transaction details: {transaction_details}"})
            except Exception as e:
                # If there was an error getting the transaction details, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "get_transactions_id_range":
            start_id = "123456"
            end_id = "123460"
            try:
                transactions_range = get_transactions_id_range(ACCOUNT_ID, start_id, end_id)
                # Add the transactions within the ID range to the messages as a system message
                messages.append({"role": "system", "content": f"Transactions range: {transactions_range}"})
            except Exception as e:
                # If there was an error getting the transactions within the ID range, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "get_transactions_since_id":
            since_id = "123456"
            try:
                transactions_since_id = get_transactions_since_id(ACCOUNT_ID, since_id)
                # Add the transactions since the ID to the messages as a system message
                messages.append({"role": "system", "content": f"Transactions since ID: {transactions_since_id}"})
            except Exception as e:
                # If there was an error getting the transactions since the ID, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "get_transaction_stream":
            try:
                transaction_stream = get_transaction_stream(ACCOUNT_ID)
                # Add the transaction stream to the messages as a system message
                messages.append({"role": "system", "content": f"Transaction stream: {transaction_stream}"})
            except Exception as e:
                # If there was an error getting the transaction stream, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "get_latest_candles":
            instrument = "EUR_USD"
            try:
                latest_candles = get_latest_candles(instrument)
                # Add the latest candles to the messages as a system message
                messages.append({"role": "system", "content": f"Latest candles: {latest_candles}"})
            except Exception as e:
                # If there was an error getting the latest candles, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "get_pricing":
            instrument = "EUR_USD"
            try:
                pricing = get_pricing(instrument)
                # Add the pricing to the messages as a system message
                messages.append({"role": "system", "content": f"Pricing: {pricing}"})
            except Exception as e:
                # If there was an error getting the pricing, add that to the messages
                messages.append({"role": "system", "content": str(e)})

        elif matched_endpoint == "get_pricing_stream":
            instrument = "EUR_USD"
            try:
                pricing_stream = get_pricing_stream(instrument)
                # Add the pricing stream to the messages as a system message
                messages.append({"role": "system", "content": f"Pricing stream: {pricing_stream}"})
            except Exception as e:
                # If there was an error getting the pricing stream, add that to the messages
                messages.append({"role": "system", "content": str(e)})


            
        else:
            messages.append({"role": "user", "content": user_input})

                    #------------------------------
            
                    #-    GPT 3-4 model           -
             
                    #------------------------------am


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
    