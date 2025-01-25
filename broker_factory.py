from oanda_broker import OandaBroker 
from alpaca_broker import AlpacaBroker
import configparser
from typing import Tuple, Optional
from models import User, BrokerConfig

class BrokerFactory:
    def __init__(self, config_path='config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        self.brokers = {}
        self.broker_status = {}
        
    def initialize_user_brokers(self, user: User):
        """Initialize brokers based on user's configurations"""
        self.brokers = {}
        
        for broker_config in user.broker_configs:
            if not broker_config.is_active:
                continue
                
            if broker_config.broker_type == 'oanda':
                self.brokers['oanda'] = OandaBroker(
                    api_key=broker_config.api_key,
                    account_id=broker_config.account_id,
                    base_url="https://api-fxpractice.oanda.com"
                )
                
            elif broker_config.broker_type == 'alpaca':
                self.brokers['alpaca'] = AlpacaBroker(
                    api_key=broker_config.api_key,
                    secret_key=broker_config.api_secret,
                    base_url="https://paper-api.alpaca.markets"
                )
            
            self.broker_status[broker_config.broker_type] = 'connected'

    def get_broker(self, message: Optional[str] = None, user_prefs = None) -> Tuple[object, str]:
        """Get appropriate broker based on message content, user preferences and availability"""
        if not self.brokers:
            raise ValueError("No brokers initialized. Please configure broker credentials.")

        if message:
            message = message.lower()
            
            # Check user's preferred market types
            if user_prefs and user_prefs.preferred_markets:
                if 'forex' in user_prefs.preferred_markets and 'oanda' in self.brokers:
                    return self.brokers['oanda'], 'oanda'
                elif 'stocks' in user_prefs.preferred_markets and 'alpaca' in self.brokers:
                    return self.brokers['alpaca'], 'alpaca'
            
            # Check message context
            if any(term in message for term in ['forex', 'currency', 'oanda', 'eur/usd', 'gbp/usd']):
                if 'oanda' in self.brokers:
                    return self.brokers['oanda'], 'oanda'
            elif any(term in message for term in ['stock', 'shares', 'alpaca', 'nasdaq', 'nyse']):
                if 'alpaca' in self.brokers:
                    return self.brokers['alpaca'], 'alpaca'

        # Return first available broker
        broker_name = next(iter(self.brokers))
        return self.brokers[broker_name], broker_name

    def check_broker_status(self, broker_name: str) -> bool:
        """Check if broker is connected and working"""
        if broker_name not in self.brokers:
            return False
            
        try:
            # Test broker connection
            broker = self.brokers[broker_name]
            broker.get_account_details()
            self.broker_status[broker_name] = 'connected'
            return True
        except Exception:
            self.broker_status[broker_name] = 'disconnected'
            return False

    def get_available_brokers(self) -> list:
        """Get list of available and connected brokers"""
        return [name for name, broker in self.brokers.items() 
                if self.check_broker_status(name)]

    def get_broker_status(self, broker_name: str) -> str:
        """Get current status of specific broker"""
        return self.broker_status.get(broker_name, 'not_configured')