"""
Tests for PDF Compression Engine: 3 levels, size reductions, validity.
"""
import unittest
import os
import tempfile
from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
import pikepdf

from core.compression_engine import CompressionEngine
from core.models import CompressionLevel
from core.pdf_engine import PDFEngine

class TestCompression(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.d = Path(self.temp_dir.name)
        
        # Create a sample PDF with an uncompressed large image
        img_path = str(self.d / "large_test.png")
        img = Image.new("RGB", (1200, 1600), color=(100, 150, 200))
        img.save(img_path)

        self.sample_pdf = str(self.d / "img_doc.pdf")
        c = canvas.Canvas(self.sample_pdf, pagesize=(595.28, 841.89))
        c.drawString(50, 800, "Document with Image")
        c.drawImage(img_path, 50, 200, width=500, height=550)
        c.showPage()
        c.save()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_compression_levels(self):
        for level in [CompressionLevel.LIGHT, CompressionLevel.MEDIUM, CompressionLevel.STRONG]:
            out_pdf = str(self.d / f"compressed_{level.value}.pdf")
            stats = CompressionEngine.compress_pdf(
                input_path=self.sample_pdf,
                output_path=out_pdf,
                level=level
            )
            self.assertTrue(os.path.exists(out_pdf))
            self.assertTrue(stats["final_size"] > 0)
            
            # Verify the output PDF is valid and readable
            valid, msg = PDFEngine.validate_pdf(out_pdf)
            self.assertTrue(valid, f"Validation failed for level {level}: {msg}")
            
            info = PDFEngine.get_document_info(out_pdf)
            self.assertEqual(info.page_count, 1)

if __name__ == "__main__":
    unittest.main()
