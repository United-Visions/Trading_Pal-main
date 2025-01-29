from flask import config
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
        self.current_broker = None
        self.active_brokers = set()

    def initialize_user_brokers(self, user: User):
        """Initialize all active brokers for a user"""
        try:
            configs = BrokerConfig.query.filter_by(
                user_id=user.id,
                is_active=True
            ).all()
            
            success = False
            
            for config in configs:
                credentials = config.get_credentials()
                if config.broker_type == 'oanda':
                    success = self.add_broker(
                        broker_type='oanda',
                        api_key=config.oanda_api_key,
                        account_id=config.oanda_account_id
                    )
                elif config.broker_type == 'alpaca':
                    success = self.add_broker(
                        broker_type='alpaca',
                        api_key=config.alpaca_api_key,
                        api_secret=config.alpaca_api_secret
                    )
                
                if success:
                    self.active_brokers.add(config.broker_type)
                    
                    # Set current broker if not set
                    if not self.current_broker:
                        self.current_broker = config.broker_type
                        
            return success
            
        except Exception as e:
            print(f"Error initializing brokers: {e}")
            return False

    def add_broker(self, broker_type, api_key=None, api_secret=None, account_id=None):
        """Add a broker instance to the factory with improved error handling"""
        try:
            broker = None
            if broker_type == 'oanda':
                if not api_key:
                    api_key = config.oanda_api_key
                if not account_id:
                    account_id = config.oanda_account_id
                    
                broker = OandaBroker(api_key=api_key, account_id=account_id)
                
            elif broker_type == 'alpaca':
                if not api_key:
                    api_key = config.alpaca_api_key
                if not api_secret:
                    api_secret = config.alpaca_api_secret
                    
                broker = AlpacaBroker(api_key=api_key, api_secret=api_secret)
            else:
                raise ValueError(f"Unsupported broker type: {broker_type}")

            # Test connection before storing
            if not broker or not broker.test_connection():
                self.broker_status[broker_type] = "disconnected"
                return False

            self.brokers[broker_type] = broker
            self.broker_status[broker_type] = "connected"
            self.active_brokers.add(broker_type)
            
            if not self.current_broker:
                self.current_broker = broker_type
                
            return True

        except Exception as e:
            print(f"Error adding broker {broker_type}: {str(e)}")
            self.broker_status[broker_type] = "error"
            return False

    def get_broker(self, broker_type=None):
        """Get appropriate broker based on type or first available"""
        # Use current_broker if no specific type requested
        broker_type = broker_type or self.current_broker
        
        if broker_type and broker_type in self.brokers:
            return self.brokers[broker_type]
        elif self.brokers:
            return next(iter(self.brokers.values()))
        raise ValueError("No brokers initialized. Please configure broker credentials.")

    def test_broker_connection(self, broker_type, api_key, api_secret=None, account_id=None):
        """Test broker connection before saving credentials"""
        try:
            if broker_type == 'oanda':
                broker = OandaBroker(api_key=api_key, account_id=account_id)
            elif broker_type == 'alpaca':
                broker = AlpacaBroker(api_key=api_key, api_secret=api_secret)
            else:
                return False
                
            return broker.test_connection()
            
        except Exception as e:
            print(f"Connection test failed for {broker_type}: {e}")
            return False

    def is_broker_available(self, broker_type):
        return broker_type in self.brokers

    def get_available_brokers(self):
        return list(self.brokers.keys())

    def get_broker_status(self, broker_type):
        if broker_type in self.brokers:
            try:
                broker = self.brokers[broker_type]
                return "connected" if broker.test_connection() else "disconnected"
            except:
                return "disconnected"
        return "not_configured"