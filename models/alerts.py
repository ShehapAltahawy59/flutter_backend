from datetime import datetime
from typing import List, Dict, Optional
from bson import ObjectId
from utils.db import DatabaseConnection

class SOSAlert:
    def __init__(self, data: Dict):
        self._id = data.get('_id', ObjectId())
        self.user_id = data['user_id']
        self.family_id = data['family_id']
        self.location = data['location']
        self.message = data.get('message', '')
        self.status = data.get('status', 'active')  # active, acknowledged, resolved
        self.created_at = data.get('created_at', datetime.utcnow())
        self.updated_at = data.get('updated_at', datetime.utcnow())
        self.acknowledged_by = data.get('acknowledged_by', [])  # List of user IDs
        self.resolved_at = data.get('resolved_at')
        self.resolved_by = data.get('resolved_by')  # User ID

    def to_dict(self) -> Dict:
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'family_id': self.family_id,
            'location': self.location,
            'message': self.message,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'acknowledged_by': self.acknowledged_by,
            'resolved_at': self.resolved_at,
            'resolved_by': self.resolved_by
        }

    @classmethod
    def create_alert(cls, alert_data):
        db = DatabaseConnection.get_instance()
        alert_data['created_at'] = datetime.utcnow()
        alert_data['status'] = 'active'
        return db.get_sos_alerts_collection().insert_one(alert_data)

    @classmethod
    def get_alert(cls, alert_id):
        db = DatabaseConnection.get_instance()
        return db.get_sos_alerts_collection().find_one({"_id": ObjectId(alert_id)})

    @classmethod
    def get_active_alerts(cls, family_id):
        db = DatabaseConnection.get_instance()
        return list(db.get_sos_alerts_collection().find({
            "family_id": ObjectId(family_id),
            "status": "active"
        }).sort("created_at", -1))

    @classmethod
    def get_alert_history(cls, family_id):
        db = DatabaseConnection.get_instance()
        return list(db.get_sos_alerts_collection().find({
            "family_id": ObjectId(family_id),
            "status": {"$ne": "active"}
        }).sort("created_at", -1))

    @classmethod
    def acknowledge_alert(cls, alert_id, user_id):
        db = DatabaseConnection.get_instance()
        return db.get_sos_alerts_collection().update_one(
            {"_id": ObjectId(alert_id)},
            {
                "$addToSet": {"acknowledged_by": ObjectId(user_id)},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

    @classmethod
    def resolve_alert(cls, alert_id, user_id):
        db = DatabaseConnection.get_instance()
        return db.get_sos_alerts_collection().update_one(
            {"_id": ObjectId(alert_id)},
            {
                "$set": {
                    "status": "resolved",
                    "resolved_at": datetime.utcnow(),
                    "resolved_by": ObjectId(user_id),
                    "updated_at": datetime.utcnow()
                }
            }
        )

class Event:
    def __init__(self, data: Dict):
        self._id = data.get('_id', ObjectId())
        self.family_id = data['family_id']
        self.created_by = data['created_by']  # User ID
        self.title = data['title']
        self.description = data.get('description', '')
        self.location = data.get('location')
        self.start_time = data['start_time']
        self.end_time = data.get('end_time')
        self.type = data.get('type', 'general')  # general, emergency, reminder
        self.priority = data.get('priority', 'normal')  # low, normal, high
        self.status = data.get('status', 'active')  # active, cancelled, completed
        self.created_at = data.get('created_at', datetime.utcnow())
        self.updated_at = data.get('updated_at', datetime.utcnow())
        self.participants = data.get('participants', [])  # List of user IDs
        self.notifications = data.get('notifications', {
            'email': True,
            'push': True,
            'sms': False
        })

    def to_dict(self) -> Dict:
        return {
            '_id': self._id,
            'family_id': self.family_id,
            'created_by': self.created_by,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'type': self.type,
            'priority': self.priority,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'participants': self.participants,
            'notifications': self.notifications
        }

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
    def get_family_events(cls, family_id, start_date=None, end_date=None, event_type=None):
        db = DatabaseConnection.get_instance()
        query = {"family_id": ObjectId(family_id)}
        
        if start_date and end_date:
            query["start_time"] = {
                "$gte": start_date,
                "$lte": end_date
            }
        
        if event_type:
            query["type"] = event_type
            
        return list(db.get_events_collection().find(query).sort("start_time", 1))

    @classmethod
    def update_event(cls, event_id, update_data):
        db = DatabaseConnection.get_instance()
        update_data['updated_at'] = datetime.utcnow()
        return db.get_events_collection().update_one(
            {"_id": ObjectId(event_id)},
            {"$set": update_data}
        )

    @classmethod
    def join_event(cls, event_id, user_id):
        db = DatabaseConnection.get_instance()
        return db.get_events_collection().update_one(
            {"_id": ObjectId(event_id)},
            {
                "$addToSet": {"participants": ObjectId(user_id)},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

    @classmethod
    def leave_event(cls, event_id, user_id):
        db = DatabaseConnection.get_instance()
        return db.get_events_collection().update_one(
            {"_id": ObjectId(event_id)},
            {
                "$pull": {"participants": ObjectId(user_id)},
                "$set": {"updated_at": datetime.utcnow()}
            }
        ) 
