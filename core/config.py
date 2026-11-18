"""
PDF Master Pro - Ultimate Edition
Application Configuration and Constants
"""
import os
import sys
from pathlib import Path

APP_NAME = "PDF Master Pro"
APP_EDITION = "Ultimate Edition"
APP_VERSION = "3.5.0"

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
BIN_DIR = BASE_DIR / "bin"
ASSETS_DIR = BASE_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"

# App Data Directory for persistent settings and history
APPDATA_DIR = Path(os.environ.get("APPDATA", Path.home())) / "PDFMasterPro"
APPDATA_DIR.mkdir(parents=True, exist_ok=True)
TEMP_WORK_DIR = APPDATA_DIR / "temp"
TEMP_WORK_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_FILE = APPDATA_DIR / "settings.json"
RECENT_FILES_FILE = APPDATA_DIR / "recent_files.json"

# PDFCPU Binary Detection
PDFCPU_PATH = BIN_DIR / "pdfcpu.exe"
if not PDFCPU_PATH.exists():
    # Try system PATH
    system_pdfcpu = Path(sys.prefix) / "bin" / "pdfcpu.exe"
    if system_pdfcpu.exists():
        PDFCPU_PATH = system_pdfcpu

# Tesseract OCR standard paths
TESSERACT_CANDIDATES = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Tesseract-OCR" / "tesseract.exe"
]

def get_tesseract_path() -> str:
    for candidate in TESSERACT_CANDIDATES:
        p = Path(candidate)
        if p.exists():
            return str(p)
    return "tesseract"

# Visual Theme Constants
THEME_NAVY = "#172536"
THEME_DEEP_BLUE = "#24374D"
THEME_TEAL = "#278B91"
THEME_GOLD = "#E5A63B"
THEME_ACCENT_BLUE = "#0D74CE"
THEME_ACCENT_HOVER = "#1E88E5"
THEME_SUCCESS = "#22C55E"
THEME_DANGER = "#EF4444"
THEME_WARNING = "#F59E0B"
THEME_BG_LIGHT = "#F3F5F8"
THEME_BG_DARK = "#101924"
THEME_SURFACE_DARK = "#172536"
THEME_PANEL_DARK = "#1C2B3C"
THEME_CARD_DARK = "#24374D"
THEME_BORDER_DARK = "#2E435B"
