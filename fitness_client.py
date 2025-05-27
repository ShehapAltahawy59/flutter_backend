import requests
import json
from typing import Dict, Any, Optional
from time import sleep
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FitnessAPIClient:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session_id = None
        
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
    
    def start_session(self) -> bool:
        """Start a new fitness training session"""
        try:
            # Check for GROQ_API_KEY
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                print("Error: GROQ_API_KEY not found in environment variables")
                return False

            response = self._make_request("POST", "/api/fitness/session/start")
            if response.get('success'):
                self.session_id = response.get('session_id')
                print("Session started:", response)
                return True
            print(f"Failed to start session: {response.get('error', 'Unknown error')}")
            return False
        except Exception as e:
            print(f"Error starting session: {str(e)}")
            return False
    
    def create_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any] | None:
        """Create user fitness profile"""
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                print(f"\nCreating profile (attempt {attempt + 1}/{max_retries})...")
                headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
                
                # Use the session for consistent connection handling
                response = self.session.post(
                    f"{self.base_url}/api/fitness/profile",
                    json=profile_data,
                    headers=headers,
                    timeout=(5, 30)  # Increased timeout for model loading
                )
                
                response.raise_for_status()
                data = response.json()
                
                if data.get('status') == 'success':
                    print("Profile created successfully!")
                    print("\nProfile details:")
                    profile = data.get('profile', {})
                    print(f"Name: {profile.get('name')}")
                    print(f"Age: {profile.get('age')}")
                    print(f"Weight: {profile.get('weight')} kg")
                    print(f"Height: {profile.get('height')} cm")
                    print(f"BMI: {profile.get('bmi')}")
                    print(f"Goal: {profile.get('fitness_goal')}")
                    print(f"Experience: {profile.get('experience')}")
                    print(f"Equipment: {profile.get('equipment')}")
                    print(f"Limitations: {profile.get('limitations')}")
                    return profile
                else:
                    print(f"Failed to create profile: {data.get('message')}")
                    if attempt < max_retries - 1:
                        print(f"Retrying in {retry_delay} seconds...")
                        sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    return None
                    
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 502 and attempt < max_retries - 1:
                    print(f"Server is still initializing (502 error). Retrying in {retry_delay} seconds...")
                    sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                print(f"HTTP Error during API interaction: {str(e)}")
                return None
                
            except requests.exceptions.RequestException as e:
                print(f"Error during API interaction: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                return None
                
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                return None
        
        print("Failed to create profile after all retries")
        return None
    
    def get_profile(self) -> Dict[str, Any]:
        """Get current user profile"""
        return self._make_request("GET", "/api/fitness/profile")
    
    def update_profile(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile"""
        return self._make_request("PUT", "/api/fitness/profile", updates)
    
    def get_profile_status(self) -> Dict[str, Any]:
        """Get profile and memory initialization status"""
        try:
            print("\nChecking profile status...")
            response = self._make_request("GET", "/api/fitness/profile/status")
            
            if not response:
                print("No response received from server")
                return {
                    "success": False,
                    "error": "No response from server"
                }
            
            print(f"Status response: {response}")
            
            # Check status field instead of success
            if response.get('status') != 'success':
                error_msg = response.get('message', 'Unknown error')
                print(f"Profile status check failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "data": response.get('data', {})
                }
            
            # Get memory initialization status from data
            data = response.get('data', {})
            memory_initialized = data.get('memory_initialized', False)
            if not memory_initialized:
                error_msg = response.get('message', 'Memory initialization failed')
                print(f"Memory not initialized: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "data": data
                }
            
            print("Profile status check successful")
            return {
                "success": True,
                "data": data,
                "memory_initialized": memory_initialized
            }
            
        except Exception as e:
            print(f"Error checking profile status: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
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
    client = FitnessAPIClient("http://flutter-backend-dcqs.onrender.com")
    
    try:
        # 1. Start a session
        print("Starting session...")
        if not client.start_session():
            raise Exception("Failed to start session")
        
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
        if not profile:
            raise Exception("Failed to create profile")
        
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
        
        #3. Get workout recommendation
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
