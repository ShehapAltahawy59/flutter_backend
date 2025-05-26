from flask import Flask, jsonify
from flask_cors import CORS
from routes.workout_routes import workout_bp
from routes.user_routes import user_bp  # Import the new user blueprint
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(workout_bp, url_prefix='/api/workouts')
app.register_blueprint(user_bp, url_prefix='/api/users')  # Register user routes

@app.route('/')
def health_check():
    return {'status': 'healthy', 'message': 'Workout Planner API is running'}

if __name__ == '__main__':
    app.run(debug=True)
__vscmb5c1r0s
