from flask import Blueprint, request, jsonify
from services.workout_service import WorkoutService

workout_bp = Blueprint('workout', __name__)

@workout_bp.route('/suggest', methods=['POST'])
def suggest_workouts():
    data = request.get_json()
    user_id = data.get('user_id')
    equipment = data.get('equipment', None)
    
    response, status_code = WorkoutService.suggest_workouts(user_id, equipment)
    return jsonify(response), status_code

@workout_bp.route('/set-goals', methods=['POST'])
def set_fitness_goals():
    data = request.get_json()
    user_id = data.get('user_id')
    goals = data.get('goals')
    
    if not user_id or not goals:
        return jsonify({"error": "user_id and goals are required"}), 400
    
    response, status_code = WorkoutService.set_fitness_goals(user_id, goals)
    return jsonify(response), status_code

@workout_bp.route('/log', methods=['POST'])
def log_workout():
    data = request.get_json()
    user_id = data.get('user_id')
    workout_id = data.get('workout_id')
    notes = data.get('notes')
    rating = data.get('rating')
    
    if not user_id or not workout_id:
        return jsonify({"error": "user_id and workout_id are required"}), 400
    
    response, status_code = WorkoutService.log_completed_workout(
        user_id, workout_id, notes, rating
    )
    return jsonify(response), status_code

@workout_bp.route('/fitness-profile', methods=['POST'])
def save_fitness_profile():
    data = request.get_json()
    required_fields = ['user_id', 'age', 'weight', 'height', 'fitness_goal', 'experience', 'equipment', 'limitations']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400
    if not isinstance(data['equipment'], list):
        data['equipment'] = [data['equipment']]
    from models.user import User
    user = User.find_by_id(data['user_id'])
    if not user:
        return jsonify({"error": "User not found"}), 404
    data['name'] = user.get('name', 'Unknown')
    from models.workout import Workout
    result = Workout.create_workout(data)
    return jsonify({"success": True, "fitness_data_id": str(result.inserted_id)}), 201

@workout_bp.route('/fitness-profile/<user_id>', methods=['GET'])
def get_fitness_profile(user_id):
    from models.workout import Workout
    # Find the most recent fitness profile for the user
    profile = Workout.get_user_fitness_profile(user_id)
    if not profile:
        return jsonify({"error": "Fitness profile not found"}), 404
    # Convert ObjectId to string for JSON serialization
    profile['_id'] = str(profile['_id'])
    return jsonify(profile), 200
