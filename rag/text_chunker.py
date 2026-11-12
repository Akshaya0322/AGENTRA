from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP

def chunk_text(text: str) -> list[str]:
    """Split a long string into overlapping chunks.

    Uses LangChain's RecursiveCharacterTextSplitter with configurable
    ``CHUNK_SIZE`` and ``CHUNK_OVERLAP`` (both in characters).
    Returns a list of chunk strings.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", " "],
    )
    return splitter.split_text(text)
