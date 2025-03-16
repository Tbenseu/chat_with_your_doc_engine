import os
import logging
from typing import List, Dict
from datetime import datetime
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure
from langchain_community.document_loaders import PyPDFLoader
# from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from concurrent.futures import ThreadPoolExecutor
from config_file import Configuration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


try:
    # MongoDB client
    print(f"MONGO URI >> {Configuration.MONGO_URI}")
    print(f"MONGO DB >> {Configuration.MONGO_DB}")
    print(f"MONGO Collections >> {Configuration.MONGO_COLLECTION}")
    client = MongoClient(Configuration.MONGO_URI, server_api=ServerApi('1'))
    client.admin.command('ping')  # Test connection
    db = client[Configuration.MONGO_DB]
    chats_collection = db[Configuration.MONGO_COLLECTION]
    print("MongoDB connection successful!")
except ConnectionFailure as e:
    print(f"Failed to connect to MongoDB: {e}")
    

def store_chat_history(userID: str, chatID: str, role: str, content: str):
    """Store a message in the chat history."""
    try:
        message = {
            "userID": userID,
            "chatID": chatID,
            "timestamp": datetime.now(),
            "role": role,
            "content": content
        }
        chats_collection.insert_one(message)
        logger.info(f"Stored message in chat history for user {userID}, chat {chatID}.")
    except Exception as e:
        logger.error(f"Error storing chat history: {e}")


def retrieve_chat_history(userID: str, chatID: str, limit: int = 5) -> List[Dict[str, str]]:
    """Retrieve the most recent messages from the chat history."""
    try:
        messages = chats_collection.find(
            {"userID": userID, "chatID": chatID},
            sort=[("timestamp", -1)],  # Sort by timestamp in descending order
            limit=limit
        )
        return [{"role": msg["role"], "content": msg["content"]} for msg in messages]
    except Exception as e:
        logger.error(f"Error retrieving chat history: {e}")
        return []

def load_and_chunk_pdf(file_path: str) -> List[Document]:
    """Load and split a single PDF document."""
    try:
        loader = PyPDFLoader(file_path)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        return loader.load_and_split(text_splitter)
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return []

def load_and_chunk_folder(folder_path: str) -> List[Document]:
    """Load and chunk all PDFs in a folder."""
    if not os.path.isdir(folder_path):
        raise ValueError(f"{folder_path} is not a valid directory.")

    pdf_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".pdf")]
    if not pdf_files:
        logger.warning(f"No PDF files found in {folder_path}.")
        return []

    all_docs = []
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(load_and_chunk_pdf, pdf_file) for pdf_file in pdf_files]
        for future in futures:
            try:
                docs = future.result()
                all_docs.extend(docs)
            except Exception as e:
                logger.error(f"Error processing PDF: {e}")

    logger.info(f"Loaded and chunked {len(all_docs)} documents from {len(pdf_files)} PDFs.")
    return all_docs