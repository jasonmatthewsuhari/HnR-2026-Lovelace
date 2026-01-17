# Firebase Authentication Setup Guide

## Step 1: Get Firebase Configuration

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: **lovelace-b8ef5**
3. Click on the gear icon (⚙️) → **Project settings**
4. Scroll down to "Your apps" section
5. If you haven't added a web app yet:
   - Click on the **</>** (Web) icon
   - Register app with nickname: "Lovelace Web"
   - Click "Register app"
6. Copy the Firebase configuration values

## Step 2: Create .env.local File

Create a file named `.env.local` in the `frontend` folder with these values:

```env
NEXT_PUBLIC_FIREBASE_API_KEY=your-api-key-from-firebase
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=lovelace-b8ef5.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=lovelace-b8ef5
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=lovelace-b8ef5.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-sender-id-from-firebase
NEXT_PUBLIC_FIREBASE_APP_ID=your-app-id-from-firebase
```

**Important:** Replace the placeholder values with your actual Firebase configuration!

## Step 3: Enable Authentication Methods

### Enable Email/Password Authentication

1. In Firebase Console, go to **Authentication** → **Sign-in method**
2. Click on **Email/Password**
3. Toggle **Enable** switch
4. Click **Save**

### Enable Google OAuth

1. In the same **Sign-in method** page
2. Click on **Google**
3. Toggle **Enable** switch
4. Select a **Project support email** from the dropdown
5. Click **Save**

## Step 4: Configure Authorized Domains

1. In **Authentication** → **Settings** → **Authorized domains**
2. Make sure these domains are listed:
   - `localhost` (for development)
   - Your production domain (when you deploy)

## Step 5: Install Firebase Dependencies

```bash
cd frontend
npm install firebase
```

## Step 6: Test Authentication

1. Start the frontend:
   ```bash
   npm run dev
   ```

2. Open http://localhost:3000
3. Click "Get Started"
4. Try signing up with:
   - Google OAuth (should open popup)
   - Email/Password (create new account)

## Firestore Database Rules

Make sure your Firestore has these security rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users collection
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Clothing items
    match /clothing_items/{itemId} {
      allow read, write: if request.auth != null && 
        resource.data.user_id == request.auth.uid;
    }
    
    // Outfits
    match /outfits/{outfitId} {
      allow read, write: if request.auth != null && 
        resource.data.user_id == request.auth.uid;
    }
    
    // Collections
    match /collections/{collectionId} {
      allow read, write: if request.auth != null && 
        resource.data.user_id == request.auth.uid;
    }
  }
}
```

## Troubleshooting

### "Firebase: Error (auth/configuration-not-found)"
- Make sure `.env.local` file exists in the frontend folder
- Check that all environment variables start with `NEXT_PUBLIC_`
- Restart the Next.js dev server after creating .env.local

### "Firebase: Error (auth/unauthorized-domain)"
- Add your domain to Authorized domains in Firebase Console
- For localhost, make sure `localhost` is in the list

### Google Sign-in popup blocked
- Check if your browser is blocking popups
- Allow popups for localhost

### "Firebase: Error (auth/api-key-not-valid)"
- Double-check your API key in .env.local
- Make sure there are no extra spaces or quotes

## What's Implemented

✅ **Google OAuth** - One-click sign in with Google account
✅ **Email/Password Sign Up** - Create account with email
✅ **Email/Password Sign In** - Log in with existing account
✅ **Password Reset** - "Forgot password?" functionality
✅ **Error Handling** - User-friendly error messages
✅ **Loading States** - Spinners during authentication
✅ **Auto User Document Creation** - Creates Firestore user profile
✅ **Smart Routing** - New users → KYC, Existing users → Main app

## Next Steps

After authentication works:
1. Update KYC onboarding to save to Firestore
2. Connect clothing items to Firebase Storage for images
3. Implement backend API authentication with Firebase Admin SDK
4. Add sign out functionality in the profile page
