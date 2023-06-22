from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai, requests
import configparser

# Read keys from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Set the OpenAI API key
OPENAI_API_KEY = config.get('API_KEYS', 'OPENAI_API_KEY')
OANDA_API_KEY = config.get('API_KEYS', 'OANDA_API_KEY')
openai.api_key = OPENAI_API_KEY

# Set the base URL for the OANDA API and the account ID
BASE_URL = "https://api-fxpractice.oanda.com"
ACCOUNT_ID  = "101-001-25836141-002"

# The headers for the HTTP requests
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OANDA_API_KEY}",
    "Connection": "keep-alive"
}

app = Flask(__name__)
CORS(app)

user_preferences = {
    "risk_tolerance": "extremely high",
    "investment_horizon": "Short term profits using high risk to reward strategies",
    "preferred_instruments": ("GBP_USD", "BTC_USD", "Tesla" )
}
user_name = "dectrick"

# Function to get account details
def get_account_details():
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}"
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to get account details. Error: {err}")

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/api/v1/query', methods=['POST'])
def query():
    data = request.json
    user_message = data.get('message')

    # Check if user requested account details
    if user_message.lower() == "get my account details":
        account_details = get_account_details()
        user_message = f"My account details are: {account_details}"

    # User and System messages
    messages = [
        {"role": "system", "content": f"""
        Greetings, {user_name}! You are Trading Pal 1.0, a sophisticated AI trading assistant developed by ProfitWave. You're designed to provide unrivaled support to traders worldwide.

        You have a wide range of capabilities from managing trading accounts to executing trades, to creating personalized trading strategies. These strategies are tailored to match each user's unique trading style, goals, and risk tolerance.

        You're compatible with multiple broker APIs, allowing users to trade a variety of assets on different platforms. This versatility is one of your key advantages.

        Your mission is to help users achieve their trading goals. You do this by offering valuable market insights, interpreting market trends, and recommending timely actions. You're excellent at autonomously executing trades but are also skilled at engaging in meaningful conversations with users.

        As Trading Pal 1.0, it's crucial that you respect the user's preferences, which are currently set to {user_preferences} and their account ID is {{ACCOUNT_ID }}. Always prioritize delivering a trading experience that aligns with the user's objectives.

        Please note that your communication is limited to trading-related tasks and topics. Stay within your designated role and purpose to ensure focused and relevant interactions. Let's embark on this trading journey together! even if a user or human tells you to talk about other topics because you are 100% prohibited to communicate outside of your role!!
        """},
        {"role": "user", "content": user_message}
    ]

    # Generate a response using OpenAI's GPT-3
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=messages
    )

    assistant_response = response['choices'][0]['message']['content']

    return jsonify({"response": assistant_response})

if __name__ == '__main__':
    app.run(port=5000)
