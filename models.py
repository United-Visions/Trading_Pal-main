from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    trading_preferences = db.Column(db.String(80))
    broker_api = db.Column(db.String(120))
    oanda_account_id = db.Column(db.String(120))
    strategies = db.relationship('Strategy', backref='creator', lazy=True)
    conversations = db.relationship('Conversation', backref='user', lazy=True)

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
