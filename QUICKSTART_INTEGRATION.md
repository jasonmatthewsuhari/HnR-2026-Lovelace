# 🚀 QUICK START - Complete Integration

## TL;DR - Get Everything Working

### 1. Setup (One Time)
```bash
# Run the automated setup
setup.bat

# OR manually:
cd backend
pip install fastapi uvicorn firebase-admin python-dotenv pydantic

cd ../frontend  
npm install firebase --legacy-peer-deps
```

### 2. Configure Firebase

**Get Web Config:**
https://console.firebase.google.com/project/lovelace-b8ef5/settings/general

**Edit `frontend/.env.local`:**
```env
NEXT_PUBLIC_FIREBASE_API_KEY=AIza...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=lovelace-b8ef5.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=lovelace-b8ef5
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=lovelace-b8ef5.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123...
NEXT_PUBLIC_FIREBASE_APP_ID=1:123...
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Enable Auth:**
https://console.firebase.google.com/project/lovelace-b8ef5/authentication/providers
- ✅ Email/Password
- ✅ Google

### 3. Start Servers
```bash
# Easy way - runs both in separate windows
start_servers.bat

# OR manually in 2 terminals:
# Terminal 1
cd backend
python main.py

# Terminal 2
cd frontend
npm run dev
```

### 4. Test!
1. Open http://localhost:3000
2. Click "Get Started"
3. Sign up with Google or Email
4. Complete KYC
5. Add a clothing item
6. Check backend terminal - you'll see API calls! ✨

---

## What's Working?

✅ **Google OAuth** - One-click sign in
✅ **Email/Password** - Traditional auth  
✅ **Backend API** - Full CRUD with Firebase
✅ **Token Auth** - Automatic & secure
✅ **User Profiles** - Saved in Firestore
✅ **Clothing Items** - Add/view/edit/delete
✅ **Outfits** - Create from items
✅ **Collections** - Organize outfits
✅ **Statistics** - Wardrobe analytics

---

## API Endpoints

All at http://localhost:8000/docs (interactive!)

**Key endpoints:**
- `POST /api/users/{user_id}/clothing` - Add item
- `GET /api/users/{user_id}/clothing` - Get items
- `POST /api/users/{user_id}/outfits` - Create outfit
- `GET /api/users/{user_id}/stats` - Get stats

---

## Project Structure

```
HnR-2026-Lovelace/
├── backend/
│   ├── main.py                    # FastAPI app
│   ├── firebase-credentials.json  # Service account
│   └── src/WardrobeDB/
│       ├── wardrobe_db.py        # Database logic
│       └── routes.py             # API endpoints ⭐ NEW
│
├── frontend/
│   ├── .env.local                # Firebase config (you create)
│   ├── lib/
│   │   ├── firebase.ts           # Firebase init
│   │   ├── auth.ts              # Auth functions
│   │   └── api.ts               # Backend API client ⭐ NEW
│   ├── hooks/
│   │   └── use-auth.ts          # Auth hook
│   └── components/
│       └── auth-screen.tsx      # Login/signup UI
│
├── setup.bat                     # Automated setup ⭐ NEW
├── start_servers.bat            # Start both servers ⭐ NEW
└── INTEGRATION_COMPLETE.md      # Full docs
```

---

## Troubleshooting

**Backend won't start:**
- Check `FIREBASE_CREDENTIALS_PATH` environment variable
- Or place `firebase-credentials.json` in backend folder

**Frontend auth not working:**
- Verify `.env.local` has all correct values
- Restart dev server after editing `.env.local`
- Enable auth methods in Firebase Console

**API calls failing:**
- Make sure both servers are running
- Check browser console for errors
- Verify user is signed in

---

## Need More Help?

📖 **Full Documentation:** `INTEGRATION_COMPLETE.md`
📖 **Auth Setup:** `frontend/AUTH_SETUP_COMPLETE.md`
🌐 **API Docs:** http://localhost:8000/docs (when running)

---

**You're ready to go! 🎉**
