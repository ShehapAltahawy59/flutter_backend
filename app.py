from flask import Flask, jsonify
from flask_cors import CORS
from routes.workout_routes import workout_bp
from routes.user_routes import user_bp
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import os
from dotenv import load_dotenv
from bson import json_util
import json

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize MongoDB connection
def get_mongo_client():
    try:
        client = MongoClient(os.getenv("MONGODB_URI"), serverSelectionTimeoutMS=5000)
        # Force a connection check
        client.admin.command('ping')
        return client
    except Exception as e:
        app.logger.error(f"Database connection error: {str(e)}")
        return None

# Database connection health check endpoint
@app.route('/db-health')
def db_health_check():
    try:
        client = get_mongo_client()
        if client is None:
            return jsonify({
                'status': 'unhealthy',
                'message': 'Could not connect to database',
                'database': 'MongoDB',
                'connected': False
            }), 500

        # Check if collections exist
        db = client[os.getenv("MONGO_DBNAME", "workout_planner")]
        collections = db.list_collection_names()
        
        return jsonify({
            'status': 'healthy',
            'message': 'Database connection successful',
            'database': 'MongoDB',
            'connected': True,
            'collections_available': collections
        }), 200
        
    except ServerSelectionTimeoutError:
        return jsonify({
            'status': 'unhealthy',
            'message': 'Database connection timed out',
            'database': 'MongoDB',
            'connected': False
        }), 500
    except ConnectionFailure:
        return jsonify({
            'status': 'unhealthy',
            'message': 'Could not connect to database server',
            'database': 'MongoDB',
            'connected': False
        }), 500
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'message': str(e),
            'database': 'MongoDB',
            'connected': False
        }), 500

# Main health check endpoint
@app.route('/')
def health_check():
    db_status = db_health_check().json
    return {
        'status': 'healthy' if db_status['connected'] else 'degraded',
        'message': 'Workout Planner API is running',
        'services': {
            'database': db_status
        }
    }

# Register blueprints
app.register_blueprint(workout_bp, url_prefix='/api/workouts')
app.register_blueprint(user_bp, url_prefix='/api/users')

# Database connection middleware
@app.before_request
def before_request():
    app.mongo_client = get_mongo_client()
    if app.mongo_client is None:
        return jsonify({
            'error': 'Database connection failed',
            'message': 'Service unavailable'
        }), 503

@app.teardown_appcontext
def teardown_db(exception):
    if hasattr(app, 'mongo_client') and app.mongo_client:
        app.mongo_client.close()

if __name__ == '__main__':
    app.run(debug=True)
