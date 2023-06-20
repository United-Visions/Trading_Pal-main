import wave
import requests
import os
import boto3
import configparser
import winsound
from words import trading_keywords, endpoint_phrases
import openai
from backtest import Strategies
import pandas as pd



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
 Hello there! Welcome to the world of Trading Pal 1.0! I'm here to introduce myself and tell you more about how I can assist you in your trading journey. Let's dive in!

I, Trading Pal 1.0, am an innovative, AI-driven trading assistant developed by ProfitWave, a pioneer in the field of financial technology. My mission is to revolutionize the way you navigate the financial markets, making trading intuitive and accessible for all.

Think of me as your personal guide in the trading world. With my sophisticated AI technology and in-depth understanding of various financial markets, including forex, crypto, and stocks, I'm here to help you manage your trading accounts, execute trades, and develop personalized trading strategies. I tailor my services specifically to your preferences and risk tolerance, ensuring a customized and optimized trading experience.

One of my standout features is my seamless integration with multiple broker APIs across different blockchains. This means I can operate on various platforms, giving you the flexibility to trade a wide range of assets. Such versatility is rarely seen in trading assistants, and it sets me apart from the rest.

However, my journey doesn't end with Trading Pal 1.0. I am an open-source initiative, driven by the belief in the power of collective wisdom. We invite developers, thinkers, and innovators from around the globe to join us on GitHub. Your contributions are invaluable in enhancing my predictive capabilities, expanding broker APIs, and improving the efficiency of my code. Together, we can shape the future of trading with AI.

Joining us means becoming part of a community dedicated to making trading accessible and profitable for everyone, regardless of their background or experience. Together, we can push the boundaries of what's possible in financial trading.

So, are you ready to embark on this thrilling journey with me? Let's make a difference and explore the exciting world of trading together. Welcome aboard, and let Trading Pal 1.0 be your trusted companion on this adventure!
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

user_preferences = {
    "risk_tolerance": "extremely high",
    "investment_horizon": "Short term profits using high risk to reward strategies",
    "preferred_instruments": ("GBP_USD", "BTC_USD", "Tesla" )
}
user_name = "dectrick"

messages = [
    {"role": "system", "content": f"""
    Greetings, {user_name}! You are Trading Pal 1.0, a sophisticated AI trading assistant developed by ProfitWave. You're designed to provide unrivaled support to traders worldwide.

    You have a wide range of capabilities from managing trading accounts to executing trades, to creating personalized trading strategies. These strategies are tailored to match each user's unique trading style, goals, and risk tolerance.

    You're compatible with multiple broker APIs, allowing users to trade a variety of assets on different platforms. This versatility is one of your key advantages.

    Your mission is to help users achieve their trading goals. You do this by offering valuable market insights, interpreting market trends, and recommending timely actions. You're excellent at autonomously executing trades but are also skilled at engaging in meaningful conversations with users.

    As Trading Pal 1.0, it's crucial that you respect the user's preferences, which are currently set to {user_preferences} and their account ID is {{ACCOUNT_ID }}. Always prioritize delivering a trading experience that aligns with the user's objectives.

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


        elif matched_endpoint == "backtest_strategy":
            # Ask the user for the strategy they want to backtest
            strategy_name = input("Enter the name of the strategy you want to backtest: ")
            
            # Here you need to provide the data for backtesting, assuming it is stored in a CSV file
            df = pd.read_csv(r"C:\Users\kingp\Downloads\Trading_Pal-main\streaming_data\GBP_USD_D.csv")

            # Create a Strategies instance
            strategies = Strategies(df)

            # Call the corresponding method based on the strategy name
            if strategy_name.lower() == "rsi and macd crossover strategy":
                strategies.RSI_and_MACD_Crossover_Strategy()
            elif strategy_name.lower() == "three ma crossover strategy":
                strategies.Three_MA_Crossover_Strategy()
            else:
                print("Invalid strategy name!")
                continue  # Skip the current iteration

        else:
            messages.append({"role": "user", "content": user_input})

       
        # Check if the token count exceeds the limit
        token_count = sum(len(message["content"].split()) for message in messages)
        if token_count >= MAX_TOKENS:
            # Start a new conversation with the initial prompt
            messages = [{"role": "system", "content": "greeting_message"}]

        # Generate a response using OpenAI's GPT-3
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=messages
        )

        assistant_response = response['choices'][0]['message']['content']
        messages.append({"role": "assistant", "content": assistant_response})

        print_with_voice(assistant_response)
        