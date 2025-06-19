from flask import Blueprint, request, jsonify
from models.event import Event
from models.family import Family
from bson import json_util, ObjectId
import json

event_bp = Blueprint('event', __name__, url_prefix='/api/events')

@event_bp.route('/', methods=['POST'])
def create_event():
    data = request.get_json()
    result = Event.create_event(data)
    return jsonify({
        "message": "Event created successfully",
        "event_id": str(result.inserted_id)
    }), 201

@event_bp.route('/<event_id>', methods=['GET'])
def get_event(event_id):
    event = Event.get_event(event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404
    return json.loads(json_util.dumps(event)), 200

@event_bp.route('/', methods=['GET'])
def get_all_events():
    status = request.args.get('status')
    family_id = request.args.get('family_id')
    
    query = {}
    if status:
        query['status'] = status
    if family_id:
        query['family_id'] = ObjectId(family_id)
        
    events = Event.get_all_events(query)
    return json.loads(json_util.dumps(events)), 200

@event_bp.route('/family/<family_id>', methods=['GET'])
def get_family_events(family_id):
    events = Event.get_family_events(family_id)
    return json.loads(json_util.dumps(events)), 200

@event_bp.route('/<event_id>', methods=['PUT'])
def update_event(event_id):
    data = request.get_json()
    result = Event.update_event(event_id, data)
    if not result:
        return jsonify({"error": "Event not found"}), 404
    return jsonify({"message": "Event updated successfully"}), 200

@event_bp.route('/<event_id>/status', methods=['PUT'])
def update_event_status(event_id):
    data = request.get_json()
    Event.update_event_status(event_id, data['status'])
    return jsonify({"message": "Event status updated"}), 200

@event_bp.route('/<event_id>/join', methods=['POST'])
def join_event(event_id):
    try:
        user_id = request.json.get('user_id')
        user_name = request.json.get('name')
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
            
        result = Event.join_event(event_id, user_id,user_name)
        if not result:
            return jsonify({"error": "Event not found"}), 404
            
        return jsonify({
            "success": True,
            "message": "Successfully joined event"
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@event_bp.route('/<event_id>/leave', methods=['POST'])
def leave_event(event_id):
    try:
        user_id = request.json.get('user_id')
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
            
        result = Event.leave_event(event_id, user_id)
        if not result:
            return jsonify({"error": "Event not found"}), 404
            
        return jsonify({
            "success": True,
            "message": "Successfully left event"
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@event_bp.route('/<event_id>', methods=['DELETE'])
def delete_event(event_id):
    result = Event.delete_event(event_id)
    if not result:
        return jsonify({"error": "Event not found"}), 404
    return jsonify({"message": "Event deleted successfully"}), 200

@event_bp.route('/user/<user_id>/family-events', methods=['GET'])
def get_user_family_events(user_id):
    """Get all events in the user's family"""
    try:
        # First find the family the user belongs to
        families = Family.find_by_member(user_id)
        
        if not families:
            return jsonify({
                'success': False,
                'error': 'User not part of any family'
            }), 404
            
        # Get the first family (assuming user belongs to one family)
        family = families[0]
        family_id = str(family['_id'])
        
        # Get all events for this family
        events = Event.get_family_events(family_id)
        
        return jsonify({
            'success': True,
            'family_id': family_id,
            'family_name': family['name'],
            'events': json.loads(json_util.dumps(events))
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
