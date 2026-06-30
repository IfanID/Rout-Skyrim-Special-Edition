@echo off
echo ========================================
echo   SKYRIM STRING TRANSLATOR
echo   source.txt -^> translated/source_translated.txt
echo ========================================
echo.
cd /d "%~dp0"
python scripts\translate.py
echo.
echo ========================================
echo   TRANSLATE SELESAI
echo ========================================