import os
import tempfile
import unittest
from uuid import uuid4

from agents.document_agent import DocumentProcessingAgent
from agents.retrieval_agent import RetrievalAgent

class TestRetrieval(unittest.TestCase):
    def setUp(self):
        # temporary directory for uploads
        self.tmpdir = tempfile.mkdtemp()
        self.session_id = str(uuid4())
        # create a simple PDF with known text
        from reportlab.pdfgen import canvas
        self.pdf_path = os.path.join(self.tmpdir, "sample.pdf")
        c = canvas.Canvas(self.pdf_path)
        c.drawString(100, 750, "The quick brown fox jumps over the lazy dog.")
        c.save()
        # Process the PDF to populate Chroma
        doc_agent = DocumentProcessingAgent(self.session_id)
        doc_agent.process_pdf(self.pdf_path)

    def test_retrieval(self):
        retrieval = RetrievalAgent(self.session_id)
        results = retrieval.retrieve("fox jumps", top_k=3)
        self.assertTrue(len(results) > 0)
        # Check that returned metadata contains our document name
        any_doc = any('sample.pdf' in meta['metadata'].get('document_name', '') for meta in results)
        self.assertTrue(any_doc)

    def tearDown(self):
        # cleanup temp files and folder
        try:
            os.remove(self.pdf_path)
            os.rmdir(self.tmpdir)
        except Exception:
            pass

if __name__ == "__main__":
    unittest.main()
