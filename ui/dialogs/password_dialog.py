"""
PDF Master Pro - Password Prompt Dialog
Clean, secure dialog when opening password-protected PDFs.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
)
from PySide6.QtCore import Qt

class PasswordDialog(QDialog):
    def __init__(self, file_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("مستند محمي بكلمة مرور")
        self.setFixedSize(360, 180)
        self.file_name = file_name
        self.password = ""
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        icon_lbl = QLabel("🔒 هذا الملف مشفر ومحمي بكلمة مرور:")
        icon_lbl.setStyleSheet("font-weight: bold; font-size: 13px; color: #FFFFFF;")
        layout.addWidget(icon_lbl)

        fn_lbl = QLabel(self.file_name)
        fn_lbl.setStyleSheet("color: #E5A63B; font-size: 12px;")
        layout.addWidget(fn_lbl)

        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setPlaceholderText("أدخل كلمة المرور هنا...")
        layout.addWidget(self.pass_input)

        btns = QHBoxLayout()
        self.btn_ok = QPushButton("فتح المستند")
        self.btn_ok.setObjectName("PrimaryBtn")
        self.btn_ok.clicked.connect(self.on_ok)
        
        self.btn_cancel = QPushButton("إلغاء")
        self.btn_cancel.clicked.connect(self.reject)

        btns.addWidget(self.btn_ok)
        btns.addWidget(self.btn_cancel)
        layout.addLayout(btns)

    def on_ok(self):
        self.password = self.pass_input.text()
        self.accept()
