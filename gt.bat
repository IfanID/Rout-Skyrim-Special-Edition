@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

if "%~1"=="" (
    echo Usage: gt input/filenya.xml [target_script]
    echo Contoh:
    echo   gt Dialog.xml
    echo   gt input/Quest.xml
    echo   gt MyFile.xml scripts/export.py
    pause
    exit /b 1
)

echo ========================================
echo   GANTI DEFAULT_INPUT
echo ========================================
echo.
if "%~2"=="" (
    echo Mengganti DEFAULT_INPUT di scripts/export.py menjadi "%~1"
    echo.
    python scripts\ganti.py "%~1"
) else (
    echo Mengganti DEFAULT_INPUT di %2 menjadi "%~1"
    echo.
    python scripts\ganti.py "%~1" "%~2"
)
echo.