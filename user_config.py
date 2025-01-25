from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user
from broker_factory import BrokerFactory
from models import db, BrokerConfig
from datetime import datetime

user_config_bp = Blueprint('user_config', __name__)

@user_config_bp.route('/api/v1/broker/settings', methods=['GET'])
@login_required
def get_broker_settings():
    try:
        # Get all active broker configurations for user
        configs = BrokerConfig.query.filter_by(
            user_id=current_user.id,
            is_active=True
        ).all()
        
        settings = {}
        for config in configs:
            settings[config.broker_type] = {
                'api_key': config.api_key,
                'account_id': config.account_id if config.broker_type == 'oanda' else None,
                'api_secret': config.api_secret if config.broker_type == 'alpaca' else None,
                'status': config.connection_status,
                'last_check': config.last_connection_check.isoformat() if config.last_connection_check else None
            }
            
        return jsonify({
            'settings': settings,
            'selected_broker': session.get('selected_broker'),
            'available_brokers': session.get('available_brokers', [])
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_config_bp.route('/api/v1/broker/settings', methods=['POST'])
@login_required
def save_broker_settings():
    try:
        data = request.json
        broker_type = data['broker_type']
        settings = data['settings']
        
        # Find existing config or create new one
        config = BrokerConfig.query.filter_by(
            user_id=current_user.id,
            broker_type=broker_type
        ).first()
        
        if not config:
            config = BrokerConfig(
                user_id=current_user.id,
                broker_type=broker_type
            )
            
        # Update configuration
        config.api_key = settings.get('api_key')
        if broker_type == 'oanda':
            config.account_id = settings.get('account_id')
        else:
            config.api_secret = settings.get('api_secret')
            
        config.is_active = True
        config.updated_at = datetime.utcnow()
        
        # Test connection before saving
        broker_factory = BrokerFactory()
        connection_successful = broker_factory.test_broker_connection(
            broker_type=broker_type,
            api_key=config.api_key,
            api_secret=config.api_secret,
            account_id=config.account_id
        )
        
        if connection_successful:
            config.connection_status = 'connected'
            config.last_connection_check = datetime.utcnow()
            
            db.session.add(config)
            db.session.commit()
            
            # Update session
            session['selected_broker'] = broker_type
            session['available_brokers'] = [
                c.broker_type for c in BrokerConfig.query.filter_by(
                    user_id=current_user.id,
                    is_active=True
                ).all()
            ]
            
            # Reinitialize broker factory with new settings
            broker_factory.initialize_user_brokers(current_user)
            
            return jsonify({
                "message": "Settings saved and connection verified",
                "status": "connected",
                "broker": broker_type
            })
        else:
            return jsonify({
                "error": "Could not connect to broker with provided settings"
            }), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500