"""
PDF Master Pro - Conversion Engine
Conversion between PDF and images (both directions) and text export.
"""
from pathlib import Path
from typing import List, Optional, Callable

from PIL import Image
import pikepdf
from PySide6.QtCore import QSize
from PySide6.QtPdf import QPdfDocument, QPdfDocumentRenderOptions
from PySide6.QtGui import QImage

class ConversionEngine:
    @staticmethod
    def images_to_pdf(
        image_paths: List[str],
        output_pdf_path: str,
        page_size_mode: str = "fit_a4", # "fit_a4", "original"
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> bool:
        if not image_paths:
            raise ValueError("No images selected for conversion")
            
        pil_images = []
        total = len(image_paths)
        
        # A4 in points: 595.28 x 841.89
        a4_w_pt, a4_h_pt = 595.28, 841.89
        
        for idx, img_path in enumerate(image_paths):
            if progress_callback:
                progress_callback(idx + 1, total, f"معالجة الصورة {Path(img_path).name}...")
            img = Image.open(img_path)
            if img.mode in ("RGBA", "LA", "P"):
                # Convert to RGB with white background
                bg = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "RGBA":
                    bg.paste(img, mask=img.split()[3])
                else:
                    bg.paste(img.convert("RGBA"))
                img = bg
            elif img.mode != "RGB":
                img = img.convert("RGB")
                
            pil_images.append(img)
            
        first_img = pil_images[0]
        rest = pil_images[1:] if len(pil_images) > 1 else []
        
        first_img.save(
            output_pdf_path,
            "PDF",
            resolution=150.0,
            save_all=True,
            append_images=rest
        )
        return True

    @staticmethod
    def pdf_to_images(
        pdf_path: str,
        output_dir: str,
        image_format: str = "png", # "png", "jpeg", "webp"
        dpi: int = 150,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> List[str]:
        output_paths = []
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        stem = Path(pdf_path).stem
        
        doc = QPdfDocument()
        err = doc.load(pdf_path)
        if err != QPdfDocument.Error.None_:
            raise RuntimeError(f"Failed to load PDF with code {err}")
            
        total_pages = doc.pageCount()
        render_options = QPdfDocumentRenderOptions()
        
        scale_factor = dpi / 72.0
        
        for i in range(total_pages):
            if progress_callback:
                progress_callback(i + 1, total_pages, f"رسم وحفظ الصفحة {i + 1} من {total_pages}...")
                
            pt_size = doc.pagePointSize(i)
            pixel_w = int(pt_size.width() * scale_factor)
            pixel_h = int(pt_size.height() * scale_factor)
            
            q_img = doc.render(i, QSize(pixel_w, pixel_h), render_options)
            
            ext = image_format.lower()
            if ext == "jpeg":
                ext = "jpg"
            out_file = str(out_dir / f"{stem}_page_{i + 1}.{ext}")
            
            q_img.save(out_file)
            output_paths.append(out_file)
            
        doc.close()
        return output_paths
