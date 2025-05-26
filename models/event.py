from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()

class Event:
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client[os.getenv("MONGO_DBNAME", "workout_planner")]
    collection = db['events']

    @classmethod
    def create_event(cls, event_data):
        event_data['created_at'] = datetime.utcnow()
        event_data['status'] = 'upcoming'
        return cls.collection.insert_one(event_data)

    @classmethod
    def get_family_events(cls, family_id):
        return list(cls.collection.find({
            "family_id": ObjectId(family_id),
            "status": "upcoming"
        }).sort("datetime", 1))

    @classmethod
    def update_event_status(cls, event_id, status):
        return cls.collection.update_one(
            {"_id": ObjectId(event_id)},
            {"$set": {"status": status}}
        )
