"""
PDF Master Pro - Bottom Status Bar
Displays file metadata, page size, zoom slider, progress indicator, and task manager button.
"""
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QProgressBar, QPushButton, QSlider, QFrame
)
from PySide6.QtCore import Qt, Signal

from ui.i18n import tr

class BottomStatusBar(QWidget):
    tasks_clicked = Signal()
    zoom_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("BottomStatusBar")
        self.setFixedHeight(38)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.setSpacing(16)

        # Status Badge (Ready / Processing)
        self.status_badge = QLabel(f"✔ {tr('status_ready')}")
        self.status_badge.setObjectName("StatusBadge")
        layout.addWidget(self.status_badge)

        # Separator line
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.VLine)
        sep1.setStyleSheet("color: #2E435B;")
        layout.addWidget(sep1)

        # Page count
        self.lbl_pages = QLabel(f"📄 0 {tr('page_unit')}")
        self.lbl_pages.setStyleSheet("color: #CBD5E1; font-weight: 500;")
        layout.addWidget(self.lbl_pages)

        # File size
        self.lbl_size = QLabel("💾 0.0 MB")
        self.lbl_size.setStyleSheet("color: #CBD5E1; font-weight: 500;")
        layout.addWidget(self.lbl_size)

        # Page dimensions (e.g. A4 (210x297 mm))
        self.lbl_dims = QLabel("📐 A4 (210×297 mm)")
        self.lbl_dims.setStyleSheet("color: #CBD5E1; font-weight: 500;")
        layout.addWidget(self.lbl_dims)

        layout.addStretch()

        # Zoom Controls: (-) Slider (+)
        zoom_box = QHBoxLayout()
        zoom_box.setSpacing(6)

        btn_zoom_sub = QPushButton("-")
        btn_zoom_sub.setFixedSize(22, 22)
        btn_zoom_sub.clicked.connect(self.decrement_zoom)
        zoom_box.addWidget(btn_zoom_sub)

        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(20, 300)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setFixedWidth(100)
        self.zoom_slider.valueChanged.connect(self.on_slider_changed)
        zoom_box.addWidget(self.zoom_slider)

        btn_zoom_add = QPushButton("+")
        btn_zoom_add.setFixedSize(22, 22)
        btn_zoom_add.clicked.connect(self.increment_zoom)
        zoom_box.addWidget(btn_zoom_add)

        self.lbl_zoom = QLabel("100%")
        self.lbl_zoom.setFixedWidth(40)
        self.lbl_zoom.setStyleSheet("color: #94A3B8; font-weight: bold;")
        zoom_box.addWidget(self.lbl_zoom)

        layout.addLayout(zoom_box)

        # Smooth Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(150)
        self.progress_bar.setValue(100)
        layout.addWidget(self.progress_bar)

        # Task manager button "عرض العمليات"
        self.btn_tasks = QPushButton(f"☰ {tr('show_tasks')}")
        self.btn_tasks.setCursor(Qt.PointingHandCursor)
        self.btn_tasks.clicked.connect(self.tasks_clicked.emit)
        layout.addWidget(self.btn_tasks)

    def set_status(self, text: str, is_busy: bool = False):
        if is_busy:
            self.status_badge.setText(f"⏳ {text}")
            self.status_badge.setStyleSheet("background-color: #78350F; color: #FBBF24; border-radius: 6px; padding: 4px 10px; font-weight: bold;")
        else:
            self.status_badge.setText(f"✔ {text}")
            self.status_badge.setStyleSheet("background-color: #064E3B; color: #34D399; border-radius: 6px; padding: 4px 10px; font-weight: bold;")

    def set_document_info(self, page_count: int, file_size_str: str, dims_str: str = "A4 (210×297 mm)"):
        self.lbl_pages.setText(f"📄 {page_count} {tr('page_unit')}")
        self.lbl_size.setText(f"💾 {file_size_str}")
        self.lbl_dims.setText(f"📐 {dims_str}")

    def set_progress(self, current: int, total: int):
        if total > 0:
            pct = int((current / total) * 100)
            self.progress_bar.setValue(pct)
        else:
            self.progress_bar.setValue(0)

    def on_slider_changed(self, val: int):
        self.lbl_zoom.setText(f"{val}%")
        self.zoom_changed.emit(val)

    def set_zoom_value(self, val: int):
        self.zoom_slider.blockSignals(True)
        self.zoom_slider.setValue(val)
        self.lbl_zoom.setText(f"{val}%")
        self.zoom_slider.blockSignals(False)

    def increment_zoom(self):
        self.zoom_slider.setValue(min(300, self.zoom_slider.value() + 10))

    def decrement_zoom(self):
        self.zoom_slider.setValue(max(20, self.zoom_slider.value() - 10))
