import requests
import json
from typing import Dict, Any, Optional
from time import sleep
from urllib.parse import urljoin

class FitnessAPIClient:
    def __init__(self, base_url: str = "https://flutter-backend-dcqs.onrender.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def _make_request(self, method: str, endpoint: str, payload: Optional[Dict] = None, retries: int = 3) -> Dict[str, Any]:
        """Helper method to handle all API requests with retry logic"""
        url = urljoin(self.base_url, endpoint)
        
        for attempt in range(retries):
            try:
                response = self.session.request(
                    method,
                    url,
                    json=payload,
                    timeout=10  # 10 seconds timeout
                )
                
                # Handle 429 Too Many Requests
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 5))
                    if attempt < retries - 1:
                        sleep(retry_after)
                        continue
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                if attempt == retries - 1:
                    return {
                        "success": False,
                        "error": str(e),
                        "status_code": getattr(e.response, 'status_code', 500)
                    }
                sleep(1 * (attempt + 1))  # Exponential backoff
    
    def start_session(self) -> Dict[str, Any]:
        """Start a new fitness training session"""
        return self._make_request("POST", "/api/fitness/session/start")
    
    def create_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create user fitness profile"""
        # Validate required fields
        required_fields = ['name', 'age', 'weight', 'height', 'fitness_goal', 'experience']
        if not all(field in profile_data for field in required_fields):
            return {
                "success": False,
                "error": f"Missing required fields: {required_fields}"
            }
        
        return self._make_request("POST", "/api/fitness/profile", profile_data)
    
    def get_profile(self) -> Dict[str, Any]:
        """Get current user profile"""
        return self._make_request("GET", "/api/fitness/profile")
    
    def update_profile(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile"""
        return self._make_request("PUT", "/api/fitness/profile", updates)
    
    def chat(self, message: str) -> Dict[str, Any]:
        """Send message to fitness AI"""
        if not message or not isinstance(message, str):
            return {
                "success": False,
                "error": "Message must be a non-empty string"
            }
        
        return self._make_request("POST", "/api/fitness/chat", {"message": message.strip()})
    
    def generate_workout(self, 
                       workout_type: str = "general", 
                       duration: int = 30, 
                       intensity: str = "moderate") -> Dict[str, Any]:
        """Generate personalized workout"""
        params = {
            "workout_type": workout_type,
            "duration": duration,
            "intensity": intensity
        }
        return self._make_request("POST", "/api/fitness/workout", params)
    
    def get_chat_history(self) -> Dict[str, Any]:
        """Get chat history"""
        return self._make_request("GET", "/api/fitness/chat/history")
    
    def end_session(self) -> Dict[str, Any]:
        """End current session"""
        return self._make_request("POST", "/api/fitness/session/end")

# Example Usage
if __name__ == "__main__":
    client = FitnessAPIClient("https://flutter-backend-dcqs.onrender.com")
    
    try:
        # 1. Start a session
        print("Starting session...")
        session = client.start_session()
        if not session.get('success'):
            raise Exception(f"Failed to start session: {session.get('error')}")
        print("Session started:", session)
        
        # 2. Create profile
        print("\nCreating profile...")
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
        if not profile.get('success'):
            raise Exception(f"Failed to create profile: {profile.get('error')}")
        print("Profile created:", profile)
        
        # 3. Get workout recommendation
        print("\nGenerating workout...")
        workout = client.generate_workout(
            workout_type="strength",
            duration=45,
            intensity="high"
        )
        if not workout.get('success'):
            raise Exception(f"Failed to generate workout: {workout.get('error')}")
        print("Workout plan:", json.dumps(workout, indent=2))
        
        # 4. Chat with fitness AI
        print("\nChatting with AI...")
        chat_response = client.chat("Create a weekly workout plan for me focusing on upper body")
        if not chat_response.get('success'):
            raise Exception(f"Failed to chat: {chat_response.get('error')}")
        print("AI Response:", chat_response.get('response'))
        
        # 5. Update profile
        print("\nUpdating profile...")
        update_response = client.update_profile({"weight": 76, "fitness_goal": "strength"})
        if not update_response.get('success'):
            raise Exception(f"Failed to update profile: {update_response.get('error')}")
        print("Profile updated:", update_response)
        
        # 6. End session
        print("\nEnding session...")
        end_session = client.end_session()
        if not end_session.get('success'):
            raise Exception(f"Failed to end session: {end_session.get('error')}")
        print("Session ended:", end_session)
        
    except Exception as e:
        print(f"\nError during API interaction: {str(e)}")
