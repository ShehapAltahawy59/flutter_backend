from flask import Blueprint, request, jsonify
from models.event import Event
from bson import json_util
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

@event_bp.route('/family/<family_id>', methods=['GET'])
def get_family_events(family_id):
    events = Event.get_family_events(family_id)
    return json.loads(json_util.dumps(events)), 200

@event_bp.route('/<event_id>/status', methods=['PUT'])
def update_event_status(event_id):
    data = request.get_json()
    Event.update_event_status(event_id, data['status'])
    return jsonify({"message": "Event status updated"}), 200
