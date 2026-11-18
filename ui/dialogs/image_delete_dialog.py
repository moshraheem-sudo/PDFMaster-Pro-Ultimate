"""
PDF Master Pro - Visual Embedded Image Deleter Dialog
Allows users to visually browse detected images in the PDF, select items to remove or replace, and save changes.
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QFileDialog, QMessageBox, QFrame, QScrollArea, QSplitter
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QIcon

from core.pdf_engine import PDFEngine

class ImageDeleteDialog(QDialog):
    def __init__(self, pdf_path: str, current_page: int = 0, parent=None):
        super().__init__(parent)
        self.setWindowTitle("محرر وحذف الصور المضمنة في PDF")
        self.setMinimumSize(680, 480)
        self.pdf_path = pdf_path
        self.current_page = current_page
        self.detected_images = []
        self.selected_image_names = set()
        self.init_ui()
        self.load_images()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        info = QLabel(f"الصور المكتشفة داخل الصفحة {self.current_page + 1}:")
        info.setStyleSheet("font-weight: bold; font-size: 14px; color: #FFFFFF;")
        layout.addWidget(info)

        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(100, 100))
        self.list_widget.setViewMode(QListWidget.IconMode)
        self.list_widget.setResizeMode(QListWidget.Adjust)
        self.list_widget.setSpacing(10)
        self.list_widget.setStyleSheet("""
            QListWidget::item {
                background-color: #24374D;
                border: 2px solid #334B66;
                border-radius: 8px;
                padding: 6px;
                color: #FFFFFF;
            }
            QListWidget::item:selected {
                background-color: #7F1D1D;
                border-color: #EF4444;
            }
        """)
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.list_widget)

        self.status_lbl = QLabel("حدد الصور التي ترغب في حذفها من الصفحة...")
        self.status_lbl.setStyleSheet("color: #94A3B8;")
        layout.addWidget(self.status_lbl)

        btns = QHBoxLayout()
        self.btn_delete = QPushButton("🗑️ حذف الصور المحددة")
        self.btn_delete.setObjectName("BigActionBtn")
        self.btn_delete.setStyleSheet("background: #DC2626; border-color: #F87171;")
        self.btn_delete.clicked.connect(self.on_delete_selected)
        btns.addWidget(self.btn_delete)

        btn_cancel = QPushButton("إغلاق")
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_cancel)

        layout.addLayout(btns)

    def load_images(self):
        self.list_widget.clear()
        self.detected_images = PDFEngine.get_embedded_images_info(self.pdf_path, self.current_page)
        
        if not self.detected_images:
            self.status_lbl.setText("لم يتم العثور على صور مستقلة قابلة للحذف في هذه الصفحة.")
            return

        for img_info in self.detected_images:
            name = img_info["name"]
            w = img_info["width"]
            h = img_info["height"]
            item = QListWidgetItem(f"صورة {name}\n({w}×{h})")
            item.setData(Qt.UserRole, name)
            self.list_widget.addItem(item)

        self.status_lbl.setText(f"تم العثور على {len(self.detected_images)} صورة.")

    def on_selection_changed(self):
        items = self.list_widget.selectedItems()
        self.selected_image_names = {it.data(Qt.UserRole) for it in items}
        self.btn_delete.setEnabled(len(self.selected_image_names) > 0)

    def on_delete_selected(self):
        if not self.selected_image_names:
            return
            
        out_path, _ = QFileDialog.getSaveFileName(self, "حفظ المستند بعد حذف الصور", "cleaned.pdf", "PDF Files (*.pdf)")
        if not out_path:
            return
            
        try:
            mapping = {self.current_page: list(self.selected_image_names)}
            PDFEngine.delete_embedded_images(self.pdf_path, out_path, mapping)
            QMessageBox.information(self, "نجاح", "تم حذف الصور المختارة بنجاح من الصفحة وحفظ المستند الجديد!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"تعذر حذف الصور: {str(e)}")
