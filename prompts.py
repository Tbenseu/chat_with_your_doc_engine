from typing import List, Dict

class AdvancedPrompts:
    @staticmethod
    def retrieval_prompt(query: str) -> str:
        """Advanced prompt for retrieval."""
        return f"""
        You are an expert retrieval system. Rewrite the following query to improve retrieval:
        Original Query: {query}
        Rewritten Query:
        """

    @staticmethod
    def metadata_filter_prompt(query: str, metadata: Dict[str, str]) -> str:
        """Advanced prompt for metadata filtering."""
        return f"""
        You are an expert retrieval system. Add metadata to the query for better filtering:
        Original Query: {query}
        Metadata: {metadata}
        Enhanced Query:
        """

    @staticmethod
    def generation_prompt(context: str, question: str) -> str:
        """Advanced prompt for generation."""
        return f"""
        You are an expert in talent management and career development. Use the following context to answer the question.
        Context: {context}
        ---
        Question: {question}
        Answer in markdown with sources. If unsure, say "I don't know".
        """

    @staticmethod
    def can_answer_from_history_prompt(query: str, chat_history: List[Dict[str, str]]) -> str:
        """Prompt to check if the query can be answered from chat history."""
        return f"""
        Can the following query be answered using the provided chat history? Answer with "yes" or "no".
        Query: {query}
        Chat History:
        {chat_history}
        Answer:
        """

    @staticmethod
    def enhance_query_with_history_prompt(query: str, chat_history: List[Dict[str, str]]) -> str:
        """Prompt to enhance the query using chat history."""
        return f"""
        Rewrite the following query to include relevant context from the chat history only if necessary:
        Query: {query}
        Chat History:
        {chat_history}
        Enhanced Query:
        """

    @staticmethod
    def answer_from_history_prompt(chat_history: List[Dict[str, str]], question: str) -> str:
        """Prompt to generate an answer from chat history."""
        return f"""
        You are an expert in talent management and career development. Use the following chat history to answer the question.
        Chat History:
        {chat_history}
        ---
        Question: {question}
        Answer in markdown with sources. If unsure, say "I don't know".
        """