from pymongo import MongoClient
from typing import Dict, Any
from config import MONGODB_URI, DB_NAME, COLLECTIONS

class DatabaseConnection:
    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self._client = MongoClient(MONGODB_URI)
            self._db = self._client[DB_NAME]

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_collection(self, collection_name: str):
        """Get a collection by name"""
        if collection_name not in COLLECTIONS:
            raise ValueError(f"Unknown collection: {collection_name}")
        return self._db[COLLECTIONS[collection_name]]

    def get_users_collection(self):
        """Get users collection"""
        return self.get_collection('users')

    def get_families_collection(self):
        """Get families collection"""
        return self.get_collection('families')

    def get_events_collection(self):
        """Get events collection"""
        return self.get_collection('events')

    def get_sos_alerts_collection(self):
        """Get SOS alerts collection"""
        return self.get_collection('sos_alerts')

    def get_fitness_data_collection(self):
        """Get fitness data collection"""
        return self.get_collection('fitness_data')

    def get_notifications_collection(self):
        """Get notifications collection"""
        return self.get_collection('notifications')

    def get_chat_history_collection(self):
        """Get chat history collection"""
        return self.get_collection('chat_history')

    def close(self):
        """Close the database connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            self._instance = None 
