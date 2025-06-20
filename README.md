# Fitness AI Backend

A Flask-based backend service for AI-powered fitness, family, and emergency management.

## Features
- AI-powered fitness training and workout generation
- User, family, event, and emergency management
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

Start the Flask development server:
```bash
python app.py
```

The server will be available at `http://localhost:5000` by default.

---

# API Endpoints & Postman Testing

## User Endpoints

### Create User
- **POST** `/api/users`
- **Body:**
```json
{
  "email": "user@example.com",
  "name": "User Name",
  "phone": "+1234567890",
  "password_hash": "hashed_password"
}
```

### Get All Users
- **GET** `/api/users`

### Get User by ID
- **GET** `/api/users/<user_id>`

### Delete User
- **DELETE** `/api/users/<user_id>`

---

## Family Endpoints

### Create Family
- **POST** `/api/families`
- **Body:**
```json
{
  "name": "Family Name",
  "admin_user_id": "<user_id>"
}
```

### Add Member to Family
- **POST** `/api/families/<family_id>/members`
- **Body:**
```json
{
  "user_id": "<user_id>",
  "role": "member" // or "admin"
}
```

### Get Family by ID
- **GET** `/api/families/<family_id>`

### Get Families for User
- **GET** `/api/families/user/<user_id>`

### Get All Members of User's Family
- **GET** `/api/families/user/<user_id>/members`

---

## Event Endpoints

### Create Event
- **POST** `/api/events`
- **Body:**
```json
{
  "family_id": "<family_id>",
  "created_by": "<user_id>",
  "title": "Event Title",
  "description": "...",
  "location": "123 Main St, City",
  "start_time": "2025-06-01T10:00:00Z",
  "end_time": "2025-06-01T12:00:00Z",
  "type": "general",
  "priority": "normal"
}
```

### Get All Events
- **GET** `/api/events`

### Get Event by ID
- **GET** `/api/events/<event_id>`

### Update Event
- **PUT** `/api/events/<event_id>`
- **Body:** (any updatable fields)

### Delete Event
- **DELETE** `/api/events/<event_id>`

### Join Event
- **POST** `/api/events/<event_id>/join`
- **Body:**
```json
{
  "user_id": "<user_id>",
  "user_name": "User Name"
}
```

### Leave Event
- **POST** `/api/events/<event_id>/leave`
- **Body:**
```json
{
  "user_id": "<user_id>"
}
```

### Get Family Events
- **GET** `/api/events/user/<user_id>/family-events`

---

## Emergency Endpoints

### Create Emergency Alert
- **POST** `/api/emergency`
- **Body:**
```json
{
  "user_id": "<user_id>",
  "family_id": "<family_id>",
  "location": "123 Main St, City",
  "message": "Emergency message"
}
```

### Get Active Family Emergencies
- **GET** `/api/emergency/family/<family_id>`

### Acknowledge Emergency
- **POST** `/api/emergency/<alert_id>/acknowledge`
- **Body:**
```json
{
  "user_id": "<user_id>"
}
```

### Resolve Emergency
- **POST** `/api/emergency/<alert_id>/resolve`
- **Body:**
```json
{
  "user_id": "<user_id>"
}
```

---

## Fitness & Workout Endpoints

### Analyze Profile & Generate Workout
- **POST** `/api/fitness/generate_workout`
- **Body:**
```json
{
  "user_id": "<user_id>",
  "name": "User Name",
  "age": 30,
  "weight": 75.5,
  "height": 180,
  "fitness_goal": "muscle gain",
  "experience": "intermediate",
  "equipment": "dumbbells, resistance bands",
  "limitations": "bad knee"
}
```

### Get User Workouts
- **GET** `/api/fitness/user_workouts/<user_id>`

### Save Fitness Profile
- **POST** `/api/fitness/fitness-profile`
- **Body:**
```json
{
  "user_id": "<user_id>",
  "age": 30,
  "weight": 75.5,
  "height": 180,
  "fitness_goal": "muscle gain",
  "experience": "intermediate",
  "equipment": ["dumbbells", "resistance bands"],
  "limitations": "bad knee"
}
```

---

# Testing Endpoints with Postman

1. Set the method and URL as shown above.
2. For POST/PUT requests, set `Content-Type: application/json` and provide the body as shown.
3. Click **Send** to test the endpoint.
4. Check the response for success or error messages.

---

# Notes
- All IDs must be valid MongoDB ObjectIds (as strings).
- Timestamps should be in ISO8601 format.

