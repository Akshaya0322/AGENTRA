import os
import uuid
from pathlib import Path
from typing import List, Dict, Any

import PyPDF2

from rag.text_chunker import chunk_text
from rag.embeddings import get_embedding_model
from rag.vector_store import get_vector_store


class DocumentProcessingAgent:
    """Agent that processes uploaded PDFs into text chunks and stores them.

    It extracts text per page, adds metadata, chunks the text, and inserts
    embeddings into the vector store.
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.vector_store = get_vector_store(session_id)
        self.embedder = get_embedding_model()

    def process_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract, chunk, embed and store a PDF.

        Returns a list of stored chunk metadata dictionaries.
        """
        pdf_reader = PyPDF2.PdfReader(file_path)
        doc_name = Path(file_path).name
        all_chunks = []
        for page_num, page in enumerate(pdf_reader.pages, start=1):
            try:
                text = page.extract_text() or ""
            except Exception:
                text = ""
            if not text.strip():
                continue
            chunks = chunk_text(text)
            for i, chunk in enumerate(chunks):
                chunk_id = f"{uuid.uuid4()}"
                metadata = {
                    "document_id": self.session_id,
                    "document_name": doc_name,
                    "page_number": page_num,
                    "chunk_id": chunk_id,
                    "text": chunk,
                }
                embedding = self.embedder.embed_query(chunk)
                self.vector_store.add(
    ids=[chunk_id],
    documents=[chunk],
    metadatas=[metadata],
    embeddings=[embedding],
)
                all_chunks.append(metadata)
        return all_chunks
