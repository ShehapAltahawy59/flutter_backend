from models.family import Family
from models.user import User
import requests  # For push notifications
import os
from dotenv import load_dotenv
from flask_socketio import SocketIO, emit

load_dotenv()

socketio = SocketIO()

def init_socketio(app):
    socketio.init_app(app, cors_allowed_origins="*")

class NotificationService:
    @staticmethod
    def send_family_notification(family_id, title, message):
        family = Family.get_family_by_id(family_id)
        if not family:
            return False
        
        for member in family['members']:
            user = User.find_by_id(member['user_id'])
            if user and 'notification_token' in user:
                # Send push notification (example using Firebase)
                requests.post(
                    'https://fcm.googleapis.com/fcm/send',
                    headers={
                        'Authorization': f'key={os.getenv("FIREBASE_KEY")}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'to': user['notification_token'],
                        'notification': {
                            'title': title,
                            'body': message
                        }
                    }
                )
        return True

    @staticmethod
    def send_emergency_alert(user_id, family_id, location):
        user = User.find_by_id(user_id)
        family = Family.get_family_by_id(family_id)
        
        if not user or not family:
            return False
        
        message = f"EMERGENCY! {user['name']} needs help at {location}"
        return NotificationService.send_family_notification(
            family_id,
            "Emergency Alert",
            message
        )


