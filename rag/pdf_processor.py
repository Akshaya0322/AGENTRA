import os
from pathlib import Path
import PyPDF2
from typing import List, Tuple

def extract_text_per_page(pdf_path: str) -> List[Tuple[int, str]]:
    """Extract raw text from each page of a PDF.

    Returns a list of ``(page_number, text)`` tuples. Empty pages are skipped.
    """
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    try:
        reader = PyPDF2.PdfReader(pdf_path)
    except Exception as e:
        raise ValueError(f"Failed to read PDF {pdf_path}: {e}")
    pages_text = []
    for i, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        if text.strip():
            pages_text.append((i, text))
    return pages_text
