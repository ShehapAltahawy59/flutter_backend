from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

class User:
    # MongoDB connection
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client['workout_planner']
    collection = db['users']
    
    @classmethod
    def find_by_id(cls, user_id):
        return cls.collection.find_one({"_id": user_id})
    
    @classmethod
    def create(cls, user_data):
        return cls.collection.insert_one(user_data)
    
    @classmethod
    def update_fitness_goals(cls, user_id, goals):
        return cls.collection.update_one(
            {"_id": user_id},
            {"$set": {"fitness.goals": goals}}
        )
