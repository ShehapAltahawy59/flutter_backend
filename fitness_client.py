import requests
import json
from typing import Dict, Any, Optional
from time import sleep
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class FitnessAPIClient:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=2,  # reduced number of retries
            backoff_factor=0.3,  # shorter backoff
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def _make_request(self, method: str, endpoint: str, payload: Optional[Dict] = None) -> Dict[str, Any]:
        """Helper method to handle all API requests with optimized retry logic"""
        url = urljoin(self.base_url, endpoint)
        
        try:
            response = self.session.request(
                method,
                url,
                json=payload,
                timeout=(5, 15)  # (connect timeout, read timeout) - increased timeouts
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": getattr(e.response, 'status_code', 500) if hasattr(e, 'response') else 500
            }
    
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
    
    def get_profile_status(self) -> Dict[str, Any]:
        """Get profile and memory initialization status"""
        return self._make_request("GET", "/api/fitness/profile")
    
    def chat(self, message: str) -> Dict[str, Any]:
        """Send message to fitness AI"""
        if not message or not isinstance(message, str):
            return {
                "success": False,
                "error": "Message must be a non-empty string"
            }
        
        # Check profile status first
        status = self.get_profile_status()
        if not status.get('success'):
            return status
        
        if not status.get('memory_initialized'):
            return {
                "success": False,
                "error": "AI trainer is not ready. Please try again in a few seconds."
            }
        
        # Try up to 3 times with increasing delays
        for attempt in range(3):
            try:
                response = self._make_request("POST", "/api/fitness/chat", {"message": message.strip()})
                if response.get('success'):
                    return response
                
                # If we get a 503, wait and retry
                if response.get('status_code') == 503:
                    if attempt < 2:  # Don't sleep on the last attempt
                        sleep(2 * (attempt + 1))  # Exponential backoff: 2s, 4s
                        continue
                
                return response
                
            except Exception as e:
                if attempt == 2:  # Last attempt
                    return {
                        "success": False,
                        "error": str(e),
                        "status_code": getattr(e.response, 'status_code', 500) if hasattr(e, 'response') else 500
                    }
                sleep(2 * (attempt + 1))
        
        return {
            "success": False,
            "error": "Failed to get response after multiple attempts"
        }
    
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
    client = FitnessAPIClient("http://localhost:5000")
    
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
        
        # Wait for memory initialization
        print("Waiting for AI trainer to initialize...")
        max_attempts = 5
        for attempt in range(max_attempts):
            status = client.get_profile_status()
            if status.get('success') and status.get('memory_initialized'):
                print("AI trainer is ready!")
                break
            if attempt < max_attempts - 1:
                error_msg = status.get('error', 'Unknown error')
                print(f"AI trainer is still initializing... (attempt {attempt + 1}/{max_attempts})")
                print(f"Error: {error_msg}")
                sleep(3)
            else:
                error_msg = status.get('error', 'Unknown error')
                raise Exception(f"AI trainer failed to initialize after multiple attempts. Last error: {error_msg}")
        
        # 3. Get workout recommendation
        # print("\nGenerating workout...")
        # workout = client.generate_workout(
        #     workout_type="strength",
        #     duration=45,
        #     intensity="high"
        # )
        # if not workout.get('success'):
        #     raise Exception(f"Failed to generate workout: {workout.get('error')}")
        # print("Workout plan:", json.dumps(workout, indent=2))
        
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
