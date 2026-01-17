@echo off
echo ============================================================
echo          LOVELACE - Complete Setup Script
echo ============================================================
echo.

echo [1/4] Checking Backend Dependencies...
cd backend
python -c "import fastapi, firebase_admin" 2>nul
if errorlevel 1 (
    echo Installing backend dependencies...
    pip install fastapi uvicorn firebase-admin python-dotenv pydantic
) else (
    echo Backend dependencies OK
)
echo.

echo [2/4] Checking Frontend Dependencies...
cd ..\frontend
if not exist node_modules\firebase (
    echo Installing firebase...
    call npm install firebase --legacy-peer-deps
) else (
    echo Firebase already installed
)
echo.

echo [3/4] Checking Environment Files...
if not exist .env.local (
    echo Creating .env.local template...
    echo NEXT_PUBLIC_FIREBASE_API_KEY=your-api-key-here > .env.local
    echo NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=lovelace-b8ef5.firebaseapp.com >> .env.local
    echo NEXT_PUBLIC_FIREBASE_PROJECT_ID=lovelace-b8ef5 >> .env.local
    echo NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=lovelace-b8ef5.appspot.com >> .env.local
    echo NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-sender-id-here >> .env.local
    echo NEXT_PUBLIC_FIREBASE_APP_ID=your-app-id-here >> .env.local
    echo NEXT_PUBLIC_API_URL=http://localhost:8000 >> .env.local
    echo.
    echo [ACTION REQUIRED] Please edit frontend\.env.local with your Firebase config!
    echo Get config from: https://console.firebase.google.com/project/lovelace-b8ef5/settings/general
) else (
    echo .env.local exists
)
echo.

echo [4/4] Checking Firebase Credentials...
cd ..\backend
if not exist firebase-credentials.json (
    echo [WARNING] firebase-credentials.json not found!
    echo Please download from Firebase Console
) else (
    echo Firebase credentials found
)
echo.

echo ============================================================
echo                    SETUP COMPLETE!
echo ============================================================
echo.
echo NEXT STEPS:
echo 1. Edit frontend\.env.local with your Firebase web config
echo 2. Enable Email/Password and Google auth in Firebase Console
echo 3. Run start_servers.bat to start both backend and frontend
echo.
echo Need help? See INTEGRATION_COMPLETE.md
echo ============================================================

pause
