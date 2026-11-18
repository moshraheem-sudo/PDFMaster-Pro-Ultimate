"""
PDF Master Pro - Home Dashboard
A modern welcome screen with quick-action cards, drag-and-drop zone, and recent files list.
"""
from typing import List, Dict, Any, Callable
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent

from ui.i18n import tr
from core.file_manager import FileManager

class ActionCard(QFrame):
    clicked = Signal(str)

    def __init__(self, key: str, icon: str, title: str, desc: str, color_accent: str = "#0D74CE", parent=None):
        super().__init__(parent)
        self.key = key
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.init_ui(icon, title, desc, color_accent)

    def init_ui(self, icon: str, title: str, desc: str, color_accent: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        # Header with icon and title
        header = QHBoxLayout()
        header.setSpacing(10)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 24px; padding: 4px; background-color: #172536; border-radius: 8px;")
        header.addWidget(icon_lbl)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFFFFF;")
        header.addWidget(title_lbl)
        header.addStretch()

        layout.addLayout(header)

        # Description
        desc_lbl = QLabel(desc)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("font-size: 12px; color: #94A3B8; line-height: 1.4;")
        layout.addWidget(desc_lbl)

        self.setStyleSheet(f"""
            ActionCard {{
                background-color: #24374D;
                border: 1px solid #334B66;
                border-radius: 12px;
            }}
            ActionCard:hover {{
                border: 1px solid {color_accent};
                background-color: #2A425C;
            }}
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.key)
        super().mousePressEvent(event)

class DropZoneWidget(QFrame):
    files_dropped = Signal(list)
    browse_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 24, 30, 24)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)

        icon = QLabel("📂")
        icon.setStyleSheet("font-size: 44px;")
        layout.addWidget(icon, alignment=Qt.AlignCenter)

        prompt = QLabel(tr("drop_prompt"))
        prompt.setStyleSheet("font-size: 15px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(prompt, alignment=Qt.AlignCenter)

        btn = QPushButton(f"✨ {tr('or_browse')}")
        btn.setObjectName("PrimaryBtn")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self.browse_clicked.emit)
        layout.addWidget(btn, alignment=Qt.AlignCenter)

        self.setStyleSheet("""
            DropZoneWidget {
                background-color: #172536;
                border: 2px dashed #0D74CE;
                border-radius: 14px;
            }
            DropZoneWidget:hover {
                border-color: #278B91;
                background-color: #1A2C3F;
            }
        """)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        paths = [url.toLocalFile() for url in event.mimeData().urls() if url.toLocalFile()]
        if paths:
            self.files_dropped.emit(paths)

class HomeDashboard(QWidget):
    open_file_requested = Signal()
    files_dropped = Signal(list)
    action_requested = Signal(str) # tool key
    file_open_requested = Signal(str) # file path from recents

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(16)

        # Welcome Banner
        banner = QVBoxLayout()
        banner.setSpacing(4)
        title = QLabel(f"👑 {tr('welcome_title')}")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
        banner.addWidget(title)

        subtitle = QLabel(tr("app_subtitle"))
        subtitle.setStyleSheet("font-size: 13px; color: #94A3B8;")
        banner.addWidget(subtitle)
        layout.addLayout(banner)

        # Drop Zone
        self.drop_zone = DropZoneWidget()
        self.drop_zone.browse_clicked.connect(self.open_file_requested.emit)
        self.drop_zone.files_dropped.connect(self.files_dropped.emit)
        layout.addWidget(self.drop_zone)

        # Quick Action Cards Header
        sec_title = QLabel("الأدوات والوظائف السريعة")
        sec_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #E5A63B; margin-top: 6px;")
        layout.addWidget(sec_title)

        # Grid of Cards
        cards_grid = QGridLayout()
        cards_grid.setSpacing(12)

        cards_data = [
            ("compress_pdf", "🗜️", tr("card_compress_title"), tr("card_compress_desc"), "#0D74CE"),
            ("split_merge", "✂️", tr("card_split_title"), tr("card_split_desc"), "#278B91"),
            ("split_merge", "📑", tr("card_merge_title"), tr("card_merge_desc"), "#3B82F6"),
            ("edit_pdf", "✏️", tr("card_edit_title"), tr("card_edit_desc"), "#F59E0B"),
            ("compress_images", "🖼️", tr("card_img_compress_title"), tr("card_img_compress_desc"), "#10B981"),
            ("extract_images", "🔍", tr("card_extract_img_title"), tr("card_extract_img_desc"), "#8B5CF6"),
            ("security", "🔒", tr("card_security_title"), tr("card_security_desc"), "#EF4444"),
            ("watermark", "💧", tr("card_watermark_title"), tr("card_watermark_desc"), "#06B6D4"),
            ("ocr", "🔤", tr("card_ocr_title"), tr("card_ocr_desc"), "#EC4899"),
            ("convert", "🔄", tr("card_convert_title"), tr("card_convert_desc"), "#14B8A6"),
        ]

        for idx, (key, icon, t, d, color) in enumerate(cards_data):
            card = ActionCard(key, icon, t, d, color)
            card.clicked.connect(self.action_requested.emit)
            r = idx // 2
            c = idx % 2
            cards_grid.addWidget(card, r, c)

        layout.addLayout(cards_grid)

        # Recent Files Section
        recents_header = QHBoxLayout()
        rec_title = QLabel(f"🕒 {tr('recent_files')}")
        rec_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        recents_header.addWidget(rec_title)
        recents_header.addStretch()

        clear_btn = QPushButton(f"🗑️ {tr('clear_history')}")
        clear_btn.setStyleSheet("background: transparent; color: #94A3B8; border: none; font-size: 12px;")
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.clicked.connect(self.on_clear_history)
        recents_header.addWidget(clear_btn)
        layout.addLayout(recents_header)

        # Recent files table
        self.recents_table = QTableWidget()
        self.recents_table.setColumnCount(4)
        self.recents_table.setHorizontalHeaderLabels(["اسم الملف", "الحجم", "الصفحات", "المسار"])
        self.recents_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.recents_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.recents_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.recents_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.recents_table.verticalHeader().setVisible(False)
        self.recents_table.setStyleSheet("""
            QTableWidget {
                background-color: #172536;
                border: 1px solid #2B3D52;
                border-radius: 8px;
                gridline-color: #24374D;
            }
            QHeaderView::section {
                background-color: #1F3044;
                color: #CBD5E1;
                font-weight: bold;
                padding: 6px;
                border: 1px solid #24374D;
            }
            QTableWidget::item:hover {
                background-color: #24374D;
            }
        """)
        self.recents_table.cellDoubleClicked.connect(self.on_recent_double_clicked)
        self.recents_table.setFixedHeight(180)
        layout.addWidget(self.recents_table)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        self.refresh_recent_files()

    def refresh_recent_files(self):
        recents = FileManager.get_recent_files()
        self.recents_table.setRowCount(len(recents))
        for row, item in enumerate(recents):
            name_item = QTableWidgetItem(item.get("name", ""))
            name_item.setData(Qt.UserRole, item.get("path"))
            size_item = QTableWidgetItem(item.get("size_str", ""))
            pages_item = QTableWidgetItem(str(item.get("page_count", "-")))
            path_item = QTableWidgetItem(item.get("path", ""))

            self.recents_table.setItem(row, 0, name_item)
            self.recents_table.setItem(row, 1, size_item)
            self.recents_table.setItem(row, 2, pages_item)
            self.recents_table.setItem(row, 3, path_item)

    def on_recent_double_clicked(self, row: int, col: int):
        item = self.recents_table.item(row, 0)
        if item:
            path = item.data(Qt.UserRole)
            if path and Path(path).exists():
                self.file_open_requested.emit(path)

    def on_clear_history(self):
        FileManager.clear_recent_files()
        self.refresh_recent_files()
