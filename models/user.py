from datetime import datetime
from typing import List, Dict, Optional
from bson import ObjectId
from utils.db import DatabaseConnection

class User:
    def __init__(self, data: Dict):
        self._id = data.get('_id', ObjectId())
        self.email = data['email']
        self.name = data['name']
        self.phone = data['phone']
        self.password_hash = data['password_hash']
        self.family_id = data.get('family_id')  # Reference to family group
        self.role = data.get('role', 'member')  # admin, member
        self.created_at = data.get('created_at', datetime.utcnow())
        self.updated_at = data.get('updated_at', datetime.utcnow())
        self.last_login = data.get('last_login')
        self.is_active = data.get('is_active', True)
        self.emergency_contacts = data.get('emergency_contacts', [])
        self.location = data.get('location', {
            'latitude': None,
            'longitude': None,
            'last_updated': None
        })
        self.settings = data.get('settings', {
            'notifications_enabled': True,
            'location_sharing': True,
            'fitness_data_private': True
        })

    def to_dict(self) -> Dict:
        return {
            '_id': self._id,
            'email': self.email,
            'name': self.name,
            'phone': self.phone,
            'password_hash': self.password_hash,
            'family_id': self.family_id,
            'role': self.role,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'last_login': self.last_login,
            'is_active': self.is_active,
            'emergency_contacts': self.emergency_contacts,
            'location': self.location,
            'settings': self.settings
        }

    @classmethod
    def find_by_id(cls, user_id):
        try:
            db = DatabaseConnection.get_instance()
            print(f"[DEBUG] Finding user with ID: {user_id}")
            # Convert string ID to ObjectId
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            print(f"[DEBUG] Converted user_id to ObjectId: {user_id}")
            
            user = db.get_users_collection().find_one({"_id": user_id})
            print(f"[DEBUG] Found user: {user}")
            return user
        except Exception as e:
            print(f"[DEBUG] Error finding user by ID: {str(e)}")
            print(f"[DEBUG] Error type: {type(e)}")
            return None
    
    @classmethod
    def create(cls, user_data):
        try:
            db = DatabaseConnection.get_instance()
            print(f"[DEBUG] Creating user with data: {user_data}")
            
            # If _id is provided as string, convert to ObjectId
            if '_id' in user_data and isinstance(user_data['_id'], str):
                user_data['_id'] = ObjectId(user_data['_id'])
                print(f"[DEBUG] Converted _id to ObjectId: {user_data['_id']}")
            
            result = db.get_users_collection().insert_one(user_data)
            print(f"[DEBUG] User created with ID: {result.inserted_id}")
            return result
        except Exception as e:
            print(f"[DEBUG] Error creating user: {str(e)}")
            raise
    
    @classmethod
    def update_fitness_goals(cls, user_id, goals):
        db = DatabaseConnection.get_instance()
        return db.get_users_collection().update_one(
            {"_id": user_id},
            {"$set": {"fitness.goals": goals}}
        )

class Family:
    def __init__(self, data: Dict):
        self._id = data.get('_id', ObjectId())
        self.name = data['name']
        self.created_by = data['created_by']  # User ID of creator
        self.members = data.get('members', [])  # List of user IDs
        self.created_at = data.get('created_at', datetime.utcnow())
        self.updated_at = data.get('updated_at', datetime.utcnow())
        self.settings = data.get('settings', {
            'location_sharing': True,
            'event_notifications': True,
            'sos_notifications': True
        })

    def to_dict(self) -> Dict:
        return {
            '_id': self._id,
            'name': self.name,
            'created_by': self.created_by,
            'members': self.members,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'settings': self.settings
        }
