#is not finished
import requests
import json
import openai
import configparser

# Read keys from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Set the OpenAI API key
OPENAI_API_KEY = config.get('API_KEYS', 'OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

def get_forex_news(currency_pair):
    """Get the latest forex news for a given currency pair"""
    news_info = {
        "currency_pair": currency_pair,
        "headline": "EUR/USD falls to fresh session low as dollar holds firmer on the day",
        "summary": "EUR/USD slips below 1.1800 as the dollar keeps a more positive tone in European morning trade. The pair is down 0.2% on the day, extending its decline from yesterday's high of 1.1877.",
        "url": "https://www.forexfactory.com/news"
    }
    return json.dumps(news_info)

# Get the forex news for the currency pair "EUR/USD"
forex_news = get_forex_news("EUR/USD")

# Define the message to send to the API
messages = [{"role": "system", "content": f"I have called the function 'get_forex_news' and obtained the following news: {forex_news}"},
            {"role": "user", "content": "What's the latest news on EUR/USD?"}]

# Call the OpenAI API
response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
    )

response_message = response["choices"][0]["message"]
print(response_message)
