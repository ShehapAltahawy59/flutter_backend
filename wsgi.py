import os
from app import create_app

# Set environment variables for production
os.environ['FLASK_ENV'] = 'production'
os.environ['HOST'] = '0.0.0.0'
os.environ['PORT'] = os.getenv('PORT', '5000')
os.environ['BASE_URL'] = os.getenv('BASE_URL', f"http://{os.getenv('HOST', '0.0.0.0')}:{os.getenv('PORT', '5000')}")
os.environ['CORS_ORIGINS'] = os.getenv('CORS_ORIGINS', '*')

# Create the Flask app
app = create_app()

if __name__ == '__main__':
    app.run(debug=True) 
