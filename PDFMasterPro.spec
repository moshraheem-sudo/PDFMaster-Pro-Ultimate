# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('bin/pdfcpu.exe', 'bin'),
        ('assets', 'assets')
    ],
    hiddenimports=[
        'PIL',
        'pikepdf',
        'pypdf',
        'reportlab',
        'pytesseract',
        'PySide6.QtPdf',
        'PySide6.QtPdfWidgets',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'core',
        'core.config',
        'core.models',
        'core.pdf_engine',
        'core.image_engine',
        'core.compression_engine',
        'core.security_engine',
        'core.watermark_engine',
        'core.ocr_engine',
        'core.conversion_engine',
        'core.file_manager',
        'core.task_manager',
        'core.settings_manager',
        'ui',
        'ui.theme',
        'ui.i18n',
        'ui.main_window',
        'ui.widgets.header_bar',
        'ui.widgets.sidebar',
        'ui.widgets.thumbnail_bar',
        'ui.widgets.home_dashboard',
        'ui.widgets.pdf_viewer',
        'ui.widgets.properties_panel',
        'ui.widgets.status_bar',
        'ui.dialogs.password_dialog',
        'ui.dialogs.task_dialog',
        'ui.dialogs.settings_dialog',
        'ui.dialogs.image_delete_dialog'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PDFMasterPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PDFMasterPro',
)
