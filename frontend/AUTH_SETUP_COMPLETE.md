# 🔐 Complete Authentication Setup Guide

## ✨ What's Implemented

I've built a complete Firebase authentication system with:

✅ **Google OAuth** - One-click sign in  
✅ **Email/Password** - Traditional authentication  
✅ **Smart Routing** - New users → KYC, Existing → Main app  
✅ **Password Reset** - "Forgot password?" functionality  
✅ **Error Handling** - User-friendly messages  
✅ **Loading States** - Professional UX  
✅ **Auto Profile Creation** - Firestore user documents  

---

## 🚀 Quick Setup (5 minutes)

### Step 1: Install Firebase

```bash
cd frontend
npm install firebase
```

### Step 2: Get Firebase Web Config

1. **Go to Firebase Console:**  
   https://console.firebase.google.com/project/lovelace-b8ef5/settings/general

2. **Scroll to "Your apps" section** (bottom of page)

3. **If no Web app exists:**
   - Click the `</>` Web icon
   - App nickname: `Lovelace Web`
   - Click "Register app"
   - Copy the `firebaseConfig` object

4. **If Web app exists:**
   - Click on the existing web app
   - Scroll to "SDK setup and configuration"
   - Select "Config" radio button
   - Copy the `firebaseConfig` values

### Step 3: Create .env.local

Create `frontend/.env.local` file:

```env
NEXT_PUBLIC_FIREBASE_API_KEY=AIza... (your actual key)
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=lovelace-b8ef5.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=lovelace-b8ef5
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=lovelace-b8ef5.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123... (your actual ID)
NEXT_PUBLIC_FIREBASE_APP_ID=1:123... (your actual app ID)
```

**⚠️ Important:** 
- Replace placeholder values with YOUR actual Firebase config
- Never commit this file to git (it's in .gitignore)
- All variables MUST start with `NEXT_PUBLIC_`

### Step 4: Enable Authentication

1. **Go to Authentication page:**  
   https://console.firebase.google.com/project/lovelace-b8ef5/authentication/providers

2. **Enable Email/Password:**
   - Click "Email/Password"
   - Toggle "Enable"
   - Click "Save"

3. **Enable Google Sign-In:**
   - Click "Google"
   - Toggle "Enable"
   - Select support email from dropdown
   - Click "Save"

### Step 5: Test It!

```bash
cd frontend
npm run dev
```

1. Open http://localhost:3000
2. Click "Get Started"
3. Try signing up with:
   - Google (popup should appear)
   - Email (create new account)

---

## 📁 Files Created

```
frontend/
├── lib/
│   ├── firebase.ts        # Firebase initialization
│   └── auth.ts            # Auth functions (sign in/up/out)
├── hooks/
│   └── use-auth.ts        # React hook for auth state
├── components/
│   └── auth-screen.tsx    # Updated with real auth
├── .env.local             # YOU CREATE THIS (not in git)
└── FIREBASE_SETUP.md      # This guide

backend/
└── get_firebase_web_config.py  # Helper script
```

---

## 🔥 How It Works

### Authentication Flow

```
Landing Page
    ↓ Click "Get Started"
Loading Screen
    ↓
Auth Screen ←─────────────┐
    ↓                     │
    ├─→ Google OAuth      │
    │   • Opens popup     │
    │   • Auto-creates    │
    │     Firestore doc   │
    │                     │
    └─→ Email/Password    │
        • Sign Up →       │
          Creates user    │
          → KYC Onboarding│
        • Log In →        │
          Existing user   │
          → Main App      │
                          │
Toggle Login/Signup ───────┘
```

### User Document Structure

When a user signs up, a Firestore document is created:

```javascript
/users/{userId}/
  - uid: string
  - email: string
  - displayName: string
  - photoURL: string
  - createdAt: timestamp
  - updatedAt: timestamp
  - firstName: string
  - lastName: string
  - username: string
  - onboardingCompleted: boolean
  - location: object
  - gender: string
  - bodySize: object
  - preferences: object
```

---

## 🎯 Features Explained

### 1. Google OAuth (`signInWithGoogle()`)

```typescript
// lib/auth.ts
export async function signInWithGoogle() {
  const result = await signInWithPopup(auth, googleProvider)
  // Auto-creates user document if new user
  // Returns { user, error, isNewUser }
}
```

**What happens:**
1. Opens Google sign-in popup
2. User selects account
3. Checks if user exists in Firestore
4. Creates user document if new
5. Routes to KYC (new) or Main App (existing)

### 2. Email/Password

```typescript
// Sign Up
signUpWithEmail(email, password, displayName)

// Sign In
signInWithEmail(email, password)
```

**Validation:**
- Email must be valid format
- Password minimum 6 characters
- Display name stored in user profile

### 3. Password Reset

```typescript
resetPassword(email)
// Sends email with reset link
```

**Flow:**
1. User clicks "Forgot password?"
2. Enters email
3. Firebase sends reset email
4. User clicks link in email
5. Firebase shows password reset page

### 4. Error Handling

All Firebase errors are converted to user-friendly messages:

```typescript
auth/email-already-in-use → "This email is already registered"
auth/weak-password → "Password should be at least 6 characters"
auth/user-not-found → "No account found with this email"
```

### 5. Auth State Persistence

```typescript
// hooks/use-auth.ts
const { user, userProfile, loading, isAuthenticated } = useAuth()
```

Automatically:
- Persists auth across page refreshes
- Loads user profile from Firestore
- Updates when user signs in/out

---

## 🔒 Security

### Firestore Security Rules

Make sure you have these rules set in Firebase Console:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only read/write their own data
    match /users/{userId} {
      allow read, write: if request.auth != null 
                         && request.auth.uid == userId;
    }
    
    match /clothing_items/{itemId} {
      allow read, write: if request.auth != null 
                         && resource.data.user_id == request.auth.uid;
    }
    
    match /outfits/{outfitId} {
      allow read, write: if request.auth != null 
                         && resource.data.user_id == request.auth.uid;
    }
  }
}
```

**To update rules:**
1. Go to Firestore Database → Rules tab
2. Paste the rules above
3. Click "Publish"

---

## 🐛 Troubleshooting

### "Firebase: Error (auth/configuration-not-found)"

**Solution:**
1. Check `.env.local` exists in `frontend/` folder
2. All variables start with `NEXT_PUBLIC_`
3. Restart dev server: `npm run dev`

### "Firebase: Error (auth/unauthorized-domain)"

**Solution:**
1. Go to Authentication → Settings → Authorized domains
2. Add `localhost` (should already be there)
3. For production, add your domain

### Google popup blocked

**Solution:**
- Allow popups for localhost in browser settings
- Try different browser

### "Firebase: Error (auth/api-key-not-valid)"

**Solution:**
- Double-check API key in `.env.local`
- Make sure you copied from Firebase Console correctly
- No spaces or quotes around values

### TypeScript errors in IDE

**Solution:**
```bash
cd frontend
npm install firebase
```

### Changes not appearing

**Solution:**
- Restart Next.js dev server after creating `.env.local`
- Clear browser cache
- Check browser console for errors

---

## 📦 Next Steps

After authentication works:

### 1. Update KYC Onboarding

Save KYC data to Firestore instead of localStorage:

```typescript
// In kyc-onboarding.tsx
import { doc, updateDoc } from 'firebase/firestore'
import { db } from '@/lib/firebase'
import { getCurrentUser } from '@/lib/auth'

