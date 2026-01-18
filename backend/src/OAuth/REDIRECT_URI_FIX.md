# 🔧 Fix: Google OAuth redirect_uri_mismatch Error

## The Problem

You're seeing this error because the **redirect URI** configured in your Google Cloud Console doesn't match the one your app is using.

```
Error 400: redirect_uri_mismatch
```

## Why This Happens

Your app has multiple components:
- **Frontend (Next.js)**: Runs on `http://localhost:3000`
- **Backend (FastAPI)**: Runs on `http://localhost:8000`
- **OAuth Callback**: Should redirect to `http://localhost:3000/calendar/auth/callback`

But the default configuration uses `http://localhost:8080/oauth2callback`, which causes the mismatch.

---

## ✅ Solution: Configure the Correct Redirect URI

### Step 1: Add Redirect URI to Google Cloud Console

1. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com/apis/credentials
   - Select your project (the one with your OAuth Client ID)

2. **Find Your OAuth 2.0 Client ID:**
   - Under "OAuth 2.0 Client IDs" section
   - Click on your client ID (the one you're using for Lovelace)

3. **Add the Correct Redirect URI:**
   - Scroll down to "Authorized redirect URIs"
   - Click **"+ ADD URI"**
   - Add this **EXACT** URI:
     ```
     http://localhost:3000/calendar/auth/callback
     ```
   - **IMPORTANT:** Make sure there are NO trailing slashes, NO extra spaces

4. **Also Keep These URIs** (for different scenarios):
   ```
   http://localhost:3000/calendar/auth/callback
   http://localhost:8000/api/calendar/auth/callback
   http://localhost:8080
   ```

5. **Click "SAVE"** at the bottom of the page

6. **Wait 1-2 minutes** for changes to propagate

### Step 2: Configure Environment Variables

1. **Navigate to the project root:**
   ```bash
   cd HnR-2026-Lovelace
   ```

2. **Create/Edit `.env` file** at the project root (if it doesn't exist, copy from `backend/env.example`):
   ```bash
   # If .env doesn't exist:
   copy backend\env.example .env
   
   # Then edit .env
   ```
   
   **IMPORTANT:** The `.env` file should be at `HnR-2026-Lovelace/.env` (same level as README.md), NOT in the backend folder!

3. **Add these OAuth configuration variables** to your `.env` file:
   ```env
   # === Google OAuth Configuration ===
   # Get these from: https://console.cloud.google.com/apis/credentials
   OAUTH_CLIENT_ID=your_actual_client_id.apps.googleusercontent.com
   OAUTH_CLIENT_SECRET=your_actual_client_secret
   OAUTH_REDIRECT_URI=http://localhost:3000/calendar/auth/callback
   ```

4. **Replace the placeholder values** with your actual credentials:
   - `OAUTH_CLIENT_ID`: Copy from Google Cloud Console → Credentials
   - `OAUTH_CLIENT_SECRET`: Copy from Google Cloud Console → Credentials
   - `OAUTH_REDIRECT_URI`: Use exactly `http://localhost:3000/calendar/auth/callback`

### Step 3: Verify OAuth Configuration in Code

The backend should automatically pick up these environment variables. But let's verify:

1. **Check that `calendar_routes.py` is setting the correct redirect URI:**
   - File: `backend/src/OAuth/calendar_routes.py`
   - Line 37 should read:
     ```python
     oauth_manager.redirect_uri = os.getenv('OAUTH_REDIRECT_URI', 'http://localhost:3000/calendar/auth/callback')
     ```

2. **This is already correct in your code**, so no changes needed!

### Step 4: Restart Your Servers

After making these changes, restart both servers:

```bash
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

---

## 🧪 Test the Fix

1. **Open your app:**
   - Go to: http://localhost:3000

2. **Try Google Calendar Sync:**
   - Navigate to the Calendar page
   - Click "Connect to Google Calendar"
   - You should see the Google OAuth consent screen
   - Grant permissions
   - You should be redirected back to your app successfully!

---

## 🔍 Troubleshooting

### Still Getting redirect_uri_mismatch?

**Double-check these:**

1. ✅ **Exact match in Google Cloud Console**
   - The URI in Google Cloud Console must be EXACTLY:
     ```
     http://localhost:3000/calendar/auth/callback
     ```
   - No trailing slash, no extra spaces, no typos

2. ✅ **Wait for propagation**
   - Changes in Google Cloud Console can take 1-2 minutes to take effect
   - Try waiting a bit and testing again

3. ✅ **Check your .env file**
   - Make sure `.env` is at **project root** (`HnR-2026-Lovelace/.env`), NOT in backend folder
   - Make sure `OAUTH_REDIRECT_URI` is set correctly
   - Make sure the file is named `.env` not `.env.txt` or something else

4. ✅ **Clear browser cache**
   - Sometimes browser caches old OAuth flows
   - Try in an incognito/private window

5. ✅ **Verify environment variables are loaded**
   - In your backend terminal, you should see the OAuth manager initialize
   - No errors about missing credentials

### Error: "OAuth credentials not found in environment"

This means your `.env` file isn't being loaded. Make sure:

1. File is named exactly `.env` (not `.env.txt`)
2. File is at the **project root** (`HnR-2026-Lovelace/.env`), same level as README.md
3. NOT in the backend folder - the backend loads it from the project root
4. File contains valid `OAUTH_CLIENT_ID` and `OAUTH_CLIENT_SECRET`
5. You restarted the backend server after creating the file

### Error: "User not authenticated. Please log in first."

This is a different error - it means:
1. The Google OAuth worked! ✅
2. But you're not logged into the Lovelace app with Firebase
3. Solution: Log in to Lovelace first, THEN connect Google Calendar

---

## 📋 Complete Environment Variables Checklist

Your `.env` file (at project root: `HnR-2026-Lovelace/.env`) should include:

```env
# === Google OAuth Configuration ===
OAUTH_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
OAUTH_CLIENT_SECRET=GOCSPX-abcdefghijklmnop
OAUTH_REDIRECT_URI=http://localhost:3000/calendar/auth/callback

# === Other Configuration (from env.example) ===
GEMINI_API_KEY=your_gemini_api_key_here
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
FIREBASE_PROJECT_ID=your-firebase-project-id
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

---

## 🚀 For Production Deployment

When you deploy to production, you'll need to:

1. **Add production redirect URI to Google Cloud Console:**
   ```
   https://yourdomain.com/calendar/auth/callback
   ```

2. **Update environment variable:**
   ```env
   OAUTH_REDIRECT_URI=https://yourdomain.com/calendar/auth/callback
   ```

3. **Update authorized domains** in Google Cloud Console:
   - Add your production domain to "Authorized domains"

---

## 📚 Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [OAuth Redirect URI Best Practices](https://developers.google.com/identity/protocols/oauth2/web-server#uri-validation)
- See also: `backend/src/OAuth/README.MD` for full OAuth setup guide

---

## ✨ Quick Reference

**What you need:**
- ✅ Google Cloud Project with OAuth credentials
- ✅ Redirect URI: `http://localhost:3000/calendar/auth/callback` added to Google Cloud Console
- ✅ `backend/.env` file with `OAUTH_CLIENT_ID`, `OAUTH_CLIENT_SECRET`, and `OAUTH_REDIRECT_URI`
- ✅ Both servers running (backend on :8000, frontend on :3000)

**Where to configure:**
1. Google Cloud Console: https://console.cloud.google.com/apis/credentials
2. Backend .env file: `backend/.env`
3. Both servers restarted after changes

That's it! Your Google Calendar sync should now work! 🎉
