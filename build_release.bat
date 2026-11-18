@echo off
chcp 65001 > nul
title بناء نسخة التوزيع - PDF Master Pro
echo ========================================================
echo     بناء النسخة التنفيذية PDF Master Pro (Release)
echo ========================================================
echo.

where py >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set PY_CMD=py -3.12
) else (
    set PY_CMD=python
)

echo تثبيت والتحقق من pyinstaller...
%PY_CMD% -m pip install pyinstaller

echo.
echo بدء عملية التجميع بواسطة PyInstaller...
%PY_CMD% -m PyInstaller --noconfirm --onedir --windowed ^
    --name "PDFMasterPro" ^
    --add-data "bin\pdfcpu.exe;bin" ^
    --hidden-import "PIL" ^
    --hidden-import "pikepdf" ^
    --hidden-import "pypdf" ^
    --hidden-import "reportlab" ^
    --hidden-import "PySide6.QtPdf" ^
    --hidden-import "PySide6.QtPdfWidgets" ^
    main.py

echo.
if exist "dist\PDFMasterPro\PDFMasterPro.exe" (
    echo ========================================================
    echo  اكتمل البناء بنجاح!
    echo  الملف التنفيذي جاهز في: dist\PDFMasterPro\PDFMasterPro.exe
    echo ========================================================
) else (
    echo فشلت عملية البناء. يرجى مراجعة سجل الأخطاء أعلاه.
)

pause
