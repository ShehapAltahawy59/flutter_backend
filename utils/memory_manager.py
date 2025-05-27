from datetime import datetime
import os
import gc
import tempfile
import logging
import traceback
import json
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FitnessMemoryManager:
    def __init__(self, client, user_profile):
        """Initialize memory manager with Groq client and user profile"""
        print("\n=== Initializing FitnessMemoryManager ===")
        try:
            self.client = client
            self.user_profile = user_profile
            self.initialized = False
            
            print("Creating cache directories...")
            # Create cache directories in user's temp directory
            self.model_cache_dir = os.path.join(tempfile.gettempdir(), 'fitness_model_cache')
            self.chroma_db_dir = os.path.join(tempfile.gettempdir(), 'fitness_chroma_db')
            
            os.makedirs(self.model_cache_dir, exist_ok=True)
            os.makedirs(self.chroma_db_dir, exist_ok=True)
            print(f"Cache directories created at {self.model_cache_dir} and {self.chroma_db_dir}")
            
            print("Initializing conversation memory...")
            # Initialize conversation memory
            self.conversation_memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            print("Conversation memory initialized")
            
            print("Initializing memory retriever...")
            # Initialize memory retriever
            self.memory_retriever = None
            print("Memory retriever initialized")
            
            # Mark as initialized
            self.initialized = True
            print("FitnessMemoryManager initialized successfully")
            
        except Exception as e:
            print(f"Error initializing FitnessMemoryManager: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            self.initialized = False
            raise

    def is_initialized(self):
        """Check if memory manager is properly initialized"""
        return hasattr(self, 'initialized') and self.initialized

    def get_relevant_context(self, query: str) -> str:
        """Get relevant context from memory"""
        try:
            print("\n=== Getting Relevant Context ===")
            if not self.is_initialized():
                print("Memory manager not initialized")
                return ""
            
            # Get recent conversation history
            print("Getting recent conversation history...")
            recent_history = self.conversation_memory.load_memory_variables({})
            chat_history = recent_history.get("chat_history", [])
            
            # Format conversation history
            formatted_history = []
            for message in chat_history:
                if isinstance(message, HumanMessage):
                    formatted_history.append(f"User: {message.content}")
                elif isinstance(message, AIMessage):
                    formatted_history.append(f"Assistant: {message.content}")
            
            # Combine into context
            context = "\n".join(formatted_history[-5:]) if formatted_history else ""
            print(f"Retrieved {len(formatted_history)} recent messages")
            
            return context
            
        except Exception as e:
            print(f"Error getting relevant context: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return ""

    def add_conversation_turn(self, user_message: str, ai_response: str):
        """Add a conversation turn to memory"""
        try:
            print("\n=== Adding Conversation Turn ===")
            if not self.is_initialized():
                print("Memory manager not initialized")
                return
            
            print("Adding messages to conversation memory...")
            self.conversation_memory.chat_memory.add_user_message(user_message)
            self.conversation_memory.chat_memory.add_ai_message(ai_response)
            print("Messages added successfully")
            
        except Exception as e:
            print(f"Error adding conversation turn: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")

    def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary of memory contents"""
        try:
            print("\n=== Getting Memory Summary ===")
            if not self.is_initialized():
                print("Memory manager not initialized")
                return {
                    'total_conversation_messages': 0,
                    'stored_important_memories': 0,
                    'buffer_summary_length': 0,
                    'user_profile': None
                }
            
            # Get conversation history
            recent_history = self.conversation_memory.load_memory_variables({})
            chat_history = recent_history.get("chat_history", [])
            
            summary = {
                'total_conversation_messages': len(chat_history),
                'stored_important_memories': 0,
                'buffer_summary_length': 0,
                'user_profile': self.user_profile
            }
            
            print(f"Memory summary: {summary}")
            return summary
            
        except Exception as e:
            print(f"Error getting memory summary: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return {
                'total_conversation_messages': 0,
                'stored_important_memories': 0,
                'buffer_summary_length': 0,
                'user_profile': None
            }

    def clear_session_memory(self):
        """Clear session memory"""
        try:
            print("\n=== Clearing Session Memory ===")
            if not self.is_initialized():
                print("Memory manager not initialized")
                return
            
            print("Clearing conversation memory...")
            self.conversation_memory.clear()
            print("Session memory cleared successfully")
            
        except Exception as e:
            print(f"Error clearing session memory: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")

    def export_memories(self) -> Dict[str, Any]:
        """Export memories for saving"""
        try:
            print("\n=== Exporting Memories ===")
            if not self.is_initialized():
                print("Memory manager not initialized")
                return {}
            
            # Get conversation history
            recent_history = self.conversation_memory.load_memory_variables({})
            chat_history = recent_history.get("chat_history", [])
            
            # Format messages for export
            conversation_messages = []
            for message in chat_history:
                if isinstance(message, HumanMessage):
                    conversation_messages.append({
                        'type': 'HumanMessage',
                        'content': message.content
                    })
                elif isinstance(message, AIMessage):
                    conversation_messages.append({
                        'type': 'AIMessage',
                        'content': message.content
                    })
            
            memories = {
                'conversation_messages': conversation_messages,
                'vector_memories': []
            }
            
            print(f"Exported {len(conversation_messages)} conversation messages")
            return memories
            
        except Exception as e:
            print(f"Error exporting memories: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return {}
    
    def cleanup(self):
        """Clean up resources"""
        try:
            logger.info("Cleaning up resources...")
            if self.initialized:
                self._save_memory()
            gc.collect()
            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def _save_memory(self):
        """Save memory to file"""
        if not self.initialized:
            logger.error("Memory manager not initialized")
            return
            
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.conversation_memory, f)
        except Exception as e:
            logger.error(f"Error saving memory: {str(e)}")
