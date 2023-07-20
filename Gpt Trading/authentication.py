from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import configparser
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
CORS(app)
config = configparser.ConfigParser()
config.read('config.ini')

# Database config
username = config.get('database', 'username')
password = config.get('database', 'password')
host = config.get('database', 'host')
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{username}:{password}@{host}/postgres'

# Secret keys
app.secret_key = config.get('secrets', 'flask_secret')


@app.errorhandler(400)
def bad_request_error(error):
    return jsonify({'message': 'Bad request'}), 400

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'message': 'Internal server error'}), 500

@app.route('/')
def home():
    return render_template('home.html')
 

if __name__ == '__main__':
    app.run(port=5010, debug=True)
