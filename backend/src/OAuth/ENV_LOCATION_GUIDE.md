# 📁 Where Does .env Go? Visual Guide

## ✅ CORRECT Location

```
HnR-2026-Lovelace/               ← PROJECT ROOT
├── .env                         ← ✅ PUT IT HERE! (same level as README.md)
├── README.md
├── LICENSE
├── requirements.txt
├── setup.bat
├── backend/
│   ├── env.example             ← Copy from here
│   ├── main.py
│   └── src/
│       └── OAuth/
│           ├── oauth.py
│           └── ...
└── frontend/
    └── ...
```

## ❌ WRONG Location

```
HnR-2026-Lovelace/
├── README.md
└── backend/
    ├── .env                     ← ❌ NOT HERE!
    ├── env.example
    └── ...
```

## 🚀 How to Create It

### From Project Root (Recommended):

```bash
# Navigate to project root first
cd HnR-2026-Lovelace

# Windows:
copy backend\env.example .env

# Linux/Mac:
cp backend/env.example .env
```

### From Backend Folder:

```bash
# If you're in backend folder:
cd ..

# Now you're at project root, then:
# Windows:
copy backend\env.example .env

# Linux/Mac:
cp backend/env.example .env
```

## 🔍 How to Verify Location

### Windows PowerShell:
```powershell
# Check if .env exists at project root
Test-Path .env

# Should return: True
```

### Command Prompt:
```cmd
# Check if .env exists
dir .env

# Should show the file
```

### Linux/Mac:
```bash
# Check if .env exists
ls -la .env

# Should show the file
```

## 📝 What Should Be in .env

Your `.env` file at project root should contain:

```env
# === Google OAuth Configuration (for Calendar Sync) ===
OAUTH_CLIENT_ID=your_client_id.apps.googleusercontent.com
OAUTH_CLIENT_SECRET=your_client_secret
OAUTH_REDIRECT_URI=http://localhost:3000/calendar/auth/callback

# === Gemini API (for Clothes Search & AI features) ===
GEMINI_API_KEY=your_gemini_api_key_here

# === Tripo3D API (for Product-to-3D Pipeline) ===
TRIPO_API_KEY=your_tripo3d_api_key_here

# === Firebase Configuration ===
FIREBASE_CREDENTIALS_PATH=./backend/firebase-credentials.json
FIREBASE_PROJECT_ID=your-firebase-project-id

# === Server Configuration ===
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

## 🤔 Why Project Root?

The `.env` file is at the project root because:

1. ✅ **Both backend and frontend** can access it
2. ✅ **Consistent across all scripts** - no confusion
3. ✅ **Standard practice** for monorepo projects
4. ✅ **Already in .gitignore** at the root level
5. ✅ **Backend's dotenv** automatically looks there when you run from project root

## 🆘 Troubleshooting

### "OAuth credentials not found"

This usually means the backend can't find your `.env` file.

**Check:**
1. ✅ File is named exactly `.env` (not `.env.txt`)
2. ✅ File is at **project root** (`HnR-2026-Lovelace/.env`)
3. ✅ File contains `OAUTH_CLIENT_ID` and `OAUTH_CLIENT_SECRET`
4. ✅ You're running the backend from the correct directory:
   ```bash
   cd HnR-2026-Lovelace/backend
   uvicorn main:app --reload
   ```

### Backend Can't Load .env

If the backend is running from `backend/` directory, it will look for `.env` one level up (at project root).

This is the correct setup! The backend's `main.py` uses:
```python
from dotenv import load_dotenv
load_dotenv()  # Automatically looks in parent directories
```

### I Already Have .env in backend/

No problem! Just:

1. Move it to project root:
   ```bash
   # From backend folder:
   move .env ..\.env    # Windows
   mv .env ../.env      # Linux/Mac
   ```

2. Or copy the content and create new one at root

## ✨ Quick Test

Run this to check your setup:

```bash
cd backend/src/OAuth
python check_oauth_config.py
```

This will tell you:
- ✅ Where it's looking for .env
- ✅ If it found the file
- ✅ If your OAuth variables are set correctly

---

**See also:**
- Quick Fix: `QUICKFIX.md`
- Detailed Guide: `REDIRECT_URI_FIX.md`
- Setup Wizard: `python setup_oauth_wizard.py`
