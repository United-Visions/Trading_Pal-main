from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from broker_factory import BrokerFactory
from models import User, db, BrokerConfig
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login')
def login_page():
    return render_template('auth.html')

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        email = data.get('email')
        username = data.get('username')
        password = data.get('password')

        if not all([email, username, password]):
            return jsonify({"error": "Missing required fields"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already exists"}), 400
            
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 400

        user = User(
            email=email,
            username=username,
            is_active=True
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        login_user(user)
        return jsonify({"message": "Registration successful", "redirect": url_for('main')})

    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {str(e)}")
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        email = data.get('email')
        password = data.get('password')

        if not all([email, password]):
            return jsonify({"error": "Missing email or password"}), 400

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=True)  # Enable remember me
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Store user settings in session
            session['user_id'] = user.id
            session['selected_broker'] = None  # Will be set after initialization
            
            # Initialize broker configurations
            try:
                broker_configs = BrokerConfig.query.filter_by(user_id=user.id, is_active=True).all()
                broker_factory = BrokerFactory()
                
                if broker_configs:
                    for config in broker_configs:
                        broker_factory.add_broker(
                            broker_type=config.broker_type,
                            api_key=config.api_key,
                            api_secret=config.api_secret,
                            account_id=config.account_id
                        )
                        if not session['selected_broker']:
                            session['selected_broker'] = config.broker_type
                            
                    session['available_brokers'] = [c.broker_type for c in broker_configs]
                    
                return jsonify({
                    "message": "Login successful",
                    "redirect": url_for('main'),
                    "brokers": session.get('available_brokers', [])
                })
            
            except Exception as e:
                print(f"Broker initialization error: {str(e)}")
                # Still allow login even if broker init fails
                return jsonify({
                    "message": "Login successful but broker initialization failed",
                    "redirect": url_for('main'),
                    "warning": str(e)
                })

        return jsonify({"error": "Invalid email or password"}), 401

    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({"error": f"Login failed: {str(e)}"}), 500

@auth_bp.route('/session/check')
def check_session():
    """Check if user session is valid and brokers are initialized"""
    if current_user.is_authenticated:
        try:
            # Verify broker configurations
            broker_configs = BrokerConfig.query.filter_by(
                user_id=current_user.id,
                is_active=True
            ).all()
            
            brokers = [config.broker_type for config in broker_configs]
            
            return jsonify({
                "authenticated": True,
                "user": {
                    "id": current_user.id,
                    "email": current_user.email,
                    "username": current_user.username
                },
                "brokers": brokers,
                "selected_broker": session.get('selected_broker')
            })
        except Exception as e:
            return jsonify({
                "authenticated": True,
                "error": f"Failed to verify broker configurations: {str(e)}"
            })
    return jsonify({"authenticated": False}), 401

@auth_bp.route('/logout')
@login_required
def logout():
    session.clear()  # Clear all session data
    logout_user()
    return redirect(url_for('landing'))
