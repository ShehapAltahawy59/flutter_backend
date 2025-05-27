from datetime import datetime
from bson import ObjectId
from utils.db import DatabaseConnection

class Event:
    @classmethod
    def create_event(cls, event_data):
        db = DatabaseConnection.get_instance()
        event_data['created_at'] = datetime.utcnow()
        event_data['status'] = 'upcoming'
        return db.get_events_collection().insert_one(event_data)

    @classmethod
    def get_event(cls, event_id):
        db = DatabaseConnection.get_instance()
        return db.get_events_collection().find_one({"_id": ObjectId(event_id)})

    @classmethod
    def get_all_events(cls, query=None):
        db = DatabaseConnection.get_instance()
        if query is None:
            query = {}
        return list(db.get_events_collection().find(query).sort("datetime", 1))

    @classmethod
    def get_family_events(cls, family_id):
        db = DatabaseConnection.get_instance()
        return list(db.get_events_collection().find({
            "family_id": ObjectId(family_id),
            "status": "upcoming"
        }).sort("datetime", 1))

    @classmethod
    def update_event(cls, event_id, update_data):
        db = DatabaseConnection.get_instance()
        result = db.get_events_collection().update_one(
            {"_id": ObjectId(event_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0

    @classmethod
    def update_event_status(cls, event_id, status):
        db = DatabaseConnection.get_instance()
        return db.get_events_collection().update_one(
            {"_id": ObjectId(event_id)},
            {"$set": {"status": status}}
        )

    @classmethod
    def delete_event(cls, event_id):
        db = DatabaseConnection.get_instance()
        result = db.get_events_collection().delete_one({"_id": ObjectId(event_id)})
        return result.deleted_count > 0
