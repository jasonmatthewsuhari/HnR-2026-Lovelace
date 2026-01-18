# 🚨 QUICK FIX: redirect_uri_mismatch Error

## TL;DR - Fix in 3 Steps

### 1️⃣ Add Redirect URI to Google Cloud Console

**Go to:** https://console.cloud.google.com/apis/credentials

1. Click on your OAuth Client ID
2. Add this to "Authorized redirect URIs":
   ```
   http://localhost:3000/calendar/auth/callback
   ```
3. Click **SAVE**
4. Wait 1-2 minutes

### 2️⃣ Configure Environment Variables

**Create/Edit:** `.env` (at project root, NOT in backend folder)

**Location:** `HnR-2026-Lovelace/.env` (same level as README.md)

**Not sure where to put it?** See: `ENV_LOCATION_GUIDE.md` for visual guide

```bash
# From project root:
copy backend\env.example .env    # Windows
cp backend/env.example .env      # Linux/Mac
```

Then edit `.env` and add:

```env
OAUTH_CLIENT_ID=your_client_id.apps.googleusercontent.com
OAUTH_CLIENT_SECRET=your_client_secret
OAUTH_REDIRECT_URI=http://localhost:3000/calendar/auth/callback
```

Get Client ID & Secret from: https://console.cloud.google.com/apis/credentials

### 3️⃣ Restart Servers

```bash
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

---

## ✅ Verify Configuration

Run this checker script:

```bash
cd backend/src/OAuth
python check_oauth_config.py
```

This will tell you exactly what's wrong (if anything).

---

## 🧪 Test

1. Go to http://localhost:3000
2. Navigate to Calendar page
3. Click "Connect to Google Calendar"
4. Should work! ✨

---

## 🆘 Still Not Working?

See full guide: **`REDIRECT_URI_FIX.md`** (same folder)

### Common Issues:

**"OAuth credentials not found"**
- Make sure `.env` file exists at **project root** (same level as README.md)
- NOT in `backend/` folder - it should be `HnR-2026-Lovelace/.env`
- Check that you have valid `OAUTH_CLIENT_ID` and `OAUTH_CLIENT_SECRET`

**Still getting redirect_uri_mismatch**
- Wait 2-3 minutes after adding URI to Google Cloud Console
- Clear browser cache or try incognito window
- Double-check the URI is EXACTLY: `http://localhost:3000/calendar/auth/callback`

**"User not authenticated"**
- Different issue - you need to log into Lovelace app first
- Then try connecting Google Calendar

---

## 📋 Checklist

- [ ] OAuth Client ID & Secret from Google Cloud Console
- [ ] Redirect URI added to Google Cloud Console
- [ ] `.env` file created at project root with OAuth credentials
- [ ] Google Calendar API enabled in Google Cloud Console
- [ ] Both servers running (backend :8000, frontend :3000)
- [ ] Waited 1-2 minutes after Google Cloud Console changes
- [ ] Tested in browser

---

## 📚 Full Documentation

- **File Location Guide:** `ENV_LOCATION_GUIDE.md` ← Where does .env go?
- **Detailed Fix Guide:** `REDIRECT_URI_FIX.md`
- **OAuth Setup:** `README.MD`
- **Configuration Checker:** `check_oauth_config.py`

All in: `backend/src/OAuth/`
