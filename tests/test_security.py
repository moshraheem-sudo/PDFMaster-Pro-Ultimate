"""
Tests for Security & Password Engine: AES-256 encryption, permissions, decryption.
"""
import unittest
import os
import tempfile
from pathlib import Path
from reportlab.pdfgen import canvas
import pikepdf

from core.security_engine import SecurityEngine
from core.models import SecurityConfig

class TestSecurity(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.d = Path(self.temp_dir.name)
        
        self.sample_pdf = str(self.d / "test_sec.pdf")
        c = canvas.Canvas(self.sample_pdf, pagesize=(595.28, 841.89))
        c.drawString(100, 750, "Confidential Document")
        c.showPage()
        c.save()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_encryption_and_decryption(self):
        enc_pdf = str(self.d / "encrypted.pdf")
        cfg = SecurityConfig(
            user_password="secret_password_123",
            owner_password="admin_master_pass",
            allow_printing=False,
            allow_copying=False
        )
        
        # 1. Encrypt
        res = SecurityEngine.encrypt_pdf(self.sample_pdf, enc_pdf, cfg)
        self.assertTrue(res)

        # 2. Verify encrypted status
        st = SecurityEngine.check_encryption_status(enc_pdf)
        self.assertTrue(st["is_encrypted"])
        self.assertTrue(st["requires_password"])

        # 3. Fail with wrong password
        dec_wrong = str(self.d / "decrypted_wrong.pdf")
        success, msg = SecurityEngine.decrypt_pdf(enc_pdf, dec_wrong, "wrong_pass")
        self.assertFalse(success)

        # 4. Succeed with correct password
        dec_pdf = str(self.d / "decrypted.pdf")
        success, msg = SecurityEngine.decrypt_pdf(enc_pdf, dec_pdf, "secret_password_123")
        self.assertTrue(success)
        
        # 5. Check decrypted is no longer encrypted
        st_dec = SecurityEngine.check_encryption_status(dec_pdf)
        self.assertFalse(st_dec["is_encrypted"])

if __name__ == "__main__":
    unittest.main()
