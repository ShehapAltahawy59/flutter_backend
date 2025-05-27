import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional
import time

class EmergencyAPIClient:
    def __init__(self, base_url: str = "https://flutter-backend-dcqs.onrender.com"):
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
        
        # Test IDs (must match setup_test_data.py)
        self.test_user_id = "507f1f77bcf86cd799439011"
        self.test_family_id = "507f1f77bcf86cd799439012"
    
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
    
    def create_sos_alert(self, location: Dict[str, float], message: str = "") -> Dict[str, Any]:
        """Create a new SOS alert"""
        payload = {
            "location": {
                "type": "Point",
                "coordinates": [location["longitude"], location["latitude"]]  # [longitude, latitude] for GeoJSON
            },
            "message": message,
            "user_id": self.test_user_id,
            "family_id": self.test_family_id
        }
        return self._make_request("POST", "/api/emergency", payload)
    
    def acknowledge_sos_alert(self, alert_id: str) -> Dict[str, Any]:
        """Acknowledge an SOS alert"""
        return self._make_request("PUT", f"/api/emergency/resolve/{alert_id}")
    
    def resolve_sos_alert(self, alert_id: str) -> Dict[str, Any]:
        """Resolve an SOS alert"""
        return self._make_request("PUT", f"/api/emergency/resolve/{alert_id}")
    
    def get_active_alerts(self) -> Dict[str, Any]:
        """Get active SOS alerts"""
        return self._make_request("GET", f"/api/emergency/family/{self.test_family_id}")
    
    def get_alert_history(self) -> Dict[str, Any]:
        """Get SOS alert history"""
        return self._make_request("GET", f"/api/emergency/family/{self.test_family_id}")

def test_emergency_system():
    """Test the emergency system endpoints"""
    client = EmergencyAPIClient("https://flutter-backend-dcqs.onrender.com")
    
    print("\n=== Testing Emergency System ===\n")
    
    try:
        # 1. Create SOS Alert
        print("1. Creating SOS Alert...")
        location = {
            "latitude": 37.7749,
            "longitude": -122.4194
        }
        sos_response = client.create_sos_alert(
            location=location,
            message="Test emergency situation"
        )
        
        if not sos_response.get('success'):
            raise Exception(f"Failed to create SOS alert: {sos_response.get('error')}")
        
        alert_id = sos_response.get('emergency_id')
        if not alert_id:
            raise Exception("No emergency ID returned from create response")
            
        print(f"SOS Alert created with ID: {alert_id}")
        
        # 2. Get Active Alerts
        print("\n2. Getting Active Alerts...")
        active_alerts = client.get_active_alerts()
        if not active_alerts.get('success'):
            raise Exception(f"Failed to get active alerts: {active_alerts.get('error')}")
        print(f"Active Alerts: {json.dumps(active_alerts.get('alerts'), indent=2)}")
        
        # 3. Acknowledge Alert
        print("\n3. Acknowledging Alert...")
        acknowledge_response = client.acknowledge_sos_alert(alert_id)
        if not acknowledge_response.get('success'):
            raise Exception(f"Failed to acknowledge alert: {acknowledge_response.get('error')}")
        print("Alert acknowledged successfully")
        
        # 4. Get Alert History
        print("\n4. Getting Alert History...")
        history = client.get_alert_history()
        if not history.get('success'):
            raise Exception(f"Failed to get alert history: {history.get('error')}")
        print(f"Alert History: {json.dumps(history.get('alerts'), indent=2)}")
        
        # 5. Resolve Alert
        print("\n5. Resolving Alert...")
        resolve_response = client.resolve_sos_alert(alert_id)
        if not resolve_response.get('success'):
            raise Exception(f"Failed to resolve alert: {resolve_response.get('error')}")
        print("Alert resolved successfully")
        
        # 6. Verify Alert Status
        print("\n6. Verifying Final Alert Status...")
        final_alerts = client.get_active_alerts()
        if not final_alerts.get('success'):
            raise Exception(f"Failed to get final alert status: {final_alerts.get('error')}")
        print(f"Final Alert Status: {json.dumps(final_alerts.get('alerts'), indent=2)}")
        
        print("\n=== Emergency System Tests Completed Successfully ===\n")
        
    except Exception as e:
        print(f"\nError during testing: {str(e)}")
        raise

if __name__ == "__main__":
    test_emergency_system() 
