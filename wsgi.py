from app import create_app
import os

# Set environment variables for production
os.environ['FLASK_ENV'] = 'production'
os.environ['HOST'] = '0.0.0.0'
os.environ['PORT'] = os.getenv('PORT', '5000')

# Create the Flask app instance
app = create_app()

if __name__ == "__main__":
    app.run() 
