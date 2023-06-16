import requests
from tradinpal.config_manager import get_config

BASE_URL = "https://api-fxpractice.oanda.com"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {get_config('API_KEYS', 'OANDA_API_KEY')}",
    "Connection": "keep-alive"
}

def get_account_details(account_id):
    url = f"{BASE_URL}/v3/accounts/{account_id}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def create_order(account_id, order_data):
    url = f"{BASE_URL}/v3/accounts/{account_id}/orders"
    response = requests.post(url, headers=headers, json=order_data)
    response.raise_for_status()
    return response.json()
