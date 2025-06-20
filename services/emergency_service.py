from bson import ObjectId
from models.emergency import Emergency
from models.family import Family
from models.user import User
from services.notification_service import NotificationService
from datetime import datetime

class EmergencyService:
    @staticmethod
    def trigger_emergency(user_id, family_id, location, message=None):
        # 1. Verify user belongs to family
        family = Family.get_family_with_members(family_id)
        if not any(m['user_id'] == user_id for m in family['members']):
            return False

        # 2. Get emergency contacts
        contacts = family.get('settings', {}).get('emergency_contacts', [])
        
        # 3. Send notifications
        user = User.find_by_id(user_id)
        notification_sent = NotificationService.send_emergency_alert(
            user_id=user_id,
            family_id=family_id,
            location=location,
            message=message
        )
        
        # 4. Log emergency
        if notification_sent:
            emergency_data = {
                "user_id": ObjectId(user_id),
                "family_id": ObjectId(family_id),
                "location": location,
                "message": message,
                "status": "active",
                "timestamp": datetime.utcnow(),
                "notified_contacts": contacts
            }
            Emergency.collection.insert_one(emergency_data)
            
        return notification_sent
