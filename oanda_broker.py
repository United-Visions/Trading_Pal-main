
import requests
from oandapyV20 import API
from oandapyV20.exceptions import V20Error
from oandapyV20.endpoints.instruments import InstrumentsCandles
import pandas as pd
import json

class OandaBroker:
    def __init__(self, api_key, account_id, base_url="https://api-fxpractice.oanda.com"):
        self.api_key = api_key
        self.account_id = account_id
        self.base_url = base_url
        self.api = API(access_token=api_key)
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "Accept-Datetime-Format": "RFC3339"
        }

    def get_account_details(self):
        """Get account details with enhanced error handling"""
        try:
            url = f"{self.base_url}/v3/accounts/{self.account_id}/summary"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                return {"error": f"Failed to get account details. Status: {response.status_code}, Response: {response.text}"}
                
            return response.json()
            
        except requests.exceptions.RequestException as err:
            return {"error": f"Network error getting account details: {str(err)}"}
        except Exception as err:
            return {"error": f"Unexpected error getting account details: {str(err)}"}

    def create_order(self, order_data):
        """Create a new trading order"""
        try:
            url = f"{self.base_url}/v3/accounts/{self.account_id}/orders"
            response = requests.post(url, headers=self.headers, json=order_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            raise Exception(f"Failed to create order: {err}")

    def get_positions(self):
        """Get current positions"""
        url = f"{self.base_url}/v3/accounts/{self.account_id}/positions"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def close_position(self, instrument):
        """Close a position for given instrument"""
        url = f"{self.base_url}/v3/accounts/{self.account_id}/positions/{instrument}/close"
        response = requests.put(url, headers=self.headers)
        return response.json()

    def get_candlestick_data(self, instrument, granularity="M1", count=100):
        """Get candlestick data for an instrument"""
        try:
            params = {
                "count": count,
                "granularity": granularity
            }
            request = InstrumentsCandles(instrument=instrument, params=params)
            self.api.request(request)
            return request.response
        except V20Error as e:
            raise ValueError(f"Failed to fetch candlestick data: {str(e)}")

    def get_order_book(self, instrument):
        """Get order book for an instrument"""
        url = f"{self.base_url}/v3/instruments/{instrument}/orderBook"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_trades(self):
        """Get open trades"""
        url = f"{self.base_url}/v3/accounts/{self.account_id}/trades"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def process_order_request(self, order_request):
        """Process and validate order request"""
        required_fields = ['units', 'instrument', 'type']
        order_data = order_request.get('order', {})
        
        if not all(field in order_data for field in required_fields):
            raise ValueError("Required fields are missing in order request")

        # Convert units to integer
        order_data['units'] = int(order_data['units'])

        # Handle additional parameters
        if order_data['type'] in ["LIMIT", "STOP"]:
            order_data["price"] = order_request.get('price')

        # Add risk management parameters if provided
        if 'take_profit' in order_request:
            order_data["takeProfitOnFill"] = {
                "price": order_request['take_profit'],
                "timeInForce": "GTC"
            }

        if 'stop_loss' in order_request:
            order_data["stopLossOnFill"] = {
                "price": order_request['stop_loss'],
                "timeInForce": "GTC"
            }

        if 'trailing_stop_loss_distance' in order_request:
            order_data["trailingStopLossOnFill"] = {
                "distance": order_request['trailing_stop_loss_distance']
            }

        return {"order": order_data}
