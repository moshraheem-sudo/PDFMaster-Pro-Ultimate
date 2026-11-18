"""
PDF Master Pro - Settings Dialog
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QCheckBox, QPushButton, QLineEdit, QFileDialog
)
from ui.i18n import tr
from core.settings_manager import SettingsManager

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إعدادات البرنامج")
        self.setFixedSize(420, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        s = SettingsManager.load_settings()

        # Theme
        layout.addWidget(QLabel("السمة والمظهر:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("الوضع الداكن (Dark Mode)", "dark")
        self.theme_combo.addItem("الوضع الفاتح (Light Mode)", "light")
        self.theme_combo.setCurrentIndex(0 if s.get("theme") == "dark" else 1)
        layout.addWidget(self.theme_combo)

        # Language
        layout.addWidget(QLabel("اللغة الافتراضية:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("العربية (Arabic)", "ar")
        self.lang_combo.addItem("English (إنجليزية)", "en")
        self.lang_combo.setCurrentIndex(0 if s.get("language") == "ar" else 1)
        layout.addWidget(self.lang_combo)

        # Backup
        self.chk_backup = QCheckBox("إنشاء نسخة احتياطية تلقائياً قبل الكتابة فوق الملفات")
        self.chk_backup.setChecked(s.get("auto_backup", True))
        layout.addWidget(self.chk_backup)

        # Tesseract path
        layout.addWidget(QLabel("مسار محرك Tesseract OCR:"))
        tess_box = QHBoxLayout()
        self.tess_input = QLineEdit(s.get("tesseract_path", ""))
        btn_tess = QPushButton("استعراض...")
        btn_tess.clicked.connect(self.browse_tess)
        tess_box.addWidget(self.tess_input)
        tess_box.addWidget(btn_tess)
        layout.addLayout(tess_box)

        layout.addStretch()

        btns = QHBoxLayout()
        btn_save = QPushButton("حفظ الإعدادات")
        btn_save.setObjectName("PrimaryBtn")
        btn_save.clicked.connect(self.save)
        btn_cancel = QPushButton("إلغاء")
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_save)
        btns.addWidget(btn_cancel)
        layout.addLayout(btns)

    def browse_tess(self):
        f, _ = QFileDialog.getOpenFileName(self, "اختر ملف tesseract.exe", "", "Executable (*.exe)")
        if f:
            self.tess_input.setText(f)

    def save(self):
        s = {
            "theme": self.theme_combo.currentData(),
            "language": self.lang_combo.currentData(),
            "auto_backup": self.chk_backup.isChecked(),
            "tesseract_path": self.tess_input.text()
        }
        SettingsManager.save_settings(s)
        self.accept()
