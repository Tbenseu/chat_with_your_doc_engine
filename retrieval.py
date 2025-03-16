from typing import List, Dict
from langchain.schema import Document
from sklearn.cluster import KMeans
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from rank_bm25 import BM25Okapi
from config_file import Configuration
from utils import logger
from models import GeminiModel
import json
from collections import Counter

class HierarchicalIndex:
    def __init__(self, documents: List[Document], embedding_model):
        self.documents = documents
        self.embedding_model = embedding_model
        self.index = self._build_index()

    def _build_index(self):
        """Build a hierarchical index using embeddings."""
        embeddings = self.embedding_model.embed_documents([doc.page_content for doc in self.documents])
        self.index = self._cluster_documents(embeddings)
        return self.index

    def _cluster_documents(self, embeddings, n_clusters=10):
        """Cluster documents into hierarchical groups."""
        kmeans = KMeans(n_clusters=n_clusters)
        clusters = kmeans.fit_predict(embeddings)
        return {i: [] for i in range(n_clusters)}

    def retrieve(self, query: str, top_k: int = Configuration.TOP_K) -> List[Document]:
        """Retrieve documents from the hierarchical index."""
        query_embedding = self.embedding_model.embed_query(query)
        # For simplicity, return top-k documents (can be enhanced with hierarchical search)
        return self.documents[:top_k]

class MetadataExtractor:
    @staticmethod
    def extract_from_query(query: str) -> Dict[str, str]:
        """Extract metadata from the query using an LLM."""
        prompt = f"""
        Extract metadata from the following query. Return the result as a JSON object with keys like "year", "topic", "location", etc.
        Query: {query}
        Metadata (JSON):
        """
        llm = GeminiModel().llm
        response = llm.invoke(prompt).content
        try:
            metadata = json.loads(response)
            return metadata
        except Exception as e:
            logger.error(f"Error parsing metadata: {e}")
            return {}

class MetadataInferrer:
    @staticmethod
    def infer_from_documents(documents: List[Document]) -> Dict[str, str]:
        """Infer metadata from the document set."""
        metadata = {}
        
        # Example: Infer the most recent year
        years = [doc.metadata.get("year") for doc in documents if "year" in doc.metadata]
        if years:
            metadata["year"] = max(years)
        
        # Example: Infer the most common topic
        topics = [doc.metadata.get("topic") for doc in documents if "topic" in doc.metadata]
        if topics:
            metadata["topic"] = Counter(topics).most_common(1)[0][0]
        
        return metadata

def combine_metadata(query_metadata: Dict[str, str], document_metadata: Dict[str, str]) -> Dict[str, str]:
    """Combine metadata from the query and documents."""
    combined = {}
    combined.update(document_metadata)  # Start with document metadata
    combined.update(query_metadata)    # Override with query metadata (if any)
    return combined

class HybridRetriever:
    def __init__(self, vector_store, bm25_retriever):
        self.vector_store = vector_store
        self.bm25_retriever = bm25_retriever

    def retrieve(self, query: str, top_k: int = Configuration.TOP_K) -> List[Document]:
        # Semantic Search
        vector_results = self.vector_store.similarity_search(query, k=top_k)
        # Keyword Search
        bm25_docs = self.bm25_retriever.get_relevant_documents(query)
        # Combine and deduplicate
        combined = vector_results + bm25_docs
        seen = set()
        return [doc for doc in combined if not (doc.page_content in seen or seen.add(doc.page_content))]

class Reranker:
    def __init__(self, model_name=Configuration.RERANKER_MODEL):
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            logger.info(f"Loaded reranking model: {model_name}")
        except Exception as e:
            logger.error(f"Error loading reranking model: {e}")
            raise

    def rerank(self, query: str, documents: List[Document], top_n: int = Configuration.TOP_N) -> List[Document]:
        try:
            pairs = [(query, doc.page_content) for doc in documents]
            features = self.tokenizer(pairs, padding=True, truncation=True, return_tensors="pt")
            scores = self.model(**features).logits
            sorted_indices = scores.argsort(descending=True)
            return [documents[i] for i in sorted_indices[:top_n]]
        except Exception as e:
            logger.error(f"Error during reranking: {e}")
            return documents[:top_n]  # Fallback to top N documents