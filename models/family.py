from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()

class Family:
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client[os.getenv("MONGO_DBNAME", "flutter_project")]
    collection = db['families']

    @classmethod
    def create_family(cls, name, admin_user_id):
        """Create a new family group"""
        family_data = {
            "name": name,
            "admin_user_id": ObjectId(admin_user_id),
            "members": [{
                "user_id": ObjectId(admin_user_id),
                "join_date": datetime.utcnow(),
                "role": "admin",
                "permissions": {
                    "manage_events": True,
                    "manage_members": True,
                    "send_emergencies": True
                }
            }],
            "settings": {
                "emergency_contacts": [],
                "notification_preferences": {
                    "events": True,
                    "emergencies": True,
                    "reminders": True
                }
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        return cls.collection.insert_one(family_data)

    @classmethod
    def add_member(cls, family_id, user_id, role="member"):
        """Add a member to the family with default permissions"""
        permissions = {
            "manage_events": role in ["admin", "parent"],
            "manage_members": role == "admin",
            "send_emergencies": True
        }
        
        return cls.collection.update_one(
            {"_id": ObjectId(family_id)},
            {
                "$push": {
                    "members": {
                        "user_id": ObjectId(user_id),
                        "join_date": datetime.utcnow(),
                        "role": role,
                        "permissions": permissions
                    }
                },
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

    @classmethod
    def find_by_id(cls, family_id):
        """Find a family by its ID"""
        return cls.collection.find_one({"_id": ObjectId(family_id)})

    @classmethod
    def find_by_member(cls, user_id):
        """Find all families a user belongs to"""
        return list(cls.collection.find({"members.user_id": ObjectId(user_id)}))

    @classmethod
    def update_settings(cls, family_id, settings):
        """Update family settings"""
        return cls.collection.update_one(
            {"_id": ObjectId(family_id)},
            {
                "$set": {
                    "settings": settings,
                    "updated_at": datetime.utcnow()
                }
            }
        )
