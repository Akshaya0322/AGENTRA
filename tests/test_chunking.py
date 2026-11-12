import unittest
from rag.text_chunker import chunk_text

class TestChunking(unittest.TestCase):
    def test_chunk_basic(self):
        text = "This is a sample sentence. " * 100  # ~2400 chars
        chunks = chunk_text(text)
        # Ensure we get more than one chunk when text > CHUNK_SIZE (default 1000)
        self.assertTrue(len(chunks) >= 2)
        # Ensure each chunk length <= CHUNK_SIZE + overlap
        from config.settings import CHUNK_SIZE
        for c in chunks:
            self.assertLessEqual(len(c), CHUNK_SIZE + 200)  # overlap default 200

if __name__ == "__main__":
    unittest.main()
