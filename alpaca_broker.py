try:
    import alpaca_trade_api as tradeapi
except ImportError:
    raise ImportError(
        "The alpaca-trade-api package is required. "
        "Please install it using: pip install alpaca-trade-api"
    )
import pandas as pd
from datetime import datetime

class AlpacaBroker:
    def __init__(self, api_key, secret_key, base_url="https://paper-api.alpaca.markets"):
        self.api = tradeapi.REST(api_key, secret_key, base_url, api_version='v2')
        self.base_url = base_url

    def get_account_details(self):
        """Get account details with enhanced error handling"""
        try:
            account = self.api.get_account()
            return {
                "account": {
                    "balance": account.cash,
                    "equity": account.equity,
                    "buying_power": account.buying_power,
                    "currency": "USD",
                    "positions_count": account.position_count,
                    "trading_blocked": account.trading_blocked,
                    "pattern_day_trader": account.pattern_day_trader
                }
            }
        except Exception as err:
            return {"error": f"Failed to get account details: {str(err)}"}

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
