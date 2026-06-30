@echo off
echo ========================================
echo   SKYRIM REC EXTRACTOR
echo   XML -^> rec.txt
echo ========================================
echo.
cd /d "%~dp0"
python scripts\extract_rec.py
echo.
echo ========================================
echo   EXTRACT REC SELESAI
echo ========================================
pause