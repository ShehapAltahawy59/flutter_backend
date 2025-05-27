from pymongo import MongoClient
from pymongo.database import Database
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnection:
    _instance: Optional['DatabaseConnection'] = None
    _client: Optional[MongoClient] = None
    _db: Optional[Database] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self._client = MongoClient(os.getenv('MONGODB_URI'))
            self._db = self._client[os.getenv('MONGODB_DB_NAME', 'flutter_project')]

    @property
    def db(self) -> Database:
        return self._db

    def get_collection(self, collection_name: str):
        return self._db[collection_name]

    def close(self):
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            DatabaseConnection._instance = None

# Collections
def get_users_collection():
    return DatabaseConnection().get_collection('users')

def get_families_collection():
    return DatabaseConnection().get_collection('families')

def get_sos_alerts_collection():
    return DatabaseConnection().get_collection('sos_alerts')

def get_events_collection():
    return DatabaseConnection().get_collection('events')

def get_fitness_data_collection():
    return DatabaseConnection().get_collection('fitness_data') 
