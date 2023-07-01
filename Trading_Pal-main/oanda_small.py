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
from news import get_google_search_results, generate_gpt3_response



# Read keys from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Set the OpenAI API key
OPENAI_API_KEY = config.get('API_KEYS', 'OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY
MAX_TOKENS= 3055




# Set the base URL for the OANDA API
BASE_URL = "https://api-fxpractice.oanda.com"
ACCOUNT_ID  = "101-02"

# The headers for the HTTP requests
OANDA_API_KEY = config.get('API_KEYS', 'OANDA_API_KEY')
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OANDA_API_KEY}",
    "Connection": "keep-alive"
}


# Initialize backtest module
strategies_instance = Strategies(pd)



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

        
  
                
        elif matched_endpoint == "perform_search":
            user_query = input("Please enter your search query: ")
            gpt3_prompt = f"Search the web for '{user_query}'"
            search_results = get_google_search_results(user_query)
            gpt3_response = generate_gpt3_response(gpt3_prompt, search_results)

            print(f"Search results: {gpt3_response}")

            # Ask for user feedback
            user_feedback = input("Was the response satisfactory? (yes/no): ")
            while user_feedback.lower() != 'yes':
                user_query = input("Please refine your query or ask in a different way: ")
                gpt3_prompt = f"{gpt3_response}. {user_query}"
                search_results = get_google_search_results(user_query)
                gpt3_response = generate_gpt3_response(gpt3_prompt, search_results)

                print(f"Search results: {gpt3_response}")
                user_feedback = input("Was the response satisfactory? (yes/no): ")


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

        print(assistant_response)
        