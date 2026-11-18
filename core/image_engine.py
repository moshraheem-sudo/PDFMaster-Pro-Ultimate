"""
PDF Master Pro - Image Processing Engine
Comprehensive image editing, compression, and conversion using Pillow.
"""
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Callable
from PIL import Image, ImageOps

class ImageEngine:
    @staticmethod
    def process_image(
        input_path: str,
        output_path: str,
        resize_mode: str = "none", # "none", "exact", "percentage", "max_edge"
        target_width: Optional[int] = None,
        target_height: Optional[int] = None,
        scale_pct: float = 100.0,
        keep_aspect: bool = True,
        rotate_angle: int = 0, # 0, 90, 180, 270
        flip_h: bool = False,
        flip_v: bool = False,
        crop_box: Optional[Tuple[int, int, int, int]] = None, # (left, top, right, bottom)
        target_format: Optional[str] = None, # "JPEG", "PNG", "WEBP", None (keep)
        quality: int = 80,
        dpi: Optional[int] = None,
        optimize: bool = True
    ) -> Dict[str, Any]:
        """
        Processes a single image according to specified parameters.
        Returns compression/processing statistics.
        """
        in_p = Path(input_path)
        out_p = Path(output_path)
        orig_size = in_p.stat().st_size
        
        with Image.open(input_path) as img:
            # Handle orientation from EXIF if present
            img = ImageOps.exif_transpose(img)
            
            # Format detection
            orig_format = img.format or "PNG"
            out_format = (target_format or orig_format).upper()
            if out_format == "JPG":
                out_format = "JPEG"
                
            # Crop
            if crop_box:
                img = img.crop(crop_box)
                
            # Rotate
            if rotate_angle != 0:
                img = img.rotate(-rotate_angle, expand=True)
                
            # Flip
            if flip_h:
                img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            if flip_v:
                img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                
            # Resize
            orig_w, orig_h = img.size
            if resize_mode == "exact" and target_width and target_height:
                if keep_aspect:
                    img.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
                else:
                    img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            elif resize_mode == "percentage" and scale_pct != 100.0:
                new_w = max(1, int(orig_w * (scale_pct / 100.0)))
                new_h = max(1, int(orig_h * (scale_pct / 100.0)))
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            elif resize_mode == "max_edge" and target_width:
                max_edge = target_width
                if max(orig_w, orig_h) > max_edge:
                    img.thumbnail((max_edge, max_edge), Image.Resampling.LANCZOS)
                    
            # Color Mode adjustments for formats
            if out_format == "JPEG" and img.mode in ("RGBA", "LA", "P"):
                # Composite on white background for JPEG
                bg = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "RGBA":
                    bg.paste(img, mask=img.split()[3])
                else:
                    bg.paste(img.convert("RGBA"))
                img = bg
            elif out_format in ("PNG", "WEBP") and img.mode not in ("RGB", "RGBA", "L"):
                img = img.convert("RGBA")
                
            # Save options
            save_kwargs: Dict[str, Any] = {"optimize": optimize}
            if out_format in ("JPEG", "WEBP"):
                save_kwargs["quality"] = max(1, min(100, quality))
            if dpi:
                save_kwargs["dpi"] = (dpi, dpi)
                
            img.save(output_path, format=out_format, **save_kwargs)
            
        final_size = out_p.stat().st_size
        saved_bytes = max(0, orig_size - final_size)
        saving_pct = (saved_bytes / orig_size * 100.0) if orig_size > 0 else 0.0
        
        return {
            "original_size": orig_size,
            "final_size": final_size,
            "saved_bytes": saved_bytes,
            "saving_ratio_pct": round(saving_pct, 1),
            "original_formatted": ImageEngine.format_size(orig_size),
            "final_formatted": ImageEngine.format_size(final_size),
            "output_path": str(out_p.resolve())
        }

    @staticmethod
    def batch_process(
        image_paths: List[str],
        output_dir: str,
        settings: Dict[str, Any],
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> List[Dict[str, Any]]:
        results = []
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        total = len(image_paths)
        
        for idx, img_path in enumerate(image_paths):
            p = Path(img_path)
            target_fmt = settings.get("target_format", p.suffix.lstrip(".").upper())
            ext = target_fmt.lower()
            if ext == "jpeg":
                ext = "jpg"
            out_file = str(out_dir / f"{p.stem}_processed.{ext}")
            
            if progress_callback:
                progress_callback(idx + 1, total, f"معالجة {p.name}...")
                
            try:
                res = ImageEngine.process_image(
                    input_path=img_path,
                    output_path=out_file,
                    resize_mode=settings.get("resize_mode", "none"),
                    target_width=settings.get("target_width"),
                    target_height=settings.get("target_height"),
                    scale_pct=settings.get("scale_pct", 100.0),
                    keep_aspect=settings.get("keep_aspect", True),
                    rotate_angle=settings.get("rotate_angle", 0),
                    flip_h=settings.get("flip_h", False),
                    flip_v=settings.get("flip_v", False),
                    target_format=settings.get("target_format"),
                    quality=settings.get("quality", 80),
                    dpi=settings.get("dpi"),
                    optimize=settings.get("optimize", True)
                )
                results.append(res)
            except Exception as e:
                results.append({"error": str(e), "input_path": img_path})
                
        return results

    @staticmethod
    def format_size(size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
