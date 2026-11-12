import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)

# Gemini API configuration
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

# RAG configuration defaults
CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 1000))  # characters per chunk
CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 200))
EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

# Chroma collection name (per session we will use a unique name, but default here)
CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "agentra_collection")

# Vector store directory (persisted locally)
CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", str(BASE_DIR / "data"))

# Gemini model to use (configurable via env)
GEMINI_MODEL_NAME: str = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
