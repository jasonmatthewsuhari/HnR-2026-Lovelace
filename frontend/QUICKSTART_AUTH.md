# 🚀 Quick Start - Firebase Authentication

## TL;DR - Get Auth Working in 5 Minutes

### 1. Install Firebase
```bash
cd frontend
npm install firebase
```

### 2. Get Your Config
1. Open: https://console.firebase.google.com/project/lovelace-b8ef5/settings/general
2. Scroll to "Your apps" → Web app (or add one with `</>` icon)
3. Copy the config values

### 3. Create .env.local
Create `frontend/.env.local`:
```env
NEXT_PUBLIC_FIREBASE_API_KEY=AIza... 
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=lovelace-b8ef5.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=lovelace-b8ef5
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=lovelace-b8ef5.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123...
NEXT_PUBLIC_FIREBASE_APP_ID=1:123...
```
*Replace with your actual values from Firebase!*

### 4. Enable Auth Methods
1. Open: https://console.firebase.google.com/project/lovelace-b8ef5/authentication/providers
2. Enable "Email/Password" 
3. Enable "Google"

### 5. Run It!
```bash
cd frontend
npm run dev
```

Visit http://localhost:3000 → Click "Get Started" → Try signing up! 🎉

---

## What's Working?

✅ Google OAuth (one-click sign in)  
✅ Email/Password sign up & login  
✅ Password reset ("Forgot password?")  
✅ Auto user profile creation  
✅ Error messages  
✅ Loading states  
✅ Smart routing (new users → KYC, existing → app)

---

## Files Added

```
frontend/
├── lib/firebase.ts         # Firebase setup
├── lib/auth.ts            # Auth functions
├── hooks/use-auth.ts      # React auth hook
├── components/auth-screen.tsx  # Updated UI
└── .env.local            # YOU CREATE THIS!
```

---

## Need Help?

See `AUTH_SETUP_COMPLETE.md` for detailed guide with troubleshooting!
