from oandapyV20 import API
from oandapyV20.contrib.requests import MarketOrderRequest
from oandapyV20.endpoints.pricing import PricingStream
from oandapyV20.endpoints.orders import OrderCreate
from oandapyV20.exceptions import V20Error
import time

account_id = "101-001-25836141-002"
api_key = "ba62e5ad63f2a8759ee31761ba01e196-fb6f30ba3b58d44a94152fa5cd4f3ce2"
api = API(access_token=api_key, environment="practice")
instrument = "GBP_USD"

prices = []
moving_average_period = 5
moving_average_sum = 0
position = 0
position_time = None
position_timeout = 30  # Position timeout in seconds

try:
    r = PricingStream(accountID=account_id, params={"instruments": instrument})
    for msg in api.request(r):
        if msg["type"] == "HEARTBEAT":
            continue

        if msg["type"] == "PRICE":
            bids = msg["bids"]
            asks = msg["asks"]
            closeout_bid = bids[0]["price"]
            closeout_ask = asks[0]["price"]
            curr_close = (float(closeout_bid) + float(closeout_ask)) / 2

            if len(prices) == moving_average_period:
                moving_average_sum -= prices[0]
                prices = prices[1:]

            moving_average_sum += curr_close
            prices.append(curr_close)
            moving_average = moving_average_sum / len(prices)

            if position != 0 and time.time() - position_time >= position_timeout:
                if position == 1:
                    order_data = MarketOrderRequest(instrument=instrument, units=-1000)
                else:
                    order_data = MarketOrderRequest(instrument=instrument, units=1000)
                r = OrderCreate(account_id, data=order_data.data)
                api.request(r)
                position = 0
                print(f"Position closed due to timeout. Time: {time.time()}")

            elif position == 0:
                if curr_close > moving_average:
                    position = 1
                    order_data = MarketOrderRequest(instrument=instrument, units=1000)
                    r = OrderCreate(account_id, data=order_data.data)
                    api.request(r)
                    position_time = time.time()
                    print(f"Position opened at {curr_close}. Time: {time.time()}")
                elif curr_close < moving_average:
                    position = -1
                    order_data = MarketOrderRequest(instrument=instrument, units=-1000)
                    r = OrderCreate(account_id, data=order_data.data)
                    api.request(r)
                    position_time = time.time()
                    print(f"Position opened at {curr_close}. Time: {time.time()}")
            elif position == 1 and curr_close < moving_average:
                position = 0
                order_data = MarketOrderRequest(instrument=instrument, units=-1000)
                r = OrderCreate(account_id, data=order_data.data)
                api.request(r)
                print(f"Position closed at {curr_close}. Time: {time.time()}")
            elif position == -1 and curr_close > moving_average:
                position = 0
                order_data = MarketOrderRequest(instrument=instrument, units=1000)
                r = OrderCreate(account_id, data=order_data.data)
                api.request(r)
                print(f"Position closed at {curr_close}. Time: {time.time()}")
                
except V20Error as e:
    print("V20Error occurred: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")