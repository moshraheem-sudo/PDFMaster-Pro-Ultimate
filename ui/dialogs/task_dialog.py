"""
PDF Master Pro - Task Manager Dialog
Monitors running background jobs, progress, and history.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QProgressBar
)
from PySide6.QtCore import Qt

class TaskDialog(QDialog):
    def __init__(self, task_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("مدير العمليات والمهام")
        self.setFixedSize(480, 320)
        self.task_manager = task_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        layout.addWidget(QLabel("العمليات النشطة والمكتملة:"))
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        # Refresh button
        btns = QHBoxLayout()
        refresh_btn = QPushButton("تحديث")
        refresh_btn.clicked.connect(self.refresh_list)
        close_btn = QPushButton("إغلاق")
        close_btn.clicked.connect(self.accept)
        btns.addWidget(refresh_btn)
        btns.addWidget(close_btn)
        layout.addLayout(btns)

        self.refresh_list()

    def refresh_list(self):
        self.list_widget.clear()
        # Active
        for name in self.task_manager.active_tasks.keys():
            item = QListWidgetItem(f"⏳ قيد المعالجة: {name}")
            self.list_widget.addItem(item)
            
        # History
        for h in reversed(self.task_manager.history[-10:]):
            st = "✅ نجاح" if h.get("success") else "❌ خطأ"
            item = QListWidgetItem(f"{st}: {h.get('name')} - {h.get('msg')}")
            self.list_widget.addItem(item)
