from flask import Blueprint, request, jsonify, session
from datetime import datetime
import json
import os
from typing import Dict, Any
from models.user import User
from models.alerts import SOSAlert, Event
from utils.db import get_users_collection, get_sos_alerts_collection, get_events_collection
from bson import ObjectId

emergency_bp = Blueprint('emergency', __name__)

@emergency_bp.route('/sos', methods=['POST'])
def create_sos_alert():
    """Create a new SOS alert"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Get user and their family
        user = User.find_by_id(ObjectId(session['user_id']))
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        if not user.get('family_id'):
            return jsonify({'success': False, 'error': 'User not part of a family group'}), 400
        
        # Create SOS alert
        alert = SOSAlert({
            'user_id': str(user['_id']),
            'family_id': str(user['family_id']),
            'location': data.get('location', user.get('location', {})),
            'message': data.get('message', ''),
            'status': 'active'
        })
        
        # Save alert
        result = get_sos_alerts_collection().insert_one(alert.to_dict())
        
        # Create emergency event for family
        event = Event({
            'family_id': str(user['family_id']),
            'created_by': str(user['_id']),
            'title': f"SOS Alert from {user['name']}",
            'description': data.get('message', 'Emergency situation'),
            'location': data.get('location', user.get('location', {})),
            'start_time': datetime.utcnow(),
            'type': 'emergency',
            'priority': 'high',
            'status': 'active',
            'participants': [str(user['_id'])]  # Initially only the alert creator
        })
        
        # Save event
        get_events_collection().insert_one(event.to_dict())
        
        # TODO: Send notifications to family members
        # This would integrate with your notification system
        
        return jsonify({
            'success': True,
            'alert_id': str(result.inserted_id),
            'message': 'SOS alert created and family notified'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@emergency_bp.route('/sos/<alert_id>/acknowledge', methods=['POST'])
def acknowledge_sos_alert(alert_id):
    """Acknowledge an SOS alert"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        # Get alert
        alert = get_sos_alerts_collection().find_one({'_id': ObjectId(alert_id)})
        if not alert:
            return jsonify({'success': False, 'error': 'Alert not found'}), 404
        
        # Check if user is in the same family
        user = User.find_by_id(ObjectId(session['user_id']))
        if not user or str(user['family_id']) != alert['family_id']:
            return jsonify({'success': False, 'error': 'Not authorized'}), 403
        
        # Update alert
        get_sos_alerts_collection().update_one(
            {'_id': ObjectId(alert_id)},
            {
                '$addToSet': {'acknowledged_by': str(user['_id'])},
                '$set': {
                    'status': 'acknowledged',
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        # Update related event
        get_events_collection().update_one(
            {
                'family_id': alert['family_id'],
                'type': 'emergency',
                'created_at': alert['created_at']
            },
            {
                '$addToSet': {'participants': str(user['_id'])},
                '$set': {'status': 'acknowledged'}
            }
        )
        
        return jsonify({
            'success': True,
            'message': 'Alert acknowledged'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@emergency_bp.route('/sos/<alert_id>/resolve', methods=['POST'])
def resolve_sos_alert(alert_id):
    """Resolve an SOS alert"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        # Get alert
        alert = get_sos_alerts_collection().find_one({'_id': ObjectId(alert_id)})
        if not alert:
            return jsonify({'success': False, 'error': 'Alert not found'}), 404
        
        # Check if user is in the same family
        user = User.find_by_id(ObjectId(session['user_id']))
        if not user or str(user['family_id']) != alert['family_id']:
            return jsonify({'success': False, 'error': 'Not authorized'}), 403
        
        # Update alert
        get_sos_alerts_collection().update_one(
            {'_id': ObjectId(alert_id)},
            {
                '$set': {
                    'status': 'resolved',
                    'resolved_at': datetime.utcnow(),
                    'resolved_by': str(user['_id']),
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        # Update related event
        get_events_collection().update_one(
            {
                'family_id': alert['family_id'],
                'type': 'emergency',
                'created_at': alert['created_at']
            },
            {
                '$set': {
                    'status': 'completed',
                    'end_time': datetime.utcnow()
                }
            }
        )
        
        return jsonify({
            'success': True,
            'message': 'Alert resolved'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@emergency_bp.route('/sos/active', methods=['GET'])
def get_active_alerts():
    """Get active SOS alerts for user's family"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        # Get user and their family
        user = User.find_by_id(ObjectId(session['user_id']))
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        if not user.get('family_id'):
            return jsonify({'success': False, 'error': 'User not part of a family group'}), 400
        
        # Get active alerts
        alerts = list(get_sos_alerts_collection().find({
            'family_id': str(user['family_id']),
            'status': {'$in': ['active', 'acknowledged']}
        }).sort('created_at', -1))
        
        # Convert ObjectId to string for JSON serialization
        for alert in alerts:
            alert['_id'] = str(alert['_id'])
        
        return jsonify({
            'success': True,
            'alerts': alerts
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@emergency_bp.route('/sos/history', methods=['GET'])
def get_alert_history():
    """Get SOS alert history for user's family"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        # Get user and their family
        user = User.find_by_id(ObjectId(session['user_id']))
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        if not user.get('family_id'):
            return jsonify({'success': False, 'error': 'User not part of a family group'}), 400
        
        # Get all alerts
        alerts = list(get_sos_alerts_collection().find({
            'family_id': str(user['family_id'])
        }).sort('created_at', -1))
        
        # Convert ObjectId to string for JSON serialization
        for alert in alerts:
            alert['_id'] = str(alert['_id'])
        
        return jsonify({
            'success': True,
            'alerts': alerts
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 
