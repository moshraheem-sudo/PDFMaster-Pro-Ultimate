"""
PDF Master Pro - Settings Manager
Persistent application settings.
"""
import json
from pathlib import Path
from typing import Dict, Any

from core.config import CONFIG_FILE

DEFAULT_SETTINGS = {
    "theme": "dark",           # "dark" or "light"
    "language": "ar",          # "ar" or "en"
    "auto_backup": True,
    "default_dpi": 150,
    "jpeg_quality": 80,
    "recent_files_limit": 15,
    "tesseract_path": ""
}

class SettingsManager:
    @staticmethod
    def load_settings() -> Dict[str, Any]:
        if not CONFIG_FILE.exists():
            return dict(DEFAULT_SETTINGS)
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                merged = dict(DEFAULT_SETTINGS)
                merged.update(saved)
                return merged
        except Exception:
            return dict(DEFAULT_SETTINGS)

    @staticmethod
    def save_settings(settings: Dict[str, Any]) -> bool:
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        settings = SettingsManager.load_settings()
        return settings.get(key, default)

    @staticmethod
    def set(key: str, value: Any) -> None:
        settings = SettingsManager.load_settings()
        settings[key] = value
        SettingsManager.save_settings(settings)
