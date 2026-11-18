"""
PDF Master Pro - Ultimate Edition
Main Application Entry Point
"""
import sys
import os
from pathlib import Path

# Ensure root directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QFont

from core.config import APP_NAME, APP_EDITION, APP_VERSION
from core.settings_manager import SettingsManager
from ui.i18n import I18n
from ui.theme import get_stylesheet
from ui.main_window import MainWindow

def main():
    # Enable high DPI pixmaps
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("PDF Master Pro")

    # Load persistent settings
    settings = SettingsManager.load_settings()
    theme = settings.get("theme", "dark")
    language = settings.get("language", "ar")

    # Keep visual structure aligned with the reference design (Sidebar on left, properties on right)
    app.setLayoutDirection(Qt.LeftToRight)

    app.setStyleSheet(get_stylesheet(theme))

    # Font setup with Arabic fallback
    font = QFont("Segoe UI", 10)
    font.setStyleHint(QFont.SansSerif)
    app.setFont(font)

    # Initialize main window
    window = MainWindow()
    window.show()

    # Open file if passed via CLI
    if len(sys.argv) > 1:
        initial_file = sys.argv[1]
        if Path(initial_file).exists():
            window.open_pdf_file(initial_file)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
