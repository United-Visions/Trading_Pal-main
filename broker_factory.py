from flask import config, session
from oanda_broker import OandaBroker
from alpaca_broker import AlpacaBroker
import configparser
from typing import Dict, Optional, Any
from models import User, BrokerConfig
import logging

logger = logging.getLogger(__name__)

class BrokerFactory:
    def __init__(self, config_path='config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        self.brokers: Dict[str, Any] = {}
        self.broker_status: Dict[str, str] = {}
        self.current_broker: Optional[str] = None
        self.active_brokers = set()

    def initialize_user_brokers(self, user: User) -> bool:
        """Initialize all active brokers for a user"""
        try:
            logger.info(f"Initializing brokers for user {user.id}")
            configs = BrokerConfig.query.filter_by(
                user_id=user.id,
                is_active=True
            ).all()
            
            success = False
            
            for config in configs:
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
                    logger.info(f"Successfully initialized {config.broker_type} broker")
                    
                    # Set current broker if not set
                    if not self.current_broker:
                        self.set_current_broker(config.broker_type)
                        
            return success
            
        except Exception as e:
            logger.error(f"Error initializing brokers: {e}")
            return False

    def add_broker(self, broker_type: str, api_key: str = None, api_secret: str = None, account_id: str = None) -> bool:
        """Add a broker instance to the factory"""
        try:
            logger.info(f"Adding broker: {broker_type}")
            if broker_type == 'oanda':
                if not api_key or not account_id:
                    raise ValueError("OANDA requires both API key and account ID")
                broker = OandaBroker(api_key=api_key, account_id=account_id)
                
            elif broker_type == 'alpaca':
                if not api_key or not api_secret:
                    raise ValueError("Alpaca requires both API key and secret")
                broker = AlpacaBroker(api_key=api_key, api_secret=api_secret)
            else:
                raise ValueError(f"Unsupported broker type: {broker_type}")

            # Test connection
            if broker.test_connection():
                self.brokers[broker_type] = broker
                self.broker_status[broker_type] = "connected"
                self.active_brokers.add(broker_type)
                logger.info(f"Successfully added and connected {broker_type} broker")
                return True
            else:
                self.broker_status[broker_type] = "disconnected"
                logger.error(f"Failed to connect to {broker_type} broker")
                return False

        except Exception as e:
            logger.error(f"Error adding broker {broker_type}: {str(e)}")
            self.broker_status[broker_type] = "error"
            return False

    def get_broker(self, broker_type: Optional[str] = None) -> Any:
        """Get broker instance, defaulting to current if none specified"""
        try:
            # Use provided type or current broker
            broker_type = broker_type or self.current_broker
            
            if not broker_type:
                raise ValueError("No broker type specified and no current broker set")
                
            logger.info(f"Getting broker: {broker_type}")
            
            if broker_type not in self.brokers:
                raise ValueError(f"Broker {broker_type} not initialized")
                
            return self.brokers[broker_type]
            
        except Exception as e:
            logger.error(f"Error getting broker: {str(e)}")
            raise

    def set_current_broker(self, broker_type: str) -> None:
        """Set the current active broker"""
        if broker_type not in self.brokers:
            raise ValueError(f"Cannot set current broker to {broker_type} - not initialized")
            
        self.current_broker = broker_type
        session['selected_broker'] = broker_type
        logger.info(f"Set current broker to: {broker_type}")

    def get_current_broker(self) -> Optional[str]:
        """Get current broker type"""
        return self.current_broker

    def get_broker_status(self, broker_type: str) -> str:
        """Get connection status for a broker"""
        return self.broker_status.get(broker_type, "not_configured")

    def get_available_brokers(self) -> list:
        """Get list of initialized broker types"""
        return list(self.brokers.keys())

    def get_active_brokers(self) -> set:
        """Get set of active broker types"""
        return self.active_brokers

    def check_broker_ready(self, broker_type: str) -> bool:
        """Check if a broker is initialized and connected"""
        return (
            broker_type in self.brokers and 
            self.broker_status.get(broker_type) == "connected"
        )

    def cleanup(self) -> None:
        """Clean up broker connections"""
        self.brokers.clear()
        self.broker_status.clear()
        self.current_broker = None
        self.active_brokers.clear()