from flask import Flask, jsonify
from flask_cors import CORS
from flask_session import Session
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
from services.notification_service import socketio
from datetime import datetime

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
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": SECURITY_CONFIG['cors_headers']
        }
    })
    
    # Configure session
    app.config['SECRET_KEY'] = SECURITY_CONFIG['secret_key']
    app.config['SESSION_TYPE'] = SECURITY_CONFIG['session_type']
    app.config['PERMANENT_SESSION_LIFETIME'] = SECURITY_CONFIG['session_lifetime']
    Session(app)
    
    # Initialize database connection
    try:
        db = DatabaseConnection.get_instance()
        logger.info("Database connection initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database connection: {str(e)}")
        raise
    
    # Initialize model loader and pre-download models
    try:
        logger.info("Initializing model loader and pre-downloading models...")
        model_loader = ModelLoader()
        logger.info("Model initialization complete")
    except Exception as e:
        logger.error(f"Failed to initialize model loader: {str(e)}")
        # Don't raise here, as model loading is not critical for basic functionality
    
    # Register blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(event_bp)
    app.register_blueprint(emergency_bp)
    app.register_blueprint(family_bp)
    app.register_blueprint(fitness_bp)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        try:
            # Test database connection
            db = DatabaseConnection.get_instance()
            db.get_db().command('ping')
            return jsonify({
                "status": "healthy",
                "environment": os.getenv('FLASK_ENV', 'development'),
                "base_url": API_CONFIG['base_url'],
                "database": "connected"
            }), 200
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return jsonify({
                "status": "unhealthy",
                "error": str(e),
                "environment": os.getenv('FLASK_ENV', 'development')
            }), 500
    
    # API health check endpoint
    @app.route('/api/health', methods=['GET'])
    def api_health_check():
        try:
            # Test database connection
            db = DatabaseConnection.get_instance()
            db.get_db().command('ping')
            return jsonify({
                "status": "healthy",
                "version": "2",
                "environment": os.getenv('FLASK_ENV', 'development'),
                "base_url": API_CONFIG['base_url'],
                "database": "connected"
            }), 200
        except Exception as e:
            logger.error(f"API health check failed: {str(e)}")
            return jsonify({
                "status": "unhealthy",
                "error": str(e),
                "environment": os.getenv('FLASK_ENV', 'development')
            }), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
