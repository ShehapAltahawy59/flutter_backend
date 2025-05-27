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

4. Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
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

## Running Tests

### Standard Tests

1. Run all tests:
```bash
python -m pytest
```

2. Run specific test files:
```bash
python -m pytest tests/test_fitness_client.py
python -m pytest tests/test_chatbot_routes.py
```

### Emergency Tests

The emergency tests verify critical functionality and error handling:

1. Run emergency tests:
```bash
python run_emergency_test.py
```

This test suite:
- Verifies server startup and shutdown
- Tests error handling for invalid API keys
- Checks memory manager initialization
- Validates session management
- Tests server recovery after errors

### Event Tests

The event tests simulate real-world usage scenarios:

1. Run event tests:
```bash
python run_event_test.py
```

This test suite:
- Simulates user sessions
- Tests profile creation and updates
- Verifies chat functionality
- Tests workout generation
- Validates memory persistence
- Checks concurrent user handling

### Test Output

Both test suites provide detailed output:
- Test progress and results
- Error messages and stack traces
- Performance metrics
- Memory usage statistics

Example output:
```
=== Running Emergency Tests ===
[✓] Server startup
[✓] API key validation
[✓] Memory manager initialization
[✓] Session management
[✓] Error recovery

=== Running Event Tests ===
[✓] User session simulation
[✓] Profile management
[✓] Chat functionality
[✓] Workout generation
[✓] Memory persistence
[✓] Concurrent users
```

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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Emergency System Check

To check if your system is working properly, run:
```bash
python run_emergency_test.py
```

This will test if:
- Your server can start up
- Your API key is working
- The memory system is working
- Error handling is working
- Everything is properly connected

If you see any errors, check your API key and server configuration.

## Test Files

The project includes two main test files:

1. `run_emergency_test.py`:
   - This is a diagnostic test that checks if your server is working properly
   - It tests basic things like:
     - Can the server start up?
     - Is your API key working?
     - Can it handle errors without crashing?
     - Is the memory system working?
   - You run it when you want to check if your server is healthy

2. `run_event_test.py`:
   - This simulates a real user using your fitness app
   - It tests things like:
     - Creating a user profile
     - Having a conversation with the AI trainer
     - Getting workout recommendations
     - Updating user information
   - You run it to make sure all the main features work together

To run either test, just use:
```bash
python run_emergency_test.py
# or
python run_event_test.py
```

The emergency test is like a health check, while the event test is like having a real user try out your app. 
