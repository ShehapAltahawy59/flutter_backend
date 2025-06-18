from flask import Blueprint, request, jsonify
from models.emergency import Emergency
from models.family import Family
from models.user import User
from bson import json_util, ObjectId
import json
import firebase_admin
from firebase_admin import credentials, messaging
import os
from dotenv import load_dotenv; 
load_dotenv(override=True)
firebase_creds = {
            "type": os.getenv("FIREBASE_TYPE"),
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
            "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_CERT_URL"),
            "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL")
        }

        # Initialize Firebase Admin SDK with the constructed credentials
cred = credentials.Certificate(firebase_creds)

firebase_admin.initialize_app(cred)

emergency_bp = Blueprint('emergency', __name__, url_prefix='/api/emergency')

def send_family_notification(family_id, title, body, data=None):
    topic = "family_"+str(family_id)
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        topic=topic,
        data=data or {}
    )
    response = messaging.send(message)
    return response

@emergency_bp.route('/', methods=['POST'])
def create_emergency():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Convert string IDs to ObjectId
        user_id = str(data['user_id'])
        family_id = str(data['family_id'])

        # Fetch user from DB to get name
        user = User.find_by_id(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        user_name = user.get('name', 'A family member')

        result = Emergency.create_emergency(
            user_id,
            family_id,
            data['location'],
            data.get('message','Emergency situation')
        )
        send_family_notification(
            family_id=family_id,
            title="SOS Alert!",
            body=f"SOS alert from {user_name}: {data.get('message', 'Emergency situation')}",
            data={"type": "sos", "family_id": str(family_id)}
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
