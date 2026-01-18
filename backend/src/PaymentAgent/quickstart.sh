#!/bin/bash
# Quick start script for Payment Agent on Unix/Mac

set -e

echo "========================================"
echo "Payment Agent - Quick Start"
echo "========================================"
echo

echo "[1/5] Checking Python..."
python3 --version || {
    echo "ERROR: Python not found!"
    echo "Please install Python 3.8+ from python.org"
    exit 1
}
echo

echo "[2/5] Installing dependencies..."
pip3 install -r requirements.txt || {
    echo "ERROR: Failed to install dependencies"
    exit 1
}
echo

echo "[3/5] Installing Playwright browsers..."
playwright install chromium || {
    echo "WARNING: Playwright installation failed"
    echo "You may need to install manually: playwright install chromium"
}
echo

echo "[4/5] Checking environment variables..."
if [ ! -f "../../.env" ]; then
    echo "WARNING: .env file not found!"
    echo "Please create backend/.env with:"
    echo "  GEMINI_API_KEY=your_key"
    echo "  STRIPE_SECRET_KEY=sk_test_your_key"
    echo
    read -p "Press enter to continue..."
fi
echo

echo "[5/5] Running setup test..."
python3 test_setup.py || {
    echo
    echo "Setup test found issues. Please fix them before continuing."
    exit 1
}
echo

echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo
echo "Next steps:"
echo "  1. Run demo: python3 demo.py"
echo "  2. Start server: cd ../.. && python3 main.py"
echo "  3. Visit: http://localhost:8000/docs"
echo
