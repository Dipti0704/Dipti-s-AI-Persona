from backend.app.knowledge.search import get_vector_store

store = get_vector_store()

def search_knowledge_base(query: str, limit: int = 3) -> str:
    """
    Search the candidate knowledge base (resume and project repositories) for matching details.
    """
    try:
        results = store.search(query, limit=limit)
        if not results:
            return "No matching information found in Dipti's knowledge base."
            
        formatted_chunks = []
        for r in results:
            src = r["metadata"].get("source", "unknown")
            title = r["metadata"].get("title", "Document Section")
            content = r["content"]
            formatted_chunks.append(f"--- SOURCE: {src} | SECTION: {title} ---\n{content}\n")
            
        return "\n".join(formatted_chunks)
    except Exception as e:
        return f"Error executing RAG search: {e}"
