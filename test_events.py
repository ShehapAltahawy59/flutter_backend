import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import time
from pymongo import MongoClient
from config import MONGODB_URI, DB_NAME, COLLECTIONS

class EventAPIClient:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        # Add authentication headers
        self.session.headers.update({
            "Authorization": "Bearer test_token"  # Replace with actual token if needed
        })
        
        # Get test user and family IDs from database
        self.test_user_id, self.test_family_id = self._get_test_ids()
    
    def _get_test_ids(self) -> tuple[str, str]:
        """Get a test user ID and their family ID from the database"""
        try:
            client = MongoClient(MONGODB_URI)
            db = client[DB_NAME]
            
            # Get first user from database
            user = db[COLLECTIONS['users']].find_one()
            if not user:
                raise Exception("No users found in database")
            
            user_id = str(user['_id'])
            
            # Get user's family
            family = db[COLLECTIONS['families']].find_one({"members": user_id})
            
            # If no family exists, create one
            if not family:
                print(f"No family found for user {user_id}, creating new family...")
                new_family = {
                    "name": "Test Family",
                    "members": [user_id],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                result = db[COLLECTIONS['families']].insert_one(new_family)
                family_id = str(result.inserted_id)
                print(f"Created new family with ID: {family_id}")
            else:
                family_id = str(family['_id'])
            
            print(f"Using test user ID: {user_id}")
            print(f"Using test family ID: {family_id}")
            
            return user_id, family_id
            
        except Exception as e:
            print(f"Error getting test IDs: {str(e)}")
            raise
        finally:
            client.close()
    
    def _make_request(self, method: str, endpoint: str, payload: Optional[Dict] = None) -> Dict[str, Any]:
        """Helper method to handle all API requests"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            print(f"\nMaking {method} request to {url}")
            if payload:
                print(f"Request payload: {json.dumps(payload, indent=2)}")
            
            response = self.session.request(
                method,
                url,
                json=payload,
                timeout=(5, 15)
            )
            
            print(f"Response status code: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            try:
                response_data = response.json()
                print(f"Response data: {json.dumps(response_data, indent=2)}")
                return response_data
            except json.JSONDecodeError:
                print(f"Raw response content: {response.text}")
                return {
                    "success": False,
                    "error": f"Invalid JSON response: {response.text}",
                    "status_code": response.status_code
                }
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f"\nStatus code: {e.response.status_code}"
                try:
                    error_msg += f"\nResponse: {e.response.json()}"
                except:
                    error_msg += f"\nResponse text: {e.response.text}"
            print(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "status_code": getattr(e.response, 'status_code', 500) if hasattr(e, 'response') else 500
            }
    
    def create_event(self, title: str, description: str, location: Dict[str, float], 
                    start_time: datetime, end_time: datetime, event_type: str = "general",
                    priority: str = "medium") -> Dict[str, Any]:
        """Create a new event"""
        try:
            payload = {
                "title": title,
                "description": description,
                "location": {
                    "type": "Point",
                    "coordinates": [location["longitude"], location["latitude"]]
                },
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "type": event_type,
                "priority": priority,
                "family_id": self.test_family_id,
                "created_by": self.test_user_id
            }
            
            print("\nCreating event with payload:")
            print(json.dumps(payload, indent=2))
            
            response = self._make_request("POST", "/api/events", payload)
            
            if not response.get('success'):
                error_msg = response.get('error', 'Unknown error')
                print(f"Failed to create event. Error: {error_msg}")
                return response
                
            return response
            
        except Exception as e:
            error_msg = f"Error creating event: {str(e)}"
            print(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def get_event(self, event_id: str) -> Dict[str, Any]:
        """Get event details"""
        return self._make_request("GET", f"/api/events/{event_id}")
    
    def update_event(self, event_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update event details"""
        return self._make_request("PUT", f"/api/events/{event_id}", updates)
    
    def get_family_events(self, start_date: datetime, end_date: datetime, 
                         event_type: Optional[str] = None) -> Dict[str, Any]:
        """Get family events within date range"""
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        if event_type:
            params["type"] = event_type
            
        return self._make_request("GET", f"/api/events/family/{self.test_family_id}", params)
    
    def join_event(self, event_id: str) -> Dict[str, Any]:
        """Join an event"""
        return self._make_request("POST", f"/api/events/{event_id}/join", {
            "user_id": self.test_user_id
        })
    
    def leave_event(self, event_id: str) -> Dict[str, Any]:
        """Leave an event"""
        return self._make_request("POST", f"/api/events/{event_id}/leave", {
            "user_id": self.test_user_id
        })

def test_event_system():
    """Test the event system endpoints"""
    client = EventAPIClient("http://localhost:5000")
    
    print("\n=== Testing Event System ===\n")
    
    try:
        # 1. Create Event
        print("1. Creating Event...")
        start_time = datetime.utcnow() + timedelta(days=1)
        end_time = start_time + timedelta(hours=2)
        
        create_response = client.create_event(
            title="Test Family Event",
            description="A test event for the family",
            location={
                "latitude": 37.7749,
                "longitude": -122.4194
            },
            start_time=start_time,
            end_time=end_time,
            event_type="family",
            priority="high"
        )
        
        # Check for event_id in response
        event_id = create_response.get('event_id')
        if not event_id:
            raise Exception(f"Failed to create event: {create_response.get('message', 'Unknown error')}")
            
        print(f"Event created with ID: {event_id}")
        
        # 2. Get Event Details
        print("\n2. Getting Event Details...")
        event_details = client.get_event(event_id)
        if not event_details:
            raise Exception("Failed to get event details: Empty response")
            
        # Convert MongoDB ObjectId to string for JSON serialization
        if '_id' in event_details and '$oid' in event_details['_id']:
            event_details['_id'] = event_details['_id']['$oid']
        if 'created_at' in event_details and '$date' in event_details['created_at']:
            event_details['created_at'] = event_details['created_at']['$date']
            
        print(f"Event Details: {json.dumps(event_details, indent=2)}")
        
        # 3. Update Event
        print("\n3. Updating Event...")
        update_response = client.update_event(event_id, {
            "description": "Updated test event description",
            "priority": "medium"
        })
        if not update_response.get('message') == "Event updated successfully":
            raise Exception(f"Failed to update event: {update_response.get('message', 'Unknown error')}")
        print("Event updated successfully")
        
        # 4. Join Event
        print("\n4. Joining Event...")
        join_response = client.join_event(event_id)
        if not join_response.get('success'):
            raise Exception(f"Failed to join event: {join_response.get('error')}")
        print("Successfully joined event")
        
        # 5. Get Family Events
        print("\n5. Getting Family Events...")
        family_events = client.get_family_events(
            start_date=start_time - timedelta(days=1),
            end_date=end_time + timedelta(days=1),
            event_type="family"
        )
        
        # Convert MongoDB ObjectIds to strings for JSON serialization
        for event in family_events:
            if '_id' in event and '$oid' in event['_id']:
                event['_id'] = event['_id']['$oid']
            if 'created_at' in event and '$date' in event['created_at']:
                event['created_at'] = event['created_at']['$date']
                
        print(f"Family Events: {json.dumps(family_events, indent=2)}")
        
        # 6. Leave Event
        print("\n6. Leaving Event...")
        leave_response = client.leave_event(event_id)
        if not leave_response.get('success'):
            raise Exception(f"Failed to leave event: {leave_response.get('error')}")
        print("Successfully left event")
        
        print("\n=== Event System Tests Completed Successfully ===\n")
        
    except Exception as e:
        print(f"\nError during testing: {str(e)}")
        raise

if __name__ == "__main__":
    test_event_system() 
