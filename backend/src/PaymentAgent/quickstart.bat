@echo off
REM Quick start script for Payment Agent on Windows

echo ========================================
echo Payment Agent - Quick Start
echo ========================================
echo.

echo [1/5] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)
echo.

echo [2/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo [3/5] Installing Playwright browsers...
playwright install chromium
if errorlevel 1 (
    echo WARNING: Playwright installation failed
    echo You may need to install manually: playwright install chromium
)
echo.

echo [4/5] Checking environment variables...
if not exist "..\..\\.env" (
    echo WARNING: .env file not found!
    echo Please create backend/.env with:
    echo   GEMINI_API_KEY=your_key
    echo   STRIPE_SECRET_KEY=sk_test_your_key
    echo.
    pause
)
echo.

echo [5/5] Running setup test...
python test_setup.py
if errorlevel 1 (
    echo.
    echo Setup test found issues. Please fix them before continuing.
    pause
    exit /b 1
)
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Run demo: python demo.py
echo   2. Start server: cd ..\.. ^&^& python main.py
echo   3. Visit: http://localhost:8000/docs
echo.
pause
