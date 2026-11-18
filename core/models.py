"""
PDF Master Pro - Data Models
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any

class CompressionLevel(Enum):
    LIGHT = "light"       # High quality print
    MEDIUM = "medium"     # Balanced
    STRONG = "strong"     # Maximum compression

class RotationAngle(Enum):
    DEG_90 = 90
    DEG_180 = 180
    DEG_270 = 270

@dataclass
class DocumentMetadata:
    title: str = ""
    author: str = ""
    subject: str = ""
    keywords: str = ""
    creator: str = ""
    producer: str = ""
    creation_date: str = ""
    mod_date: str = ""
    is_encrypted: bool = False
    permissions: Dict[str, bool] = field(default_factory=dict)

@dataclass
class DocumentInfo:
    file_path: str
    file_name: str
    file_size_bytes: int
    page_count: int
    page_dimensions: str = "A4 (210×297 mm)"
    metadata: DocumentMetadata = field(default_factory=DocumentMetadata)
    is_encrypted: bool = False

    @property
    def file_size_formatted(self) -> str:
        size = self.file_size_bytes
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"

@dataclass
class WatermarkConfig:
    is_text: bool = True
    text: str = "PDF Master Pro"
    image_path: Optional[str] = None
    font_size: int = 40
    color: str = "#888888"
    opacity: float = 0.3
    rotation: int = 45
    all_pages: bool = True
    page_range: str = "1-"
    position: str = "center" # center, top-left, top-right, bottom-left, bottom-right

@dataclass
class SecurityConfig:
    user_password: str = ""
    owner_password: str = ""
    allow_printing: bool = True
    allow_copying: bool = True
    allow_modifying: bool = False
    allow_annotations: bool = True
    encryption_algorithm: str = "AES-256"

@dataclass
class TaskProgress:
    current: int = 0
    total: int = 100
    status_text: str = ""
    is_cancelled: bool = False
