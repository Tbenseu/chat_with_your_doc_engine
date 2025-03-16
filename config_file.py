import os
from dotenv import load_dotenv
load_dotenv()

class Configuration:
    PDF_FOLDER_PATH = "/content/Rag_data"  # Folder containing PDFs
    CHROMA_PERSIST_DIR = "./chroma_db"  # Directory to persist Chroma vector store
    EMBEDDING_MODEL = "models/embedding-001"  # Gemini embedding model
    RERANKER_MODEL = "BAAI/bge-reranker-base"  # Reranking model
    GENERATION_MODEL = "gemini-2.0-flash"  # Gemini generation model
    TOP_K = 5  # Default number of documents to retrieve
    TOP_N = 3  # Default number of documents to rerank

    # # MongoDB configuration
    # MONGO_URI = os.getenv("MONGO_URI")
    # MONGO_DB = "chat_history_db"
    # MONGO_COLLECTION = "chats"
    
    # MongoDB configuration
    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DB = "chat_history"
    MONGO_COLLECTION = "history_store"