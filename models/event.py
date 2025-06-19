from datetime import datetime
from bson import ObjectId
from utils.db import DatabaseConnection

class Event:
    @classmethod
    def create_event(cls, event_data):
        db = DatabaseConnection.get_instance()
        event_data['created_at'] = datetime.utcnow()
        event_data['status'] = 'upcoming'
        event_data['participants'] = []  # Initialize empty participants list
        
        # Handle location data - ensure it's a string
        if 'location' in event_data and not isinstance(event_data['location'], str):
            if isinstance(event_data['location'], dict) and 'address' in event_data['location']:
                event_data['location'] = event_data['location']['address']
            else:
                event_data['location'] = str(event_data['location'])
                    
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
            "family_id": str(family_id),
            "status": "upcoming"
        }).sort("datetime", 1))

    @classmethod
    def update_event(cls, event_id, update_data):
        db = DatabaseConnection.get_instance()
        # Handle location update - ensure it's a string
        if 'location' in update_data and not isinstance(update_data['location'], str):
            if isinstance(update_data['location'], dict) and 'address' in update_data['location']:
                update_data['location'] = update_data['location']['address']
            else:
                update_data['location'] = str(update_data['location'])
                    
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
    def join_event(cls, event_id, user_id, user_name):
        """Add a user to the event's participants list"""
        db = DatabaseConnection.get_instance()
        result = db.get_events_collection().update_one(
            {"_id": ObjectId(event_id)},
            {
                "$addToSet": {"participants": {
                    "user_id": ObjectId(user_id),
                    "user_name": user_name
                }},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return result.modified_count > 0

    @classmethod
    def leave_event(cls, event_id, user_id):
        """Remove a user from the event's participants list"""
        db = DatabaseConnection.get_instance()
        result = db.get_events_collection().update_one(
            {"_id": ObjectId(event_id)},
            {
                "$pull": {"participants": ObjectId(user_id)},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return result.modified_count > 0

    @classmethod
    def delete_event(cls, event_id):
        db = DatabaseConnection.get_instance()
        result = db.get_events_collection().delete_one({"_id": ObjectId(event_id)})
        return result.deleted_count > 0
