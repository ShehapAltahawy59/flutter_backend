from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))
db = client['flutter_project']

class Workout:
    collection = db['workouts']
    
    @classmethod
    def create(cls, workout_data):
        return cls.collection.insert_one(workout_data)
    
    @classmethod
    def find_by_goals_and_level(cls, goals, fitness_level, equipment=None):
        query = {
            "target_goals": {"$in": goals},
            "fitness_level": fitness_level
        }
        if equipment:
            query["required_equipment"] = {"$in": equipment}
        return list(cls.collection.find(query))
    
    @classmethod
    def log_workout(cls, user_id, workout_id, completion_data):
        return cls.collection.update_one(
            {"_id": workout_id},
            {"$push": {"completion_history": {
                "user_id": user_id,
                **completion_data
            }}}
        )