const handleComplete = async () => {
  const user = getCurrentUser()
  if (user) {
    await updateDoc(doc(db, 'users', user.uid), {
      firstName: formData.firstName,
      lastName: formData.lastName,
      username: formData.username,
      onboardingCompleted: true,
      // ... other KYC data
    })
  }
  onComplete()
}
```

### 2. Add Sign Out

In profile page:

```typescript
import { signOut } from '@/lib/auth'

const handleSignOut = async () => {
  await signOut()
  // Redirect to landing page
  window.location.href = '/'
}
```

### 3. Protect Routes

Check authentication in pages:

```typescript
const { user, loading } = useAuth()

if (loading) return <LoadingScreen />
if (!user) return <Navigate to="/auth" />
```

### 4. Connect Backend

Backend can verify Firebase tokens:

```python
# backend/main.py
from firebase_admin import auth

def verify_token(token: str):
    decoded_token = auth.verify_id_token(token)
    return decoded_token['uid']
```

---

## 🎨 UI Features

- **Loading spinners** during auth operations
- **Error messages** with icons
- **Success feedback** for password reset
- **Disabled states** while loading
- **Form validation** (required fields)
- **Toggle between login/signup** smoothly
- **Forgot password** modal view

---

## 💡 Tips

1. **Test with real emails** - Use your personal email for testing
2. **Check spam folder** for password reset emails
3. **Use browser DevTools** - Console shows Firebase errors
4. **Test both flows** - Google OAuth and email/password
5. **Clear localStorage** if you see old test data

---

## 📞 Support

If something doesn't work:

1. Check all steps above
2. Look at browser console for errors
3. Check Firebase Console → Authentication → Users
4. Verify `.env.local` values are correct
5. Make sure authentication methods are enabled in Firebase

---

**Made with 💜 for Lovelace**
