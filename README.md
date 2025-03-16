# Chat with Your Document Engine

The **Chat with Your Document Engine** is a powerful question-answering chatbot that allows you to interact with your PDF documents using natural language. Built with **FastAPI**, **Streamlit**, **LangChain**, and **Google's Gemini model**, this system leverages advanced retrieval-augmented generation (RAG) techniques to provide accurate and context-aware answers.

---

## Features

- **Document Upload**: Upload multiple PDFs and embed them into a vector database for efficient retrieval.
- **Hybrid Search**: Combines keyword-based (BM25) and semantic search for optimal document retrieval.
- **Reranking**: Uses a transformer-based reranker to prioritize the most relevant documents.
- **Chat Interface**: A user-friendly Streamlit interface for interacting with the chatbot.
- **Chat History**: Stores and retrieves chat history for each user and session.
- **Metadata Extraction**: Extracts metadata from queries and documents to enhance retrieval.
- **Advanced Prompting**: Uses advanced prompts to improve query rewriting and answer generation.

---

## System Architecture

The system consists of two main components:

1. **Backend (FastAPI)**:
   - Handles document upload, embedding, and retrieval.
   - Manages chat history and user interactions.
   - Integrates with Google's Gemini model for answer generation.

2. **Frontend (Streamlit)**:
   - Provides a user-friendly interface for uploading documents and chatting.
   - Displays chat history and bot responses in real-time.

---

## Implementation


### Prerequisites

- Python 3.9 or 3.10
- Docker (optional, for containerized deployment)



### Installation

1. **Clone the Repository:**

        ```bash
        git clone https://github.com/your-repo/chat-with-your-document.git
        cd chat-with-your-document

2. **Create a Virtual Environment:**

        ```bash
        python3.9 -m venv venv
        source venv/bin/activate  # On Windows: venv\Scripts\activate

3.  **Install Dependencies:**

        ```bash
        pip install -r requirements.txt

4.  **Set Up Environment Variables:**
    Create a .env file in the root directory and add the following variables:

        ```bash
        GOOGLE_API_KEY=your_google_api_key
        MONGO_URI=your_mongo_uri
    Replace your_google_api_key with your Google API key and your_mongo_uri with your MongoDB connection string.

---

**Running the System**
1.  Backend (FastAPI)
    -Start the FastAPI Server:

        ```bash
        uvicorn app:app --reload
    The backend will be available at http://localhost:8000.

2.  Frontend (Streamlit)
    - Start the Streamlit App:

        ```bash
        streamlit run streamlit_app.py
    The frontend will be available at http://localhost:8501.

3. Docker Deployment
    - Build the Docker Image:

        ```bash
        docker build -t qa-chatbot .
    
    - Run the Docker Container:
   
        ```bash
        docker run -e GOOGLE_API_KEY="your_google_api_key" -e MONGO_URI="your_mongo_uri" -p 8000:8000 qa-chatbot

**Access the Application:**

- Backend: http://localhost:8000

- Frontend: http://localhost:8501

---

**Usage**
1. **Register a User:**

    Enter a username and click "Register" to create a new account.

2. **Upload PDFs:**

    Use the "Upload PDFs" section to upload one or more PDF documents.

3. **Start Chatting:**

    Enter your question in the chat input box and press Enter.

    The chatbot will generate a response based on the uploaded documents.

4. **View Chat History:**

    The sidebar displays all your chats. Click on a chat to view its history.

---

**Code Structure:**
- *app.py:* FastAPI backend for document processing and chat management.

- *streamlit_app.py:* Streamlit frontend for user interaction.

- *config.py:* Configuration settings for the application.

- *retrieval.py:* Implements hybrid search, reranking, and metadata extraction.

- *models.py:* Integrates with Google's Gemini model.

- *utils.py:* Utility functions for document processing and MongoDB operations.

- *prompts.py:* Advanced prompting strategies for query rewriting and answer generation.

- *requirements.txt:* Lists all Python dependencies.

- *Dockerfile:* Docker configuration for containerized deployment.

---

**Contributing:**
*Contributions are welcome! Please follow these steps:*

- Fork the repository.

- Create a new branch for your feature or bugfix.

- Submit a pull request with a detailed description of your changes.

---

**License:**
This project is licensed under the MIT License. See the LICENSE file for details.

**Support:**
For any questions or issues, please open an issue on the GitHub repository.

*Enjoy chatting with your documents! 🚀*