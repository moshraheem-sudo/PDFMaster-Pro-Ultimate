"""
PDF Master Pro - Watermark Engine
Comprehensive text & image watermark application and removal using pikepdf, reportlab, and pdfcpu.
"""
import io
import math
import subprocess
from pathlib import Path
from typing import Optional, List, Callable, Tuple

import pikepdf
from reportlab.pdfgen import canvas
from reportlab.lib import colors

from core.config import PDFCPU_PATH
from core.models import WatermarkConfig

class WatermarkEngine:
    @staticmethod
    def _create_text_watermark_pdf(
        page_width_pt: float,
        page_height_pt: float,
        config: WatermarkConfig
    ) -> io.BytesIO:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=(page_width_pt, page_height_pt))
        
        # Color & Alpha
        hex_color = config.color.lstrip("#")
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
        else:
            r, g, b = 0.5, 0.5, 0.5
            
        c.setFillColor(colors.Color(r, g, b, alpha=config.opacity))
        c.setFont("Helvetica-Bold", config.font_size)
        
        # Position
        if config.position == "center":
            x = page_width_pt / 2.0
            y = page_height_pt / 2.0
        elif config.position == "top-left":
            x = page_width_pt * 0.2
            y = page_height_pt * 0.8
        elif config.position == "top-right":
            x = page_width_pt * 0.8
            y = page_height_pt * 0.8
        elif config.position == "bottom-left":
            x = page_width_pt * 0.2
            y = page_height_pt * 0.2
        else: # bottom-right
            x = page_width_pt * 0.8
            y = page_height_pt * 0.2
            
        c.saveState()
        c.translate(x, y)
        c.rotate(config.rotation)
        c.drawCentredString(0, 0, config.text)
        c.restoreState()
        
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    @staticmethod
    def _create_image_watermark_pdf(
        page_width_pt: float,
        page_height_pt: float,
        image_path: str,
        opacity: float = 0.3,
        scale: float = 0.5,
        rotation: int = 0
    ) -> io.BytesIO:
        from PIL import Image
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=(page_width_pt, page_height_pt))
        
        with Image.open(image_path) as img:
            img_w, img_h = img.size
            
        # Desired size in points
        target_w = page_width_pt * scale
        target_h = target_w * (img_h / img_w)
        
        c.saveState()
        c.setFillAlpha(opacity)
        c.translate(page_width_pt / 2.0, page_height_pt / 2.0)
        if rotation != 0:
            c.rotate(rotation)
        c.drawImage(image_path, -target_w / 2.0, -target_h / 2.0, width=target_w, height=target_h, mask='auto')
        c.restoreState()
        
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    @staticmethod
    def add_watermark(
        input_path: str,
        output_path: str,
        config: WatermarkConfig,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> bool:
        with pikepdf.open(input_path) as base_pdf:
            total_pages = len(base_pdf.pages)
            
            # Determine pages to apply
            target_indices = set(range(total_pages)) if config.all_pages else set()
            if not config.all_pages and config.page_range:
                # Parse range like "1,3,5-7"
                parts = config.page_range.split(",")
                for part in parts:
                    part = part.strip()
                    if "-" in part:
                        s, e = part.split("-", 1)
                        s_idx = max(0, int(s) - 1) if s else 0
                        e_idx = min(total_pages - 1, int(e) - 1) if e else total_pages - 1
                        target_indices.update(range(s_idx, e_idx + 1))
                    elif part.isdigit():
                        idx = int(part) - 1
                        if 0 <= idx < total_pages:
                            target_indices.add(idx)
                            
            for i, page in enumerate(base_pdf.pages):
                if progress_callback:
                    progress_callback(i + 1, total_pages, f"إضافة العلامة لصفحة {i + 1}...")
                if i in target_indices:
                    box = page.mediabox
                    w = float(box[2]) - float(box[0])
                    h = float(box[3]) - float(box[1])
                    
                    if config.is_text:
                        wm_buf = WatermarkEngine._create_text_watermark_pdf(w, h, config)
                    else:
                        wm_buf = WatermarkEngine._create_image_watermark_pdf(w, h, config.image_path or "", opacity=config.opacity, rotation=config.rotation)
                        
                    with pikepdf.open(wm_buf) as stamp_pdf:
                        stamp_page = stamp_pdf.pages[0]
                        # Overlay stamp on page
                        page.add_overlay(stamp_page)
                        
            base_pdf.save(output_path)
        return True

    @staticmethod
    def remove_watermark(
        input_path: str,
        output_path: str,
        method: str = "pdfcpu", # "pdfcpu" or "redact"
        redact_rect: Optional[Tuple[float, float, float, float]] = None, # (x0, y0, x1, y1) in points
        page_indices: Optional[List[int]] = None
    ) -> Tuple[bool, str]:
        """
        Removes watermark via pdfcpu or visual rectangle redaction.
        """
        if method == "pdfcpu" and Path(PDFCPU_PATH).exists():
            try:
                res = subprocess.run(
                    [str(PDFCPU_PATH), "watermark", "remove", input_path, output_path],
                    capture_output=True,
                    text=True,
                    creationflags=0x08000000 if subprocess.os.name == "nt" else 0
                )
                if res.returncode == 0:
                    return True, "تمت إزالة العلامات المائية بنجاح باستخدام محرك pdfcpu."
            except Exception:
                pass
                
        # If method is redact or pdfcpu didn't find watermark objects
        if redact_rect:
            with pikepdf.open(input_path) as pdf:
                targets = set(page_indices) if page_indices is not None else set(range(len(pdf.pages)))
                # Draw white rectangle over the redacted region via overlay
                for i in targets:
                    if 0 <= i < len(pdf.pages):
                        page = pdf.pages[i]
                        box = page.mediabox
                        w = float(box[2]) - float(box[0])
                        h = float(box[3]) - float(box[1])
                        
                        buf = io.BytesIO()
                        c = canvas.Canvas(buf, pagesize=(w, h))
                        c.setFillColor(colors.white)
                        c.setStrokeColor(colors.white)
                        rx, ry, rw, rh = redact_rect
                        c.rect(rx, ry, rw, rh, fill=1, stroke=0)
                        c.showPage()
                        c.save()
                        buf.seek(0)
                        
                        with pikepdf.open(buf) as mask_pdf:
                            page.add_overlay(mask_pdf.pages[0])
                pdf.save(output_path)
            return True, "تمت تغطية وإزالة المنطقة المحددة كعلامة مائية بنجاح."
            
        return False, "لم يتم العثور على علامات مائية مسجلة ككائنات مستقلة؛ يمكنك استخدام أداة التعتيم/التغطية اليدوية."
