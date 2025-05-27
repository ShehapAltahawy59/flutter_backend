import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import time

class EventAPIClient:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def _make_request(self, method: str, endpoint: str, payload: Optional[Dict] = None) -> Dict[str, Any]:
        """Helper method to handle all API requests"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method,
                url,
                json=payload,
                timeout=(5, 15)
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": getattr(e.response, 'status_code', 500) if hasattr(e, 'response') else 500
            }
    
    def create_event(self, 
                    title: str,
                    description: str,
                    location: Dict[str, float],
                    start_time: datetime,
                    end_time: datetime,
                    event_type: str = "general",
                    priority: str = "medium") -> Dict[str, Any]:
        """Create a new event"""
        payload = {
            "title": title,
            "description": description,
            "location": location,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "type": event_type,
            "priority": priority
        }
        return self._make_request("POST", "/api/events", payload)
    
    def update_event(self, event_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing event"""
        return self._make_request("PUT", f"/api/events/{event_id}", updates)
    
    def get_event(self, event_id: str) -> Dict[str, Any]:
        """Get a specific event"""
        return self._make_request("GET", f"/api/events/{event_id}")
    
    def get_family_events(self, 
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None,
                         event_type: Optional[str] = None) -> Dict[str, Any]:
        """Get events for the user's family"""
        params = {}
        if start_date:
            params['start_date'] = start_date.isoformat()
        if end_date:
            params['end_date'] = end_date.isoformat()
        if event_type:
            params['type'] = event_type
            
        return self._make_request("GET", "/api/events/family", params)
    
    def join_event(self, event_id: str) -> Dict[str, Any]:
        """Join an event as a participant"""
        return self._make_request("POST", f"/api/events/{event_id}/join")
    
    def leave_event(self, event_id: str) -> Dict[str, Any]:
        """Leave an event"""
        return self._make_request("POST", f"/api/events/{event_id}/leave")

def test_event_system():
    """Test the event system endpoints"""
    client = EventAPIClient("https://flutter-backend-dcqs.onrender.com")
    
    print("\n=== Testing Event System ===\n")
    
    try:
        # 1. Create Event
        print("1. Creating Event...")
        start_time = datetime.utcnow() + timedelta(days=1)
        end_time = start_time + timedelta(hours=2)
        
        event_response = client.create_event(
            title="Family Dinner",
            description="Monthly family dinner at our favorite restaurant",
            location={
                "latitude": 37.7749,
                "longitude": -122.4194
            },
            start_time=start_time,
            end_time=end_time,
            event_type="family",
            priority="high"
        )
        
        if not event_response.get('success'):
            raise Exception(f"Failed to create event: {event_response.get('error')}")
        
        event_id = event_response.get('event_id')
        print(f"Event created with ID: {event_id}")
        
        # 2. Get Event Details
        print("\n2. Getting Event Details...")
        event_details = client.get_event(event_id)
        if not event_details.get('success'):
            raise Exception(f"Failed to get event details: {event_details.get('error')}")
        print(f"Event Details: {json.dumps(event_details.get('event'), indent=2)}")
        
        # 3. Update Event
        print("\n3. Updating Event...")
        update_response = client.update_event(event_id, {
            "description": "Updated: Monthly family dinner with special guests",
            "priority": "high"
        })
        if not update_response.get('success'):
            raise Exception(f"Failed to update event: {update_response.get('error')}")
        print("Event updated successfully")
        
        # 4. Join Event
        print("\n4. Joining Event...")
        join_response = client.join_event(event_id)
        if not join_response.get('success'):
            raise Exception(f"Failed to join event: {join_response.get('error')}")
        print("Successfully joined the event")
        
        # 5. Get Family Events
        print("\n5. Getting Family Events...")
        family_events = client.get_family_events(
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=7),
            event_type="family"
        )
        if not family_events.get('success'):
            raise Exception(f"Failed to get family events: {family_events.get('error')}")
        print(f"Family Events: {json.dumps(family_events.get('events'), indent=2)}")
        
        # 6. Leave Event
        print("\n6. Leaving Event...")
        leave_response = client.leave_event(event_id)
        if not leave_response.get('success'):
            raise Exception(f"Failed to leave event: {leave_response.get('error')}")
        print("Successfully left the event")
        
        # 7. Verify Final Event Status
        print("\n7. Verifying Final Event Status...")
        final_event = client.get_event(event_id)
        if not final_event.get('success'):
            raise Exception(f"Failed to get final event status: {final_event.get('error')}")
        print(f"Final Event Status: {json.dumps(final_event.get('event'), indent=2)}")
        
        print("\n=== Event System Tests Completed Successfully ===\n")
        
    except Exception as e:
        print(f"\nError during testing: {str(e)}")
        raise

if __name__ == "__main__":
    test_event_system() 
