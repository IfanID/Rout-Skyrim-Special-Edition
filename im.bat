@echo off
echo ========================================
echo   SKYRIM STRING IMPORTER
echo   source_translated.txt -^> XML
echo ========================================
echo.
cd /d "%~dp0"
python scripts\import.py
echo.
echo ========================================
echo   IMPORT SELESAI
echo ========================================
pause