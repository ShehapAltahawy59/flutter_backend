from datetime import datetime
import os
import gc
import tempfile
import logging
import traceback
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FitnessMemoryManager:
    def __init__(self, client, user_profile):
        """Initialize memory manager with optimized settings"""
        logger.info("Initializing FitnessMemoryManager...")
        logger.info(f"User profile: {user_profile}")
        
        self.client = client
        self.user_profile = user_profile
        self.initialized = False
        
        try:
            # Create memory storage directory
            self.temp_dir = tempfile.gettempdir()
            self.memory_dir = os.path.join(self.temp_dir, "fitness_memories")
            os.makedirs(self.memory_dir, exist_ok=True)
            
            # Initialize conversation memory
            logger.info("Initializing conversation memory...")
            self.conversation_memory = []
            self.memory_file = os.path.join(self.memory_dir, f"memory_{user_profile.get('name', 'default')}.json")
            
            # Load existing memory if available
            if os.path.exists(self.memory_file):
                try:
                    with open(self.memory_file, 'r') as f:
                        self.conversation_memory = json.load(f)
                except Exception as e:
                    logger.error(f"Error loading memory file: {str(e)}")
                    self.conversation_memory = []
            
            # Mark as initialized
            self.initialized = True
            logger.info("Memory manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing memory manager: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            self.initialized = False
            self.cleanup()
            raise
    
    def is_initialized(self):
        """Check if memory manager is properly initialized"""
        return self.initialized
    
    def add_conversation_turn(self, user_message: str, ai_response: str):
        """Add a conversation turn to memory"""
        if not self.initialized:
            logger.error("Memory manager not initialized")
            return
            
        try:
            logger.info("Adding conversation turn to memory...")
            
            # Add messages to conversation memory
            self.conversation_memory.append({
                "user": user_message,
                "ai": ai_response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Keep only last 10 conversations to manage memory
            if len(self.conversation_memory) > 10:
                self.conversation_memory = self.conversation_memory[-10:]
            
            # Save to file
            self._save_memory()
            
            logger.info("Conversation turn added successfully")
            
        except Exception as e:
            logger.error(f"Error adding conversation turn: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def get_relevant_context(self, query: str) -> str:
        """Get relevant context from memory for the given query"""
        if not self.initialized:
            logger.error("Memory manager not initialized")
            return ""
            
        try:
            logger.info(f"Getting relevant context for query: {query}")
            
            # Get recent conversation history
            context = []
            
            # Add recent conversation history
            if self.conversation_memory:
                context.append("Recent conversation:")
                for msg in self.conversation_memory[-3:]:  # Last 3 messages
                    context.append(f"User: {msg['user']}")
                    context.append(f"AI: {msg['ai']}")
            
            # Join all context with newlines
            return "\n".join(context) if context else ""
            
        except Exception as e:
            logger.error(f"Error getting relevant context: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return ""
    
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
    
    def get_memory_summary(self):
        """Get summary of current memory state"""
        if not self.initialized:
            logger.error("Memory manager not initialized")
            return {
                "error": "Memory manager not initialized",
                "user_profile": self.user_profile
            }
            
        try:
            logger.info("Getting memory summary...")
            summary = {
                "total_conversation_messages": len(self.conversation_memory),
                "user_profile": self.user_profile,
                "initialized": self.initialized
            }
            logger.info(f"Memory summary: {summary}")
            return summary
        except Exception as e:
            logger.error(f"Error getting memory summary: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "error": str(e),
                "user_profile": self.user_profile,
                "initialized": self.initialized
            }
    
    def clear_session_memory(self):
        """Clear session memory"""
        if not self.initialized:
            logger.error("Memory manager not initialized")
            return
            
        try:
            logger.info("Clearing session memory...")
            self.conversation_memory = []
            self._save_memory()
            gc.collect()
            logger.info("Session memory cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing session memory: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def export_memories(self):
        """Export memories for saving"""
        if not self.initialized:
            logger.error("Memory manager not initialized")
            return {}
            
        try:
            logger.info("Exporting memories...")
            return {
                "conversation_messages": self.conversation_memory,
                "initialized": self.initialized
            }
        except Exception as e:
            logger.error(f"Error exporting memories: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {} 
