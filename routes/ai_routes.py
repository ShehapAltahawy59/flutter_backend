from flask import Blueprint, request, jsonify

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

@ai_bp.route('/profile-analyze', methods=['POST'])
def analyze_profile():
    data = request.get_json()
    required_fields = ['name', 'age', 'weight', 'height', 'fitness_goal', 'experience', 'equipment', 'limitations']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    # Dummy AI logic (replace with real AI call if available)
    ai_response = {
        "summary": f"Hello {data['name']}, based on your goal '{data['fitness_goal']}' and experience '{data['experience']}', here is your personalized recommendation...",
        "recommendation": "Start with 3 days of full-body workouts using your available equipment."
    }

    return jsonify({"success": True, "ai_response": ai_response}), 200 
