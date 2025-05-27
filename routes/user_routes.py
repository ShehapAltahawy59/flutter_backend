from flask import Blueprint, request, jsonify
from models.user import User
from utils.db import DatabaseConnection
from bson import json_util
import json
from datetime import datetime
from bson import ObjectId

user_bp = Blueprint('users', __name__, url_prefix='/api/users')

@user_bp.route('/', methods=['GET'])
def get_all_users():
    try:
        db = DatabaseConnection.get_instance()
        users = list(db.get_users_collection().find({}))
        # Convert MongoDB ObjectId to string for JSON serialization
        users_json = json.loads(json_util.dumps(users))
        return jsonify(users_json), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        print(f"Looking up user with ID: {user_id}")
        user = User.find_by_id(user_id)
        
        if user:
            print(f"Found user: {user}")
            return json.loads(json_util.dumps(user)), 200
        else:
            print(f"No user found with ID: {user_id}")
            return jsonify({
                'error': 'User not found',
                'user_id': user_id
            }), 404
    except Exception as e:
        print(f"Error getting user: {str(e)}")
        return jsonify({
            'error': str(e),
            'user_id': user_id
        }), 500

@user_bp.route('/', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'name', 'phone', 'password_hash']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Add timestamps
        data['created_at'] = datetime.utcnow()
        data['updated_at'] = datetime.utcnow()
        
        # Create user
        result = User.create(data)
        
        if result.inserted_id:
            # Get the created user
            created_user = User.find_by_id(result.inserted_id)
            return json.loads(json_util.dumps(created_user)), 201
        else:
            return jsonify({
                'error': 'Failed to create user'
            }), 500
            
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500

@user_bp.route('/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        print(f"Attempting to delete user with ID: {user_id}")
        
        # First check if user exists
        user = User.find_by_id(user_id)
        if not user:
            return jsonify({
                'error': 'User not found',
                'user_id': user_id
            }), 404
        
        # Delete the user
        db = DatabaseConnection.get_instance()
        result = db.get_users_collection().delete_one({"_id": ObjectId(user_id)})
        
        if result.deleted_count > 0:
            return jsonify({
                'message': 'User deleted successfully',
                'user_id': user_id
            }), 200
        else:
            return jsonify({
                'error': 'Failed to delete user',
                'user_id': user_id
            }), 500
            
    except Exception as e:
        print(f"Error deleting user: {str(e)}")
        return jsonify({
            'error': str(e),
            'user_id': user_id
        }), 500
