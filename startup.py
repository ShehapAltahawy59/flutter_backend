import os
import logging
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
import tempfile
import gc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_models():
    """Initialize all models and dependencies at server startup"""
    try:
        logger.info("Starting model initialization...")
        
        # Create cache directories
        temp_dir = tempfile.gettempdir()
        model_cache_dir = os.path.join(temp_dir, "fitness_model_cache")
        chroma_db_dir = os.path.join(temp_dir, "fitness_chroma_db")
        
        os.makedirs(model_cache_dir, exist_ok=True)
        os.makedirs(chroma_db_dir, exist_ok=True)
        
        logger.info(f"Cache directories created at: {temp_dir}")
        
        # Initialize HuggingFace embeddings
        logger.info("Loading HuggingFace embeddings...")
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True},
            cache_folder=model_cache_dir
        )
        logger.info("HuggingFace embeddings loaded successfully")
        
        # Initialize Chroma vector store
        logger.info("Initializing Chroma vector store...")
        vector_store = Chroma(
            collection_name="fitness_memories",
            embedding_function=embeddings,
            persist_directory=chroma_db_dir
        )
        logger.info("Chroma vector store initialized successfully")
        
        # Force garbage collection
        gc.collect()
        
        logger.info("All models initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error during model initialization: {str(e)}")
        return False

def on_starting(server):
    """Gunicorn hook for server startup"""
    logger.info("Server starting, initializing models...")
    if initialize_models():
        logger.info("Server startup complete")
    else:
        logger.error("Server startup failed")
        sys.exit(1) 
