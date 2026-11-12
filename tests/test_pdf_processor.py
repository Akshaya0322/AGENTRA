import os
import tempfile
import unittest
from rag.pdf_processor import extract_text_per_page
from reportlab.pdfgen import canvas

class TestPDFProcessor(unittest.TestCase):
    def setUp(self):
        # create a temporary PDF file
        self.tmpdir = tempfile.mkdtemp()
        self.pdf_path = os.path.join(self.tmpdir, "test.pdf")
        c = canvas.Canvas(self.pdf_path)
        c.drawString(100, 750, "Hello World")
        c.showPage()
        c.drawString(100, 750, "Second page text")
        c.save()

    def test_extract_text(self):
        pages = extract_text_per_page(self.pdf_path)
        self.assertTrue(len(pages) >= 2)
        # Ensure each page has non‑empty text
        for page_num, text in pages:
            self.assertIsInstance(page_num, int)
            self.assertTrue(text.strip())

    def tearDown(self):
        # cleanup temporary files
        try:
            os.remove(self.pdf_path)
            os.rmdir(self.tmpdir)
        except Exception:
            pass

if __name__ == "__main__":
    unittest.main()
