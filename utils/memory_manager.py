from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.memory import ConversationBufferMemory
import os
import gc

class FitnessMemoryManager:
    def __init__(self, client, user_profile):
        """Initialize memory manager with optimized settings"""
        print("Initializing FitnessMemoryManager...")
        self.client = client
        self.user_profile = user_profile
        
        # Create cache directories if they don't exist
        os.makedirs("/tmp/model_cache", exist_ok=True)
        os.makedirs("/tmp/chroma_db", exist_ok=True)
        
        # Force garbage collection before loading model
        gc.collect()
        
        try:
            # Use a lighter model and optimize memory usage
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True},
                cache_folder="/tmp/model_cache"  # Use temporary storage
            )
            
            # Initialize vector store with optimized settings
            self.vector_store = Chroma(
                collection_name="fitness_memories",
                embedding_function=self.embeddings,
                persist_directory="/tmp/chroma_db"  # Use temporary storage
            )
            
            # Initialize conversation memory with smaller buffer
            self.conversation_memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                max_token_limit=1000  # Limit memory size
            )
            
            # Initialize memory retriever with optimized settings
            self.memory_retriever = self.vector_store.as_retriever(
                search_kwargs={"k": 3}  # Limit number of retrieved memories
            )
            
            print("Memory manager initialized successfully")
            
        except Exception as e:
            print(f"Error initializing memory manager: {str(e)}")
            # Clean up on error
            self.cleanup()
            raise
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if hasattr(self, 'vector_store'):
                self.vector_store = None
            if hasattr(self, 'embeddings'):
                self.embeddings = None
            gc.collect()
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
    
    def get_memory_summary(self):
        """Get summary of current memory state"""
        try:
            return {
                "total_conversation_messages": len(self.conversation_memory.chat_memory.messages),
                "stored_important_memories": len(self.vector_store.get()['ids']),
                "buffer_summary_length": len(str(self.conversation_memory.buffer)),
                "user_profile": self.user_profile
            }
        except Exception as e:
            print(f"Error getting memory summary: {str(e)}")
            return {
                "error": str(e),
                "user_profile": self.user_profile
            }
    
    def clear_session_memory(self):
        """Clear session memory while preserving vector store"""
        try:
            self.conversation_memory.clear()
            gc.collect()
        except Exception as e:
            print(f"Error clearing session memory: {str(e)}")
    
    def export_memories(self):
        """Export memories for saving"""
        try:
            return {
                "conversation_messages": [
                    {"type": msg.__class__.__name__, "content": msg.content}
                    for msg in self.conversation_memory.chat_memory.messages
                ],
                "vector_memories": self.vector_store.get()
            }
        except Exception as e:
            print(f"Error exporting memories: {str(e)}")
            return {} 
