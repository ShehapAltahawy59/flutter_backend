from flask import Blueprint, request, jsonify
from models.family import Family
from models.user import User
from bson import json_util, ObjectId
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

@family_bp.route('/<family_id>/members', methods=['POST'])
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

@family_bp.route('/user/<user_id>/members', methods=['GET'])
def get_user_family_members(user_id):
    """Get all members of the family that the user belongs to"""
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
        
        # Get all members' details
        members = []
        for member_id in family.get('members', []):
            user = User.find_by_id(member_id)
            if user:
                members.append({
                    'user_id': str(user['_id']),
                    'name': user['name'],
                    'email': user['email'],
                    'phone': user['phone']
                })
        
        return jsonify({
            'success': True,
            'family_id': str(family['_id']),
            'family_name': family['name'],
            'members': members
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
