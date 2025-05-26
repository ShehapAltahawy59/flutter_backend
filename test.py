import requests
import json

url = "https://flutter-backend-dcqs.onrender.com/api/events"
headers = {"Content-Type": "application/json"}
data = {
    "title": "Family Yoga Session",
    "description": "Weekly family yoga",
    "creator_id": "507f1f77bcf86cd799439011",
    "family_id": "5f8d8a7b4e4b4e3d1c9e7b1a",
    "datetime": "2023-08-25T18:00:00Z",
    "location": "Central Park",
    "event_type": "workout"
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print(response.status_code)
print(response.json())
