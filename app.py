from flask import Flask, jsonify
from flask_cors import CORS
from flask_session import Session
from routes.workout_routes import workout_bp
from routes.user_routes import user_bp  # Import the new user blueprint
from routes.event_routes import event_bp
from routes.emergency_routes import emergency_bp
from routes.family_routes import family_bp
from routes.chatbot_routes import fitness_bp  # Import fitness trainer blueprint
import os
from dotenv import load_dotenv
from utils.model_loader import ModelLoader
from utils.db import DatabaseConnection
import logging
from config import API_CONFIG, LOGGING

load_dotenv()

# Configure logging
logging.basicConfig(
    level=LOGGING['level'],
    format=LOGGING['format'],
    filename=LOGGING['file']
)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    # Initialize database connection
    logger.info("Initializing database connection...")
    db = DatabaseConnection.get_instance()
    
    # Initialize models
    logger.info("Initializing ML models...")
    model_loader = ModelLoader.get_instance()
    if not model_loader.initialize_models():
        logger.error("Failed to initialize models!")
    
    # Configuration for sessions (needed for fitness trainer)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
    app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'flask_session')

    # Initialize CORS and Session
    CORS(app, supports_credentials=True)
    Session(app)

    # Create required directories
    os.makedirs('flask_session', exist_ok=True)
    os.makedirs('fitness_data', exist_ok=True)

    # Register blueprints
    app.register_blueprint(workout_bp, url_prefix='/api/workouts')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(event_bp, url_prefix='/api/events')
    app.register_blueprint(emergency_bp, url_prefix='/api/emergency')
    app.register_blueprint(family_bp)
    app.register_blueprint(fitness_bp, url_prefix='/api/fitness')

    @app.route('/')
    def health_check():
        return {
            'status': 'healthy', 
            'message': 'Workout Planner API is running',
            'available_services': [
                'workouts',
                'users', 
                'events',
                'emergency',
                'family',
                'fitness-trainer'
            ],
            'endpoints': {
                'workouts': '/api/workouts',
                'users': '/api/users',
                'events': '/api/events', 
                'emergency': '/api/emergency',
                'family': '/api/family',
                'fitness_trainer': '/api/fitness'
            }
        }

    @app.route('/api/health')
    def api_health():
        return jsonify({
            'status': 'healthy',
            'services': {
                'workout_planner': 'active',
                'user_management': 'active',
                'event_management': 'active',
                'emergency_services': 'active',
                'family_management': 'active',
                'fitness_trainer_ai': 'active'
            }
        })

    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Endpoint not found',
            'available_endpoints': [
                '/api/workouts',
                '/api/users',
                '/api/events',
                '/api/emergency', 
                '/api/family',
                '/api/fitness'
            ]
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    
    return app

if __name__ == '__main__':
    # Check for required environment variables for fitness trainer
    if not os.getenv('GROQ_API_KEY'):
        print("⚠️  Warning: GROQ_API_KEY not found. Fitness AI trainer features may not work.")
    
    print("🚀 Starting Workout Planner API with Fitness Trainer...")
    print("📍 Available services:")
    print("   - Workouts: http://localhost:5000/api/workouts")
    print("   - Users: http://localhost:5000/api/users") 
    print("   - Events: http://localhost:5000/api/events")
    print("   - Emergency: http://localhost:5000/api/emergency")
    print("   - Family: http://localhost:5000/api/family")
    print("   - Fitness Trainer AI: http://localhost:5000/api/fitness")
    
    app = create_app()
    app.run(
        host=API_CONFIG['host'],
        port=API_CONFIG['port'],
        debug=API_CONFIG['debug']
    )
