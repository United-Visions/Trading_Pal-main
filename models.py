from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    broker_configs = db.relationship('BrokerConfig', backref='user', lazy=True)
    trading_preferences = db.relationship('TradingPreferences', backref='user', lazy=True)
    conversations = db.relationship('Conversation', backref='user', lazy=True)
    strategies = db.relationship('Strategy', backref='user', lazy=True)

class BrokerConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    broker_type = db.Column(db.String(20), nullable=False)  # 'oanda' or 'alpaca'
    api_key = db.Column(db.String(255), nullable=False)
    api_secret = db.Column(db.String(255))  # Only for Alpaca
    account_id = db.Column(db.String(50))   # Only for OANDA
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TradingPreferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    default_units = db.Column(db.Integer, default=100)
    risk_percentage = db.Column(db.Float, default=1.0)
    preferred_pairs = db.Column(db.JSON)  # Store as JSON array
    preferred_stocks = db.Column(db.JSON)  # Store as JSON array
    preferred_cryptos = db.Column(db.JSON)  # Store as JSON array
    trading_style = db.Column(db.String(50))  # e.g., 'swing', 'day', 'scalping'
    default_timeframe = db.Column(db.String(20), default='H1')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    response = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Strategy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    is_private = db.Column(db.Boolean, default=True)
    algo_code = db.Column(db.String)
    currency_pair = db.Column(db.String(50))
    time_frame = db.Column(db.String(50))
    backtest_results = db.relationship('BacktestResult', backref='strategy', lazy=True)
    reviews = db.relationship('Review', backref='strategy', lazy=True)
    comments = db.relationship('Comment', backref='strategy', lazy=True)

class BacktestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategy.id'), nullable=False)
    results = db.Column(db.String)
    analysis = db.Column(db.String)
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
