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
        print(f"[DEBUG] Searching for user_id: {user_id}")
        families = list(db.get_families_collection().find({
            "members": {
                "$elemMatch": {
                    "user_id": ObjectId(user_id)
                }
            }
        }))
        print(f"[DEBUG] Found families: {families}")
        return families

    @classmethod
    def get_user_families(cls, user_id):
        db = DatabaseConnection.get_instance()
        return list(db.get_families_collection().find({
            "members": {
                "$elemMatch": {
                    "user_id": ObjectId(user_id)
                }
            }
        }))

    @classmethod
    def add_member(cls, family_id, user_id, role="member"):
        db = DatabaseConnection.get_instance()
        return db.get_families_collection().update_one(
            {"_id": ObjectId(family_id)},
            {
                "$addToSet": {
                    "members": {
                        "user_id": ObjectId(user_id),
                        "role": role,
                        "joined_at": datetime.utcnow()
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
