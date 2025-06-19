from datetime import datetime
from bson import ObjectId
from utils.db import DatabaseConnection

class Workout:
    @classmethod
    def create_workout(cls, workout_data):
        db = DatabaseConnection.get_instance()
        workout_data['created_at'] = datetime.utcnow()
        return db.get_fitness_data_collection().insert_one(workout_data)

    @classmethod
    def get_workout(cls, workout_id):
        db = DatabaseConnection.get_instance()
        return db.get_fitness_data_collection().find_one({"_id": ObjectId(workout_id)})

    @classmethod
    def get_user_workouts(cls, user_id, start_date=None, end_date=None):
        db = DatabaseConnection.get_instance()
        query = {"user_id": ObjectId(user_id), "type": "workout"}
        
        if start_date and end_date:
            query["date"] = {
                "$gte": start_date,
                "$lte": end_date
            }
            
        return list(db.get_fitness_data_collection().find(query).sort("date", -1))

    @classmethod
    def update_workout(cls, workout_id, update_data):
        db = DatabaseConnection.get_instance()
        update_data['updated_at'] = datetime.utcnow()
        return db.get_fitness_data_collection().update_one(
            {"_id": ObjectId(workout_id)},
            {"$set": update_data}
        )

    @classmethod
    def delete_workout(cls, workout_id):
        db = DatabaseConnection.get_instance()
        result = db.get_fitness_data_collection().delete_one({"_id": ObjectId(workout_id)})
        return result.deleted_count > 0

    @classmethod
    def get_workout_stats(cls, user_id, period="week"):
        db = DatabaseConnection.get_instance()
        now = datetime.utcnow()
        
        if period == "week":
            start_date = now.replace(day=now.day-7)
        elif period == "month":
            start_date = now.replace(month=now.month-1)
        else:
            start_date = now.replace(year=now.year-1)
            
        pipeline = [
            {
                "$match": {
                    "user_id": ObjectId(user_id),
                    "type": "workout",
                    "date": {"$gte": start_date}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_workouts": {"$sum": 1},
                    "total_duration": {"$sum": "$duration"},
                    "total_calories": {"$sum": "$calories_burned"}
                }
            }
        ]
        
        result = list(db.get_fitness_data_collection().aggregate(pipeline))
        return result[0] if result else {
            "total_workouts": 0,
            "total_duration": 0,
            "total_calories": 0
        }

    @classmethod
    def get_user_fitness_profile(cls, user_id):
        db = DatabaseConnection.get_instance()
        # Find the most recent fitness profile for the user
        return db.get_fitness_data_collection().find_one(
            {"user_id": ObjectId(user_id)},
            sort=[("created_at", -1)]
        )
    
    @classmethod
    def get_user_workouts(cls, user_id):
        db = DatabaseConnection.get_instance()
        return list(db.get_fitness_data_collection().find({"user_id": user_id}).sort("created_at", -1))
