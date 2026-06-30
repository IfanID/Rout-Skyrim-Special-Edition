@echo off
echo ========================================
echo   SKYRIM STRING IMPORTER
echo   source_translated.txt -^> final/Skyrim_english_english.xml
echo ========================================
echo.
cd /d "%~dp0"
python scripts\import.py
echo.
echo ========================================
echo   IMPORT SELESAI
echo ========================================