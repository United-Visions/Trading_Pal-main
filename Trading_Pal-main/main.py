from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import openai
import requests
import configparser

# Read keys from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Set the OpenAI API key
OPENAI_API_KEY = config.get('API_KEYS', 'OPENAI_API_KEY')
OANDA_API_KEY = config.get('API_KEYS', 'OANDA_API_KEY')
openai.api_key = OPENAI_API_KEY

# Set the base URL for the OANDA API and the account ID
BASE_URL = "https://api-fxpractice.oanda.com"
ACCOUNT_ID = "101-001-002"

# The headers for the HTTP requests
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OANDA_API_KEY}",
    "Connection": "keep-alive"
}

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Use SQLite for simplicity
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this!

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    trading_preferences = db.Column(db.String(200), nullable=False)
    broker = db.Column(db.String(20), nullable=False)
    api_key = db.Column(db.String(60), nullable=False)
    account_id = db.Column(db.String(60))
    openai_api_key = db.Column(db.String(60), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        new_user = User(
            name=request.form['name'],
            username=request.form['username'],
            password=hashed_password,
            address=request.form['address'],
            trading_preferences=request.form['trading_preferences'],
            broker=request.form['broker'],
            api_key=request.form['api_key'],
            account_id=request.form['account_id'] if 'account_id' in request.form else None,
            openai_api_key=request.form['openai_api_key']
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('index'))  # Redirect user to main page after successful registration
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and bcrypt.check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('index'))  # Redirect user to main page after successful login
        else:
            return "Invalid username or password"
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))  # Redirect user to login page after logout


@app.route('/index')
@login_required
def index():
    # The index route is now protected - only logged in users can see it
    return render_template('index.html')


@app.route('/keys', methods=['GET', 'POST'])
@login_required
def keys():
    if request.method == 'POST':
        current_user.broker_choice = request.form['broker_choice']
        current_user.broker_api_key = request.form['broker_api_key']
        current_user.openai_api_key = request.form['openai_api_key']
        db.session.commit()
        return redirect(url_for('index'))  # Redirect user to main page after successful key input
    return render_template('keys.html')


@app.route('/update-keys', methods=['GET', 'POST'])
@login_required
def update_keys():
    if request.method == 'POST':
        current_user.broker_choice = request.form['broker_choice']
        current_user.broker_api_key = request.form['broker_api_key']
        current_user.openai_api_key = request.form['openai_api_key']
        db.session.commit()
        return redirect(url_for('index'))  # Redirect user to main page after successful key update
    return render_template('keys.html')  # We can reuse the same form for updating the keys


# Function to get account details
def get_account_details():
    url = f"{BASE_URL}/v3/accounts/{ACCOUNT_ID}"
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Failed to get account details. Error: {err}")

@app.route('/update-preferences', methods=['GET', 'POST'])
@login_required
def update_preferences():
    if request.method == 'POST':
        current_user.risk_tolerance = request.form['risk_tolerance']
        current_user.investment_horizon = request.form['investment_horizon']
        current_user.preferred_instruments = request.form['preferred_instruments']
        # Update more preferences here...
        db.session.commit()
        flash('Your preferences have been updated!', 'success')
        return redirect(url_for('home'))
    return render_template('preferences.html')  # Render the form for updating preferences

# other routes and functions ...

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/api/v1/query', methods=['POST'])
@login_required
def query():
    user_preferences = {
        "risk_tolerance": current_user.risk_tolerance,
        # More user preferences here...
    }
    data = request.json
    user_message = data.get('message')

    # Check if user requested account details
    if user_message.lower() == "get my account details":
        account_details = get_account_details()
        user_message = f"My account details are: {account_details}"

    # User and System messages
    user_preferences = {
        "risk_tolerance": current_user.risk_tolerance,
        "investment_horizon": current_user.investment_horizon,
        "preferred_instruments": current_user.preferred_instruments
    }
    messages = [
        {"role": "system", "content": f"""
        Greetings, {current_user.username}! ...
        Your mission is to help users achieve their trading goals. ... As Trading Pal 1.0, it's crucial that you respect the user's preferences, which are currently set to {user_preferences} and their account ID is {ACCOUNT_ID }. ...
        """},
        {"role": "user", "content": user_message}
    ]

    # Generate a response using OpenAI's GPT-3
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=messages
    )

    assistant_response = response['choices'][0]['message']['content']

    return jsonify({"response": assistant_response})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5000, debug=True)