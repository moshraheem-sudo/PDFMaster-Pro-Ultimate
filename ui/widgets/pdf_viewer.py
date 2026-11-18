"""
PDF Master Pro - Multi-Format Document & Image Viewer Widget
High-performance native canvas supporting simultaneous PDF documents and Image viewing with tabs.
"""
from typing import Optional, List, Dict, Any
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QScrollArea, QLineEdit, QTabBar, QSpacerItem, QSizePolicy, QFileDialog, QStackedWidget
)
from PySide6.QtCore import Qt, Signal, QSize, QPoint
from PySide6.QtGui import QPixmap, QImage, QWheelEvent, QMouseEvent, QPainter, QTransform
from PySide6.QtPdf import QPdfDocument, QPdfDocumentRenderOptions

from ui.i18n import tr

class DocumentCanvas(QScrollArea):
    page_changed = Signal(int)
    zoom_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mode = "none" # "pdf", "image", "none"
        self.doc: Optional[QPdfDocument] = None
        self.original_pixmap: Optional[QPixmap] = None
        self.current_page = 0
        self.zoom_factor = 1.0 # 100%
        self.rotation_angle = 0
        self.flip_horizontal = False
        
        # Drag to pan
        self.setMouseTracking(True)
        self._is_panning = False
        self._pan_start_pos = QPoint()

        self.init_ui()

    def init_ui(self):
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background-color: #101924; border: none;")

        self.content_label = QLabel()
        self.content_label.setAlignment(Qt.AlignCenter)
        self.content_label.setStyleSheet("background-color: white; border-radius: 6px; box-shadow: 0 4px 10px rgba(0,0,0,0.4);")
        self.setWidget(self.content_label)
        self.setWidgetResizable(True)

    def set_pdf(self, doc: QPdfDocument, initial_page: int = 0):
        self.mode = "pdf"
        self.doc = doc
        self.original_pixmap = None
        self.current_page = initial_page
        self.rotation_angle = 0
        self.flip_horizontal = False
        self.render_content()

    def set_image(self, image_path: str):
        self.mode = "image"
        self.doc = None
        self.original_pixmap = QPixmap(image_path)
        self.current_page = 0
        self.rotation_angle = 0
        self.flip_horizontal = False
        self.render_content()

    def set_page(self, page_index: int):
        if self.mode == "pdf" and self.doc and 0 <= page_index < self.doc.pageCount():
            self.current_page = page_index
            self.render_content()
            self.page_changed.emit(self.current_page)

    def set_zoom(self, zoom_pct: int):
        self.zoom_factor = max(0.15, min(5.0, zoom_pct / 100.0))
        self.render_content()
        self.zoom_changed.emit(int(self.zoom_factor * 100))

    def rotate_image(self, angle_delta: int = 90):
        self.rotation_angle = (self.rotation_angle + angle_delta) % 360
        self.render_content()

    def flip_image_h(self):
        self.flip_horizontal = not self.flip_horizontal
        self.render_content()

    def render_content(self):
        if self.mode == "pdf":
            if not self.doc or self.doc.pageCount() == 0:
                self.content_label.clear()
                return

            pt_size = self.doc.pagePointSize(self.current_page)
            render_opts = QPdfDocumentRenderOptions()
            
            pixel_w = int(pt_size.width() * 1.5 * self.zoom_factor)
            pixel_h = int(pt_size.height() * 1.5 * self.zoom_factor)

            q_img = self.doc.render(self.current_page, QSize(pixel_w, pixel_h), render_opts)
            pixmap = QPixmap.fromImage(q_img)
            self.content_label.setPixmap(pixmap)
            self.content_label.setFixedSize(pixel_w, pixel_h)

        elif self.mode == "image":
            if not self.original_pixmap or self.original_pixmap.isNull():
                self.content_label.clear()
                return

            # Apply transformations (rotation, flip)
            trans = QTransform()
            if self.rotation_angle != 0:
                trans.rotate(self.rotation_angle)
            if self.flip_horizontal:
                trans.scale(-1, 1)

            transformed = self.original_pixmap.transformed(trans, Qt.SmoothTransformation)

            target_w = max(10, int(transformed.width() * self.zoom_factor))
            target_h = max(10, int(transformed.height() * self.zoom_factor))

            scaled_pix = transformed.scaled(
                target_w, target_h,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            self.content_label.setPixmap(scaled_pix)
            self.content_label.setFixedSize(scaled_pix.size())

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            step = 10 if delta > 0 else -10
            self.set_zoom(int(self.zoom_factor * 100) + step)
            event.accept()
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MiddleButton or (event.button() == Qt.LeftButton and event.modifiers() & Qt.AltModifier):
            self._is_panning = True
            self._pan_start_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_panning:
            delta = event.pos() - self._pan_start_pos
            self._pan_start_pos = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._is_panning:
            self._is_panning = False
            self.setCursor(Qt.ArrowCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)

class PDFViewer(QWidget):
    page_changed = Signal(int)
    zoom_changed = Signal(int)
    toggle_thumbnails_clicked = Signal()
    new_tab_clicked = Signal()
    item_switched = Signal(dict)
    all_tabs_closed = Signal()
    files_dropped = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.open_items: List[Dict[str, Any]] = []
        self.current_item_index = -1
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Tab Bar Header
        tab_layout = QHBoxLayout()
        tab_layout.setContentsMargins(8, 4, 8, 0)
        
        self.tab_bar = QTabBar()
        self.tab_bar.setTabsClosable(True)
        self.tab_bar.setMovable(True)
        self.tab_bar.tabCloseRequested.connect(self.close_tab)
        self.tab_bar.currentChanged.connect(self.on_tab_switched)
        tab_layout.addWidget(self.tab_bar)

        self.btn_add_tab = QPushButton("➕")
        self.btn_add_tab.setFixedSize(30, 28)
        self.btn_add_tab.setToolTip("فتح ملفات ومستندات جديدة في تبويب")
        self.btn_add_tab.clicked.connect(self.new_tab_clicked.emit)
        tab_layout.addWidget(self.btn_add_tab)
        tab_layout.addStretch()
        layout.addLayout(tab_layout)

        # Dynamic Toolbar Widget
        self.toolbar_widget = QWidget()
        self.toolbar_widget.setStyleSheet("background-color: #172536; border-bottom: 1px solid #24374D;")
        self.toolbar_layout = QHBoxLayout(self.toolbar_widget)
        self.toolbar_layout.setContentsMargins(12, 6, 12, 6)
        self.toolbar_layout.setSpacing(8)

        # PDF Navigation Controls
        self.btn_toggle_thumbs = QPushButton("📑")
        self.btn_toggle_thumbs.setFixedSize(32, 30)
        self.btn_toggle_thumbs.setToolTip("إظهار / إخفاء المصغرات")
        self.btn_toggle_thumbs.clicked.connect(self.toggle_thumbnails_clicked.emit)
        self.toolbar_layout.addWidget(self.btn_toggle_thumbs)

        self.btn_prev = QPushButton("◀")
        self.btn_prev.setFixedSize(32, 30)
        self.btn_prev.clicked.connect(self.prev_page_or_item)
        self.toolbar_layout.addWidget(self.btn_prev)

        self.page_input = QLineEdit("1")
        self.page_input.setFixedWidth(45)
        self.page_input.setAlignment(Qt.AlignCenter)
        self.page_input.returnPressed.connect(self.on_page_input)
        self.toolbar_layout.addWidget(self.page_input)

        self.page_total_lbl = QLabel("/ 0")
        self.page_total_lbl.setStyleSheet("color: #94A3B8; font-weight: bold;")
        self.toolbar_layout.addWidget(self.page_total_lbl)

        self.btn_next = QPushButton("▶")
        self.btn_next.setFixedSize(32, 30)
        self.btn_next.clicked.connect(self.next_page_or_item)
        self.toolbar_layout.addWidget(self.btn_next)

        # Image Specific Buttons (Hidden when viewing PDF)
        self.btn_rotate_img = QPushButton("🔄 تدوير 90°")
        self.btn_rotate_img.clicked.connect(self.on_rotate_clicked)
        self.btn_rotate_img.setVisible(False)
        self.toolbar_layout.addWidget(self.btn_rotate_img)

        self.btn_flip_img = QPushButton("↔️ قلب أفقي")
        self.btn_flip_img.clicked.connect(self.on_flip_clicked)
        self.btn_flip_img.setVisible(False)
        self.toolbar_layout.addWidget(self.btn_flip_img)

        self.toolbar_layout.addSpacing(16)

        # Zoom Controls
        self.btn_zoom_out = QPushButton("🔍-")
        self.btn_zoom_out.setFixedSize(36, 30)
        self.btn_zoom_out.clicked.connect(self.zoom_out)
        self.toolbar_layout.addWidget(self.btn_zoom_out)

        self.zoom_combo = QComboBox()
        self.zoom_combo.setFixedWidth(85)
        self.zoom_combo.addItems(["50%", "75%", "100%", "125%", "150%", "200%"])
        self.zoom_combo.setCurrentText("100%")
        self.zoom_combo.currentTextChanged.connect(self.on_zoom_combo_changed)
        self.toolbar_layout.addWidget(self.zoom_combo)

        self.btn_zoom_in = QPushButton("🔍+")
        self.btn_zoom_in.setFixedSize(36, 30)
        self.btn_zoom_in.clicked.connect(self.zoom_in)
        self.toolbar_layout.addWidget(self.btn_zoom_in)

        self.toolbar_layout.addStretch()
        layout.addWidget(self.toolbar_widget)

        # Canvas
        self.canvas = DocumentCanvas()
        self.canvas.page_changed.connect(self.on_canvas_page_changed)
        self.canvas.zoom_changed.connect(self.on_canvas_zoom_changed)
        layout.addWidget(self.canvas)

    @property
    def doc(self) -> Optional[QPdfDocument]:
        curr = self.get_current_item()
        if curr and curr.get("type") == "pdf":
            return curr.get("doc")
        return None

    def get_current_item(self) -> Optional[Dict[str, Any]]:
        if 0 <= self.current_item_index < len(self.open_items):
            return self.open_items[self.current_item_index]
        return None

    def add_file(self, file_path: str, password: Optional[str] = None) -> bool:
        p = Path(file_path).resolve()
        if not p.exists():
            return False

        ext = p.suffix.lower()
        is_pdf = (ext == ".pdf")

        # Check if already open
        for idx, item in enumerate(self.open_items):
            if item["path"] == str(p):
                self.tab_bar.setCurrentIndex(idx)
                return True

        if is_pdf:
            doc = QPdfDocument(self)
            if password:
                doc.setPassword(password)
            err = doc.load(str(p))
            if err != QPdfDocument.Error.None_:
                return False

            item = {
                "type": "pdf",
                "path": str(p),
                "name": p.name,
                "doc": doc,
                "page_count": doc.pageCount(),
                "file_size": p.stat().st_size
            }
            tab_title = f"📄 {p.name}"
        else: # Image
            from PIL import Image
            try:
                with Image.open(str(p)) as im:
                    w, h = im.size
            except Exception:
                w, h = 0, 0

            item = {
                "type": "image",
                "path": str(p),
                "name": p.name,
                "dimensions": f"{w}×{h} px",
                "file_size": p.stat().st_size
            }
            tab_title = f"🖼️ {p.name}"

        self.open_items.append(item)
        tab_idx = self.tab_bar.addTab(tab_title)
        self.tab_bar.setCurrentIndex(tab_idx)
        return True

    def on_tab_switched(self, index: int):
        if index < 0 or index >= len(self.open_items):
            return

        self.current_item_index = index
        item = self.open_items[index]

        if item["type"] == "pdf":
            self.canvas.set_pdf(item["doc"])
            self.btn_toggle_thumbs.setVisible(True)
            self.btn_rotate_img.setVisible(False)
            self.btn_flip_img.setVisible(False)
            self.page_input.setVisible(True)
            self.page_total_lbl.setVisible(True)
            self.page_total_lbl.setText(f"/ {item['page_count']}")
            self.page_input.setText(str(self.canvas.current_page + 1))
        else:
            self.canvas.set_image(item["path"])
            self.btn_toggle_thumbs.setVisible(False)
            self.btn_rotate_img.setVisible(True)
            self.btn_flip_img.setVisible(True)
            # Count images
            img_items = [it for it in self.open_items if it["type"] == "image"]
            img_idx = img_items.index(item) + 1 if item in img_items else 1
            self.page_input.setVisible(True)
            self.page_total_lbl.setVisible(True)
            self.page_total_lbl.setText(f"/ {len(img_items)}")
            self.page_input.setText(str(img_idx))

        self.item_switched.emit(item)

    def close_tab(self, index: int):
        if 0 <= index < len(self.open_items):
            item = self.open_items.pop(index)
            if item.get("type") == "pdf" and "doc" in item:
                item["doc"].close()
            self.tab_bar.removeTab(index)

            if len(self.open_items) == 0:
                self.current_item_index = -1
                self.canvas.content_label.clear()
                self.all_tabs_closed.emit()
            else:
                new_idx = min(index, len(self.open_items) - 1)
                self.tab_bar.setCurrentIndex(new_idx)

    def prev_page_or_item(self):
        item = self.get_current_item()
        if not item:
            return
        if item["type"] == "pdf":
            if self.canvas.current_page > 0:
                self.canvas.set_page(self.canvas.current_page - 1)
        else: # Image: switch to prev image tab
            img_indices = [i for i, it in enumerate(self.open_items) if it["type"] == "image"]
            if self.current_item_index in img_indices:
                curr_pos = img_indices.index(self.current_item_index)
                if curr_pos > 0:
                    self.tab_bar.setCurrentIndex(img_indices[curr_pos - 1])

    def next_page_or_item(self):
        item = self.get_current_item()
        if not item:
            return
        if item["type"] == "pdf":
            if self.doc and self.canvas.current_page < self.doc.pageCount() - 1:
                self.canvas.set_page(self.canvas.current_page + 1)
        else: # Image: switch to next image tab
            img_indices = [i for i, it in enumerate(self.open_items) if it["type"] == "image"]
            if self.current_item_index in img_indices:
                curr_pos = img_indices.index(self.current_item_index)
                if curr_pos < len(img_indices) - 1:
                    self.tab_bar.setCurrentIndex(img_indices[curr_pos + 1])

    def on_page_input(self):
        txt = self.page_input.text().strip()
        item = self.get_current_item()
        if txt.isdigit() and item:
            num = int(txt) - 1
            if item["type"] == "pdf" and self.doc and 0 <= num < self.doc.pageCount():
                self.canvas.set_page(num)

    def on_rotate_clicked(self):
        self.canvas.rotate_image(90)

    def on_flip_clicked(self):
        self.canvas.flip_image_h()

    def on_canvas_page_changed(self, p_idx: int):
        self.page_input.setText(str(p_idx + 1))
        self.page_changed.emit(p_idx)

    def on_canvas_zoom_changed(self, pct: int):
        self.zoom_combo.blockSignals(True)
        self.zoom_combo.setCurrentText(f"{pct}%")
        self.zoom_combo.blockSignals(False)
        self.zoom_changed.emit(pct)

    def zoom_in(self):
        cur = int(self.canvas.zoom_factor * 100)
        self.canvas.set_zoom(cur + 15)

    def zoom_out(self):
        cur = int(self.canvas.zoom_factor * 100)
        self.canvas.set_zoom(cur - 15)

    def on_zoom_combo_changed(self, text: str):
        val = text.replace("%", "").strip()
        if val.isdigit():
            self.canvas.set_zoom(int(val))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        paths = [url.toLocalFile() for url in event.mimeData().urls() if url.toLocalFile()]
        if paths:
            self.files_dropped.emit(paths)
