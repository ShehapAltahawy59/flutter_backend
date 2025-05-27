# Fitness AI Backend

A Flask-based backend service that provides AI-powered fitness training capabilities using Groq's LLM API.

## Features

- AI-powered fitness training and workout generation
- User profile management
- Session-based chat with memory
- Personalized workout recommendations
- Memory management for context-aware responses

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A Groq API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd flutter_backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```



## Running the Server

1. Start the Flask development server:
```bash
python app.py
```

2. For production deployment:
```bash
gunicorn -c gunicorn.conf.py app:app
```

The server will be available at `http://localhost:5000` by default.

## Using the FitnessClient

The `FitnessClient` provides a Python interface to interact with the Fitness AI backend.

### Basic Usage

```python
from fitness_client import FitnessAPIClient

# Initialize the client
client = FitnessAPIClient("http://localhost:5000")  # or your deployed server URL

# Start a session
client.start_session()

# Create a profile
profile_data = {
    "name": "John Doe",
    "age": 30,
    "weight": 75.5,
    "height": 180,
    "fitness_goal": "muscle gain",
    "experience": "intermediate",
    "equipment": "dumbbells, resistance bands",
    "limitations": "bad knee"
}
profile = client.create_profile(profile_data)

# Wait for AI trainer initialization
max_attempts = 5
for attempt in range(max_attempts):
    status = client.get_profile_status()
    if status.get('success') and status.get('memory_initialized'):
        print("AI trainer is ready!")
        break
    sleep(3)

# Generate a workout
workout = client.generate_workout(
    workout_type="strength",
    duration=45,
    intensity="high"
)

# Chat with the AI trainer
response = client.chat("Create a weekly workout plan for me focusing on upper body")

# Update profile
client.update_profile({"weight": 76, "fitness_goal": "strength"})

# End session
client.end_session()
```

### Client Methods

- `start_session()`: Start a new fitness training session
- `create_profile(profile_data)`: Create a new user profile
- `get_profile()`: Get current user profile
- `update_profile(updates)`: Update user profile
- `get_profile_status()`: Check profile and memory initialization status
- `chat(message)`: Send message to fitness AI
- `generate_workout(workout_type, duration, intensity)`: Generate personalized workout
- `end_session()`: End current session

## Error Handling

The client includes robust error handling:
- Automatic retries for failed requests
- Exponential backoff for rate limiting
- Detailed error messages
- Session management
- Memory initialization checks

## Deployment

For deployment on Render:
1. Set up a new Web Service
2. Connect your repository
3. Set environment variables:
   - `GROQ_API_KEY`
   - `PYTHON_VERSION`: 3.8 or higher
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `gunicorn -c gunicorn.conf.py app:app`



## Emergency System Check

To verify that your emergency system is working properly, run:
```bash
python run_emergency_test.py
```

This test will:
1. Create a test SOS alert with location data
2. Check if the alert was created successfully
3. Get active alerts for the test family
4. Acknowledge the alert
5. Get alert history
6. Resolve the alert
7. Verify the final alert status

The test uses a test user and family ID to simulate emergency situations. If any step fails, you'll see detailed error messages to help diagnose the issue.

Make sure your MongoDB connection is working and your server is running before running this test.

## Event System Check

To verify that your event system is working properly, run:
```bash
python run_event_test.py
```

This test will:
1. Create a test family event with location and timing details
2. Get the event details to verify creation
3. Update the event with new information
4. Join the event as a test user
5. Get all family events within a date range
6. Leave the event
7. Verify all changes were successful

The test uses test data to simulate real event management scenarios. If any step fails, you'll see detailed error messages to help diagnose the issue.

Make sure your MongoDB connection is working and your server is running before running this test.

## Fitness Client Check

To verify that your fitness client is working properly, run:
```bash
python fitness_client.py
```

This test will:
1. Test client initialization and session management
2. Create and update user profiles
3. Test profile status checks
4. Verify chat functionality with the AI trainer
5. Test workout generation
6. Check memory initialization and persistence
7. Verify error handling and retries

The test uses a test API key and simulates real user interactions. If any step fails, you'll see detailed error messages to help diagnose the issue.

Make sure your server is running and your GROQ API key is properly configured before running this test.
