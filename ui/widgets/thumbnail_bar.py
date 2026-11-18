"""
PDF Master Pro - Page Thumbnails Strip
Visual page list with rendering, active page badge, and navigation.
"""
from typing import Optional, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel, QFrame, QPushButton
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtPdf import QPdfDocument, QPdfDocumentRenderOptions

class ThumbnailCard(QFrame):
    clicked = Signal(int) # page_index

    def __init__(self, page_index: int, pixmap: QPixmap, parent=None):
        super().__init__(parent)
        self.page_index = page_index
        self.is_active = False
        self.setCursor(Qt.PointingHandCursor)
        self.init_ui(pixmap)

    def init_ui(self, pixmap: QPixmap):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(4)

        # Image container
        self.img_label = QLabel()
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setPixmap(pixmap)
        self.img_label.setStyleSheet("border-radius: 4px; background: white;")
        layout.addWidget(self.img_label)

        # Page number badge circle
        self.num_badge = QLabel(str(self.page_index + 1))
        self.num_badge.setFixedSize(22, 22)
        self.num_badge.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.num_badge, alignment=Qt.AlignCenter)

        self.update_style()

    def set_active(self, active: bool):
        self.is_active = active
        self.update_style()

    def update_style(self):
        if self.is_active:
            self.setStyleSheet("""
                ThumbnailCard {
                    background-color: #1A3450;
                    border: 2px solid #0D74CE;
                    border-radius: 8px;
                }
            """)
            self.num_badge.setStyleSheet("""
                background-color: #0D74CE;
                color: white;
                border-radius: 11px;
                font-weight: bold;
                font-size: 11px;
            """)
        else:
            self.setStyleSheet("""
                ThumbnailCard {
                    background-color: #172536;
                    border: 1px solid #2B3D52;
                    border-radius: 8px;
                }
                ThumbnailCard:hover {
                    border-color: #278B91;
                    background-color: #1E3146;
                }
            """)
            self.num_badge.setStyleSheet("""
                background-color: #2B3D52;
                color: #CBD5E1;
                border-radius: 11px;
                font-size: 11px;
            """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.page_index)
        super().mousePressEvent(event)

class ThumbnailBar(QWidget):
    page_selected = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(180)
        self.cards: List[ThumbnailCard] = []
        self.active_page = 0
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Header bar
        header = QHBoxLayout()
        header.setContentsMargins(4, 2, 4, 2)
        self.title_label = QLabel("الصفحات")
        self.title_label.setStyleSheet("font-weight: bold; color: #94A3B8; font-size: 11px;")
        header.addWidget(self.title_label)
        layout.addLayout(header)

        # Scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")

        self.container = QWidget()
        self.cards_layout = QVBoxLayout(self.container)
        self.cards_layout.setContentsMargins(4, 4, 4, 4)
        self.cards_layout.setSpacing(8)
        self.cards_layout.setAlignment(Qt.AlignTop)

        self.scroll_area.setWidget(self.container)
        layout.addWidget(self.scroll_area)

    def load_document(self, doc: QPdfDocument):
        self.clear()
        if not doc or doc.pageCount() == 0:
            return

        render_opts = QPdfDocumentRenderOptions()
        count = doc.pageCount()
        thumb_width = 130

        for i in range(count):
            pt_size = doc.pagePointSize(i)
            aspect = pt_size.height() / max(1.0, pt_size.width())
            thumb_height = int(thumb_width * aspect)
            
            # Render thumbnail
            q_img = doc.render(i, QSize(thumb_width, thumb_height), render_opts)
            pix = QPixmap.fromImage(q_img)
            
            card = ThumbnailCard(i, pix)
            card.clicked.connect(self.on_card_clicked)
            self.cards.append(card)
            self.cards_layout.addWidget(card)

        if self.cards:
            self.set_active_page(0)

    def on_card_clicked(self, page_index: int):
        self.set_active_page(page_index)
        self.page_selected.emit(page_index)

    def set_active_page(self, page_index: int):
        self.active_page = page_index
        for card in self.cards:
            card.set_active(card.page_index == page_index)

    def clear(self):
        for card in self.cards:
            self.cards_layout.removeWidget(card)
            card.deleteLater()
        self.cards.clear()
