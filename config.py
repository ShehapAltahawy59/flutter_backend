import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
DB_NAME = os.getenv('MONGO_DBNAME', 'flutter_project')

# MongoDB Connection Settings
MONGODB_CONFIG = {
    'connectTimeoutMS': 5000,
    'serverSelectionTimeoutMS': 5000,
    'retryWrites': True,
    'retryReads': True,
    'maxPoolSize': 10,
    'minPoolSize': 1,
    'maxIdleTimeMS': 30000,
    'waitQueueTimeoutMS': 5000,
    'heartbeatFrequencyMS': 10000
}

# Collection Names
COLLECTIONS = {
    'users': 'users',
    'families': 'families',
    'events': 'events',
    'sos_alerts': 'sos_alerts',
    'fitness_data': 'fitness_data',
    'notifications': 'notifications',
    'chat_history': 'chat_history'
}

# API Configuration
API_CONFIG = {
    'debug': os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
    'base_url': os.getenv('BASE_URL', 'https://flutter-backend-dcqs.onrender.com'),  # Use the actual server URL
    'cors_origins': os.getenv('CORS_ORIGINS', '*').split(',')  # Allow multiple origins
}

# Security Configuration
SECURITY = {
    'jwt_secret': os.getenv('JWT_SECRET', 'your-secret-key'),
    'jwt_expiration': int(os.getenv('JWT_EXPIRATION', 86400)),  # 24 hours
    'password_salt': os.getenv('PASSWORD_SALT', 'your-salt')
}

# Feature Flags
FEATURES = {
    'enable_location_tracking': True,
    'enable_fitness_tracking': True,
    'enable_sos_alerts': True,
    'enable_family_events': True,
    'enable_notifications': True
}

# Notification Settings
NOTIFICATION_SETTINGS = {
    'email_enabled': True,
    'push_enabled': True,
    'sms_enabled': False,
    'default_notification_types': ['events', 'sos_alerts', 'reminders']
}

# Location Settings
LOCATION_SETTINGS = {
    'update_interval': 300,  # 5 minutes
    'accuracy_threshold': 100,  # meters
    'max_history_days': 30
}

# Event Settings
EVENT_SETTINGS = {
    'max_participants': 50,
    'reminder_times': [3600, 1800, 300],  # 1 hour, 30 minutes, 5 minutes
    'max_recurring_events': 52  # 1 year of weekly events
}

# SOS Alert Settings
SOS_SETTINGS = {
    'max_active_alerts': 3,
    'alert_timeout': 3600,  # 1 hour
    'notification_retry_interval': 300  # 5 minutes
}

# Fitness Settings
FITNESS_SETTINGS = {
    'workout_types': ['running', 'walking', 'cycling', 'swimming', 'gym'],
    'max_history_days': 365,
    'goal_types': ['steps', 'distance', 'calories', 'duration']
}

# Cache Settings
CACHE_SETTINGS = {
    'enabled': True,
    'type': 'redis',
    'host': os.getenv('REDIS_HOST', 'localhost'),
    'port': int(os.getenv('REDIS_PORT', 6379)),
    'ttl': 3600  # 1 hour
}

# Logging Configuration
LOGGING = {
    'level': os.getenv('LOG_LEVEL', 'INFO'),
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': os.getenv('LOG_FILE', 'app.log')
}

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'fitness_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}

# Security Configuration
SECURITY_CONFIG = {
    'secret_key': os.getenv('FLASK_SECRET_KEY', 'dev_key_please_change'),
    'session_type': 'filesystem',
    'session_lifetime': 3600,  # 1 hour in seconds
    'cors_headers': ['Content-Type', 'Authorization', 'X-Requested-With'],
    'cors_methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
} 
