@echo off
echo ========================================
echo   SKYRIM STRING EXPORTER
echo   XML -^> source.txt
echo ========================================
echo.
cd /d "%~dp0"
python scripts\export.py
echo.
echo ========================================
echo   EXPORT SELESAI
echo ========================================
pause