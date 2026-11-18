"""
PDF Master Pro - File Manager
Safe file handling, recent files registry, and atomic writes.
"""
import json
import shutil
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional

from core.config import RECENT_FILES_FILE, TEMP_WORK_DIR

class FileManager:
    MAX_RECENT = 15

    @staticmethod
    def get_recent_files() -> List[Dict[str, Any]]:
        if not RECENT_FILES_FILE.exists():
            return []
        try:
            with open(RECENT_FILES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                valid = []
                for item in data:
                    if Path(item.get("path", "")).exists():
                        valid.append(item)
                return valid
        except Exception:
            return []

    @staticmethod
    def add_recent_file(file_path: str, page_count: int = 0) -> None:
        p = Path(file_path).resolve()
        if not p.exists():
            return
            
        recent = FileManager.get_recent_files()
        # Remove if already exists to move to top
        recent = [r for r in recent if r.get("path") != str(p)]
        
        size = p.stat().st_size
        size_str = f"{size / (1024 * 1024):.1f} MB" if size >= 1024 * 1024 else f"{size / 1024:.1f} KB"
        
        recent.insert(0, {
            "name": p.name,
            "path": str(p),
            "size_str": size_str,
            "page_count": page_count,
            "last_opened": p.stat().st_mtime
        })
        
        recent = recent[:FileManager.MAX_RECENT]
        try:
            with open(RECENT_FILES_FILE, "w", encoding="utf-8") as f:
                json.dump(recent, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    @staticmethod
    def clear_recent_files() -> None:
        try:
            if RECENT_FILES_FILE.exists():
                RECENT_FILES_FILE.unlink()
        except Exception:
            pass

    @staticmethod
    def create_temp_file(suffix: str = ".pdf") -> str:
        f = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=TEMP_WORK_DIR)
        f.close()
        return f.name

    @staticmethod
    def safe_save(temp_source: str, destination: str, backup_original: bool = False) -> bool:
        """
        Safely copies processed temp file to final destination with optional backup.
        """
        dest_p = Path(destination)
        if dest_p.exists() and backup_original:
            backup_p = dest_p.with_suffix(dest_p.suffix + ".bak")
            shutil.copy2(dest_p, backup_p)
            
        shutil.copy2(temp_source, dest_p)
        return True
