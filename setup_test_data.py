from datetime import datetime
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

def setup_test_data():
    """Set up test data for emergency system"""
    print("\n=== Setting up test data ===\n")
    
    # API base URL
    base_url = "https://flutter-backend-dcqs.onrender.com"
    
    # Create test IDs (24-character hex strings)
    test_user_id = "507f1f77bcf86cd799439011"  # Valid 24-character hex string
    test_family_id = "507f1f77bcf86cd799439012"  # Valid 24-character hex string
    
    # Create test user data
    test_user = {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "1234567890",
        "location": {
            "type": "Point",
            "coordinates": [-122.4194, 37.7749]  # [longitude, latitude] for GeoJSON
        },
        "family_id": test_family_id,
        "password_hash": "test_password_hash"  # Required field for user creation
    }
    
    try:
        # First try to delete by ID
        print("Clearing existing test data by ID...")
        response = requests.delete(f"{base_url}/api/users/{test_user_id}")
        print(f"Delete by ID response: {response.status_code}")
        
        # Then try to delete by email
        print("\nClearing existing test data by email...")
        response = requests.delete(f"{base_url}/api/users/email/{test_user['email']}")
        print(f"Delete by email response: {response.status_code}")
        
        # Create test user
        print("\nCreating test user...")
        print(f"Request payload: {json.dumps(test_user, indent=2)}")
        response = requests.post(
            f"{base_url}/api/users/",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Create response status: {response.status_code}")
        print(f"Create response content: {response.text}")
        
        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to create test user: {response.text}")
        
        # Get the created user ID from response
        response_data = response.json()
        created_user_id = response_data.get('_id', {}).get('$oid', test_user_id)
        
        print("\n✅ Test data setup completed successfully!")
        print("\nTest Data Summary:")
        print(f"- User ID: {created_user_id}")
        print(f"- Family ID: {test_family_id}")
        print(f"- User created with test data")
        
        # Verify user creation
        print("\nVerifying user creation...")
        response = requests.get(f"{base_url}/api/users/{created_user_id}")
        print(f"Verify response status: {response.status_code}")
        print(f"Verify response content: {response.text}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"User verified: {json.dumps(user_data, indent=2)}")
        else:
            print(f"Warning: Could not verify user creation: {response.text}")
        
    except Exception as e:
        print(f"\n❌ Error setting up test data: {str(e)}")
        raise

if __name__ == "__main__":
    setup_test_data() 
