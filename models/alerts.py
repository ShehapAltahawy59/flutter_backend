from datetime import datetime
from typing import List, Dict, Optional
from bson import ObjectId

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
