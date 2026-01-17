@echo off
echo ============================================================
echo          Starting Lovelace Servers
echo ============================================================
echo.

echo Starting Backend (FastAPI) on http://localhost:8000...
start "Lovelace Backend" cmd /k "cd backend && python main.py"

timeout /t 3 /nobreak > nul

echo Starting Frontend (Next.js) on http://localhost:3000...
start "Lovelace Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ============================================================
echo   Both servers are starting in separate windows!
echo ============================================================
echo.
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Frontend: http://localhost:3000
echo.
echo Close this window to keep servers running
echo Or press Ctrl+C to stop
echo ============================================================

pause
