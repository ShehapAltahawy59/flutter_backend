from flask import Flask
from flask_cors import CORS
from routes.workout_routes import workout_bp
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(workout_bp, url_prefix='/api/workouts')

@app.route('/')
def health_check():
    return {'status': 'healthy', 'message': 'Workout Planner API is running'}

if __name__ == '__main__':
    app.run(debug=True)
