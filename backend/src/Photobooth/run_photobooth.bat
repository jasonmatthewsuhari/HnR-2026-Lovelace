@echo off
REM Quick launcher for Lovelace Photobooth
REM Double-click this file to run the photobooth

echo.
echo ======================================================================
echo                   Lovelace Photobooth Launcher
echo ======================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Check if API key is set
if "%GEMINI_API_KEY%"=="" (
    echo [ERROR] GEMINI_API_KEY not set!
    echo.
    echo Set it with:
    echo   $env:GEMINI_API_KEY='your-key-here'
    echo.
    echo Get your key at: https://ai.google.dev/
    echo.
    pause
    exit /b 1
)

echo [OK] API key configured
echo.

REM Run photobooth
echo Starting photobooth...
echo.
python photobooth.py

pause
