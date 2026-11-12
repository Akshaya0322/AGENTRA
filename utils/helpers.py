import uuid

def generate_session_id() -> str:
    """Return a new UUID string for isolating a user session."""
    return str(uuid.uuid4())

def clean_text(text: str) -> str:
    """Basic text cleaning – strip, collapse multiple newlines, and ensure UTF‑8 safety."""
    import re
    cleaned = text.strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = re.sub(r"(\n\s*){2,}", "\n\n", cleaned)
    return cleaned

def validate_pdf(file_path: str) -> bool:
    """Check that a file exists, is a PDF, and is not empty.
    Returns True if the file passes validation, False otherwise.
    """
    import os
    if not os.path.isfile(file_path):
        return False
    if not file_path.lower().endswith('.pdf'):
        return False
    if os.path.getsize(file_path) == 0:
        return False
    return True
