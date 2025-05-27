from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.memory import ConversationBufferMemory
from langchain.schema.messages import HumanMessage, AIMessage
import os
import gc
import tempfile
import logging
import traceback
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for preloaded models
_embeddings = None
_vector_store = None

def get_preloaded_models():
    """Get or initialize preloaded models"""
    global _embeddings, _vector_store
    
    if _embeddings is None or _vector_store is None:
        temp_dir = tempfile.gettempdir()
        model_cache_dir = os.path.join(temp_dir, "fitness_model_cache")
        chroma_db_dir = os.path.join(temp_dir, "fitness_chroma_db")
        
        _embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True},
            cache_folder=model_cache_dir
        )
        
        _vector_store = Chroma(
            collection_name="fitness_memories",
            embedding_function=_embeddings,
            persist_directory=chroma_db_dir
        )
    
    return _embeddings, _vector_store

class FitnessMemoryManager:
    def __init__(self, client, user_profile):
        """Initialize memory manager with optimized settings"""
        logger.info("Initializing FitnessMemoryManager...")
        logger.info(f"User profile: {user_profile}")
        
        self.client = client
        self.user_profile = user_profile
        
        try:
            # Get preloaded models
            self.embeddings, self.vector_store = get_preloaded_models()
            
            # Initialize conversation memory with smaller buffer
            logger.info("Initializing conversation memory...")
            self.conversation_memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                max_token_limit=1000  # Limit memory size
            )
            logger.info("Conversation memory initialized successfully")
            
            # Initialize memory retriever with optimized settings
            logger.info("Initializing memory retriever...")
            self.memory_retriever = self.vector_store.as_retriever(
                search_kwargs={"k": 3}  # Limit number of retrieved memories
            )
            logger.info("Memory retriever initialized successfully")
            
            logger.info("Memory manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing memory manager: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Clean up on error
            self.cleanup()
            raise
    
    def add_conversation_turn(self, user_message: str, ai_response: str):
        """Add a conversation turn to memory"""
        try:
            logger.info("Adding conversation turn to memory...")
            
            # Add messages to conversation memory
            self.conversation_memory.chat_memory.add_user_message(user_message)
            self.conversation_memory.chat_memory.add_ai_message(ai_response)
            
            # Store important information in vector store
            conversation_text = f"User: {user_message}\nAI: {ai_response}"
            self.vector_store.add_texts(
                texts=[conversation_text],
                metadatas=[{
                    "type": "conversation",
                    "timestamp": datetime.now().isoformat(),
                    "user": self.user_profile.get('name', 'unknown')
                }]
            )
            
            logger.info("Conversation turn added successfully")
            
        except Exception as e:
            logger.error(f"Error adding conversation turn: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def get_relevant_context(self, query: str) -> str:
        """Get relevant context from memory for the given query"""
        try:
            logger.info(f"Getting relevant context for query: {query}")
            
            # Get relevant documents from vector store
            docs = self.memory_retriever.get_relevant_documents(query)
            
            # Get conversation history
            chat_history = self.conversation_memory.chat_memory.messages
            
            # Combine context from both sources
            context = []
            
            # Add relevant documents
            if docs:
                context.append("Relevant past conversations:")
                for doc in docs:
                    context.append(f"- {doc.page_content}")
            
            # Add recent conversation history
            if chat_history:
                context.append("\nRecent conversation:")
                for msg in chat_history[-3:]:  # Last 3 messages
                    role = "User" if isinstance(msg, HumanMessage) else "AI"
                    context.append(f"{role}: {msg.content}")
            
            # Join all context with newlines
            return "\n".join(context) if context else ""
            
        except Exception as e:
            logger.error(f"Error getting relevant context: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return ""
    
    def cleanup(self):
        """Clean up resources"""
        try:
            logger.info("Cleaning up resources...")
            if hasattr(self, 'vector_store'):
                self.vector_store = None
                logger.info("Vector store cleaned up")
            if hasattr(self, 'embeddings'):
                self.embeddings = None
                logger.info("Embeddings cleaned up")
            gc.collect()
            logger.info("Garbage collection completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def get_memory_summary(self):
        """Get summary of current memory state"""
        try:
            logger.info("Getting memory summary...")
            summary = {
                "total_conversation_messages": len(self.conversation_memory.chat_memory.messages),
                "stored_important_memories": len(self.vector_store.get()['ids']),
                "buffer_summary_length": len(str(self.conversation_memory.buffer)),
                "user_profile": self.user_profile
            }
            logger.info(f"Memory summary: {summary}")
            return summary
        except Exception as e:
            logger.error(f"Error getting memory summary: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "error": str(e),
                "user_profile": self.user_profile
            }
    
    def clear_session_memory(self):
        """Clear session memory while preserving vector store"""
        try:
            logger.info("Clearing session memory...")
            self.conversation_memory.clear()
            gc.collect()
            logger.info("Session memory cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing session memory: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def export_memories(self):
        """Export memories for saving"""
        try:
            logger.info("Exporting memories...")
            memories = {
                "conversation_messages": [
                    {"type": msg.__class__.__name__, "content": msg.content}
                    for msg in self.conversation_memory.chat_memory.messages
                ],
                "vector_memories": self.vector_store.get()
            }
            logger.info(f"Exported {len(memories['conversation_messages'])} conversation messages")
            return memories
        except Exception as e:
            logger.error(f"Error exporting memories: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {} 
