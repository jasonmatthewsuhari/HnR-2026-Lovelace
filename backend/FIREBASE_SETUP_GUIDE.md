# 🔥 Firebase Google Login Setup - Complete Guide

You've already set up Firebase and enabled Google Sign-In. Here's what to do next:

## ✅ What You've Done
- Created Firebase project
- Enabled Google Authentication

## 📋 What You Need to Get

### 1. Service Account Credentials (for Backend)
This allows your Python backend to access Firebase.

**Steps:**
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Click ⚙️ (Settings) → **Project settings**
4. Go to **Service accounts** tab
5. Click **"Generate new private key"**
6. Click **"Generate key"** (downloads a JSON file)
7. Save it as `firebase-credentials.json` in your `backend/` folder

### 2. Web App Configuration (for Frontend)
This allows your Next.js frontend to use Firebase.

**Steps:**
1. In Firebase Console, click ⚙️ (Settings) → **Project settings**
2. Scroll down to **"Your apps"** section
3. If no web app exists, click **</>** (Web) icon
4. Register app (nickname: "Lovelace Web")
5. Copy the `firebaseConfig` object that looks like:
```javascript
const firebaseConfig = {
  apiKey: "AIza...",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123:web:abc123"
};
```

### 3. Google Calendar API (Optional - for Calendar Sync)

**Steps:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select the same project as your Firebase
3. Go to **APIs & Services** → **Library**
4. Search for "Google Calendar API"
5. Click **Enable**
6. Go to **Credentials** tab
7. Click **Create Credentials** → **OAuth client ID**
8. Choose **Web application**
9. Add authorized redirect URI: `http://localhost:8000/auth/google/callback`
10. Copy the **Client ID** and **Client Secret**

## 🚀 Run the Setup Script

I've created an interactive setup script for you:

```bash
cd backend
python setup_firebase_auth.py
```

This script will:
1. ✅ Ask for your service account JSON file location
2. ✅ Ask for your Firebase web config values
3. ✅ Create a `.env` file with all settings
4. ✅ Create frontend Firebase config file
5. ✅ Test the connection
6. ✅ Guide you through security rules setup

## 📝 Manual Setup (Alternative)

If you prefer to do it manually:

### 1. Create `.env` file in `backend/` folder:

```env
# Firebase
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_API_KEY=AIza...
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_STORAGE_BUCKET=your-project.appspot.com

# Google Calendar (optional)
GOOGLE_CALENDAR_CLIENT_ID=xxxxx.apps.googleusercontent.com
GOOGLE_CALENDAR_CLIENT_SECRET=GOCSPX-xxxxx
GOOGLE_CALENDAR_REDIRECT_URI=http://localhost:8000/auth/google/callback

# Server
ENVIRONMENT=development
PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# JWT (generate with: openssl rand -hex 32)
JWT_SECRET_KEY=your-secret-key-here
```

### 2. Create `frontend/lib/firebase-config.ts`:

```typescript
import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

const firebaseConfig = {
  apiKey: "AIza...",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123:web:abc123"
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const db = getFirestore(app);
export const googleProvider = new GoogleAuthProvider();

export default app;
```

### 3. Set up Firestore Security Rules

In Firebase Console → Firestore Database → Rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can read/write their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    match /clothing_items/{itemId} {
      allow read, write: if request.auth != null && 
        resource.data.user_id == request.auth.uid;
    }
    
    match /outfits/{outfitId} {
      allow read, write: if request.auth != null && 
        resource.data.user_id == request.auth.uid;
    }
    
    match /collections/{collectionId} {
      allow read, write: if request.auth != null && 
        resource.data.user_id == request.auth.uid;
    }
  }
}
```

## 🧪 Test Your Setup

### 1. Test Backend:
```bash
cd backend
pip install -r requirements.txt
python main.py
```

Visit: http://localhost:8000/health

### 2. Test Frontend Firebase:
```bash
cd frontend
npm install firebase
npm run dev
```

Visit: http://localhost:3000

## 🔐 What Each Credential Does

| Credential | Used By | Purpose |
|------------|---------|---------|
| Service Account JSON | Backend Python | Access Firestore database |
| Firebase Web Config | Frontend React | User authentication, Firestore |
| OAuth Client ID/Secret | Backend Python | Google Calendar access |
| JWT Secret | Backend Python | Secure user sessions |

## 🎯 Priority Order

**Start with these (Essential):**
1. ✅ Service Account JSON - Backend database access
2. ✅ Firebase Web Config - Frontend authentication

**Add later (Optional features):**
3. Google Calendar OAuth - Calendar sync feature
4. OpenAI API - AI recommendations
5. Replicate API - 3D model generation

## 🆘 Troubleshooting

### "Firebase not initialized"
→ Check that `firebase-credentials.json` exists in backend folder
→ Check `FIREBASE_CREDENTIALS_PATH` in `.env`

### "Auth domain mismatch"
→ Add `localhost:3000` to authorized domains in Firebase Console
→ Authentication → Settings → Authorized domains

### "CORS errors"
→ Check `CORS_ORIGINS` in `.env` includes frontend URL
→ Restart backend server after changing `.env`

## ✨ Next Steps After Setup

Once you have Firebase configured:

1. **Test Google Sign-In** on frontend
2. **Add a clothing item** to test database
3. **Create an outfit** to test relationships
4. **Check Firestore** in Firebase Console to see your data

## 💡 Quick Commands

```bash
# Run the automated setup
python backend/setup_firebase_auth.py

# Start backend
cd backend && python main.py

# Start frontend
cd frontend && npm run dev

# Test database
cd backend/src/WardrobeDB && python wardrobe_db.py
```

---

**Ready to set up?** Run:
```bash
cd backend
python setup_firebase_auth.py
```

This will walk you through everything step-by-step! 🚀
