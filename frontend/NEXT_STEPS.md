# 🔥 Firebase Configuration Needed!

## ✅ Step 1: Firebase is Installed

Firebase SDK has been successfully installed! Now you need to configure it.

## 📝 Step 2: Create .env.local File

Create a new file at `frontend/.env.local` with this content:

```env
NEXT_PUBLIC_FIREBASE_API_KEY=your-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=lovelace-b8ef5.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=lovelace-b8ef5
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=lovelace-b8ef5.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
NEXT_PUBLIC_FIREBASE_APP_ID=your-app-id
```

## 🔍 Step 3: Get Your Firebase Values

1. **Open Firebase Console:**
   ```
   https://console.firebase.google.com/project/lovelace-b8ef5/settings/general
   ```

2. **Scroll down to "Your apps" section**

3. **If you see a Web app (`</>`)**:
   - Click on it
   - You'll see the Firebase SDK snippet
   - Copy the values from `firebaseConfig`

4. **If NO Web app exists**:
   - Click the `</>` (Web) icon
   - App nickname: `Lovelace Web`
   - Click "Register app"
   - Copy the `firebaseConfig` values shown

## 📋 Example Firebase Config

The Firebase Console will show something like:

```javascript
const firebaseConfig = {
  apiKey: "AIzaSyC...",  // ← Copy this to NEXT_PUBLIC_FIREBASE_API_KEY
  authDomain: "lovelace-b8ef5.firebaseapp.com",
  projectId: "lovelace-b8ef5",
  storageBucket: "lovelace-b8ef5.appspot.com",
  messagingSenderId: "123456789",  // ← Copy to NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID
  appId: "1:123456789:web:abc123"  // ← Copy to NEXT_PUBLIC_FIREBASE_APP_ID
};
```

## 🎯 Quick Action

**Copy and paste this into your terminal:**

```bash
# Windows PowerShell
@"
NEXT_PUBLIC_FIREBASE_API_KEY=your-api-key-here
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=lovelace-b8ef5.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=lovelace-b8ef5
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=lovelace-b8ef5.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-sender-id-here
NEXT_PUBLIC_FIREBASE_APP_ID=your-app-id-here
"@ | Out-File -FilePath "frontend\.env.local" -Encoding utf8
```

Then edit `frontend/.env.local` and replace the placeholder values!

## ⚡ Step 4: Enable Authentication

1. Go to: https://console.firebase.google.com/project/lovelace-b8ef5/authentication/providers
2. Enable **Email/Password**
3. Enable **Google**

## 🚀 Step 5: Restart Dev Server

After creating `.env.local`:

```bash
cd frontend
npm run dev
```

## ✨ That's It!

Your authentication should now work! Click "Get Started" and try:
- Google sign in
- Email/password sign up

---

**Need help?** See `AUTH_SETUP_COMPLETE.md` for troubleshooting!
