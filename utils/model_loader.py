from langchain.embeddings import HuggingFaceEmbeddings
import logging
from config import LOGGING

# Configure logging
logging.basicConfig(
    level=LOGGING['level'],
    format=LOGGING['format'],
    filename=LOGGING['file']
)
logger = logging.getLogger(__name__)

class ModelLoader:
    _instance = None
    _embeddings = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def initialize_models(self):
        """Initialize and pre-download all required models"""
        try:
            logger.info("Starting model initialization...")
            
            # Initialize embeddings
            logger.info("Initializing HuggingFace embeddings...")
            self._embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            
            logger.info("Model initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during model initialization: {str(e)}")
            return False

    def get_embeddings(self):
        """Get the initialized embeddings model"""
        if self._embeddings is None:
            self.initialize_models()
        return self._embeddings 
