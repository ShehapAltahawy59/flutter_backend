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
    def find_by_id(cls, family_id):
        """Find a family by its ID"""
        db = DatabaseConnection.get_instance()
        return db.get_families_collection().find_one({"_id": ObjectId(family_id)})

    @classmethod
    def get_family(cls, family_id):
        db = DatabaseConnection.get_instance()
        return db.get_families_collection().find_one({"_id": ObjectId(family_id)})

    @classmethod
    def find_by_member(cls, user_id):
        """Find all families where the user is a member"""
        db = DatabaseConnection.get_instance()
        return list(db.get_families_collection().find({
            "members": str(user_id)  # Members are stored as strings
        }))

    @classmethod
    def get_user_families(cls, user_id):
        db = DatabaseConnection.get_instance()
        return list(db.get_families_collection().find({
            "members": str(user_id)  # Members are stored as strings
        }))

    @classmethod
    def add_member(cls, family_id, user_id, role="member"):
        db = DatabaseConnection.get_instance()
        return db.get_families_collection().update_one(
            {"_id": ObjectId(family_id)},
            {
                "$addToSet": {
                    "members": str(user_id)  # Store as string to match existing data
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
