from flask import Flask
from flask_migrate import Migrate
from models import db, BrokerConfig
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/tradingpal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

def update_database():
    with app.app_context():
        # Drop existing tables and recreate
        db.drop_all()
        db.create_all()
        print("Database schema updated successfully")

if __name__ == '__main__':
    update_database()
