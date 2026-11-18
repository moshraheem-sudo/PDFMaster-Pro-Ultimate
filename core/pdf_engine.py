"""
PDF Master Pro - PDF Engine
Unified processing engine leveraging pikepdf, pypdf, and pdfcpu.
"""
import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Callable

import pypdf
import pikepdf
from PIL import Image

from core.config import PDFCPU_PATH
from core.models import DocumentInfo, DocumentMetadata, RotationAngle

class PDFEngine:
    @staticmethod
    def is_pdfcpu_available() -> bool:
        return Path(PDFCPU_PATH).exists()

    @staticmethod
    def run_pdfcpu_cmd(args: List[str]) -> Tuple[bool, str]:
        if not PDFEngine.is_pdfcpu_available():
            return False, "pdfcpu executable not found"
        cmd = [str(PDFCPU_PATH)] + args
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            if res.returncode == 0:
                return True, res.stdout
            return False, res.stderr or res.stdout
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_document_info(file_path: str, password: Optional[str] = None) -> DocumentInfo:
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_size = p.stat().st_size
        doc_info = DocumentInfo(
            file_path=str(p.resolve()),
            file_name=p.name,
            file_size_bytes=file_size,
            page_count=0
        )
        
        try:
            with pikepdf.open(file_path, password=password or "") as pdf:
                doc_info.page_count = len(pdf.pages)
                doc_info.is_encrypted = pdf.is_encrypted
                
                # Page dimensions of first page
                if len(pdf.pages) > 0:
                    box = pdf.pages[0].mediabox
                    # mediabox is [x0, y0, x1, y1] in points (1 pt = 1/72 inch = 0.352778 mm)
                    w_pt = float(box[2]) - float(box[0])
                    h_pt = float(box[3]) - float(box[1])
                    w_mm = w_pt * 25.4 / 72.0
                    h_mm = h_pt * 25.4 / 72.0
                    
                    # Standard detection
                    dim_str = f"{int(round(w_mm))}×{int(round(h_mm))} mm"
                    if abs(w_mm - 210) < 5 and abs(h_mm - 297) < 5:
                        dim_str = f"A4 ({dim_str})"
                    elif abs(w_mm - 297) < 5 and abs(h_mm - 210) < 5:
                        dim_str = f"A4 Landscape ({dim_str})"
                    elif abs(w_mm - 216) < 5 and abs(h_mm - 279) < 5:
                        dim_str = f"Letter ({dim_str})"
                    doc_info.page_dimensions = dim_str
                
                # Metadata
                meta = pdf.docinfo
                metadata = DocumentMetadata(
                    title=str(meta.get("/Title", "")),
                    author=str(meta.get("/Author", "")),
                    subject=str(meta.get("/Subject", "")),
                    keywords=str(meta.get("/Keywords", "")),
                    creator=str(meta.get("/Creator", "")),
                    producer=str(meta.get("/Producer", "")),
                    is_encrypted=pdf.is_encrypted
                )
                doc_info.metadata = metadata
        except pikepdf.PasswordError:
            doc_info.is_encrypted = True
            # Try to get page count from pypdf without decrypting if possible
            try:
                reader = pypdf.PdfReader(file_path)
                doc_info.page_count = len(reader.pages)
            except Exception:
                doc_info.page_count = 0
        except Exception as e:
            # Fallback to pypdf
            reader = pypdf.PdfReader(file_path)
            doc_info.page_count = len(reader.pages)
            doc_info.is_encrypted = reader.is_encrypted
            
        return doc_info

    @staticmethod
    def merge_pdfs(
        file_paths: List[str],
        output_path: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> bool:
        if not file_paths:
            raise ValueError("No files provided for merging")
        
        total_files = len(file_paths)
        with pikepdf.new() as output_pdf:
            for idx, file_path in enumerate(file_paths):
                if progress_callback:
                    progress_callback(idx, total_files, f"دمج الملف {Path(file_path).name}...")
                with pikepdf.open(file_path) as src_pdf:
                    output_pdf.pages.extend(src_pdf.pages)
            
            if progress_callback:
                progress_callback(total_files, total_files, "جاري حفظ الملف المدمج...")
            output_pdf.save(output_path)
        return True

    @staticmethod
    def split_pdf(
        input_path: str,
        mode: str, # "each_page", "page_ranges", "fixed_count"
        output_dir: str,
        pages_per_split: int = 1,
        page_ranges: Optional[List[Tuple[int, int]]] = None, # 1-indexed
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> List[str]:
        out_files = []
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        stem = Path(input_path).stem
        
        with pikepdf.open(input_path) as pdf:
            total_pages = len(pdf.pages)
            if mode == "each_page":
                for i in range(total_pages):
                    if progress_callback:
                        progress_callback(i + 1, total_pages, f"استخراج صفحة {i + 1}...")
                    out_pdf_path = str(out_dir / f"{stem}_page_{i + 1}.pdf")
                    with pikepdf.new() as single_page_pdf:
                        single_page_pdf.pages.append(pdf.pages[i])
                        single_page_pdf.save(out_pdf_path)
                    out_files.append(out_pdf_path)
            elif mode == "fixed_count":
                group_idx = 1
                for start_idx in range(0, total_pages, pages_per_split):
                    end_idx = min(start_idx + pages_per_split, total_pages)
                    if progress_callback:
                        progress_callback(start_idx + 1, total_pages, f"استخراج الصفحات {start_idx + 1}-{end_idx}...")
                    out_pdf_path = str(out_dir / f"{stem}_part_{group_idx}.pdf")
                    with pikepdf.new() as part_pdf:
                        for p in range(start_idx, end_idx):
                            part_pdf.pages.append(pdf.pages[p])
                        part_pdf.save(out_pdf_path)
                    out_files.append(out_pdf_path)
                    group_idx += 1
            elif mode == "page_ranges" and page_ranges:
                for idx, (p_start, p_end) in enumerate(page_ranges):
                    p_start = max(1, p_start)
                    p_end = min(total_pages, p_end)
                    if progress_callback:
                        progress_callback(idx + 1, len(page_ranges), f"استخراج النطاق {p_start}-{p_end}...")
                    out_pdf_path = str(out_dir / f"{stem}_range_{p_start}_{p_end}.pdf")
                    with pikepdf.new() as range_pdf:
                        for p in range(p_start - 1, p_end):
                            range_pdf.pages.append(pdf.pages[p])
                        range_pdf.save(out_pdf_path)
                    out_files.append(out_pdf_path)
        return out_files

    @staticmethod
    def rotate_pages(
        input_path: str,
        output_path: str,
        pages: Optional[List[int]] = None, # 0-indexed, None means all
        angle: int = 90,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> bool:
        with pikepdf.open(input_path) as pdf:
            total = len(pdf.pages)
            target_pages = set(pages) if pages is not None else set(range(total))
            for i, page in enumerate(pdf.pages):
                if i in target_pages:
                    curr_rot = int(page.get("/Rotate", 0))
                    new_rot = (curr_rot + angle) % 360
                    page["/Rotate"] = new_rot
                if progress_callback:
                    progress_callback(i + 1, total, f"تدوير صفحة {i + 1}...")
            pdf.save(output_path)
        return True

    @staticmethod
    def delete_pages(
        input_path: str,
        output_path: str,
        page_indices: List[int], # 0-indexed
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> bool:
        delete_set = set(page_indices)
        with pikepdf.open(input_path) as pdf:
            total = len(pdf.pages)
            with pikepdf.new() as out_pdf:
                for i, page in enumerate(pdf.pages):
                    if i not in delete_set:
                        out_pdf.pages.append(page)
                    if progress_callback:
                        progress_callback(i + 1, total, f"معالجة صفحة {i + 1}...")
                if len(out_pdf.pages) == 0:
                    raise ValueError("Cannot delete all pages from PDF")
                out_pdf.save(output_path)
        return True

    @staticmethod
    def reorder_pages(
        input_path: str,
        output_path: str,
        new_order: List[int], # 0-indexed
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> bool:
        with pikepdf.open(input_path) as pdf:
            with pikepdf.new() as out_pdf:
                total = len(new_order)
                for idx, page_num in enumerate(new_order):
                    if 0 <= page_num < len(pdf.pages):
                        out_pdf.pages.append(pdf.pages[page_num])
                    if progress_callback:
                        progress_callback(idx + 1, total, f"ترتيب صفحة {page_num + 1}...")
                out_pdf.save(output_path)
        return True

    @staticmethod
    def duplicate_pages(
        input_path: str,
        output_path: str,
        page_indices: List[int], # 0-indexed
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> bool:
        dup_set = set(page_indices)
        with pikepdf.open(input_path) as pdf:
            with pikepdf.new() as out_pdf:
                total = len(pdf.pages)
                for i, page in enumerate(pdf.pages):
                    out_pdf.pages.append(page)
                    if i in dup_set:
                        out_pdf.pages.append(page)
                    if progress_callback:
                        progress_callback(i + 1, total, f"تكرار صفحة {i + 1}...")
                out_pdf.save(output_path)
        return True

    @staticmethod
    def extract_pages(
        input_path: str,
        output_path: str,
        page_indices: List[int], # 0-indexed
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> bool:
        with pikepdf.open(input_path) as pdf:
            with pikepdf.new() as out_pdf:
                total = len(page_indices)
                for idx, p in enumerate(page_indices):
                    if 0 <= p < len(pdf.pages):
                        out_pdf.pages.append(pdf.pages[p])
                    if progress_callback:
                        progress_callback(idx + 1, total, f"استخراج صفحة {p + 1}...")
                out_pdf.save(output_path)
        return True

    @staticmethod
    def crop_pages(
        input_path: str,
        output_path: str,
        margin_top_pt: float,
        margin_bottom_pt: float,
        margin_left_pt: float,
        margin_right_pt: float,
        page_indices: Optional[List[int]] = None
    ) -> bool:
        with pikepdf.open(input_path) as pdf:
            target_pages = set(page_indices) if page_indices is not None else set(range(len(pdf.pages)))
            for i, page in enumerate(pdf.pages):
                if i in target_pages:
                    box = page.mediabox
                    x0 = float(box[0]) + margin_left_pt
                    y0 = float(box[1]) + margin_bottom_pt
                    x1 = float(box[2]) - margin_right_pt
                    y1 = float(box[3]) - margin_top_pt
                    if x1 > x0 and y1 > y0:
                        page.mediabox = [x0, y0, x1, y1]
                        page.cropbox = [x0, y0, x1, y1]
            pdf.save(output_path)
        return True

    @staticmethod
    def extract_images(
        input_path: str,
        output_dir: str,
        selected_page: Optional[int] = None, # 0-indexed
        image_format: str = "png",
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> List[str]:
        extracted_paths = []
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        stem = Path(input_path).stem
        
        with pikepdf.open(input_path) as pdf:
            pages_to_scan = [selected_page] if selected_page is not None else range(len(pdf.pages))
            total_pages = len(pages_to_scan)
            
            img_counter = 1
            for idx, p_idx in enumerate(pages_to_scan):
                if progress_callback:
                    progress_callback(idx + 1, total_pages, f"فحص صفحة {p_idx + 1}...")
                page = pdf.pages[p_idx]
                
                # Check XObject resources
                try:
                    resources = page.get("/Resources", {})
                    xobjects = resources.get("/XObject", {})
                    for name, obj in xobjects.items():
                        if obj.get("/Subtype") == "/Image":
                            try:
                                pike_img = pikepdf.PdfImage(obj)
                                pil_img = pike_img.as_pil_image()
                                out_filename = f"{stem}_p{p_idx + 1}_img{img_counter}.{image_format.lower()}"
                                out_file_path = str(out_dir / out_filename)
                                pil_img.save(out_file_path)
                                extracted_paths.append(out_file_path)
                                img_counter += 1
                            except Exception:
                                continue
                except Exception:
                    continue
        return extracted_paths

    @staticmethod
    def get_embedded_images_info(input_path: str, page_index: Optional[int] = None) -> List[Dict[str, Any]]:
        images_info = []
        with pikepdf.open(input_path) as pdf:
            pages_to_scan = [page_index] if page_index is not None else range(len(pdf.pages))
            for p_idx in pages_to_scan:
                page = pdf.pages[p_idx]
                try:
                    resources = page.get("/Resources", {})
                    xobjects = resources.get("/XObject", {})
                    for name, obj in xobjects.items():
                        if obj.get("/Subtype") == "/Image":
                            w = int(obj.get("/Width", 0))
                            h = int(obj.get("/Height", 0))
                            colorspace = str(obj.get("/ColorSpace", "RGB"))
                            images_info.append({
                                "page_index": p_idx,
                                "name": str(name),
                                "width": w,
                                "height": h,
                                "colorspace": colorspace,
                                "obj_id": obj.objgen[0] if hasattr(obj, 'objgen') else 0
                            })
                except Exception:
                    continue
        return images_info

    @staticmethod
    def delete_embedded_images(
        input_path: str,
        output_path: str,
        image_names_by_page: Dict[int, List[str]], # {page_idx: [names]}
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> bool:
        with pikepdf.open(input_path) as pdf:
            total = len(image_names_by_page)
            for step, (p_idx, names_to_remove) in enumerate(image_names_by_page.items()):
                if progress_callback:
                    progress_callback(step + 1, total, f"إزالة الصور من صفحة {p_idx + 1}...")
                if 0 <= p_idx < len(pdf.pages):
                    page = pdf.pages[p_idx]
                    try:
                        resources = page.get("/Resources", {})
                        xobjects = resources.get("/XObject", {})
                        for name in names_to_remove:
                            if name in xobjects:
                                # Replace with 1x1 transparent/white image or remove from xobjects
                                del xobjects[name]
                    except Exception:
                        continue
            pdf.save(output_path)
        return True

    @staticmethod
    def extract_text(input_path: str, page_index: Optional[int] = None) -> str:
        text_parts = []
        reader = pypdf.PdfReader(input_path)
        pages_to_read = [page_index] if page_index is not None else range(len(reader.pages))
        for p in pages_to_read:
            page_text = reader.pages[p].extract_text()
            if page_text:
                text_parts.append(page_text)
        return "\n\n".join(text_parts)

    @staticmethod
    def update_metadata(
        input_path: str,
        output_path: str,
        title: str,
        author: str,
        subject: str,
        keywords: str
    ) -> bool:
        with pikepdf.open(input_path) as pdf:
            meta = pdf.open_metadata()
            meta["dc:title"] = title
            meta["dc:creator"] = [author] if author else []
            meta["dc:description"] = subject
            meta["pdf:Keywords"] = keywords
            pdf.docinfo["/Title"] = title
            pdf.docinfo["/Author"] = author
            pdf.docinfo["/Subject"] = subject
            pdf.docinfo["/Keywords"] = keywords
            pdf.save(output_path)
        return True

    @staticmethod
    def validate_pdf(input_path: str) -> Tuple[bool, str]:
        # 1. Try pdfcpu validate if available
        if PDFEngine.is_pdfcpu_available():
            ok, out = PDFEngine.run_pdfcpu_cmd(["validate", input_path])
            if ok:
                return True, "تم التحقق من سلامة مستند PDF بنجاح عبر محرك pdfcpu."
            # If pdfcpu reported warnings/errors, also check pikepdf
        
        # 2. Try pikepdf validation
        try:
            with pikepdf.open(input_path) as pdf:
                pdf.check()
            return True, "تم التحقق بنجاح: بنية ملف PDF سليمة وخالية من الأخطاء."
        except Exception as e:
            return False, f"تنبيه حول بنية الملف: {str(e)}"

    @staticmethod
    def repair_pdf(input_path: str, output_path: str) -> Tuple[bool, str]:
        try:
            # Rebuild xref and streams via pikepdf
            with pikepdf.open(input_path, recover=True) as pdf:
                pdf.save(output_path, recompress_flate=True)
            return True, "تم إصلاح وإعادة بناء جداول وملفات المستند بنجاح."
        except Exception as e:
            return False, f"فشل في إصلاح الملف: {str(e)}"
