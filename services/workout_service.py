from models.workout import Workout
from models.user import User

class WorkoutService:
    @staticmethod
    def suggest_workouts(user_id, equipment=None):
        user = User.find_by_id(user_id)
        if not user:
            return {"error": "User not found"}, 404
        
        goals = user.get('fitness_goals', [])
        fitness_level = user.get('fitness_level', 'beginner')
        
        if not goals:
            return {"error": "No fitness goals set"}, 400
        
        workouts = Workout.find_by_goals_and_level(goals, fitness_level, equipment)
        return {"workouts": workouts}, 200
    
    @staticmethod
    def set_fitness_goals(user_id, goals):
        result = User.update_fitness_goals(user_id, goals)
        if result.modified_count == 0:
            return {"error": "User not found or no changes made"}, 404
        return {"message": "Fitness goals updated successfully"}, 200
    
    @staticmethod
    def log_completed_workout(user_id, workout_id, notes=None, rating=None):
        completion_data = {
            "date": datetime.datetime.now(),
            "notes": notes,
            "rating": rating
        }
        result = Workout.log_workout(user_id, workout_id, completion_data)
        if result.modified_count == 0:
            return {"error": "Workout not found"}, 404
        return {"message": "Workout logged successfully"}, 200
