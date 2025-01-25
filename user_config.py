from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, BrokerConfig
from datetime import datetime

user_config_bp = Blueprint('user_config', __name__)

@user_config_bp.route('/api/v1/broker/settings', methods=['GET'])
@login_required
def get_broker_settings():
    try:
        settings = {}
        for config in current_user.broker_configs:
            if config.broker_type == 'oanda':
                settings['oanda'] = {
                    'api_key': config.api_key,
                    'account_id': config.account_id
                }
            elif config.broker_type == 'alpaca':
                settings['alpaca'] = {
                    'api_key': config.api_key,
                    'api_secret': config.api_secret
                }
        return jsonify(settings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_config_bp.route('/api/v1/broker/settings', methods=['POST'])
@login_required
def save_broker_settings():
    try:
        data = request.json
        broker_type = data['broker_type']
        settings = data['settings']
        
        config = BrokerConfig.query.filter_by(
            user_id=current_user.id,
            broker_type=broker_type
        ).first()
        
        if not config:
            config = BrokerConfig(
                user_id=current_user.id,
                broker_type=broker_type
            )
            
        config.api_key = settings.get('api_key')
        if broker_type == 'oanda':
            config.account_id = settings.get('account_id')
        else:
            config.api_secret = settings.get('api_secret')
            
        config.is_active = True
        config.updated_at = datetime.utcnow()
        
        db.session.add(config)
        db.session.commit()
        
        return jsonify({"message": "Settings saved successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
