from flask import Flask, jsonify
from flask_cors import CORS
from routes.workout_routes import workout_bp
from routes.user_routes import user_bp  # Import the new user blueprint
import os
from dotenv import load_dotenv
from routes.event_routes import event_bp
from routes.emergency_routes import emergency_bp

load_dotenv()

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(workout_bp, url_prefix='/api/workouts')
app.register_blueprint(user_bp, url_prefix='/api/users')  # Register user routes
app.register_blueprint(event_bp,url_prefix='/api/events')
app.register_blueprint(emergency_bp,url_prefix='/api/emergency')
@app.route('/')
def health_check():
    return {'status': 'healthy', 'message': 'Workout Planner API is running'}

if __name__ == '__main__':
    app.run(debug=True)
