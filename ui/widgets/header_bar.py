"""
PDF Master Pro - Header Bar Widget
Top branding, window actions, and primary action toolbar.
"""
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QComboBox, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QFont

from ui.i18n import tr, I18n

class HeaderBar(QWidget):
    open_file_clicked = Signal()
    new_file_clicked = Signal()
    save_clicked = Signal()
    save_as_clicked = Signal()
    undo_clicked = Signal()
    redo_clicked = Signal()
    settings_clicked = Signal()
    help_clicked = Signal()
    theme_toggled = Signal()
    language_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HeaderBar")
        self.setFixedHeight(94)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.is_dark_theme = True
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 6, 14, 6)
        main_layout.setSpacing(6)

        # Top line: Title & Branding + Window Utilities
        top_line = QHBoxLayout()
        top_line.setSpacing(10)

        # PDF Badge
        self.badge = QLabel("PDF")
        self.badge.setObjectName("AppTitleBadge")
        top_line.addWidget(self.badge)

        # Title: PDF Master Pro
        self.title_label = QLabel(tr("app_title"))
        self.title_label.setObjectName("AppTitleLabel")
        top_line.addWidget(self.title_label)

        top_line.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Theme toggle button
        self.theme_btn = QPushButton("🌓")
        self.theme_btn.setToolTip("تبديل الوضع الفاتح / الداكن")
        self.theme_btn.setFixedWidth(45)
        self.theme_btn.clicked.connect(self.theme_toggled.emit)
        top_line.addWidget(self.theme_btn)

        # Settings button
        self.settings_btn = QPushButton(f"⚙️ {tr('settings')}")
        self.settings_btn.clicked.connect(self.settings_clicked.emit)
        top_line.addWidget(self.settings_btn)

        # Help button
        self.help_btn = QPushButton("❓")
        self.help_btn.setFixedWidth(36)
        self.help_btn.setToolTip(tr("help"))
        self.help_btn.clicked.connect(self.help_clicked.emit)
        top_line.addWidget(self.help_btn)

        main_layout.addLayout(top_line)

        # Action Toolbar (Lower line)
        toolbar_line = QHBoxLayout()
        toolbar_line.setSpacing(8)

        # Open File Button (Primary Blue)
        self.btn_open = QPushButton(f"📁 {tr('open_file')}")
        self.btn_open.setObjectName("PrimaryBtn")
        self.btn_open.clicked.connect(self.open_file_clicked.emit)
        toolbar_line.addWidget(self.btn_open)

        # New File
        self.btn_new = QPushButton(f"➕ {tr('new_file')}")
        self.btn_new.clicked.connect(self.new_file_clicked.emit)
        toolbar_line.addWidget(self.btn_new)

        # Save
        self.btn_save = QPushButton(f"💾 {tr('save')}")
        self.btn_save.clicked.connect(self.save_clicked.emit)
        toolbar_line.addWidget(self.btn_save)

        # Save As
        self.btn_save_as = QPushButton(f"📑 {tr('save_as')}")
        self.btn_save_as.clicked.connect(self.save_as_clicked.emit)
        toolbar_line.addWidget(self.btn_save_as)

        # Undo
        self.btn_undo = QPushButton(f"↩️ {tr('undo')}")
        self.btn_undo.clicked.connect(self.undo_clicked.emit)
        toolbar_line.addWidget(self.btn_undo)

        # Redo
        self.btn_redo = QPushButton(f"↪️ {tr('redo')}")
        self.btn_redo.clicked.connect(self.redo_clicked.emit)
        toolbar_line.addWidget(self.btn_redo)

        toolbar_line.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Language Selector
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("🌐 العربية", "ar")
        self.lang_combo.addItem("🌐 English", "en")
        self.lang_combo.currentIndexChanged.connect(self.on_lang_changed)
        toolbar_line.addWidget(self.lang_combo)

        main_layout.addLayout(toolbar_line)

    def on_lang_changed(self, index: int):
        lang_code = self.lang_combo.itemData(index)
        self.language_changed.emit(lang_code)

    def update_translations(self):
        self.title_label.setText(tr("app_title"))
        self.settings_btn.setText(f"⚙️ {tr('settings')}")
        self.help_btn.setToolTip(tr("help"))
        self.btn_open.setText(f"📁 {tr('open_file')}")
        self.btn_new.setText(f"➕ {tr('new_file')}")
        self.btn_save.setText(f"💾 {tr('save')}")
        self.btn_save_as.setText(f"📑 {tr('save_as')}")
        self.btn_undo.setText(f"↩️ {tr('undo')}")
        self.btn_redo.setText(f"↪️ {tr('redo')}")
