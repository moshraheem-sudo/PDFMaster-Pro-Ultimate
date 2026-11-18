@echo off
chcp 65001 > nul
title PDF Master Pro - Ultimate Edition
echo ========================================================
echo     تشغيل PDF Master Pro - Ultimate Edition
echo ========================================================
echo.

where py >nul 2>nul
if %ERRORLEVEL% equ 0 (
    py -3.12 main.py %*
) else (
    python main.py %*
)

if %ERRORLEVEL% neq 0 (
    echo.
    echo حدث خطأ أثناء تشغيل التطبيق. يرجى التأكد من تثبيت بايثون والاعتماديات:
    echo pip install -r requirements.txt
    pause
)
