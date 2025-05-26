from flask import Blueprint, jsonify
from models.user import User
from bson import json_util
import json

user_bp = Blueprint('user', __name__)

@user_bp.route('/', methods=['GET'])
def get_all_users():
    try:
        users = list(User.collection.find({}))
        # Convert MongoDB ObjectId to string for JSON serialization
        users_json = json.loads(json_util.dumps(users))
        return jsonify(users_json), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = User.find_by_id(user_id)
        if user:
            return json.loads(json_util.dumps(user)), 200
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
