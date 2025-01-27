from flask import Flask
from flask_migrate import Migrate
from models import db, User, BrokerConfig
import os
from flask_sqlalchemy import SQLAlchemy

# Ensure instance directory exists
INSTANCE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
if not os.path.exists(INSTANCE_PATH):
    os.makedirs(INSTANCE_PATH)

# Initialize Flask app with explicit instance path
app = Flask(__name__, instance_path=INSTANCE_PATH)
app.config['SECRET_KEY'] = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(INSTANCE_PATH, "tradingpal.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

def run_migrations():
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Initialize migrations
        if not os.path.exists('migrations'):
            # Set FLASK_APP environment variable
            os.environ['FLASK_APP'] = 'run_migrations.py'
            # Initialize migrations directory
            os.system('flask db init')
        
        # Generate and run migration
        os.system('flask db migrate -m "Update broker config model"')
        os.system('flask db upgrade')
        
        print("Migration complete. Updating existing data...")
        update_existing_data()

def update_existing_data():
    """Update existing broker configurations with new structure"""
    try:
        configs = BrokerConfig.query.all()
        for config in configs:
            if config.broker_type == 'oanda':
                config.oanda_api_key = getattr(config, 'api_key', None)
                config.oanda_account_id = getattr(config, 'account_id', None)
                config.supported_markets = ['forex']
            elif config.broker_type == 'alpaca':
                config.alpaca_api_key = getattr(config, 'api_key', None)
                config.alpaca_api_secret = getattr(config, 'api_secret', None)
                config.supported_markets = ['stocks', 'crypto']
        
        db.session.commit()
        print("Successfully updated existing broker configurations")
        
    except Exception as e:
        print(f"Error updating existing data: {e}")
        db.session.rollback()

if __name__ == '__main__':
    # Set Flask environment variables
    os.environ['FLASK_APP'] = 'run_migrations.py'
    os.environ['FLASK_ENV'] = 'development'
    
    # Run migrations
    run_migrations()
