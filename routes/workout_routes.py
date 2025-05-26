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
