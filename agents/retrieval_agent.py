import os
from typing import List, Dict, Any
from rag.vector_store import get_vector_store
from rag.embeddings import get_embedding_model

class RetrievalAgent:
    """Agent responsible for retrieving relevant chunks for a query."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.vector_store = get_vector_store(session_id)
        self.embedder = get_embedding_model()

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Return top_k most similar chunks with metadata.

        Each result includes ``text`` and stored metadata (document name, page).
        """
        query_emb = self.embedder.embed_query(query)
        results = self.vector_store.query(
            query_embeddings=[query_emb],
            n_results=top_k,
            include=['documents', 'metadatas', 'distances']
        )
        # Chroma returns lists of lists; flatten one result set.
        retrieved = []
        for doc, meta, dist in zip(results['documents'][0], results['metadatas'][0], results['distances'][0]):
            entry = {
                'text': doc,
                'metadata': meta,
                'distance': dist,
            }
            retrieved.append(entry)
        return retrieved
