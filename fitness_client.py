import requests
import json
from typing import Dict, Any, Optional

class FitnessAPIClient:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def start_session(self) -> Dict[str, Any]:
        """Start a new fitness training session"""
        url = f"{self.base_url}/api/fitness/session/start"
        response = self.session.post(url)
        return self._handle_response(response)
    
    def create_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create user fitness profile"""
        url = f"{self.base_url}/api/fitness/profile/create"
        response = self.session.post(url, json=profile_data)
        return self._handle_response(response)
    
    def get_profile(self) -> Dict[str, Any]:
        """Get current user profile"""
        url = f"{self.base_url}/api/fitness/profile/get"
        response = self.session.get(url)
        return self._handle_response(response)
    
    def update_profile(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile"""
        url = f"{self.base_url}/api/fitness/profile/update"
        response = self.session.put(url, json=updates)
        return self._handle_response(response)
    
    def chat(self, message: str) -> Dict[str, Any]:
        """Send message to fitness AI"""
        url = f"{self.base_url}/api/fitness/chat"
        response = self.session.post(url, json={"message": message})
        return self._handle_response(response)
    
    def generate_workout(self, 
                        workout_type: str = "general", 
                        duration: int = 30, 
                        intensity: str = "moderate") -> Dict[str, Any]:
        """Generate personalized workout"""
        url = f"{self.base_url}/api/fitness/workout/generate"
        params = {
            "workout_type": workout_type,
            "duration": duration,
            "intensity": intensity
        }
        response = self.session.post(url, json=params)
        return self._handle_response(response)
    
    def get_chat_history(self) -> Dict[str, Any]:
        """Get chat history"""
        url = f"{self.base_url}/api/fitness/chat/history"
        response = self.session.get(url)
        return self._handle_response(response)
    
    def end_session(self) -> Dict[str, Any]:
        """End current session"""
        url = f"{self.base_url}/api/fitness/session/end"
        response = self.session.post(url)
        return self._handle_response(response)
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response"""
        try:
            return response.json()
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": f"Invalid response: {response.text}",
                "status_code": response.status_code
            }

client = FitnessAPIClient("https://flutter-backend-dcqs.onrender.com")

# 1. Start a session
session = client.start_session()
print("Session started:", session)

# 2. Create profile
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
print("Profile created:", profile)

# 3. Get workout recommendation
workout = client.generate_workout(
    workout_type="strength",
    duration=45,
    intensity="high"
)
print("Workout plan:", workout)

# 4. Chat with fitness AI
chat_response = client.chat("create a workout plan for me ")
print("AI Response:", chat_response['response'])

# 5. Update profile
update_response = client.update_profile({"weight": 76, "fitness_goal": "strength"})
print("Profile updated:", update_response)

# 6. End session
end_session = client.end_session()
print("Session ended:", end_session)
