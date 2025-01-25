try:
    from alpaca.trading.client import TradingClient
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.trading.requests import MarketOrderRequest, GetAssetsRequest
    from alpaca.trading.enums import OrderSide, TimeInForce, AssetClass
    import alpaca_trade_api as tradeapi
    from alpaca.common.exceptions import APIError
except ImportError as e:
    raise ImportError(
        f"Failed to import Alpaca SDK: {str(e)}. "
        "Please install required packages: pip install alpaca-py alpaca-trade-api"
    )

import pandas as pd
from datetime import datetime
import pytz
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlpacaBroker:
    def __init__(self, api_key, api_secret=None, paper=True):
        """Initialize Alpaca broker with proper error handling"""
        if not api_key or not api_secret:
            raise ValueError("Both API key and secret are required for Alpaca")
            
        self.api_key = api_key
        self.api_secret = api_secret
        self.paper = paper
        self.base_url = "https://paper-api.alpaca.markets" if paper else "https://api.alpaca.markets"
        self.trading_client = None
        self.data_client = None
        self.rest_api = None
        self.initialize_clients()

    def initialize_clients(self):
        """Initialize all Alpaca API clients"""
        try:
            # Initialize REST API client
            self.rest_api = tradeapi.REST(
                key_id=self.api_key,
                secret_key=self.api_secret,
                base_url=self.base_url,
                api_version='v2'
            )
            
            # Initialize Trading client
            self.trading_client = TradingClient(
                api_key=self.api_key,
                secret_key=self.api_secret,
                paper=self.paper
            )
            
            # Initialize Data client
            self.data_client = StockHistoricalDataClient(
                api_key=self.api_key,
                secret_key=self.api_secret
            )
            
            logger.info("Successfully initialized Alpaca clients")
            
        except Exception as e:
            logger.error(f"Failed to initialize Alpaca clients: {str(e)}")
            raise

    def test_connection(self):
        """Test connection to Alpaca API with detailed error handling"""
        try:
            if not self.rest_api:
                raise ValueError("REST API client not initialized")
                
            # Test authentication and get account
            account = self.rest_api.get_account()
            if account.status != 'ACTIVE':
                logger.error(f"Account not active. Status: {account.status}")
                return False
                
            return True
            
        except APIError as e:
            logger.error(f"Alpaca API error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Alpaca connection test failed: {str(e)}")
            return False

    def get_account_details(self):
        """Get account details with enhanced error handling"""
        try:
            if not self.trading_client:
                raise ValueError("Trading client not initialized")
                
            account = self.rest_api.get_account()
            
            return {
                'balance': float(account.equity),
                'currency': 'USD',
                'marginAvailable': float(account.buying_power),
                'pl': float(account.equity) - float(account.last_equity),
                'openPositionCount': len(self.rest_api.list_positions()),
                'openTradeCount': len(self.rest_api.list_orders(status='open')),
                'marginRate': float(account.multiplier)
            }
        except Exception as e:
            logger.error(f"Error getting account details: {str(e)}")
            return {"error": str(e)}

    def create_order(self, order_data):
        """Create a new trading order"""
        try:
            order = order_data.get('order', {})
            side = 'buy' if float(order.get('units', 0)) > 0 else 'sell'
            qty = abs(float(order.get('units', 0)))
            
            # Map OANDA order types to Alpaca order types
            order_type_map = {
                "MARKET": "market",
                "LIMIT": "limit",
                "STOP": "stop"
            }
            
            order_type = order_type_map.get(order.get('type', 'MARKET'), 'market')
            
            response = self.api.submit_order(
                symbol=order.get('instrument', '').replace('_', ''),
                qty=qty,
                side=side,
                type=order_type,
                time_in_force='day',
                limit_price=order.get('price') if order_type == 'limit' else None,
                stop_price=order.get('price') if order_type == 'stop' else None
            )
            
            return {
                "orderFillTransaction": {
                    "id": response.id,
                    "instrument": response.symbol,
                    "units": response.qty if side == 'buy' else -float(response.qty),
                    "time": response.submitted_at.isoformat()
                }
            }
        except Exception as err:
            raise Exception(f"Failed to create order: {err}")

    def get_positions(self):
        """Get current positions"""
        try:
            positions = self.api.list_positions()
            return {
                "positions": [
                    {
                        "instrument": pos.symbol,
                        "units": float(pos.qty),
                        "current_price": float(pos.current_price),
                        "unrealized_pl": float(pos.unrealized_pl)
                    } for pos in positions
                ]
            }
        except Exception as err:
            return {"error": f"Failed to get positions: {str(err)}"}

    def close_position(self, instrument):
        """Close a position for given instrument"""
        try:
            response = self.api.close_position(instrument.replace('_', ''))
            return {
                "orderFillTransaction": {
                    "id": response.id,
                    "instrument": response.symbol,
                    "units": response.qty,
                    "time": response.submitted_at.isoformat()
                }
            }
        except Exception as err:
            return {"error": f"Failed to close position: {str(err)}"}

    def get_candlestick_data(self, instrument, timeframe="1Min", limit=100):
        """Get candlestick data for an instrument"""
        try:
            # Convert OANDA timeframe to Alpaca timeframe
            timeframe_map = {
                "M1": "1Min",
                "M5": "5Min",
                "M15": "15Min",
                "M30": "30Min",
                "H1": "1Hour",
                "H4": "4Hour",
                "D": "1Day"
            }
            
            alpaca_timeframe = timeframe_map.get(timeframe, timeframe)
            bars = self.api.get_barset(
                instrument.replace('_', ''),
                alpaca_timeframe,
                limit=limit
            )
            
            return {
                "candles": [
                    {
                        "time": bar.t.isoformat(),
                        "volume": bar.v,
                        "mid": {
                            "o": str(bar.o),
                            "h": str(bar.h),
                            "l": str(bar.l),
                            "c": str(bar.c)
                        }
                    } for bar in bars[instrument.replace('_', '')]
                ]
            }
        except Exception as err:
            raise ValueError(f"Failed to fetch candlestick data: {str(err)}")

    def get_trades(self):
        """Get open trades"""
        try:
            trades = self.api.list_orders(status='open')
            return {
                "trades": [
                    {
                        "id": trade.id,
                        "instrument": trade.symbol,
                        "units": float(trade.qty),
                        "price": float(trade.limit_price or trade.stop_price or 0),
                        "time": trade.submitted_at.isoformat()
                    } for trade in trades
                ]
            }
        except Exception as err:
            return {"error": f"Failed to get trades: {str(err)}"}

    def process_order_request(self, data):
        """Process order request data"""
        try:
            order = data.get('order', {})
            side = OrderSide.BUY if float(order.get('units', 0)) > 0 else OrderSide.SELL
            
            # Create market order request
            request = MarketOrderRequest(
                symbol=order.get('instrument', '').replace('_', ''),
                qty=abs(float(order.get('units', 0))),
                side=side,
                time_in_force=TimeInForce.DAY
            )
            
            return request
            
        except Exception as e:
            logger.error(f"Error processing order request: {str(e)}")
            raise ValueError(f"Invalid order data: {str(e)}")
