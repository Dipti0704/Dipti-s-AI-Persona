from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseVectorStore(ABC):
    """
    Abstract Base Class for Vector Stores (Open-Closed Principle).
    Allows plugging in Pinecone, ChromaDB, or LocalInMemoryStore seamlessly.
    """
    
    @abstractmethod
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Embed and add a list of documents to the store.
        Each document should be a dict containing:
          - "id": unique identifier
          - "content": raw text content
          - "metadata": additional details (source, topic, etc.)
        """
        pass
        
    @abstractmethod
    def search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Search for most similar documents matching the query.
        Returns a list of matching documents with contents, metadata, and similarity score.
        """
        pass
