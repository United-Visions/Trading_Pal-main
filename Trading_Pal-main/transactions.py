from oandapyV20 import API
from oandapyV20.exceptions import V20Error
from oandapyV20.endpoints.transactions import TransactionsStream
import configparser
import openai
import boto3
import time
import csv

# Read keys from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Set the OpenAI API key
OPENAI_API_KEY = config.get('API_KEYS', 'OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

# Set the base URL for the OANDA API
BASE_URL = "https://api-fxpractice.oanda.com"
ACCOUNT_ID = "101-001-25836141-002"


# Initialize AWS Polly client
AWS_ACCESS_KEY_ID = config.get('AWS_KEYS', 'AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config.get('AWS_KEYS', 'AWS_SECRET_ACCESS_KEY')
AWS_REGION = config.get('AWS_KEYS', 'AWS_REGION')
sns_client = boto3.client('sns', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

OANDA_API_KEY = config.get('API_KEYS', 'OANDA_API_KEY')
api = API(access_token=OANDA_API_KEY)
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OANDA_API_KEY}",
    "Connection": "keep-alive"
}

def generate_email_body(transactions):
    prompt = f"Trading Pal here! I wanted to inform you that new transactions occurred on your Oanda account:\n\n"
    for transaction in transactions:
        prompt += f"{transaction}\n"
    prompt += "\nCan you please write an email to inform the user about these new transactions?"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
    )
    
    email_body = response['choices'][0]['message']['content']
    return email_body.strip()




def stream_transactions():
    transactions = []
    try:
        r = TransactionsStream(accountID=ACCOUNT_ID)
        for response in api.request(r):
            if response['type'] != 'HEARTBEAT':
                print(response)
                transactions.append(response)
                email_body = generate_email_body(transactions)  # Generate the email body
                send_text_message(email_body)  # Pass the email body to the function
                transactions.clear()
                time.sleep(1)  # wait for 1 second before checking for new transactions
    except V20Error as e:
        print("Error: {}".format(e))


def send_text_message(message_body):
    topic_arn = 'arn:aws:sns:us-east-1:470488217575:Transaction'  # Replace with your SNS topic ARN
    sns_client.publish(
        TopicArn=topic_arn,
        Message=message_body
    )
    save_response_to_csv(message_body)


def save_response_to_csv(response):
    with open('GPT_response.csv', mode='a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([response])


stream_transactions()
