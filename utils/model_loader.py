from langchain.embeddings import HuggingFaceEmbeddings
import logging
from config import LOGGING
import os
from pathlib import Path
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import huggingface_hub

# Configure logging
logging.basicConfig(
    level=LOGGING['level'],
    format=LOGGING['format'],
    filename=LOGGING['file']
)
logger = logging.getLogger(__name__)

class ModelLoader:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not ModelLoader._initialized:
            self._initialize()
            ModelLoader._initialized = True
    
    def _initialize(self):
        """Initialize the model loader and pre-download required models"""
        try:
            logger.info("Initializing ModelLoader...")
            
            # Set up ChromaDB client
            self.chroma_client = chromadb.Client(Settings(
                persist_directory="chroma_db",
                anonymized_telemetry=False
            ))
            
            # Pre-download the embedding model
            logger.info("Pre-downloading ChromaDB embedding model...")
            self._pre_download_embedding_model()
            
            logger.info("ModelLoader initialization complete")
            
        except Exception as e:
            logger.error(f"Error initializing ModelLoader: {str(e)}")
            raise
    
    def _pre_download_embedding_model(self):
        """Pre-download only the essential model files"""
        try:
            # The model used by ChromaDB's default embedding function
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            
            # Create cache directory if it doesn't exist
            cache_dir = Path.home() / ".cache" / "chroma" / "onnx_models" / "all-MiniLM-L6-v2"
            cache_dir.mkdir(parents=True, exist_ok=True)
            
            # Only download essential files
            logger.info(f"Downloading essential model files for {model_name}")
            huggingface_hub.snapshot_download(
                repo_id=model_name,
                cache_dir=cache_dir,
                local_files_only=False,
                resume_download=True,
                allow_patterns=[
                    "config.json",
                    "tokenizer.json",
                    "tokenizer_config.json",
                    "special_tokens_map.json",
                    "vocab.txt",
                    "model.safetensors"  # Only download the main model file
                ]
            )
            
            logger.info("Essential model files download complete")
            
        except Exception as e:
            logger.error(f"Error pre-downloading embedding model: {str(e)}")
            raise
    
    def get_chroma_client(self):
        """Get the ChromaDB client instance"""
        return self.chroma_client
    
    def get_embedding_function(self):
        """Get the default embedding function"""
        return embedding_functions.SentenceTransformerEmbeddingFunction()

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
