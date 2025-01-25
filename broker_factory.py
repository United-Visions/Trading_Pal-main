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

    def initialize_user_brokers(self, user: User):
        """Initialize all active brokers for a user"""
        try:
            configs = BrokerConfig.query.filter_by(
                user_id=user.id,
                is_active=True
            ).all()
            
            for config in configs:
                self.add_broker(
                    broker_type=config.broker_type,
                    api_key=config.api_key,
                    api_secret=config.api_secret,
                    account_id=config.account_id
                )
                
            # Set first available broker as current
            if self.brokers and not self.current_broker:
                self.current_broker = next(iter(self.brokers.keys()))
                
            return len(self.brokers) > 0
            
        except Exception as e:
            print(f"Error initializing brokers: {e}")
            return False

    def add_broker(self, broker_type, api_key, api_secret=None, account_id=None):
        """Add a broker instance to the factory with improved error handling"""
        try:
            if not api_key:
                raise ValueError(f"API key is required for {broker_type}")

            broker = None
            if broker_type == 'oanda':
                if not account_id:
                    raise ValueError("Account ID is required for OANDA")
                broker = OandaBroker(api_key=api_key, account_id=account_id)
            
            elif broker_type == 'alpaca':
                if not api_secret:
                    raise ValueError("API secret is required for Alpaca")
                try:
                    broker = AlpacaBroker(
                        api_key=api_key,
                        api_secret=api_secret,
                        paper=True
                    )
                except Exception as e:
                    raise ConnectionError(f"Failed to connect to Alpaca: {str(e)}")
            else:
                raise ValueError(f"Unsupported broker type: {broker_type}")

            # Test connection before storing
            if not broker or not broker.test_connection():
                self.broker_status[broker_type] = "disconnected"
                raise ConnectionError(f"Failed to connect to {broker_type}")

            # Store broker if connection test passes
            self.brokers[broker_type] = broker
            self.broker_status[broker_type] = "connected"
            return True

        except Exception as e:
            print(f"Error adding broker {broker_type}: {str(e)}")
            self.broker_status[broker_type] = "error"
            return False

    def get_broker(self, broker_type=None):
        """Get a specific broker or the current broker"""
        try:
            if not self.brokers:
                raise ValueError("No brokers initialized. Please configure broker credentials.")
                
            if broker_type and broker_type in self.brokers:
                return self.brokers[broker_type]
                
            if self.current_broker and self.current_broker in self.brokers:
                return self.brokers[self.current_broker]
                
            # Default to first available broker
            first_broker = next(iter(self.brokers.values()))
            if first_broker:
                return first_broker
                
            raise ValueError("No available brokers found")
            
        except Exception as e:
            print(f"Error getting broker: {e}")
            raise

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