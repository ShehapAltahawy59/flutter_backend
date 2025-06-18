from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()

class Emergency:
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client[os.getenv("MONGO_DBNAME", "workout_planner")]
    collection = db['sos_alerts']

    @classmethod
    def create_emergency(cls, user_id, family_id, location, message=None):
        emergency = {
            "user_id": ObjectId(user_id),
            "family_id": ObjectId(family_id),
            "location": location,
            "message": message,
            "status": "active",
            "timestamp": datetime.utcnow()
        }
        return cls.collection.insert_one(emergency)

    @classmethod
    def resolve_emergency(cls, emergency_id):
        return cls.collection.update_one(
            {"_id": ObjectId(emergency_id)},
            {"$set": {
                "status": "resolved",
                "resolved_at": datetime.utcnow()
            }}
        )

    @classmethod
    def get_active_family_emergencies(cls, family_id):
        return list(cls.collection.find({
            "family_id": ObjectId(family_id),
            "status": "active"
        }))
