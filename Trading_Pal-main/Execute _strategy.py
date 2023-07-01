from oandapyV20 import API
from oandapyV20.contrib.requests import MarketOrderRequest
from oandapyV20.endpoints.pricing import PricingStream
from oandapyV20.endpoints.orders import OrderCreate
from oandapyV20.exceptions import V20Error
import time

class StopLossDetails:
    def __init__(self, price, precision=1):
        rounded_price = round(price, precision)
        self.data = {
            "price": rounded_price
        }


class TakeProfitDetails:
    def __init__(self, price, precision=1):
        rounded_price = round(price, precision)
        self.data = {
            "price": rounded_price
        }


class TrailingStopLossDetails:
    def __init__(self, distance, precision=3):
        rounded_price = round(distance, precision)
        self.data = {
            "distance": distance
        }

account_id = "101002"
api_key = "ba62e5ad63f2a"

api = API(access_token=api_key, environment="practice")

instrument = "GBP_USD"

r = PricingStream(accountID=account_id, params={"instruments": instrument, "granularity": "M1"})


position = 0
stop_loss = None
take_profit = None
prev_close = None
last_trade_time = time.time()

try:
    for msg in api.request(r):
        if msg["type"] == "HEARTBEAT":
            continue
        
        if msg["type"] == "PRICE":
            bids = msg["bids"]
            asks = msg["asks"]
            closeout_bid = bids[0]["price"]
            closeout_ask = asks[0]["price"]
            curr_close = (float(closeout_bid) + float(closeout_ask)) / 2

            if position == 0:
                if prev_close is not None and curr_close > prev_close and time.time() - last_trade_time >= 60:
                    position = 1
                    stop_loss = StopLossDetails(price=prev_close).data
                    take_profit = TakeProfitDetails(price=curr_close * 1.02).data
                    trailing_stop_loss = TrailingStopLossDetails(distance=0.0010).data
                    order_data = MarketOrderRequest(instrument=instrument, units=1000, 
                                                    takeProfitOnFill=take_profit, 
                                                    stopLossOnFill=stop_loss, 
                                                    trailingStopLossOnFill=trailing_stop_loss)
                    r = OrderCreate(account_id, data=order_data.data)
                    api.request(r)
                    last_trade_time = time.time()
                elif prev_close is not None and curr_close < prev_close and time.time() - last_trade_time >= 60:
                    position = -1
                    stop_loss = StopLossDetails(price=prev_close).data
                    take_profit = TakeProfitDetails(price=curr_close * 0.98).data
                    trailing_stop_loss = TrailingStopLossDetails(distance=0.0010).data
                    order_data = MarketOrderRequest(instrument=instrument, units=-1000, 
                                                    takeProfitOnFill=take_profit, 
                                                    stopLossOnFill=stop_loss, 
                                                    trailingStopLossOnFill=trailing_stop_loss)
                    r = OrderCreate(account_id, data=order_data.data)
                    api.request(r)
                    last_trade_time = time.time()

            prev_close = curr_close

except V20Error as e:
    print("Error: {}".format(e))
