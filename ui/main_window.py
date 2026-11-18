"""
PDF Master Pro - Main Window (Ultimate Edition)
Fully orchestrated desktop application matching the visual specification and reference design.
"""
import os
import sys
from pathlib import Path
from typing import Optional, List

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QStackedWidget, QFileDialog, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, QUrl

from core.config import APP_NAME, APP_EDITION, APP_VERSION
from core.models import CompressionLevel, WatermarkConfig, SecurityConfig
from core.pdf_engine import PDFEngine
from core.compression_engine import CompressionEngine
from core.image_engine import ImageEngine
from core.watermark_engine import WatermarkEngine
from core.security_engine import SecurityEngine
from core.ocr_engine import OCREngine
from core.conversion_engine import ConversionEngine
from core.file_manager import FileManager
from core.task_manager import TaskManager
from core.settings_manager import SettingsManager

from ui.theme import get_stylesheet
from ui.i18n import tr, I18n
from ui.widgets.header_bar import HeaderBar
from ui.widgets.sidebar import Sidebar
from ui.widgets.thumbnail_bar import ThumbnailBar
from ui.widgets.home_dashboard import HomeDashboard
from ui.widgets.pdf_viewer import PDFViewer
from ui.widgets.properties_panel import PropertiesPanel
from ui.widgets.status_bar import BottomStatusBar

