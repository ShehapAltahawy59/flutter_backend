from flask import Blueprint, request, jsonify
from models.emergency import Emergency
from models.family import Family
from bson import json_util, ObjectId
import json

emergency_bp = Blueprint('emergency', __name__, url_prefix='/api/emergency')

@emergency_bp.route('/', methods=['POST'])
def create_emergency():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Convert string IDs to ObjectId
        user_id = ObjectId(data['user_id'])
        family_id = ObjectId(data['family_id'])

        result = Emergency.create_emergency(
            user_id,
            family_id,
            data['location'],
            data.get('message')
        )
        return jsonify({
            "success": True,
            "message": "Emergency alert sent to family",
            "emergency_id": str(result.inserted_id)
        }), 201
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@emergency_bp.route('/resolve/<emergency_id>', methods=['PUT'])
def resolve_emergency(emergency_id):
    try:
        Emergency.resolve_emergency(emergency_id)
        return jsonify({
            "success": True,
            "message": "Emergency resolved"
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@emergency_bp.route('/family/<family_id>', methods=['GET'])
def get_family_emergencies(family_id):
    try:
        emergencies = Emergency.get_active_family_emergencies(family_id)
        return jsonify({
            "success": True,
            "alerts": json.loads(json_util.dumps(emergencies))
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
