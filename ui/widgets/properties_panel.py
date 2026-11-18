"""
PDF Master Pro - Tool Properties Panel
Dynamic right panel that visually adapts to the active tool.
Specifically reproduces the exact design of the PDF Compression options from the reference visual!
"""
from typing import Dict, Any, Optional
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox,
    QFrame, QStackedWidget, QLineEdit, QSpinBox, QComboBox, QFileDialog,
    QListWidget, QListWidgetItem, QTextEdit, QRadioButton, QButtonGroup, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from ui.i18n import tr
from core.models import CompressionLevel

class CompressionCard(QFrame):
    selected = Signal(CompressionLevel)

    def __init__(self, level: CompressionLevel, icon: str, title: str, desc: str, is_active: bool = False, parent=None):
        super().__init__(parent)
        self.level = level
        self.is_active = is_active
        self.setObjectName("CompCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumWidth(90)
        self.init_ui(icon, title, desc)

    def init_ui(self, icon: str, title: str, desc: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 10, 4, 10)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(3)

        icon_lbl = QLabel(icon)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 22px;")
        layout.addWidget(icon_lbl)

        title_lbl = QLabel(title)
        title_lbl.setAlignment(Qt.AlignCenter)
        title_lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(title_lbl)

        desc_lbl = QLabel(desc)
        desc_lbl.setAlignment(Qt.AlignCenter)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("font-size: 11px; color: #94A3B8;")
        layout.addWidget(desc_lbl)

        self.update_selection(self.is_active)

    def update_selection(self, active: bool):
        self.is_active = active
        self.setProperty("selected", "true" if active else "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selected.emit(self.level)
        super().mousePressEvent(event)

class PropertiesPanel(QWidget):
    # Signals for tool executions
    compress_requested = Signal(dict)
    merge_requested = Signal(list, str)
    split_requested = Signal(str, int, list)
    watermark_requested = Signal(dict)
    security_requested = Signal(dict)
    ocr_requested = Signal(str)
    image_process_requested = Signal(dict)
    rotate_requested = Signal(int, list)
    extract_images_requested = Signal(str, str)
    convert_requested = Signal(str, dict)
    edit_pages_requested = Signal(str, dict)
    file_manager_file_clicked = Signal(str)
    file_manager_add_clicked = Signal()
    file_manager_merge_open = Signal()
    file_manager_convert_open = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PropertiesPanel")
        self.setFixedWidth(340)
        self.current_file_size = 12.5 * 1024 * 1024 # default demo size
        self.selected_comp_level = CompressionLevel.MEDIUM
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(12)

        # Title bar with Wrench icon
        self.header_layout = QHBoxLayout()
        self.tool_icon = QLabel("🔧")
        self.tool_icon.setStyleSheet("font-size: 20px;")
        self.header_layout.addWidget(self.tool_icon)

        self.tool_title = QLabel(tr("compression_panel_title"))
        self.tool_title.setObjectName("PropertiesPanelTitle")
        self.header_layout.addWidget(self.tool_title)
        self.header_layout.addStretch()

        main_layout.addLayout(self.header_layout)

        # Stacked pages for each sidebar section
        self.stack = QStackedWidget()
        
        # 0: Compression Page (Exact visual match to reference image)
        self.comp_page = self.create_compression_page()
        self.stack.addWidget(self.comp_page)

        # 1: Split & Merge Page
        self.split_merge_page = self.create_split_merge_page()
        self.stack.addWidget(self.split_merge_page)

        # 2: Watermark Page
        self.watermark_page = self.create_watermark_page()
        self.stack.addWidget(self.watermark_page)

        # 3: Security & Password Page
        self.security_page = self.create_security_page()
        self.stack.addWidget(self.security_page)

        # 4: OCR Page
        self.ocr_page = self.create_ocr_page()
        self.stack.addWidget(self.ocr_page)

        # 5: Image Compression Page
        self.img_page = self.create_image_page()
        self.stack.addWidget(self.img_page)

        # 6: Rotate Page
        self.rotate_page = self.create_rotate_page()
        self.stack.addWidget(self.rotate_page)

        # 7: Extract Images Page
        self.extract_img_page = self.create_extract_img_page()
        self.stack.addWidget(self.extract_img_page)

        # 8: Convert Page
        self.convert_page = self.create_convert_page()
        self.stack.addWidget(self.convert_page)

        # 9: Edit PDF Page
        self.edit_page = self.create_edit_page()
        self.stack.addWidget(self.edit_page)

        # 10: File Manager Page
        self.file_manager_page = self.create_file_manager_page()
        self.stack.addWidget(self.file_manager_page)

        main_layout.addWidget(self.stack)

    # ----------------- 0: Compression View (Reference Image) -----------------
    def create_compression_page(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # "مستوى الضغط:"
        lbl_level = QLabel(tr("compression_level_label"))
        lbl_level.setStyleSheet("font-weight: bold; font-size: 13px; color: #FFFFFF;")
        layout.addWidget(lbl_level)

        # 3 Cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(8)

        self.card_light = CompressionCard(CompressionLevel.LIGHT, "🍃", tr("comp_light_title"), tr("comp_light_desc"), False)
        self.card_medium = CompressionCard(CompressionLevel.MEDIUM, "⚖️", tr("comp_medium_title"), tr("comp_medium_desc"), True)
        self.card_strong = CompressionCard(CompressionLevel.STRONG, "🚀", tr("comp_strong_title"), tr("comp_strong_desc"), False)

        self.card_light.selected.connect(self.set_compression_level)
        self.card_medium.selected.connect(self.set_compression_level)
        self.card_strong.selected.connect(self.set_compression_level)

        cards_layout.addWidget(self.card_light)
        cards_layout.addWidget(self.card_medium)
        cards_layout.addWidget(self.card_strong)
        layout.addLayout(cards_layout)

        # Advanced options
        lbl_adv = QLabel(tr("advanced_options"))
        lbl_adv.setStyleSheet("font-weight: bold; font-size: 13px; color: #FFFFFF; margin-top: 10px;")
        layout.addWidget(lbl_adv)

        self.chk_optimize_imgs = QCheckBox(tr("opt_optimize_images"))
        self.chk_optimize_imgs.setChecked(True)
        layout.addWidget(self.chk_optimize_imgs)

        self.chk_remove_unused = QCheckBox(tr("opt_remove_unused"))
        self.chk_remove_unused.setChecked(True)
        layout.addWidget(self.chk_remove_unused)

        self.chk_compress_fonts = QCheckBox(tr("opt_compress_fonts"))
        self.chk_compress_fonts.setChecked(False)
        layout.addWidget(self.chk_compress_fonts)

        layout.addSpacing(10)

        # Stats Box (Exact visual match from reference image)
        self.stats_box = QFrame()
        self.stats_box.setObjectName("StatsBox")
        box_layout = QVBoxLayout(self.stats_box)
        box_layout.setSpacing(8)

        self.stat_orig = QLabel(f"ℹ️ {tr('original_size')} 12.5 MB")
        self.stat_orig.setStyleSheet("font-size: 13px; color: #CBD5E1;")
        box_layout.addWidget(self.stat_orig)

        self.stat_expected = QLabel(f"📉 {tr('expected_size')} 3.8 MB")
        self.stat_expected.setStyleSheet("font-size: 13px; color: #CBD5E1;")
        box_layout.addWidget(self.stat_expected)

        self.stat_ratio = QLabel(f"✅ {tr('saving_ratio')} 70%")
        self.stat_ratio.setStyleSheet("font-size: 13px; font-weight: bold; color: #34D399;")
        box_layout.addWidget(self.stat_ratio)

        layout.addWidget(self.stats_box)

        layout.addStretch()

        # Big Action Button "بدء الضغط ⚡"
        self.btn_start_compress = QPushButton(tr("start_compression_btn"))
        self.btn_start_compress.setObjectName("BigActionBtn")
        self.btn_start_compress.setCursor(Qt.PointingHandCursor)
        self.btn_start_compress.clicked.connect(self.on_start_compression)
        layout.addWidget(self.btn_start_compress)

        return widget

    def set_compression_level(self, level: CompressionLevel):
        self.selected_comp_level = level
        self.card_light.update_selection(level == CompressionLevel.LIGHT)
        self.card_medium.update_selection(level == CompressionLevel.MEDIUM)
        self.card_strong.update_selection(level == CompressionLevel.STRONG)
        self.update_compression_stats()

    def update_file_info(self, size_bytes: int):
        self.current_file_size = size_bytes
        self.update_compression_stats()

    def update_compression_stats(self):
        from core.compression_engine import CompressionEngine
        est = CompressionEngine.estimate_compression(self.current_file_size, self.selected_comp_level)
        self.stat_orig.setText(f"ℹ️ {tr('original_size')} {est['original_formatted']}")
        self.stat_expected.setText(f"📉 {tr('expected_size')} {est['expected_final_formatted']}")
        self.stat_ratio.setText(f"✅ {tr('saving_ratio')} {est['saving_ratio_pct']}%")

    def on_start_compression(self):
        opts = {
            "level": self.selected_comp_level,
            "optimize_images": self.chk_optimize_imgs.isChecked(),
            "remove_unused_resources": self.chk_remove_unused.isChecked(),
            "compress_fonts_and_streams": self.chk_compress_fonts.isChecked()
        }
        self.compress_requested.emit(opts)

    # ----------------- 1: Split & Merge -----------------
    def create_split_merge_page(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        # Tabs for Split vs Merge
        sub_tab = QHBoxLayout()
        self.btn_tab_merge = QPushButton("📑 دمج ملفات")
        self.btn_tab_split = QPushButton("✂️ تقسيم مستند")
        sub_tab.addWidget(self.btn_tab_merge)
        sub_tab.addWidget(self.btn_tab_split)
        layout.addLayout(sub_tab)

        self.sub_stack = QStackedWidget()
        
        # Merge sub-view
        merge_w = QWidget()
        mlayout = QVBoxLayout(merge_w)
        mlayout.addWidget(QLabel("ملفات PDF المراد دمجها:"))
        self.merge_list = QListWidget()
        mlayout.addWidget(self.merge_list)
        
        m_btns = QHBoxLayout()
        self.btn_add_merge_file = QPushButton("➕ إضافة ملفات")
        self.btn_add_merge_file.clicked.connect(self.on_add_merge_files)
        self.btn_clear_merge = QPushButton("مسح")
        self.btn_clear_merge.clicked.connect(self.merge_list.clear)
        m_btns.addWidget(self.btn_add_merge_file)
        m_btns.addWidget(self.btn_clear_merge)
        mlayout.addLayout(m_btns)

        btn_run_merge = QPushButton("بدء دمج الملفات ⚡")
        btn_run_merge.setObjectName("BigActionBtn")
        btn_run_merge.clicked.connect(self.on_run_merge)
        mlayout.addWidget(btn_run_merge)
        self.sub_stack.addWidget(merge_w)

        # Split sub-view
        split_w = QWidget()
        slayout = QVBoxLayout(split_w)
        slayout.addWidget(QLabel("طريقة التقسيم:"))
        
        self.split_mode_combo = QComboBox()
        self.split_mode_combo.addItems([
            "كل صفحة في ملف مستقل",
            "تقسيم كل عدد محدد من الصفحات",
            "استخراج حسب نطاق الصفحات"
        ])
        slayout.addWidget(self.split_mode_combo)

        slayout.addWidget(QLabel("عدد الصفحات لكل ملف / النطاق:"))
        self.split_val_input = QLineEdit("1")
        slayout.addWidget(self.split_val_input)

        slayout.addStretch()
        btn_run_split = QPushButton("بدء تقسيم الملف ⚡")
        btn_run_split.setObjectName("BigActionBtn")
        btn_run_split.clicked.connect(self.on_run_split)
        slayout.addWidget(btn_run_split)
        self.sub_stack.addWidget(split_w)

        self.btn_tab_merge.clicked.connect(lambda: self.sub_stack.setCurrentIndex(0))
        self.btn_tab_split.clicked.connect(lambda: self.sub_stack.setCurrentIndex(1))

        layout.addWidget(self.sub_stack)
        return widget

    def on_add_merge_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "اختر ملفات PDF للدمج", "", "PDF Files (*.pdf)")
        for f in files:
            item = QListWidgetItem(Path(f).name)
            item.setData(Qt.UserRole, f)
            self.merge_list.addItem(item)

    def on_run_merge(self):
        paths = [self.merge_list.item(i).data(Qt.UserRole) for i in range(self.merge_list.count())]
        if paths:
            out_path, _ = QFileDialog.getSaveFileName(self, "حفظ الملف المدمج", "merged.pdf", "PDF Files (*.pdf)")
            if out_path:
                self.merge_requested.emit(paths, out_path)

    def on_run_split(self):
        idx = self.split_mode_combo.currentIndex()
        modes = ["each_page", "fixed_count", "page_ranges"]
        mode = modes[idx]
        val = self.split_val_input.text().strip()
        count = int(val) if val.isdigit() else 1
        ranges = []
        if mode == "page_ranges":
            # parse 1-3, 4-6
            for part in val.split(","):
                if "-" in part:
                    s, e = part.split("-", 1)
                    if s.strip().isdigit() and e.strip().isdigit():
                        ranges.append((int(s.strip()), int(e.strip())))
        self.split_requested.emit(mode, count, ranges)

    # ----------------- 2: Watermark -----------------
    def create_watermark_page(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        layout.addWidget(QLabel("نوع العلامة:"))
        self.wm_type_combo = QComboBox()
        self.wm_type_combo.addItems(["نصية", "صورة"])
        layout.addWidget(self.wm_type_combo)

        layout.addWidget(QLabel("نص العلامة المائية:"))
        self.wm_text_input = QLineEdit("PDF Master Pro")
        layout.addWidget(self.wm_text_input)

        layout.addWidget(QLabel("درجة الشفافية (0.1 - 1.0):"))
        self.wm_opacity_input = QLineEdit("0.3")
        layout.addWidget(self.wm_opacity_input)

        layout.addWidget(QLabel("زاوية التدوير:"))
        self.wm_rot_combo = QComboBox()
        self.wm_rot_combo.addItems(["45 درجة", "0 (أفقي)", "90 (عمودي)", "-45 درجة"])
        layout.addWidget(self.wm_rot_combo)

        self.wm_all_pages_chk = QCheckBox("تطبيق على جميع الصفحات")
        self.wm_all_pages_chk.setChecked(True)
        layout.addWidget(self.wm_all_pages_chk)

        layout.addStretch()
        btn_apply_wm = QPushButton("تطبيق العلامة المائية 💧")
        btn_apply_wm.setObjectName("BigActionBtn")
        btn_apply_wm.clicked.connect(self.on_apply_watermark)
        layout.addWidget(btn_apply_wm)
        return widget

    def on_apply_watermark(self):
        rot_map = {"45 درجة": 45, "0 (أفقي)": 0, "90 (عمودي)": 90, "-45 درجة": -45}
        cfg = {
            "is_text": self.wm_type_combo.currentIndex() == 0,
            "text": self.wm_text_input.text(),
            "opacity": float(self.wm_opacity_input.text() or 0.3),
            "rotation": rot_map.get(self.wm_rot_combo.currentText(), 45),
            "all_pages": self.wm_all_pages_chk.isChecked()
        }
        self.watermark_requested.emit(cfg)

    # ----------------- 3: Security -----------------
    def create_security_page(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        layout.addWidget(QLabel("تشفير AES-256 وحماية المستند:"))

        layout.addWidget(QLabel("كلمة مرور فتح الملف:"))
        self.sec_user_pass = QLineEdit()
        self.sec_user_pass.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.sec_user_pass)

        layout.addWidget(QLabel("كلمة مرور الصلاحيات / المالك:"))
        self.sec_owner_pass = QLineEdit()
        self.sec_owner_pass.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.sec_owner_pass)

        layout.addWidget(QLabel("الصلاحيات المسموحة:"))
        self.sec_allow_print = QCheckBox("السماح بالطباعة")
        self.sec_allow_print.setChecked(True)
        layout.addWidget(self.sec_allow_print)

        self.sec_allow_copy = QCheckBox("السماح بنسخ النصوص والمحتوى")
        self.sec_allow_copy.setChecked(True)
        layout.addWidget(self.sec_allow_copy)

        self.sec_allow_modify = QCheckBox("السماح بتعديل المستند")
        self.sec_allow_modify.setChecked(False)
        layout.addWidget(self.sec_allow_modify)

        layout.addStretch()
        btn_apply_sec = QPushButton("تشفير وحماية المستند 🔒")
        btn_apply_sec.setObjectName("BigActionBtn")
        btn_apply_sec.clicked.connect(self.on_apply_security)
        layout.addWidget(btn_apply_sec)
        return widget

    def on_apply_security(self):
        cfg = {
            "user_password": self.sec_user_pass.text(),
            "owner_password": self.sec_owner_pass.text(),
            "allow_printing": self.sec_allow_print.isChecked(),
            "allow_copying": self.sec_allow_copy.isChecked(),
            "allow_modifying": self.sec_allow_modify.isChecked()
        }
        self.security_requested.emit(cfg)

    # ----------------- 4: OCR -----------------
    def create_ocr_page(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        layout.addWidget(QLabel("محرك التعرف الضوئي Tesseract OCR:"))
        layout.addWidget(QLabel("لغة المستند:"))
        self.ocr_lang_combo = QComboBox()
        self.ocr_lang_combo.addItem("العربية والإنجليزية (ara+eng)", "ara+eng")
        self.ocr_lang_combo.addItem("العربية فقط (ara)", "ara")
        self.ocr_lang_combo.addItem("الإنجليزية فقط (eng)", "eng")
        layout.addWidget(self.ocr_lang_combo)

        btn_run_ocr = QPushButton("بدء استخراج النصوص OCR 🔤")
        btn_run_ocr.setObjectName("BigActionBtn")
        btn_run_ocr.clicked.connect(self.on_run_ocr)
        layout.addWidget(btn_run_ocr)

        layout.addWidget(QLabel("النص المستخرج:"))
        self.ocr_result_box = QTextEdit()
        self.ocr_result_box.setReadOnly(True)
        layout.addWidget(self.ocr_result_box)

        btn_copy = QPushButton("📋 نسخ النص")
        btn_copy.clicked.connect(self.ocr_result_box.selectAll)
        layout.addWidget(btn_copy)
        return widget

    def on_run_ocr(self):
        lang = self.ocr_lang_combo.currentData()
        self.ocr_requested.emit(lang)

    def set_ocr_text(self, text: str):
        self.ocr_result_box.setPlainText(text)

    # ----------------- 5: Image Compression -----------------
    def create_image_page(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        layout.addWidget(QLabel("معالجة وضغط الصور:"))
        layout.addWidget(QLabel("صيغة التصدير:"))
        self.img_format_combo = QComboBox()
        self.img_format_combo.addItems(["نفس الصيغة الأصلية", "JPEG", "PNG", "WEBP"])
        layout.addWidget(self.img_format_combo)

        layout.addWidget(QLabel("جودة الصورة (1-100):"))
        self.img_quality_spin = QSpinBox()
        self.img_quality_spin.setRange(10, 100)
        self.img_quality_spin.setValue(80)
        layout.addWidget(self.img_quality_spin)

        layout.addWidget(QLabel("تغيير الحجم:"))
        self.img_resize_combo = QComboBox()
        self.img_resize_combo.addItems(["بدون تغيير", "تصغير بنسبة 50%", "تصغير بنسبة 75%", "أقصى بُعد 1920 بكسل"])
        layout.addWidget(self.img_resize_combo)

        layout.addStretch()
        btn_proc_img = QPushButton("بدء معالجة الصور 🖼️")
        btn_proc_img.setObjectName("BigActionBtn")
        btn_proc_img.clicked.connect(self.on_process_images)
        layout.addWidget(btn_proc_img)
        return widget

    def on_process_images(self):
        fmt = self.img_format_combo.currentText()
        if fmt == "نفس الصيغة الأصلية":
            target_fmt = None
        else:
            target_fmt = fmt

        resize_mode = "none"
        scale_pct = 100.0
        max_edge = None
        if "50%" in self.img_resize_combo.currentText():
            resize_mode = "percentage"
            scale_pct = 50.0
        elif "75%" in self.img_resize_combo.currentText():
            resize_mode = "percentage"
            scale_pct = 75.0
        elif "1920" in self.img_resize_combo.currentText():
            resize_mode = "max_edge"
            max_edge = 1920

        cfg = {
            "target_format": target_fmt,
            "quality": self.img_quality_spin.value(),
            "resize_mode": resize_mode,
            "scale_pct": scale_pct,
            "target_width": max_edge
        }
        self.image_process_requested.emit(cfg)

    # ----------------- 6: Rotate -----------------
    def create_rotate_page(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        layout.addWidget(QLabel("تدوير الصفحات والصور:"))
        self.rot_angle_combo = QComboBox()
        self.rot_angle_combo.addItem("90 درجة لليمين ↪️", 90)
        self.rot_angle_combo.addItem("180 درجة 🔄", 180)
        self.rot_angle_combo.addItem("270 درجة لليسار ↩️", 270)
        layout.addWidget(self.rot_angle_combo)

        self.rot_all_chk = QCheckBox("تدوير جميع الصفحات")
        self.rot_all_chk.setChecked(True)
        layout.addWidget(self.rot_all_chk)

        layout.addWidget(QLabel("أو أرقام الصفحات (مفصولة بفواصل):"))
        self.rot_pages_input = QLineEdit("1")
        layout.addWidget(self.rot_pages_input)

        layout.addStretch()
        btn_rot = QPushButton("تطبيق التدوير 🔄")
        btn_rot.setObjectName("BigActionBtn")
        btn_rot.clicked.connect(self.on_apply_rotate)
        layout.addWidget(btn_rot)
        return widget

    def on_apply_rotate(self):
        angle = self.rot_angle_combo.currentData()
        pages = None
        if not self.rot_all_chk.isChecked():
            txt = self.rot_pages_input.text()
            pages = [int(p.strip()) - 1 for p in txt.split(",") if p.strip().isdigit()]
        self.rotate_requested.emit(angle, pages)

    # ----------------- 7: Extract Images -----------------
    def create_extract_img_page(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        layout.addWidget(QLabel("استخراج الصور المضمنة في PDF:"))
        layout.addWidget(QLabel("صيغة الصور المستخرجة:"))
        self.ext_fmt_combo = QComboBox()
        self.ext_fmt_combo.addItems(["PNG", "JPEG", "WEBP"])
        layout.addWidget(self.ext_fmt_combo)

        self.ext_all_pages_chk = QCheckBox("استخراج من كامل المستند")
        self.ext_all_pages_chk.setChecked(True)
        layout.addWidget(self.ext_all_pages_chk)

        layout.addStretch()
        btn_ext = QPushButton("بدء استخراج الصور 🔍")
        btn_ext.setObjectName("BigActionBtn")
        btn_ext.clicked.connect(self.on_extract_images)
        layout.addWidget(btn_ext)
        return widget

    def on_extract_images(self):
        fmt = self.ext_fmt_combo.currentText().lower()
        scope = "all" if self.ext_all_pages_chk.isChecked() else "current"
        self.extract_images_requested.emit(fmt, scope)

    # ----------------- 8: Convert -----------------
    def create_convert_page(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        layout.addWidget(QLabel("التحويل بين الملفات:"))
        self.btn_img_to_pdf = QPushButton("🖼️ تحويل صور إلى PDF")
        self.btn_img_to_pdf.clicked.connect(lambda: self.convert_requested.emit("images_to_pdf", {}))
        layout.addWidget(self.btn_img_to_pdf)

        self.btn_pdf_to_img = QPushButton("📑 تحويل PDF إلى صور")
        self.btn_pdf_to_img.clicked.connect(lambda: self.convert_requested.emit("pdf_to_images", {}))
        layout.addWidget(self.btn_pdf_to_img)

        self.btn_pdf_to_txt = QPushButton("📄 استخراج النص كملف TXT")
        self.btn_pdf_to_txt.clicked.connect(lambda: self.convert_requested.emit("pdf_to_text", {}))
        layout.addWidget(self.btn_pdf_to_txt)

        layout.addStretch()
        return widget

    # ----------------- 9: Edit PDF -----------------
    def create_edit_page(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        layout.addWidget(QLabel("إدارة وتحرير صفحات المستند:"))
        
        btn_del_page = QPushButton("🗑️ حذف الصفحة الحالية")
        btn_del_page.clicked.connect(lambda: self.edit_pages_requested.emit("delete_current", {}))
        layout.addWidget(btn_del_page)

        btn_dup_page = QPushButton("📋 تكرار الصفحة الحالية")
        btn_dup_page.clicked.connect(lambda: self.edit_pages_requested.emit("duplicate_current", {}))
        layout.addWidget(btn_dup_page)

        btn_num_pages = QPushButton("🔢 إضافة أرقام الصفحات")
        btn_num_pages.clicked.connect(lambda: self.edit_pages_requested.emit("add_numbers", {}))
        layout.addWidget(btn_num_pages)

        btn_header_footer = QPushButton("📝 إضافة ترويسة وتذييل")
        btn_header_footer.clicked.connect(lambda: self.edit_pages_requested.emit("add_header_footer", {}))
        layout.addWidget(btn_header_footer)

        layout.addStretch()
        return widget

    # ----------------- 10: File Manager -----------------
    def create_file_manager_page(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        layout.addWidget(QLabel("الملفات المفتوحة في الجلسة الحالية:"))
        self.open_files_list = QListWidget()
        self.open_files_list.itemClicked.connect(self.on_open_file_item_clicked)
        layout.addWidget(self.open_files_list)

        btns = QHBoxLayout()
        btn_add = QPushButton("➕ إضافة ملفات أخرى")
        btn_add.clicked.connect(self.file_manager_add_clicked.emit)
        btns.addWidget(btn_add)
        layout.addLayout(btns)

        btn_merge = QPushButton("📑 دمج ملفات PDF المفتوحة")
        btn_merge.setObjectName("BigActionBtn")
        btn_merge.clicked.connect(self.file_manager_merge_open.emit)
        layout.addWidget(btn_merge)

        btn_conv = QPushButton("🖼️ تحويل الصور المفتوحة إلى PDF")
        btn_conv.clicked.connect(self.file_manager_convert_open.emit)
        layout.addWidget(btn_conv)

        layout.addStretch()
        return widget

    def on_open_file_item_clicked(self, item: QListWidgetItem):
        path = item.data(Qt.UserRole)
        if path:
            self.file_manager_file_clicked.emit(path)

    def update_open_files_list(self, open_items: list):
        self.open_files_list.clear()
        for it in open_items:
            icon = "📄" if it.get("type") == "pdf" else "🖼️"
            extra = f"({it.get('page_count')} صفحة)" if it.get("type") == "pdf" else f"({it.get('dimensions', '')})"
            item = QListWidgetItem(f"{icon} {it.get('name')} {extra}")
            item.setData(Qt.UserRole, it.get("path"))
            self.open_files_list.addItem(item)

    # ----------------- Switch Panel by Tool Key -----------------
    def switch_tool(self, tool_key: str):
        mapping = {
            "compress_pdf": (0, "🗜️", tr("compression_panel_title")),
            "split_merge": (1, "✂️", "خيارات تقسيم ودمج PDF"),
            "watermark": (2, "💧", "خيارات العلامات المائية"),
            "security": (3, "🛡️", "خيارات حماية وتشفير PDF"),
            "ocr": (4, "🔤", "خيارات التعرف الضوئي OCR"),
            "compress_images": (5, "🖼️", "خيارات ضغط ومعالجة الصور"),
            "rotate": (6, "🔄", "خيارات تدوير الصفحات"),
            "extract_images": (7, "🔍", "استخراج الصور من PDF"),
            "convert": (8, "🔁", "خيارات التحويل"),
            "edit_pdf": (9, "✏️", "أدوات تحرير وإدارة الصفحات"),
            "delete_images": (9, "🗑️", "حذف الصور من PDF"),
            "file_manager": (10, "📁", "إدارة الملفات المفتوحة")
        }

        if tool_key in mapping:
            idx, icon, title = mapping[tool_key]
            self.tool_icon.setText(icon)
            self.tool_title.setText(title)
            self.stack.setCurrentIndex(idx)
