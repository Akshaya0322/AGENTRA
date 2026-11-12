
import os
import re
from typing import List, Dict, Any

from google import genai
from google.genai import types

from rag.vector_store import get_vector_store
from rag.embeddings import get_embedding_model
from config.settings import GEMINI_API_KEY, GEMINI_MODEL_NAME


class AnswerGenerationAgent:
    """Generates document-grounded answers using Gemini."""

    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY not set in environment. Please configure .env."
            )

        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model_name = GEMINI_MODEL_NAME
        self.embedder = get_embedding_model()
        self.vector_store = None

    def set_session(self, session_id: str):
        self.vector_store = get_vector_store(session_id)

    def _is_comprehensive_query(self, query: str) -> bool:
        """Identify requests that need complete document-wide retrieval."""

        patterns = [
            r"\ball\b",
            r"\bevery\b",
            r"\bcomplete\b",
            r"\bentire\b",
            r"\bfull list\b",
            r"\blist all\b",
            r"\blist every\b",
            r"\beach\b",
            r"\btotal number\b",
        ]

        query_lower = query.lower()
        return any(re.search(pattern, query_lower) for pattern in patterns)

    def _filter_documents(
        self,
        records: Dict[str, Any],
        query: str
    ) -> List[Dict[str, Any]]:
        """Convert Chroma records into chunk dictionaries."""

        documents = records.get("documents") or []
        metadatas = records.get("metadatas") or []

        chunks = []

        for doc, metadata in zip(documents, metadatas):
            if not doc or not metadata:
                continue

            chunks.append({
                "text": doc,
                "metadata": metadata,
                "distance": None
            })

        # Try to identify a specifically mentioned PDF.
        ignored_words = {
            "resume", "pdf", "document", "documents",
            "project", "projects", "internship", "internships",
            "certification", "certifications", "list", "all",
            "every", "complete", "entire", "full", "find",
            "show", "give", "what", "which", "mentioned",
            "uploaded", "only", "in", "the", "from"
        }

        query_words = {
            word for word in re.findall(r"[a-z0-9]+", query.lower())
            if len(word) >= 4 and word not in ignored_words
        }

        matching_chunks = [
            chunk for chunk in chunks
            if any(
                word in PathName(chunk["metadata"].get("document_name", ""))
                for word in query_words
            )
        ]

        # Filter only when a filename match is found.
        if matching_chunks:
            return matching_chunks

        return chunks

    def _retrieve_all_chunks(
        self,
        query: str
    ) -> List[Dict[str, Any]]:
        """Retrieve all stored chunks for comprehensive questions."""

        records = self.vector_store.get(
            include=["documents", "metadatas"]
        )

        return self._filter_documents(records, query)

    def _retrieve_relevant_chunks(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve semantically relevant chunks for normal questions."""

        query_embedding = self.embedder.embed_query(query)

        results = self.vector_store.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        retrieved = []

        if results.get("documents") and results["documents"][0]:
            for doc, metadata, distance in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            ):
                retrieved.append({
                    "text": doc,
                    "metadata": metadata,
                    "distance": distance
                })

        return retrieved

    def _build_prompt(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> str:

        if not retrieved_chunks:
            return (
                "No relevant document content was found. "
                "Respond exactly: I could not find the answer "
                "in the uploaded documents."
            )

        context_parts = []

        for chunk in retrieved_chunks:
            metadata = chunk["metadata"]

            document_name = metadata.get(
                "document_name", "Unknown document"
            )
            page_number = metadata.get(
                "page_number", "Unknown page"
            )

            context_parts.append(
                f"Source: {document_name} (Page {page_number})\n"
                f"Content:\n{chunk['text']}"
            )

        context_text = "\n\n---\n\n".join(context_parts)

        return f"""
You are AGENTRA, an AI document assistant.

STRICT INSTRUCTIONS:
1. Answer using ONLY the supplied document context.
2. Never invent information or use outside knowledge.
3. If information is unavailable, say:
   "I could not find the answer in the uploaded documents."
4. Include the source filename and page number.
5. If the user requests ALL, EVERY, or a COMPLETE list,
   carefully inspect every supplied chunk before answering.
6. Do not stop after finding the first matching item.
7. Do not confuse information belonging to different documents.
8. Do not repeat duplicate items.
9. If the question identifies a particular document, answer
   only from that document's content.
10. Clearly state if the supplied content does not establish
    that a list is complete.

DOCUMENT CONTEXT:
{context_text}

USER QUESTION:
{query}

ANSWER:
"""

    def answer(
        self,
        session_id: str,
        query: str,
        top_k: int = 5
    ) -> Dict[str, Any]:

        try:
            expected_name = (
                f"{os.getenv('CHROMA_COLLECTION_NAME', 'agentra_collection')}"
                f"_{session_id}"
            )

            if (
                self.vector_store is None
                or self.vector_store.name != expected_name
            ):
                self.set_session(session_id)

            if self._is_comprehensive_query(query):
                retrieved = self._retrieve_all_chunks(query)
            else:
                retrieved = self._retrieve_relevant_chunks(
                    query, top_k
                )

            if not retrieved:
                return {
                    "answer": (
                        "I could not find the answer "
                        "in the uploaded documents."
                    ),
                    "sources": []
                }

            prompt = self._build_prompt(query, retrieved)

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2
                )
            )

            answer_text = (
                response.text.strip()
                if response.text
                else "Gemini returned an empty response."
            )

            # Deduplicate source references by filename and page.
            unique_sources = {}
            for chunk in retrieved:
                metadata = chunk["metadata"]
                key = (
                    metadata.get("document_name"),
                    metadata.get("page_number")
                )
                unique_sources[key] = metadata

            return {
                "answer": answer_text,
                "sources": list(unique_sources.values())
            }

        except Exception as exc:
           error_message = str(exc)

           if (
              "429" in error_message
               or "RESOURCE_EXHAUSTED" in error_message
               or "quota" in error_message.lower()
            ):
            user_message = (
            "Gemini API daily quota exceeded. "
            "Your documents are still stored safely. "
            "Please try again after your API quota resets, "
            "or check your Gemini API usage and billing limits."
           )
           else:
            user_message = f"Error generating answer: {error_message}"
        return {
        "answer": user_message,
        "sources": []
    }


def PathName(filename: str) -> str:
    """Normalize a filename for matching against query words."""
    return re.sub(r"[^a-z0-9]", "", filename.lower())
