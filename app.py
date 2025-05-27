from flask import Flask, jsonify
from flask_cors import CORS
from flask_session import Session
from routes.workout_routes import workout_bp
from routes.user_routes import user_bp
from routes.event_routes import event_bp
from routes.emergency_routes import emergency_bp
from routes.family_routes import family_bp
from routes.chatbot_routes import fitness_bp
import os
from dotenv import load_dotenv
from utils.model_loader import ModelLoader
from utils.db import DatabaseConnection
import logging
from config import API_CONFIG, LOGGING, SECURITY_CONFIG

# Load environment variables
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
    
    # Configure CORS to allow all origins
    CORS(app, resources={
        r"/api/*": {
            "origins": API_CONFIG['cors_origins'],
            "methods": SECURITY_CONFIG['cors_methods'],
            "allow_headers": SECURITY_CONFIG['cors_headers']
        }
    })
    
    # Configure session
    app.config['SECRET_KEY'] = SECURITY_CONFIG['secret_key']
    app.config['SESSION_TYPE'] = SECURITY_CONFIG['session_type']
    app.config['PERMANENT_SESSION_LIFETIME'] = SECURITY_CONFIG['session_lifetime']
    Session(app)
    
    # Initialize database connection
    DatabaseConnection.get_instance()
    
    # Initialize model loader and pre-download models
    logger.info("Initializing model loader and pre-downloading models...")
    model_loader = ModelLoader()
    logger.info("Model initialization complete")
    
    # Register blueprints
    app.register_blueprint(workout_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(event_bp)
    app.register_blueprint(emergency_bp)
    app.register_blueprint(family_bp)
    app.register_blueprint(fitness_bp)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            "status": "healthy",
            "environment": os.getenv('FLASK_ENV', 'development'),
            "base_url": API_CONFIG['base_url']
        }), 200
    
    # API health check endpoint
    @app.route('/api/health', methods=['GET'])
    def api_health_check():
        return jsonify({
            "status": "healthy",
            "version": "2",
            "environment": os.getenv('FLASK_ENV', 'development'),
            "base_url": API_CONFIG['base_url']
        }), 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host=API_CONFIG['host'],
        port=API_CONFIG['port'],
        debug=API_CONFIG['debug']
    )
