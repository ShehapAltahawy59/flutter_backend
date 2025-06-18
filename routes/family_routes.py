from flask import Blueprint, request, jsonify
from models.family import Family
from bson import json_util
import json

family_bp = Blueprint('family', __name__, url_prefix='/api/families')

@family_bp.route('/', methods=['POST'])
def create_family():
    data = request.get_json()
    if not data or 'name' not in data or 'admin_user_id' not in data:
        return jsonify({"error": "Name and admin user ID are required"}), 400
    
    result = Family.create_family(data['name'], data['admin_user_id'])
    return jsonify({
        "message": "Family created successfully",
        "family_id": str(result.inserted_id)
    }), 201

@family_bp.route('/<family_id>/members', methods=['POST','GET'])
def add_member(family_id):
    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({"error": "User ID is required"}), 400
    
    role = data.get('role', 'member')
    Family.add_member(family_id, data['user_id'], role)
    return jsonify({"message": "Member added successfully"}), 200

@family_bp.route('/<family_id>', methods=['GET'])
def get_family(family_id):
    family = Family.find_by_id(family_id)
    if not family:
        return jsonify({"error": "Family not found"}), 404
    return json.loads(json_util.dumps(family)), 200

@family_bp.route('/user/<user_id>', methods=['GET'])
def get_user_families(user_id):
    families = Family.find_by_member(user_id)
    return json.loads(json_util.dumps(families)), 200

@family_bp.route('/<family_id>/settings', methods=['PUT'])
def update_settings(family_id):
    data = request.get_json()
    if not data or 'settings' not in data:
        return jsonify({"error": "Settings data is required"}), 400
    
    Family.update_settings(family_id, data['settings'])
    return jsonify({"message": "Settings updated successfully"}), 200
