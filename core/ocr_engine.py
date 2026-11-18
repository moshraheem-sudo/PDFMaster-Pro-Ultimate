"""
PDF Master Pro - OCR Engine
Optical Character Recognition supporting Arabic and English using Tesseract OCR.
"""
import os
from pathlib import Path
from typing import List, Optional, Tuple, Callable

from PIL import Image
import pytesseract

from core.config import get_tesseract_path

class OCREngine:
    @staticmethod
    def is_available() -> bool:
        tess_path = get_tesseract_path()
        if Path(tess_path).exists() or tess_path == "tesseract":
            try:
                pytesseract.pytesseract.tesseract_cmd = tess_path
                pytesseract.get_tesseract_version()
                return True
            except Exception:
                return False
        return False

    @staticmethod
    def get_available_languages() -> List[str]:
        if not OCREngine.is_available():
            return []
        try:
            return pytesseract.get_languages(config="")
        except Exception:
            return ["ara", "eng"]

    @staticmethod
    def recognize_image(
        image_input, # Path string or PIL Image
        lang: str = "ara+eng", # "ara", "eng", or "ara+eng"
    ) -> str:
        if not OCREngine.is_available():
            raise RuntimeError("محرك Tesseract OCR غير مثبت أو غير متاح في النظام.")
            
        pytesseract.pytesseract.tesseract_cmd = get_tesseract_path()
        if isinstance(image_input, (str, Path)):
            with Image.open(str(image_input)) as img:
                return pytesseract.image_to_string(img, lang=lang)
        else:
            return pytesseract.image_to_string(image_input, lang=lang)

    @staticmethod
    def ocr_pdf_pages(
        page_images: List[Image.Image],
        lang: str = "ara+eng",
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> str:
        results = []
        total = len(page_images)
        for idx, img in enumerate(page_images):
            if progress_callback:
                progress_callback(idx + 1, total, f"التعرف الضوئي على صفحة {idx + 1}...")
            text = OCREngine.recognize_image(img, lang=lang)
            results.append(f"--- [الصفحة {idx + 1}] ---\n{text}")
        return "\n\n".join(results)
