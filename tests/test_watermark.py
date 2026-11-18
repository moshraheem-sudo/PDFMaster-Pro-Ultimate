"""
Tests for Watermark Engine: Text watermark, image watermark, and removal/redaction.
"""
import unittest
import os
import tempfile
from pathlib import Path
from reportlab.pdfgen import canvas
import pikepdf

from core.watermark_engine import WatermarkEngine
from core.models import WatermarkConfig
from core.pdf_engine import PDFEngine

class TestWatermark(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.d = Path(self.temp_dir.name)
        
        self.sample_pdf = str(self.d / "test_wm.pdf")
        c = canvas.Canvas(self.sample_pdf, pagesize=(595.28, 841.89))
        c.drawString(100, 750, "Document to watermark")
        c.showPage()
        c.save()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_text_watermark(self):
        out_wm = str(self.d / "watermarked.pdf")
        cfg = WatermarkConfig(
            is_text=True,
            text="CONFIDENTIAL",
            font_size=36,
            opacity=0.4,
            rotation=45,
            all_pages=True
        )
        res = WatermarkEngine.add_watermark(self.sample_pdf, out_wm, cfg)
        self.assertTrue(res)
        self.assertTrue(os.path.exists(out_wm))
        
        valid, msg = PDFEngine.validate_pdf(out_wm)
        self.assertTrue(valid)

    def test_watermark_redaction(self):
        out_redact = str(self.d / "redacted.pdf")
        # Redact box (100, 100, 200, 200)
        success, msg = WatermarkEngine.remove_watermark(
            self.sample_pdf,
            out_redact,
            method="redact",
            redact_rect=(100, 100, 200, 200)
        )
        self.assertTrue(success)
        self.assertTrue(os.path.exists(out_redact))

if __name__ == "__main__":
    unittest.main()
