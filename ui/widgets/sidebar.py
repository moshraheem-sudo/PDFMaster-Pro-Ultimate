"""
PDF Master Pro - Sidebar Navigation Menu
14 organized sections matching reference image and specification.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon

from ui.i18n import tr

MENU_ITEMS = [
    ("home", "menu_home", "🏠"),
    ("file_manager", "menu_file_manager", "📁"),
    ("edit_pdf", "menu_edit_pdf", "✏️"),
    ("compress_pdf", "menu_compress_pdf", "🗜️"),
    ("compress_images", "menu_compress_images", "🖼️"),
    ("split_merge", "menu_split_merge", "✂️"),
    ("rotate", "menu_rotate", "🔄"),
    ("extract_images", "menu_extract_images", "🔍"),
    ("delete_images", "menu_delete_images", "🗑️"),
    ("watermark", "menu_watermark", "💧"),
    ("security", "menu_security", "🛡️"),
    ("convert", "menu_convert", "🔁"),
    ("ocr", "menu_ocr", "🔤"),
    ("settings", "settings", "⚙️")
]

class Sidebar(QWidget):
    item_selected = Signal(str) # section_key

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(230)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 10, 6, 10)
        layout.setSpacing(4)

        self.list_widget = QListWidget()
        self.list_widget.setObjectName("SidebarList")
        self.list_widget.setSpacing(2)

        for key, tr_key, icon in MENU_ITEMS:
            text = f"{icon}  {tr(tr_key)}"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, key)
            self.list_widget.addItem(item)

        self.list_widget.currentRowChanged.connect(self.on_row_changed)
        layout.addWidget(self.list_widget)

        # Select first item by default
        self.list_widget.setCurrentRow(0)

    def on_row_changed(self, row: int):
        item = self.list_widget.item(row)
        if item:
            key = item.data(Qt.UserRole)
            self.item_selected.emit(key)

    def select_item(self, key: str):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.UserRole) == key:
                self.list_widget.setCurrentRow(i)
                break

    def update_translations(self):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            key, tr_key, icon = MENU_ITEMS[i]
            item.setText(f"{icon}  {tr(tr_key)}")
