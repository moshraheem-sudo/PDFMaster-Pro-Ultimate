"""
PDF Master Pro - Internationalization & Localization (Arabic & English)
"""
from typing import Dict

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # App Identity
    "app_title": {
        "ar": "PDF Master Pro | Ultimate Edition 👑",
        "en": "PDF Master Pro | Ultimate Edition 👑"
    },
    "app_subtitle": {
        "ar": "أداة احترافية متكاملة لمعالجة ملفات PDF والصور",
        "en": "All-in-one Professional Suite for PDF & Image Processing"
    },
    
    # Top Bar Actions
    "open_file": {
        "ar": "فتح ملف",
        "en": "Open File"
    },
    "new_file": {
        "ar": "إنشاء جديد +",
        "en": "New File +"
    },
    "save": {
        "ar": "حفظ",
        "en": "Save"
    },
    "save_as": {
        "ar": "حفظ باسم",
        "en": "Save As"
    },
    "undo": {
        "ar": "تراجع",
        "en": "Undo"
    },
    "redo": {
        "ar": "إعادة",
        "en": "Redo"
    },
    "settings": {
        "ar": "الإعدادات",
        "en": "Settings"
    },
    "help": {
        "ar": "المساعدة",
        "en": "Help"
    },
    "language": {
        "ar": "العربية",
        "en": "English"
    },
    
    # Sidebar Menu
    "menu_home": {
        "ar": "الصفحة الرئيسية",
        "en": "Home"
    },
    "menu_file_manager": {
        "ar": "إدارة الملفات",
        "en": "File Manager"
    },
    "menu_edit_pdf": {
        "ar": "تحرير PDF",
        "en": "Edit PDF"
    },
    "menu_compress_pdf": {
        "ar": "ضغط الملفات",
        "en": "Compress PDF"
    },
    "menu_compress_images": {
        "ar": "ضغط الصور",
        "en": "Compress Images"
    },
    "menu_split_merge": {
        "ar": "تقسيم ودمج",
        "en": "Split & Merge"
    },
    "menu_rotate": {
        "ar": "تدوير الصفحات والصور",
        "en": "Rotate Pages & Images"
    },
    "menu_extract_images": {
        "ar": "استخراج الصور",
        "en": "Extract Images"
    },
    "menu_delete_images": {
        "ar": "حذف الصور من PDF",
        "en": "Delete Images from PDF"
    },
    "menu_watermark": {
        "ar": "العلامات المائية",
        "en": "Watermarks"
    },
    "menu_security": {
        "ar": "حماية PDF",
        "en": "PDF Security"
    },
    "menu_convert": {
        "ar": "التحويل",
        "en": "Convert"
    },
    "menu_ocr": {
        "ar": "التعرف الضوئي OCR",
        "en": "OCR Recognition"
    },
    
    # Compression Panel (Reference Image Match)
    "compression_panel_title": {
        "ar": "خيارات الضغط على PDF",
        "en": "PDF Compression Options"
    },
    "compression_level_label": {
        "ar": "مستوى الضغط:",
        "en": "Compression Level:"
    },
    "comp_light_title": {
        "ar": "خفيف",
        "en": "Light"
    },
    "comp_light_desc": {
        "ar": "(جودة عالية)",
        "en": "(High Quality)"
    },
    "comp_medium_title": {
        "ar": "متوسط",
        "en": "Medium"
    },
    "comp_medium_desc": {
        "ar": "(توازن مثالي)",
        "en": "(Balanced)"
    },
    "comp_strong_title": {
        "ar": "قوي",
        "en": "Strong"
    },
    "comp_strong_desc": {
        "ar": "(أقل حجم)",
        "en": "(Max Savings)"
    },
    "advanced_options": {
        "ar": "خيارات متقدمة:",
        "en": "Advanced Options:"
    },
    "opt_optimize_images": {
        "ar": "تحسين الصور وتقليل الدقة",
        "en": "Optimize Images & Reduce DPI"
    },
    "opt_remove_unused": {
        "ar": "إزالة الموارد غير المستخدمة",
        "en": "Remove Unused Resources"
    },
    "opt_compress_fonts": {
        "ar": "ضغط الخطوط والبيانات",
        "en": "Compress Fonts & Stream Data"
    },
    "original_size": {
        "ar": "الحجم الأصلي:",
        "en": "Original Size:"
    },
    "expected_size": {
        "ar": "الحجم المتوقع:",
        "en": "Expected Size:"
    },
    "saving_ratio": {
        "ar": "نسبة التوفير:",
        "en": "Saving Ratio:"
    },
    "start_compression_btn": {
        "ar": "بدء الضغط ⚡",
        "en": "Start Compression ⚡"
    },
    
    # Status Bar
    "status_ready": {
        "ar": "جاهز ...",
        "en": "Ready ..."
    },
    "page_unit": {
        "ar": "صفحة",
        "en": "Pages"
    },
    "show_tasks": {
        "ar": "عرض العمليات",
        "en": "Task Manager"
    },
    
    # Dashboard / Home Screen
    "welcome_title": {
        "ar": "مرحباً بك في PDF Master Pro",
        "en": "Welcome to PDF Master Pro"
    },
    "drop_prompt": {
        "ar": "اسحب وأفلت ملفات PDF والصور هنا للبدء مباشرة",
        "en": "Drag and drop PDF or Image files here to start immediately"
    },
    "or_browse": {
        "ar": "أو استعرض من جهازك",
        "en": "Or browse from your computer"
    },
    "recent_files": {
        "ar": "الملفات الأخيرة",
        "en": "Recent Files"
    },
    "no_recent_files": {
        "ar": "لا توجد ملفات أخيرة حتى الآن",
        "en": "No recent files yet"
    },
    "clear_history": {
        "ar": "مسح السجل",
        "en": "Clear History"
    },
    
    # Tool Cards on Dashboard
    "card_merge_title": {
        "ar": "دمج ملفات PDF",
        "en": "Merge PDFs"
    },
    "card_merge_desc": {
        "ar": "تجميع عدة مستندات بترتيب مخصص في ملف واحد",
        "en": "Combine multiple documents into one in custom order"
    },
    "card_split_title": {
        "ar": "تقسيم ملفات PDF",
        "en": "Split PDFs"
    },
    "card_split_desc": {
        "ar": "فصل الصفحات أو استخراج نطاقات محددة بدقة",
        "en": "Separate pages or extract specific page ranges"
    },
    "card_compress_title": {
        "ar": "ضغط ملفات PDF",
        "en": "Compress PDFs"
    },
    "card_compress_desc": {
        "ar": "تقليص حجم المستندات باحترافية مع حفظ الجودة",
        "en": "Reduce document size with high visual quality"
    },
    "card_edit_title": {
        "ar": "تحرير الصفحات",
        "en": "Edit Pages"
    },
    "card_edit_desc": {
        "ar": "حذف، تكرار، تدوير وإعادة ترتيب الصفحات",
        "en": "Delete, duplicate, rotate, and reorder pages"
    },
    "card_img_compress_title": {
        "ar": "ضغط الصور",
        "en": "Compress Images"
    },
    "card_img_compress_desc": {
        "ar": "ضغط ومعالجة صور متعددة وتحويل الصيغ دفعة واحدة",
        "en": "Batch compress images and convert formats"
    },
    "card_extract_img_title": {
        "ar": "استخراج الصور",
        "en": "Extract Images"
    },
    "card_extract_img_desc": {
        "ar": "استخراج جميع الصور المضمنة في المستند بدقتها الأصلية",
        "en": "Extract all embedded images in their native resolution"
    },
    "card_security_title": {
        "ar": "حماية بكلمة مرور",
        "en": "Password Protection"
    },
    "card_security_desc": {
        "ar": "تشفير AES-256 متقدم وضبط صلاحيات الطباعة والنسخ",
        "en": "Advanced AES-256 encryption & permission controls"
    },
    "card_watermark_title": {
        "ar": "العلامات المائية",
        "en": "Watermarks"
    },
    "card_watermark_desc": {
        "ar": "إضافة علامات مائية نصية وصورية أو إزالتها",
        "en": "Add or remove text and image watermarks"
    },
    "card_ocr_title": {
        "ar": "التعرف الضوئي OCR",
        "en": "OCR Text Recognition"
    },
    "card_ocr_desc": {
        "ar": "استخراج النصوص العربية والإنجليزية من المستندات الممسوحة",
        "en": "Extract Arabic & English text from scanned files"
    },
    "card_convert_title": {
        "ar": "تحويل المستندات والصور",
        "en": "Convert Documents"
    },
    "card_convert_desc": {
        "ar": "تحويل الصور إلى PDF أو تصدير صفحات PDF كصور",
        "en": "Convert images to PDF or export pages as images"
    }
}

class I18n:
    _current_lang = "ar"

    @classmethod
    def set_language(cls, lang: str):
        if lang in ("ar", "en"):
            cls._current_lang = lang

    @classmethod
    def get_language(cls) -> str:
        return cls._current_lang

    @classmethod
    def is_rtl(cls) -> bool:
        return cls._current_lang == "ar"

    @classmethod
    def t(cls, key: str, default: str = "") -> str:
        entry = TRANSLATIONS.get(key)
        if entry:
            return entry.get(cls._current_lang, default or key)
        return default or key

def tr(key: str, default: str = "") -> str:
    return I18n.t(key, default)
