import os
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from config.settings import CHROMA_DB_PATH, CHROMA_COLLECTION_NAME

def get_vector_store(session_id: str):
    """Return a Chroma collection scoped to a session.

    Each session gets its own collection name to avoid mixing data across
    users. The underlying database directory is shared (``CHROMA_DB_PATH``).
    """
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection_name = f"{CHROMA_COLLECTION_NAME}_{session_id}"
    # If the collection exists we get it, otherwise we create a new one.
    try:
        collection = client.get_collection(name=collection_name)
    except Exception:
        collection = client.create_collection(name=collection_name)
    return collection
