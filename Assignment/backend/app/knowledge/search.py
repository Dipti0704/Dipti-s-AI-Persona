import numpy as np
import re
from typing import List, Dict, Any
from backend.app.core.vector_store import BaseVectorStore
from backend.app.knowledge.documents import get_all_chunks
from backend.app.config import settings
from openai import OpenAI

class LocalInMemoryStore(BaseVectorStore):
    """
    Highly robust, 100% offline, local search implementation (Open-Closed Principle).
    Uses token overlap and keyword frequency analysis for high precision without API costs.
    """
    def __init__(self):
        self.documents = []
        # Populate with local chunks initially
        self.add_documents(get_all_chunks())
        
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        self.documents.extend(documents)
        
    def _tokenize(self, text: str) -> set:
        # Convert to lowercase and find words
        return set(re.findall(r'\w+', text.lower()))
        
    def search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return self.documents[:limit]
            
        scored_docs = []
        for doc in self.documents:
            doc_tokens = self._tokenize(doc["content"])
            
            # Simple Jaccard similarity / token overlap with weighted metadata boosts
            overlap = query_tokens.intersection(doc_tokens)
            score = len(overlap) / len(query_tokens.union(doc_tokens)) if doc_tokens else 0.0
            
            # Boost score based on title/metadata matching
            title = doc["metadata"].get("title", "").lower()
            topic = doc["metadata"].get("topic", "").lower()
            
            for token in query_tokens:
                if token in title:
                    score += 0.15
                if token == topic:
                    score += 0.25  # Big boost for direct project/topic match
                    
            scored_docs.append((score, doc))
            
        # Sort by score descending
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        # Format output
        results = []
        for score, doc in scored_docs[:limit]:
            results.append({
                "id": doc["id"],
                "content": doc["content"],
                "metadata": doc["metadata"],
                "score": round(score, 4)
            })
            
        return results

class OpenAIEmbeddingsStore(BaseVectorStore):
    """
    Cloud-connected RAG store (Open-Closed Principle).
    Computes real OpenAI embeddings (text-embedding-3-small) and ranks via local cosine similarity.
    Falls back to LocalInMemoryStore automatically if credentials fail.
    """
    def __init__(self):
        self.local_store = LocalInMemoryStore()
        self.documents = []
        self.embeddings = []
        self.client = None
        
        if settings.OPENAI_API_KEY:
            try:
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
                self.documents = get_all_chunks()
                self._compute_embeddings()
            except Exception as e:
                print(f"Error initializing OpenAI client: {e}. Falling back to LocalInMemoryStore.")
                self.client = None
                
    def _compute_embeddings(self):
        if not self.client:
            return
            
        texts = [doc["content"] for doc in self.documents]
        try:
            # Batch embedding computation
            response = self.client.embeddings.create(
                input=texts,
                model="text-embedding-3-small"
            )
            self.embeddings = [item.embedding for item in response.data]
        except Exception as e:
            print(f"Failed to generate embeddings: {e}. Switching to offline search.")
            self.client = None
            
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        self.local_store.add_documents(documents)
        if self.client:
            self.documents.extend(documents)
            # Recompute
            self._compute_embeddings()
            
    def _cosine_similarity(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        
    def search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        # Fallback to local offline store if OpenAI is unavailable
        if not self.client or not self.embeddings:
            return self.local_store.search(query, limit)
            
        try:
            # Embed query
            response = self.client.embeddings.create(
                input=[query],
                model="text-embedding-3-small"
            )
            query_emb = response.data[0].embedding
            
            scored_docs = []
            for i, doc in enumerate(self.documents):
                score = self._cosine_similarity(query_emb, self.embeddings[i])
                
                # Apply small exact matching metadata boosts
                topic = doc["metadata"].get("topic", "").lower()
                if topic in query.lower():
                    score += 0.05
                    
                scored_docs.append((score, doc))
                
            scored_docs.sort(key=lambda x: x[0], reverse=True)
            
            results = []
            for score, doc in scored_docs[:limit]:
                results.append({
                    "id": doc["id"],
                    "content": doc["content"],
                    "metadata": doc["metadata"],
                    "score": round(float(score), 4)
                })
            return results
            
        except Exception as e:
            print(f"Error during OpenAI search: {e}. Falling back to offline search.")
            return self.local_store.search(query, limit)

# Export active vector store based on config availability
def get_vector_store() -> BaseVectorStore:
    if settings.OPENAI_API_KEY:
        return OpenAIEmbeddingsStore()
    return LocalInMemoryStore()