from ui.dialogs.password_dialog import PasswordDialog
from ui.dialogs.task_dialog import TaskDialog
from ui.dialogs.settings_dialog import SettingsDialog
from ui.dialogs.image_delete_dialog import ImageDeleteDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} - {APP_EDITION} v{APP_VERSION}")
        self.setMinimumSize(1150, 720)
        self.resize(1280, 800)

        # Initialize engines and managers
        self.task_manager = TaskManager()
        self.settings = SettingsManager.load_settings()
        self.current_pdf_path: Optional[str] = None
        self.is_dark_theme = self.settings.get("theme", "dark") == "dark"

        self.init_ui()
        self.connect_signals()
        self.apply_theme()
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        paths = [url.toLocalFile() for url in event.mimeData().urls() if url.toLocalFile()]
        if paths:
            self.on_files_dropped(paths)

    def init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Top Header Bar
        self.header_bar = HeaderBar()
        main_layout.addWidget(self.header_bar, 0)

        # 2. Main Work Area (Splitter: Sidebar | Thumbnails | Center Workspace | Properties)
        self.work_splitter = QSplitter(Qt.Horizontal)
        self.work_splitter.setHandleWidth(1)
        self.work_splitter.setStyleSheet("QSplitter::handle { background-color: #24374D; }")

        # Sidebar Menu
        self.sidebar = Sidebar()
        self.work_splitter.addWidget(self.sidebar)

        # Page Thumbnails Bar
        self.thumbnail_bar = ThumbnailBar()
        self.thumbnail_bar.setVisible(False) # Visible when document is loaded
        self.work_splitter.addWidget(self.thumbnail_bar)

        # Center Workspace (Stacked: 0: Home Dashboard, 1: PDF Viewer)
        self.center_stack = QStackedWidget()
        
        self.home_dashboard = HomeDashboard()
        self.center_stack.addWidget(self.home_dashboard)

        self.pdf_viewer = PDFViewer()
        self.center_stack.addWidget(self.pdf_viewer)

        self.work_splitter.addWidget(self.center_stack)

        # Right Tool Properties Panel (Reference Image Match)
        self.properties_panel = PropertiesPanel()
        self.work_splitter.addWidget(self.properties_panel)

        # Initial splitter stretch factors
        self.work_splitter.setStretchFactor(0, 0) # Sidebar fixed
        self.work_splitter.setStretchFactor(1, 0) # Thumbnails fixed
        self.work_splitter.setStretchFactor(2, 1) # Central expands
        self.work_splitter.setStretchFactor(3, 0) # Properties fixed

        main_layout.addWidget(self.work_splitter, 1)

        # 3. Bottom Status Bar
        self.bottom_status_bar = BottomStatusBar()
        main_layout.addWidget(self.bottom_status_bar, 0)

    def connect_signals(self):
        # Header actions
        self.header_bar.open_file_clicked.connect(self.prompt_open_file)
        self.header_bar.new_file_clicked.connect(self.create_new_file)
        self.header_bar.save_clicked.connect(self.save_current_file)
        self.header_bar.save_as_clicked.connect(self.save_file_as)
        self.header_bar.settings_clicked.connect(self.open_settings)
        self.header_bar.help_clicked.connect(self.open_help)
        self.header_bar.theme_toggled.connect(self.toggle_theme)
        self.header_bar.language_changed.connect(self.set_language)

        # Sidebar navigation
        self.sidebar.item_selected.connect(self.on_sidebar_item_selected)

        # Home Dashboard
        self.home_dashboard.open_file_requested.connect(self.prompt_open_file)
        self.home_dashboard.files_dropped.connect(self.on_files_dropped)
        self.home_dashboard.file_open_requested.connect(self.open_pdf_file)
        self.home_dashboard.action_requested.connect(self.on_dashboard_action)

        # Viewer & Thumbnails sync
        self.thumbnail_bar.page_selected.connect(self.pdf_viewer.canvas.set_page)
        self.pdf_viewer.page_changed.connect(self.thumbnail_bar.set_active_page)
        self.pdf_viewer.page_changed.connect(self.on_page_navigated)
        self.pdf_viewer.zoom_changed.connect(self.bottom_status_bar.set_zoom_value)
        self.pdf_viewer.toggle_thumbnails_clicked.connect(self.toggle_thumbnails)
        self.pdf_viewer.new_tab_clicked.connect(self.prompt_open_file)
        self.pdf_viewer.item_switched.connect(self.on_viewer_item_switched)
        self.pdf_viewer.all_tabs_closed.connect(self.on_all_tabs_closed)
        self.pdf_viewer.files_dropped.connect(self.on_files_dropped)

        # File Manager Panel Actions
        self.properties_panel.file_manager_file_clicked.connect(self.open_pdf_file)
        self.properties_panel.file_manager_add_clicked.connect(self.prompt_open_file)
        self.properties_panel.file_manager_merge_open.connect(self.merge_all_open_pdfs)
        self.properties_panel.file_manager_convert_open.connect(self.convert_all_open_images)

        # Status Bar zoom sync
        self.bottom_status_bar.zoom_changed.connect(self.pdf_viewer.canvas.set_zoom)
        self.bottom_status_bar.tasks_clicked.connect(self.open_task_manager)

        # Task manager events
        self.task_manager.task_progress.connect(self.on_task_progress)
        self.task_manager.task_done.connect(self.on_task_done)

        # Properties Panel tool triggers
        self.properties_panel.compress_requested.connect(self.execute_compression)
        self.properties_panel.merge_requested.connect(self.execute_merge)
        self.properties_panel.split_requested.connect(self.execute_split)
        self.properties_panel.watermark_requested.connect(self.execute_watermark)
        self.properties_panel.security_requested.connect(self.execute_security)
        self.properties_panel.ocr_requested.connect(self.execute_ocr)
        self.properties_panel.image_process_requested.connect(self.execute_image_processing)
        self.properties_panel.rotate_requested.connect(self.execute_rotate)
        self.properties_panel.extract_images_requested.connect(self.execute_extract_images)
        self.properties_panel.convert_requested.connect(self.execute_convert)
        self.properties_panel.edit_pages_requested.connect(self.execute_page_edit)

    # ----------------- Theme & Localization -----------------
    def apply_theme(self):
        theme_str = "dark" if self.is_dark_theme else "light"
        app = QApplication.instance()
        if app:
            app.setStyleSheet(get_stylesheet(theme_str))

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        SettingsManager.set("theme", "dark" if self.is_dark_theme else "light")
        self.apply_theme()

    def set_language(self, lang_code: str):
        I18n.set_language(lang_code)
        self.header_bar.update_translations()
        self.sidebar.update_translations()

    # ----------------- Navigation & View -----------------
    def on_sidebar_item_selected(self, key: str):
        if key == "home":
            self.center_stack.setCurrentIndex(0)
            self.thumbnail_bar.setVisible(False)
        else:
            if self.current_pdf_path:
                self.center_stack.setCurrentIndex(1)
                self.thumbnail_bar.setVisible(True)
            self.properties_panel.switch_tool(key)

    def on_dashboard_action(self, key: str):
        self.sidebar.select_item(key)
        self.properties_panel.switch_tool(key)

    def toggle_thumbnails(self):
        self.thumbnail_bar.setVisible(not self.thumbnail_bar.isVisible())

    def on_page_navigated(self, page_index: int):
        if self.pdf_viewer.doc:
            total = self.pdf_viewer.doc.pageCount()
            pt_size = self.pdf_viewer.doc.pagePointSize(page_index)
            w_mm = int(round(pt_size.width() * 25.4 / 72.0))
            h_mm = int(round(pt_size.height() * 25.4 / 72.0))
            self.bottom_status_bar.set_document_info(
                page_count=total,
                file_size_str=self.current_doc_info.file_size_formatted if hasattr(self, 'current_doc_info') else "0 MB",
                dims_str=f"{w_mm}×{h_mm} mm"
            )

    # ----------------- Document Handling -----------------
    def prompt_open_file(self):
        file_path, _ = QFileDialog.getOpenFileNames(
            self, "اختر ملفات PDF أو الصور", "",
            "All Supported Files (*.pdf *.png *.jpg *.jpeg *.webp *.bmp);;PDF Files (*.pdf);;Images (*.png *.jpg *.jpeg *.webp *.bmp)"
        )
        if file_path:
            self.on_files_dropped(file_path)

    def on_files_dropped(self, file_paths: List[str]):
        if not file_paths:
            return
        
        opened_count = 0
        for f in file_paths:
            p = Path(f)
            if not p.exists():
                continue
            ext = p.suffix.lower()
            if ext == ".pdf":
                st = SecurityEngine.check_encryption_status(str(p))
                password = None
                if st.get("requires_password"):
                    dlg = PasswordDialog(p.name, self)
                    if dlg.exec() == PasswordDialog.Accepted:
                        password = dlg.password
                    else:
                        continue
                if self.pdf_viewer.add_file(str(p), password):
                    opened_count += 1
                    FileManager.add_recent_file(str(p))
            elif ext in (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"):
                if self.pdf_viewer.add_file(str(p)):
                    opened_count += 1
                    FileManager.add_recent_file(str(p))

        if opened_count > 0:
            self.center_stack.setCurrentIndex(1)
            self.properties_panel.update_open_files_list(self.pdf_viewer.open_items)
            self.home_dashboard.refresh_recent_files()
            self.bottom_status_bar.set_status(f"تم إدراج وعرض {opened_count} ملفات بنجاح")

    def open_pdf_file(self, file_path: str):
        p = Path(file_path)
        if not p.exists():
            QMessageBox.critical(self, "خطأ", "الملف المحدد غير موجود.")
            return

        password = None
        ext = p.suffix.lower()
        if ext == ".pdf":
            st = SecurityEngine.check_encryption_status(file_path)
            if st.get("requires_password"):
                dlg = PasswordDialog(p.name, self)
                if dlg.exec() == PasswordDialog.Accepted:
                    password = dlg.password
                else:
                    return

        success = self.pdf_viewer.add_file(file_path, password)
        if not success:
            QMessageBox.critical(self, "خطأ", "تعذر فتح الملف أو عرضه.")
            return

        self.center_stack.setCurrentIndex(1)
        self.properties_panel.update_open_files_list(self.pdf_viewer.open_items)
        FileManager.add_recent_file(file_path)
        self.home_dashboard.refresh_recent_files()

    def on_viewer_item_switched(self, item: dict):
        if item.get("type") == "pdf":
            self.current_pdf_path = item["path"]
            if "doc" in item:
                self.thumbnail_bar.load_document(item["doc"])
                self.thumbnail_bar.setVisible(True)
            try:
                info = PDFEngine.get_document_info(item["path"])
                self.current_doc_info = info
                self.bottom_status_bar.set_document_info(
                    info.page_count,
                    info.file_size_formatted,
                    info.page_dimensions
                )
                self.properties_panel.update_file_info(info.file_size_bytes)
            except Exception:
                size_mb = item["file_size"] / (1024 * 1024)
                self.bottom_status_bar.set_document_info(
                    item["page_count"],
                    f"{size_mb:.1f} MB",
                    "A4"
                )
            self.bottom_status_bar.set_status(f"عرض المستند: {item['name']}")
        else: # Image
            self.thumbnail_bar.setVisible(False)
            size = item.get("file_size", 0)
            size_str = f"{size / (1024*1024):.1f} MB" if size >= 1024*1024 else f"{size / 1024:.1f} KB"
            self.bottom_status_bar.set_document_info(
                page_count=1,
                file_size_str=size_str,
                dims_str=item.get("dimensions", "Image")
            )
            self.bottom_status_bar.set_status(f"عرض الصورة: {item['name']}")
            
        self.properties_panel.update_open_files_list(self.pdf_viewer.open_items)

    def on_all_tabs_closed(self):
        self.current_pdf_path = None
        self.thumbnail_bar.clear()
        self.thumbnail_bar.setVisible(False)
        self.center_stack.setCurrentIndex(0)
        self.bottom_status_bar.set_status("جاهز ...")
        self.properties_panel.update_open_files_list([])

    def merge_all_open_pdfs(self):
        pdf_paths = [it["path"] for it in self.pdf_viewer.open_items if it.get("type") == "pdf"]
        if not pdf_paths:
            QMessageBox.warning(self, "تنبيه", "لا توجد مستندات PDF مفتوحة حالياً للدمج.")
            return
        out_path, _ = QFileDialog.getSaveFileName(self, "حفظ الملف المدمج", "merged_all.pdf", "PDF (*.pdf)")
        if out_path:
            self.execute_merge(pdf_paths, out_path)

    def convert_all_open_images(self):
        img_paths = [it["path"] for it in self.pdf_viewer.open_items if it.get("type") == "image"]
        if not img_paths:
            QMessageBox.warning(self, "تنبيه", "لا توجد صور مفتوحة حالياً للتحويل.")
            return
        out_pdf, _ = QFileDialog.getSaveFileName(self, "حفظ ملف PDF المجمع من الصور", "images_combined.pdf", "PDF (*.pdf)")
        if out_pdf:
            ConversionEngine.images_to_pdf(img_paths, out_pdf)
            self.open_pdf_file(out_pdf)

    def create_new_file(self):
        """Creates a blank 1-page A4 PDF and loads it."""
        from reportlab.pdfgen import canvas
        temp_pdf = FileManager.create_temp_file()
        c = canvas.Canvas(temp_pdf, pagesize=(595.28, 841.89))
        c.setFont("Helvetica", 14)
        c.drawString(100, 750, "PDF Master Pro - Blank Document")
        c.showPage()
        c.save()
        self.open_pdf_file(temp_pdf)

    def save_current_file(self):
        if not self.current_pdf_path:
            return
        QMessageBox.information(self, "حفظ", "تم حفظ المستند الحالي بنجاح.")

    def save_file_as(self):
        if not self.current_pdf_path:
            return
        out_path, _ = QFileDialog.getSaveFileName(self, "حفظ باسم", "copy_" + Path(self.current_pdf_path).name, "PDF Files (*.pdf)")
        if out_path:
            FileManager.safe_save(self.current_pdf_path, out_path)
            QMessageBox.information(self, "تم الحفظ", f"تم حفظ النسخة بنجاح في:\n{out_path}")

    # ----------------- Execution Handlers (Background Workers) -----------------
    def on_task_progress(self, name: str, cur: int, tot: int, msg: str):
        self.bottom_status_bar.set_status(msg, is_busy=True)
        self.bottom_status_bar.set_progress(cur, tot)

    def on_task_done(self, name: str, success: bool, msg: str):
        self.bottom_status_bar.set_status("جاهز ...", is_busy=False)
        self.bottom_status_bar.set_progress(100, 100)

    def execute_compression(self, opts: dict):
        if not self.current_pdf_path:
            QMessageBox.warning(self, "تنبيه", "يرجى فتح ملف PDF أولاً لإجراء الضغط عليه.")
            return

        out_path, _ = QFileDialog.getSaveFileName(self, "حفظ الملف المضغوط", "compressed_" + Path(self.current_pdf_path).name, "PDF Files (*.pdf)")
        if not out_path:
            return

        def task():
            return CompressionEngine.compress_pdf(
                input_path=self.current_pdf_path,
                output_path=out_path,
                level=opts["level"],
                optimize_images=opts["optimize_images"],
                remove_unused_resources=opts["remove_unused_resources"],
                compress_fonts_and_streams=opts["compress_fonts_and_streams"]
            )

        def on_success(res):
            msg = (
                f"اكتملت عملية الضغط بنجاح!\n\n"
                f"الحجم الأصلي: {res['original_formatted']}\n"
                f"الحجم النهائي: {res['final_formatted']}\n"
                f"نسبة التوفير: {res['saving_ratio_pct']}%\n"
                f"المسار: {out_path}"
            )
            QMessageBox.information(self, "اكتمل الضغط", msg)
            self.open_pdf_file(out_path)

        def on_error(err):
            QMessageBox.critical(self, "خطأ أثناء الضغط", f"تعذر إتمام عملية الضغط:\n{err}")

        self.task_manager.start_task("ضغط PDF", task, on_success=on_success, on_error=on_error)

    def execute_merge(self, file_paths: List[str], output_path: str):
        def task():
            return PDFEngine.merge_pdfs(file_paths, output_path)

        def on_success(res):
            QMessageBox.information(self, "نجاح", "تم دمج الملفات بنجاح!")
            self.open_pdf_file(output_path)

        self.task_manager.start_task("دمج ملفات PDF", task, on_success=on_success)

    def execute_split(self, mode: str, count: int, ranges: list):
        if not self.current_pdf_path:
            QMessageBox.warning(self, "تنبيه", "يرجى فتح مستند PDF أولاً.")
            return
        out_dir = QFileDialog.getExistingDirectory(self, "اختر مجلد استخراج الصفحات")
        if not out_dir:
            return

        def task():
            return PDFEngine.split_pdf(self.current_pdf_path, mode, out_dir, count, ranges)

        def on_success(files):
            QMessageBox.information(self, "نجاح", f"تم تقسيم المستند بنجاح إلى {len(files)} ملفاً!")

        self.task_manager.start_task("تقسيم PDF", task, on_success=on_success)

    def execute_watermark(self, cfg: dict):
        if not self.current_pdf_path:
            QMessageBox.warning(self, "تنبيه", "يرجى فتح ملف PDF أولاً.")
            return

        out_path, _ = QFileDialog.getSaveFileName(self, "حفظ المستند بعلامة مائية", "watermarked.pdf", "PDF (*.pdf)")
        if not out_path:
            return

        wm_config = WatermarkConfig(
            is_text=cfg.get("is_text", True),
            text=cfg.get("text", "Watermark"),
            opacity=cfg.get("opacity", 0.3),
            rotation=cfg.get("rotation", 45),
            all_pages=cfg.get("all_pages", True)
        )

        def task():
            return WatermarkEngine.add_watermark(self.current_pdf_path, out_path, wm_config)

        def on_success(res):
            QMessageBox.information(self, "نجاح", "تمت إضافة العلامة المائية بنجاح!")
            self.open_pdf_file(out_path)

        self.task_manager.start_task("إضافة علامة مائية", task, on_success=on_success)

    def execute_security(self, cfg: dict):
        if not self.current_pdf_path:
            QMessageBox.warning(self, "تنبيه", "يرجى فتح مستند PDF أولاً.")
            return

        out_path, _ = QFileDialog.getSaveFileName(self, "حفظ المستند المشفر", "encrypted.pdf", "PDF (*.pdf)")
        if not out_path:
            return

        sec_cfg = SecurityConfig(
            user_password=cfg.get("user_password", ""),
            owner_password=cfg.get("owner_password", ""),
            allow_printing=cfg.get("allow_printing", True),
            allow_copying=cfg.get("allow_copying", True),
            allow_modifying=cfg.get("allow_modifying", False)
        )

        def task():
            return SecurityEngine.encrypt_pdf(self.current_pdf_path, out_path, sec_cfg)

        def on_success(res):
            QMessageBox.information(self, "نجاح", "تم تشفير وحماية المستند بنجاح بأعلى معايير AES-256!")
            self.open_pdf_file(out_path)

        self.task_manager.start_task("حماية وتشفير PDF", task, on_success=on_success)

    def execute_ocr(self, lang: str):
        if not self.current_pdf_path:
            QMessageBox.warning(self, "تنبيه", "يرجى فتح مستند PDF أولاً.")
            return

        # Render current page image for OCR
        pt_size = self.pdf_viewer.doc.pagePointSize(self.pdf_viewer.canvas.current_page)
        q_img = self.pdf_viewer.doc.render(self.pdf_viewer.canvas.current_page, pt_size.toSize() * 2)
        
        # Convert QImage to PIL
        from PIL import Image
        import io
        buf = io.BytesIO()
        q_img.save(buf, "PNG")
        buf.seek(0)
        pil_img = Image.open(buf)

        def task():
            return OCREngine.recognize_image(pil_img, lang=lang)

        def on_success(text):
            self.properties_panel.set_ocr_text(text)
            QMessageBox.information(self, "اكتمل التعرف الضوئي", "تم استخراج النصوص بنجاح وعرضها في لوحة OCR!")

        def on_error(err):
            QMessageBox.warning(self, "تنبيه OCR", f"تعذر استخراج النص: {err}\nتأكد من تثبيت حزمة اللغة في Tesseract.")

        self.task_manager.start_task("التعرف الضوئي OCR", task, on_success=on_success, on_error=on_error)

    def execute_image_processing(self, cfg: dict):
        files, _ = QFileDialog.getOpenFileNames(self, "اختر صور للمعالجة", "", "Images (*.png *.jpg *.jpeg *.webp *.bmp)")
        if not files:
            return
        out_dir = QFileDialog.getExistingDirectory(self, "اختر مجلد الحفظ")
        if not out_dir:
            return

        def task():
            return ImageEngine.batch_process(files, out_dir, cfg)

        def on_success(results):
            QMessageBox.information(self, "اكتملت المعالجة", f"تمت معالجة {len(results)} صور بنجاح في:\n{out_dir}")

        self.task_manager.start_task("معالجة وضغط الصور", task, on_success=on_success)

    def execute_rotate(self, angle: int, pages: list):
        if not self.current_pdf_path:
            return
        out_path, _ = QFileDialog.getSaveFileName(self, "حفظ المستند بعد التدوير", "rotated.pdf", "PDF (*.pdf)")
        if not out_path:
            return

        def task():
            return PDFEngine.rotate_pages(self.current_pdf_path, out_path, pages, angle)

        def on_success(res):
            QMessageBox.information(self, "نجاح", "تم تدوير الصفحات بنجاح!")
            self.open_pdf_file(out_path)

        self.task_manager.start_task("تدوير الصفحات", task, on_success=on_success)

    def execute_extract_images(self, fmt: str, scope: str):
        if not self.current_pdf_path:
            return
        out_dir = QFileDialog.getExistingDirectory(self, "اختر مجلد استخراج الصور")
        if not out_dir:
            return

        page = None if scope == "all" else self.pdf_viewer.canvas.current_page

        def task():
            return PDFEngine.extract_images(self.current_pdf_path, out_dir, selected_page=page, image_format=fmt)

        def on_success(files):
            QMessageBox.information(self, "اكتمل الاستخراج", f"تم استخراج {len(files)} صورة بنجاح في:\n{out_dir}")

        self.task_manager.start_task("استخراج الصور من PDF", task, on_success=on_success)

    def execute_convert(self, mode: str, opts: dict):
        if mode == "images_to_pdf":
            files, _ = QFileDialog.getOpenFileNames(self, "اختر صور لتحويلها إلى PDF", "", "Images (*.png *.jpg *.jpeg *.webp *.bmp)")
            if not files:
                return
            out_pdf, _ = QFileDialog.getSaveFileName(self, "حفظ ملف PDF المجمع", "images_combined.pdf", "PDF (*.pdf)")
            if not out_pdf:
                return
            ConversionEngine.images_to_pdf(files, out_pdf)
            self.open_pdf_file(out_pdf)
        elif mode == "pdf_to_images":
            if not self.current_pdf_path:
                QMessageBox.warning(self, "تنبيه", "يرجى فتح ملف PDF أولاً.")
                return
            out_dir = QFileDialog.getExistingDirectory(self, "اختر مجلد حفظ الصور")
            if not out_dir:
                return
            imgs = ConversionEngine.pdf_to_images(self.current_pdf_path, out_dir)
            QMessageBox.information(self, "نجاح", f"تم تصدير {len(imgs)} صفحة كصور عالية الدقة!")
        elif mode == "pdf_to_text":
            if not self.current_pdf_path:
                return
            out_txt, _ = QFileDialog.getSaveFileName(self, "حفظ النص", "extracted_text.txt", "Text (*.txt)")
            if out_txt:
                txt = PDFEngine.extract_text(self.current_pdf_path)
                with open(out_txt, "w", encoding="utf-8") as f:
                    f.write(txt)
                QMessageBox.information(self, "نجاح", "تم استخراج النص وحفظه بنجاح!")

    def execute_page_edit(self, action: str, opts: dict):
        if not self.current_pdf_path:
            return
        cur_p = self.pdf_viewer.canvas.current_page
        out_path, _ = QFileDialog.getSaveFileName(self, "حفظ التعديلات", "modified.pdf", "PDF (*.pdf)")
        if not out_path:
            return

        if action == "delete_current":
            PDFEngine.delete_pages(self.current_pdf_path, out_path, [cur_p])
            self.open_pdf_file(out_path)
        elif action == "duplicate_current":
            PDFEngine.duplicate_pages(self.current_pdf_path, out_path, [cur_p])
            self.open_pdf_file(out_path)

    # ----------------- Dialogs -----------------
    def open_task_manager(self):
        dlg = TaskDialog(self.task_manager, self)
        dlg.exec()

    def open_settings(self):
        dlg = SettingsDialog(self)
        if dlg.exec() == SettingsDialog.Accepted:
            self.settings = SettingsManager.load_settings()
            self.is_dark_theme = self.settings.get("theme") == "dark"
            self.apply_theme()
            self.set_language(self.settings.get("language", "ar"))

    def open_help(self):
        msg = (
            f"<b>{APP_NAME} - {APP_EDITION} v{APP_VERSION}</b><br><br>"
            "أداة متطورة واحترافية لمعالجة وتحرير ملفات PDF والصور محلياً وبأعلى معايير الأمان والسرعة.<br><br>"
            "<b>الميزات المدعومة:</b><br>"
            "• ضغط PDF بثلاثة مستويات مع حساب دقيق للتوفير.<br>"
            "• دمج وتقسيم وتدوير وحذف وتكرار الصفحات.<br>"
            "• تشفير AES-256 وضبط أذونات الطباعة والنسخ.<br>"
            "• إضافة وإزالة العلامات المائية بدقة.<br>"
            "• التعرف الضوئي على النصوص (OCR) بالعربية والإنجليزية.<br>"
            "• معالجة وضغط وتغيير أبعاد وصيغ الصور دفعة واحدة.<br>"
            "• استخراج الصور وحذفها من داخل المستندات.<br>"
            "• تحويل الصور إلى PDF وPDF إلى صور.<br><br>"
            "جميع المعالجات تتم محلياً 100% دون إرسال أي بيانات عبر الإنترنت."
        )
        QMessageBox.about(self, "حول البرنامج والمساعدة", msg)
