from datetime import datetime
from bson import ObjectId
from utils.db import DatabaseConnection

class Family:
    @classmethod
    def create_family(cls, family_data):
        db = DatabaseConnection.get_instance()
        family_data['created_at'] = datetime.utcnow()
        return db.get_families_collection().insert_one(family_data)

    @classmethod
    def get_family(cls, family_id):
        db = DatabaseConnection.get_instance()
        return db.get_families_collection().find_one({"_id": ObjectId(family_id)})

    @classmethod
    def get_user_families(cls, user_id):
        db = DatabaseConnection.get_instance()
        return list(db.get_families_collection().find({
            "members": ObjectId(user_id)
        }))

    @classmethod
    def add_member(cls, family_id, user_id, role="member"):
        db = DatabaseConnection.get_instance()
        return db.get_families_collection().update_one(
            {"_id": ObjectId(family_id)},
            {
                "$addToSet": {
                    "members": ObjectId(user_id),
                    "roles": {
                        "user_id": ObjectId(user_id),
                        "role": role
                    }
                }
            }
        )

    @classmethod
    def remove_member(cls, family_id, user_id):
        db = DatabaseConnection.get_instance()
        return db.get_families_collection().update_one(
            {"_id": ObjectId(family_id)},
            {
                "$pull": {
                    "members": ObjectId(user_id),
                    "roles": {"user_id": ObjectId(user_id)}
                }
            }
        )

    @classmethod
    def update_family_settings(cls, family_id, settings):
        db = DatabaseConnection.get_instance()
        return db.get_families_collection().update_one(
            {"_id": ObjectId(family_id)},
            {"$set": {"settings": settings}}
        )

    @classmethod
    def get_family_members(cls, family_id):
        db = DatabaseConnection.get_instance()
        family = db.get_families_collection().find_one({"_id": ObjectId(family_id)})
        if family:
            return family.get("members", [])
        return []
