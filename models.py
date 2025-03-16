from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from config_file import Configuration

class GeminiModel:
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(model=Configuration.EMBEDDING_MODEL)
        self.llm = ChatGoogleGenerativeAI(model=Configuration.GENERATION_MODEL, temperature=0.3)