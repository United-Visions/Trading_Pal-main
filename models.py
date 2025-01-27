from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    broker_configs = db.relationship('BrokerConfig', backref='user', lazy=True, cascade='all, delete-orphan')
    trading_preferences = db.relationship('TradingPreferences', backref='user', lazy=True, uselist=False)
    conversations = db.relationship('Conversation', backref='user', lazy=True, cascade='all, delete-orphan')
    strategies = db.relationship('Strategy', backref='user', lazy=True, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_broker_config(self, broker_type):
        return any(config.broker_type == broker_type and config.is_active for config in self.broker_configs)

    def get_active_brokers(self):
        return [config.broker_type for config in self.broker_configs if config.is_active]

class BrokerConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    broker_type = db.Column(db.String(20), nullable=False)  # 'oanda' or 'alpaca'
    
    # Oanda specific fields
    oanda_api_key = db.Column(db.String(255))
    oanda_account_id = db.Column(db.String(50))
    oanda_environment = db.Column(db.String(20), default='practice')  # 'practice' or 'live'
    
    # Alpaca specific fields
    alpaca_api_key = db.Column(db.String(255))
    alpaca_api_secret = db.Column(db.String(255))
    alpaca_paper_trading = db.Column(db.Boolean, default=True)
     
    # Common fields
    supported_markets = db.Column(db.JSON)  # ['forex', 'crypto', 'stocks', 'options']
    is_active = db.Column(db.Boolean, default=True)
    connection_status = db.Column(db.String(20), default='disconnected')
    last_connection_check = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Backward compatibility properties
    @property
    def api_key(self):
        return self.oanda_api_key if self.broker_type == 'oanda' else self.alpaca_api_key

    @property
    def api_secret(self):
        return self.alpaca_api_secret if self.broker_type == 'alpaca' else None

    @property
    def account_id(self):
        return self.oanda_account_id if self.broker_type == 'oanda' else None

    def get_credentials(self):
        """Get broker-specific credentials"""
        if self.broker_type == 'oanda':
            return {
                'api_key': self.oanda_api_key,
                'account_id': self.oanda_account_id,
                'environment': self.oanda_environment
            }
        else:
            return {
                'api_key': self.alpaca_api_key,
                'api_secret': self.alpaca_api_secret,
                'paper_trading': self.alpaca_paper_trading
            }

    __table_args__ = (
        db.UniqueConstraint('user_id', 'broker_type', name='unique_user_broker'),
    )

class TradingPreferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Risk Management
    default_units = db.Column(db.Integer, default=100)
    risk_percentage = db.Column(db.Float, default=1.0)
    max_position_size = db.Column(db.Float)
    stop_loss_percentage = db.Column(db.Float)
    take_profit_percentage = db.Column(db.Float)
    use_trailing_stop = db.Column(db.Boolean, default=False)
    trailing_stop_distance = db.Column(db.Float)
    
    # Trading Preferences
    preferred_pairs = db.Column(db.JSON)  # Store as JSON array
    preferred_stocks = db.Column(db.JSON)  # Store as JSON array
    preferred_cryptos = db.Column(db.JSON)  # Store as JSON array
    excluded_symbols = db.Column(db.JSON)  # Symbols to avoid
    trading_style = db.Column(db.String(50))  # 'swing', 'day', 'scalping'
    default_timeframe = db.Column(db.String(20), default='H1')
    trading_hours_start = db.Column(db.Time)
    trading_hours_end = db.Column(db.Time)
    trading_days = db.Column(db.JSON)  # Array of enabled trading days
    
    # Market Preferences
    preferred_markets = db.Column(db.JSON)  # 'forex', 'stocks', 'crypto'
    market_order_preference = db.Column(db.String(20), default='market')  # 'market', 'limit'
    
    # Notification Settings
    enable_email_alerts = db.Column(db.Boolean, default=False)
    enable_trade_confirmations = db.Column(db.Boolean, default=True)
    enable_price_alerts = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def set_trading_days(self, days):
        self.trading_days = json.dumps(days)

    def get_trading_days(self):
        return json.loads(self.trading_days) if self.trading_days else []

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50))  # 'trade', 'alert', 'system'
    message = db.Column(db.String(500))
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    response = db.Column(db.String(500), nullable=False)
    broker_context = db.Column(db.String(20))  # Track which broker was active
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Strategy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    is_private = db.Column(db.Boolean, default=True)
    algo_code = db.Column(db.Text)
    currency_pair = db.Column(db.String(50))
    time_frame = db.Column(db.String(50))
    broker_type = db.Column(db.String(20))  # Strategy specific to broker
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    backtest_results = db.relationship('BacktestResult', backref='strategy', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='strategy', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='strategy', lazy=True, cascade='all, delete-orphan')

class BacktestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategy.id'), nullable=False)
    broker_type = db.Column(db.String(20))
    results = db.Column(db.Text)
    analysis = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategy.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stars = db.Column(db.Integer)
    content = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategy.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    content = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Indicator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(500))
    calculation_code = db.Column(db.Text, nullable=False)  # Python code for calculation
    parameters = db.Column(db.JSON)  # JSON representation of parameters
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Indicator {self.name}>"
