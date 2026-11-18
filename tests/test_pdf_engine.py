"""
Tests for PDF Engine operations: merge, split, rotate, delete, duplicate, info, metadata.
"""
import unittest
import os
import tempfile
from pathlib import Path
from reportlab.pdfgen import canvas
import pikepdf

from core.pdf_engine import PDFEngine
from core.models import CompressionLevel

class TestPDFEngine(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.d = Path(self.temp_dir.name)
        
        # Create a sample 3-page PDF
        self.sample_pdf = str(self.d / "sample.pdf")
        c = canvas.Canvas(self.sample_pdf, pagesize=(595.28, 841.89))
        for i in range(3):
            c.drawString(100, 750, f"Page {i + 1} Content")
            c.showPage()
        c.save()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_document_info(self):
        info = PDFEngine.get_document_info(self.sample_pdf)
        self.assertEqual(info.page_count, 3)
        self.assertFalse(info.is_encrypted)
        self.assertTrue(info.file_size_bytes > 0)
        self.assertIn("A4", info.page_dimensions)

    def test_merge_pdfs(self):
        # Create second pdf
        second_pdf = str(self.d / "second.pdf")
        c = canvas.Canvas(second_pdf, pagesize=(595.28, 841.89))
        c.drawString(100, 750, "Second PDF Page")
        c.showPage()
        c.save()

        out_merged = str(self.d / "merged.pdf")
        res = PDFEngine.merge_pdfs([self.sample_pdf, second_pdf], out_merged)
        self.assertTrue(res)
        
        info = PDFEngine.get_document_info(out_merged)
        self.assertEqual(info.page_count, 4)

    def test_split_pdf(self):
        out_files = PDFEngine.split_pdf(self.sample_pdf, "each_page", str(self.d / "split_out"))
        self.assertEqual(len(out_files), 3)
        for f in out_files:
            info = PDFEngine.get_document_info(f)
            self.assertEqual(info.page_count, 1)

    def test_rotate_pages(self):
        out_rotated = str(self.d / "rotated.pdf")
        res = PDFEngine.rotate_pages(self.sample_pdf, out_rotated, pages=[0], angle=90)
        self.assertTrue(res)
        
        with pikepdf.open(out_rotated) as pdf:
            self.assertEqual(int(pdf.pages[0].get("/Rotate", 0)), 90)
            self.assertEqual(int(pdf.pages[1].get("/Rotate", 0)), 0)

    def test_delete_pages(self):
        out_deleted = str(self.d / "deleted.pdf")
        res = PDFEngine.delete_pages(self.sample_pdf, out_deleted, [1])
        self.assertTrue(res)
        
        info = PDFEngine.get_document_info(out_deleted)
        self.assertEqual(info.page_count, 2)

    def test_duplicate_pages(self):
        out_duplicated = str(self.d / "duplicated.pdf")
        res = PDFEngine.duplicate_pages(self.sample_pdf, out_duplicated, [0])
        self.assertTrue(res)
        
        info = PDFEngine.get_document_info(out_duplicated)
        self.assertEqual(info.page_count, 4)

    def test_validation(self):
        valid, msg = PDFEngine.validate_pdf(self.sample_pdf)
        self.assertTrue(valid)

if __name__ == "__main__":
    unittest.main()
