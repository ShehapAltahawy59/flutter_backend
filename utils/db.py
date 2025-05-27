from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, ConfigurationError
import logging
from config import MONGODB_CONFIG, MONGODB_URI, DB_NAME, COLLECTIONS
import time
from typing import Dict, Any
import gc
import os

logger = logging.getLogger(__name__)

class DatabaseConnection:
    _instance = None
    _client = None
    _db = None
    _retry_count = 0
    _max_retries = 3
    _retry_delay = 1  # seconds

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if DatabaseConnection._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            DatabaseConnection._instance = self
            self._connect()

    def _connect(self):
        """Establish connection to MongoDB with retry logic"""
        while self._retry_count < self._max_retries:
            try:
                logger.info(f"Attempting to connect to MongoDB (attempt {self._retry_count + 1}/{self._max_retries})")
                
                # Get MongoDB URI from environment variable
                mongodb_uri = os.getenv('MONGODB_URI')
                if not mongodb_uri:
                    raise ConfigurationError("MONGODB_URI environment variable is not set")
                
                # Use connection pooling and configuration from MONGODB_CONFIG
                self._client = MongoClient(
                    mongodb_uri,
                    **MONGODB_CONFIG
                )
                
                # Test the connection
                self._client.admin.command('ping')
                self._db = self._client[DB_NAME]
                logger.info("Successfully connected to MongoDB")
                return
                
            except (ConnectionFailure, ServerSelectionTimeoutError, ConfigurationError) as e:
                self._retry_count += 1
                logger.error(f"MongoDB connection attempt {self._retry_count} failed: {str(e)}")
                if self._retry_count < self._max_retries:
                    logger.info(f"Retrying in {self._retry_delay} seconds...")
                    time.sleep(self._retry_delay)
                else:
                    logger.error("Max retries reached. Could not connect to MongoDB")
                    raise

    def get_db(self):
        """Get database instance with connection check"""
        try:
            # Test connection
            self._client.admin.command('ping')
        except:
            # If connection fails, try to reconnect
            self._retry_count = 0
            self._connect()
        return self._db

    def get_collection(self, collection_name):
        """Get collection instance"""
        if collection_name not in COLLECTIONS:
            raise ValueError(f"Unknown collection: {collection_name}")
        return self.get_db()[COLLECTIONS[collection_name]]

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
            gc.collect()  # Force garbage collection after closing connection 
