from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import uuid
from dotenv import load_dotenv
from config_file import Configuration
from utils import load_and_chunk_folder, store_chat_history, retrieve_chat_history
from retrieval import HybridRetriever, Reranker, MetadataExtractor, MetadataInferrer, combine_metadata
from models import GeminiModel
from prompts import AdvancedPrompts
import shutil
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever


import logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Pydantic models for request/response
class UserRegistration(BaseModel):
    username: str

class QueryInput(BaseModel):
    userID: str
    chatID: str
    question: str
    top_k: Optional[int] = Configuration.TOP_K

class QueryOutput(BaseModel):
    answer: str
    sources: List[str]

# Initialize components
gemini = GeminiModel()
vectorstore = None  # Will be initialized after PDF upload
docs = []  # Global variable to store loaded and chunked documents

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}

# User registration endpoint
@app.post("/register")
def register_user(user: UserRegistration):
    userID = str(uuid.uuid4())
    return {"userID": userID, "username": user.username}

# Upload and embed PDFs endpoint
@app.post("/upload")
async def upload_and_embed(files: List[UploadFile] = File(...)):
    try:
        # Save uploaded files to a temporary folder
        temp_folder = "temp_pdfs"
        os.makedirs(temp_folder, exist_ok=True)
        for file in files:
            file_path = os.path.join(temp_folder, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        # Load and chunk PDFs
        global docs
        docs = load_and_chunk_folder(temp_folder)

        # Initialize vector store with the uploaded documents
        global vectorstore
        vectorstore = Chroma.from_documents(docs, gemini.embeddings, persist_directory=Configuration.CHROMA_PERSIST_DIR)

        # Clean up temporary folder
        shutil.rmtree(temp_folder)

        return {"message": f"Uploaded and embedded {len(docs)} documents."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chat endpoint
@app.post("/chat", response_model=QueryOutput)
async def chat(query: QueryInput):
    try:
        if vectorstore is None:
            raise HTTPException(status_code=400, detail="No documents uploaded yet. Please upload PDFs first.")

        # Retrieve chat history
        # chat_history = retrieve_chat_history(query.userID, query.chatID)
        try:
            chat_history = retrieve_chat_history(query.userID, query.chatID)
        except Exception as e:
            logger.error(f"Error retrieving chat history: {e}")
            chat_history = []

        # Check if the query can be answered from chat history
        if AdvancedPrompts.can_answer_from_history_prompt(query.question, chat_history)=="yes":
            prompt = AdvancedPrompts.answer_from_history_prompt(chat_history, query.question)
            response = gemini.llm.invoke(prompt).content
            return QueryOutput(answer=response, sources=["chat_history"])

        # Enhance query with chat history
        enhanced_query = AdvancedPrompts.enhance_query_with_history_prompt(query.question, chat_history)

        # Extract metadata
        query_metadata = MetadataExtractor.extract_from_query(enhanced_query)
        document_metadata = MetadataInferrer.infer_from_documents(docs)
        combined_metadata = combine_metadata(query_metadata, document_metadata)

        # Rewrite query with metadata
        rewritten_query = gemini.llm.invoke(AdvancedPrompts.retrieval_prompt(enhanced_query)).content
        enhanced_query_with_metadata = gemini.llm.invoke(AdvancedPrompts.metadata_filter_prompt(rewritten_query, combined_metadata)).content

        # Retrieve and rerank documents
        bm25_retriever = BM25Retriever.from_documents(docs)
        hybrid_retriever = HybridRetriever(vectorstore, bm25_retriever)
        reranker = Reranker()
        retrieved_docs = hybrid_retriever.retrieve(enhanced_query_with_metadata, top_k=query.top_k)
        reranked_docs = reranker.rerank(enhanced_query_with_metadata, retrieved_docs)

        # Generate answer
        context = "\n\n".join([doc.page_content for doc in reranked_docs])
        prompt = AdvancedPrompts.generation_prompt(context, query.question)
        response = gemini.llm.invoke(prompt).content

        # Store chat history
        store_chat_history(query.userID, query.chatID, "user", query.question)
        store_chat_history(query.userID, query.chatID, "assistant", response)

        return QueryOutput(answer=response, sources=[doc.metadata.get("source", "unknown") for doc in reranked_docs])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)