"""
PDF Master Pro - Compression Engine
Professional 3-level compression for PDF and images.
Calculates exact sizes, reduction percentage, and maintains validity.
"""
import os
import io
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, Callable, Tuple

import pikepdf
from PIL import Image

from core.config import PDFCPU_PATH
from core.models import CompressionLevel

class CompressionEngine:
    @staticmethod
    def compress_pdf(
        input_path: str,
        output_path: str,
        level: CompressionLevel = CompressionLevel.MEDIUM,
        optimize_images: bool = True,
        remove_unused_resources: bool = True,
        compress_fonts_and_streams: bool = True,
        target_dpi: Optional[int] = None,
        jpeg_quality: Optional[int] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict[str, Any]:
        """
        Compresses a PDF file using selected level and options.
        Returns statistics: original_size, final_size, saved_bytes, saving_ratio_pct.
        """
        in_p = Path(input_path)
        out_p = Path(output_path)
        orig_size = in_p.stat().st_size
        
        # Determine parameters based on level if not explicitly provided
        if level == CompressionLevel.LIGHT:
            dpi = target_dpi or 200
            quality = jpeg_quality or 85
            recompress_imgs = optimize_images
        elif level == CompressionLevel.MEDIUM:
            dpi = target_dpi or 150
            quality = jpeg_quality or 75
            recompress_imgs = optimize_images
        else: # STRONG
            dpi = target_dpi or 96
            quality = jpeg_quality or 55
            recompress_imgs = True
            
        if progress_callback:
            progress_callback(10, 100, "بدء تحليل كائنات وملفات المستند...")
            
        with pikepdf.open(input_path) as pdf:
            total_pages = len(pdf.pages)
            
            # Step 1: Recompress embedded images if requested
            if recompress_imgs:
                for p_idx, page in enumerate(pdf.pages):
                    if progress_callback:
                        pct = 10 + int(60 * (p_idx + 1) / total_pages)
                        progress_callback(pct, 100, f"ضغط صور الصفحة {p_idx + 1} من {total_pages}...")
                    
                    try:
                        resources = page.get("/Resources", {})
                        xobjects = resources.get("/XObject", {})
                        for name, obj in list(xobjects.items()):
                            if obj.get("/Subtype") == "/Image":
                                try:
                                    # Extract image
                                    pike_img = pikepdf.PdfImage(obj)
                                    pil_img = pike_img.as_pil_image()
                                    
                                    # Only downscale if larger than target DPI requirements
                                    w, h = pil_img.size
                                    scale = 1.0
                                    # Assume 8.5x11 inch page max
                                    max_dim = int(11 * dpi)
                                    if max(w, h) > max_dim:
                                        scale = max_dim / max(w, h)
                                        new_w = max(1, int(w * scale))
                                        new_h = max(1, int(h * scale))
                                        pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                                    
                                    # Compress as JPEG if RGB or grayscale
                                    img_buffer = io.BytesIO()
                                    if pil_img.mode in ("RGB", "L"):
                                        pil_img.save(img_buffer, format="JPEG", quality=quality, optimize=True)
                                    elif pil_img.mode == "RGBA":
                                        # Keep PNG or convert to RGB with background
                                        bg = Image.new("RGB", pil_img.size, (255, 255, 255))
                                        bg.paste(pil_img, mask=pil_img.split()[3])
                                        bg.save(img_buffer, format="JPEG", quality=quality, optimize=True)
                                    else:
                                        pil_img.save(img_buffer, format="PNG", optimize=True)
                                        
                                    img_buffer.seek(0)
                                    # Replace image data in pdf
                                    new_image_data = img_buffer.getvalue()
                                    if len(new_image_data) < len(bytes(obj.read_raw_bytes())):
                                        obj.write(new_image_data, filter=pikepdf.Name("/DCTDecode") if pil_img.mode in ("RGB", "L") else pikepdf.Name("/FlateDecode"))
                                        obj["/Width"] = pil_img.width
                                        obj["/Height"] = pil_img.height
                                        obj["/ColorSpace"] = pikepdf.Name("/DeviceRGB") if pil_img.mode in ("RGB", "RGBA") else pikepdf.Name("/DeviceGray")
                                        obj["/BitsPerComponent"] = 8
                                except Exception:
                                    continue
                    except Exception:
                        continue
            
            if progress_callback:
                progress_callback(75, 100, "إزالة الموارد غير المستخدمة وتوليد تدفقات الكائنات...")
                
            # Step 2: Remove unreferenced resources
            if remove_unused_resources:
                pdf.remove_unreferenced_resources()
            
            # Step 3: Save with Flate compression & Object Streams
            save_kwargs = {
                "compress_streams": True,
                "recompress_flate": True,
                "preserve_pdfa": True
            }
            if compress_fonts_and_streams:
                save_kwargs["object_stream_mode"] = pikepdf.ObjectStreamMode.generate
            else:
                save_kwargs["object_stream_mode"] = pikepdf.ObjectStreamMode.preserve
                
            pdf.save(output_path, **save_kwargs)
            
        if progress_callback:
            progress_callback(90, 100, "التحسين النهائي...")
            
        # Optional: Run pdfcpu optimize if available and size benefits
        if Path(PDFCPU_PATH).exists():
            try:
                import subprocess
                subprocess.run(
                    [str(PDFCPU_PATH), "optimize", output_path],
                    capture_output=True,
                    creationflags=0x08000000 if os.name == "nt" else 0
                )
            except Exception:
                pass
                
        final_size = out_p.stat().st_size
        saved_bytes = max(0, orig_size - final_size)
        saving_ratio = (saved_bytes / orig_size * 100.0) if orig_size > 0 else 0.0
        
        if progress_callback:
            progress_callback(100, 100, "اكتمل الضغط بنجاح!")
            
        return {
            "original_size": orig_size,
            "final_size": final_size,
            "saved_bytes": saved_bytes,
            "saving_ratio_pct": round(saving_ratio, 1),
            "original_formatted": CompressionEngine.format_size(orig_size),
            "final_formatted": CompressionEngine.format_size(final_size),
            "saved_formatted": CompressionEngine.format_size(saved_bytes)
        }

    @staticmethod
    def estimate_compression(original_size_bytes: int, level: CompressionLevel) -> Dict[str, Any]:
        """
        Estimates expected compression for UI display before running.
        """
        if level == CompressionLevel.LIGHT:
            ratio = 30.0
        elif level == CompressionLevel.MEDIUM:
            ratio = 60.0
        else: # STRONG
            ratio = 75.0
            
        expected_saved = int(original_size_bytes * (ratio / 100.0))
        expected_final = max(1024, original_size_bytes - expected_saved)
        
        return {
            "original_formatted": CompressionEngine.format_size(original_size_bytes),
            "expected_final_formatted": CompressionEngine.format_size(expected_final),
            "saving_ratio_pct": int(ratio)
        }

    @staticmethod
    def format_size(size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
