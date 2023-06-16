import pandas as pd
import os
import configparser
import openai
from tradinpal.config_manager import get_config
from tradinpal.openai_service import create_chat_completion
from oanda_service import get_account_details, create_order
from input_handler import handle_input
from tradinpal.voice_printer import print_with_voice
from words import trading_keywords, endpoint_phrases
import requests
# Read keys from config.ini
config = configparser.ConfigParser()
config.read('config.ini')
ACCOUNT_ID = get_config('ACCOUNT_IDS', 'ACCOUNT_ID')
user_name = get_config('USER', 'USER_NAME')
risk_tolerance = get_config('USER', 'RISK_TOLERANCE')
investment_horizon = get_config('USER', 'INVESTMENT_HORIZON')
preferred_instruments = get_config('USER', 'PREFERRED_INSTRUMENTS')

# Set the OpenAI API key
OPENAI_API_KEY = config.get('API_KEYS', 'OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY
MAX_TOKENS = 16000  # Adjusted based on GPT-3 model's limitations

# Set the base URL for the OANDA API
BASE_URL = "https://api-fxpractice.oanda.com"
ACCOUNT_ID = "101-001-25836141-002"
# The headers for the HTTP requests
OANDA_API_KEY = config.get('API_KEYS', 'OANDA_API_KEY')
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OANDA_API_KEY}",
    "Connection": "keep-alive"
}

# User preferences (Dummy values for demonstration)
user_preferences = {
    "risk_tolerance": "extremely high",
    "investment_horizon": "Short term profits using high risk to reward strategies",
    "preferred_instruments": "EUR_USD",
    "indicators": {
        "moving_average": {
            "period": 20,
            "type": "sma"
        },
        "rsi": {
            "period": 14
        },
        "macd": {
            "short_period": 12,
            "long_period": 26,
            "signal_period": 9
        }
    }
}
username = "dectrick"

# Define the list of granularities
GRANULARITIES = ["S5", "M1", "M5", "M15", "M30", "H1", "H4", "D", "W", "M"]
# Define the list of instruments
INSTRUMENTS = ["EUR_USD", "USD_JPY", "GBP_USD"]  # Add more forex pairs as per your requirements

# Define the data directory
directory = "streaming_data"

def read_latest_data(instrument, granularity):
    filename = os.path.join(directory, f"{instrument}_{granularity}.csv")
    df = pd.read_csv(filename)
    return df.tail(500)  # return the last 10 rows

def process_data():
    for granularity in GRANULARITIES:
        for instrument in INSTRUMENTS:
            data = read_latest_data(instrument, granularity)
            prediction = identify_opportunities(data)
            if prediction is not None:
                print(prediction)
def get_account_details(account_id):
    url = f"{BASE_URL}/v3/accounts/{account_id}"
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
        data = response.json()
        
        # Extract only the necessary details
        significant_details = {
            "balance": data["account"]["balance"],
            "marginRate": data["account"]["marginRate"],
            "openTradeCount": data["account"]["openTradeCount"],
            "unrealizedPL": data["account"]["unrealizedPL"],
            # add any other fields you need here
        }
        
        return significant_details
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to get account details. Error: {err}")

# Retrieve account details
account_details = get_account_details(ACCOUNT_ID)

# Function to get account details
def get_account_details(ACCOUNT_ID):
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}"
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to get account details. Error: {err}")

def identify_opportunities(data):
    prompt = f"""
    You are Trading Pal, a sophisticated trading robot system developed by ProfitWave. Your role is to identify potential trading opportunities based on real-time market data.

    You have been given the following recent market data:

    Please analyze the data using technical indicators such as Moving Averages, RSI, and MACD, and consider factors such as support and resistance levels. Then, identify any trading opportunities. Provide detailed information on the potential opportunities found, including entry points, target levels, and stop-loss levels, if applicable.

    The settings for the technical indicators are as follows:

    Moving Averages:
    - Period: {user_preferences['indicators']['moving_average']['period']}
    - Type: {user_preferences['indicators']['moving_average']['type']}

    RSI:
    - Period: {user_preferences['indicators']['rsi']['period']}

    MACD:
    - Short period: {user_preferences['indicators']['macd']['short_period']}
    - Long period: {user_preferences['indicators']['macd']['long_period']}
    - Signal period: {user_preferences['indicators']['macd']['signal_period']}

    The risk tolerance level is {user_preferences['risk_tolerance']} and the trading strategy is focused on {user_preferences['investment_horizon']}.

    User's preferred trading instrument is {user_preferences['preferred_instruments']}.

    Use these settings and preferences to guide your analysis and identify potential trading opportunities. 

    {account_details}
    {risk_tolerance}
    {investment_horizon}
    {risk_tolerance}
    {user_name}
    {preferred_instruments}
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=MAX_TOKENS
    )

    # Ensure 'choices' exists in the response
    if 'choices' in response and len(response['choices']) > 0:
        # Return the generated text from the response
        return print_with_voice(response)['choices'][0]['message']['content']
    else:
        return None

if __name__ == "__main__":
    process_data()
