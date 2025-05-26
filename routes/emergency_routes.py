from flask import Blueprint, request, jsonify
from models.emergency import Emergency
from models.family import Family
from bson import json_util
import json

emergency_bp = Blueprint('emergency', __name__, url_prefix='/api/emergency')

@emergency_bp.route('/', methods=['POST'])
def create_emergency():
    data = request.get_json()
    result = Emergency.create_emergency(
        data['user_id'],
        data['family_id'],
        data['location'],
        data.get('message')
    )
    return jsonify({
        "message": "Emergency alert sent to family",
        "emergency_id": str(result.inserted_id)
    }), 201

@emergency_bp.route('/resolve/<emergency_id>', methods=['PUT'])
def resolve_emergency(emergency_id):
    Emergency.resolve_emergency(emergency_id)
    return jsonify({"message": "Emergency resolved"}), 200

@emergency_bp.route('/family/<family_id>', methods=['GET'])
def get_family_emergencies(family_id):
    emergencies = Emergency.get_active_family_emergencies(family_id)
    return json.loads(json_util.dumps(emergencies)), 200
