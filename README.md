# HnR-2026-Lovelace

**Lovelace** - AI-Powered Fashion Assistant with Virtual Boyfriend

An agentic shopping experience inspired by Love & Deepspace, featuring a 3D avatar assistant that helps you manage your wardrobe, discover new clothes, and get personalized outfit recommendations.

## ✨ Features

1. **Video Call** - Live interaction with 3D avatar
2. **Wardrobe Management** - Scan and store your outfits
3. **Clothes Discovery** - Find new clothes on e-commerce platforms
4. **Personalized AI** - Avatar with different tastes and preferences
5. **Outfit Judging** - Get feedback on your clothing choices
6. **Virtual Try-On** - See clothes on yourself virtually
7. **Google Calendar Sync** - Dress for occasions
8. **Auto-Purchase** - Buy items with your payment details
9. **Photobooth** - Take photos with your virtual boyfriend
10. **AI Recommendations** - Outfit suggestions based on your wardrobe

## 🚀 Quick Start

### One Command Setup

```bash
# 1. Configure Firebase
# Edit frontend/.env.local with your Firebase config
# Get from: https://console.firebase.google.com/project/lovelace-b8ef5/settings/general

# 2. Install dependencies
cd frontend
npm install

cd ../backend
pip install -r requirements.txt

# 3. Start everything!
cd ../frontend
npm run dev
```

Both servers will start:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

### What You Need

1. **Firebase Web Config** - Add to `frontend/.env.local`
2. **Enable Auth** - Email/Password + Google in Firebase Console
3. **Backend Credentials** - `backend/firebase-credentials.json` (already exists)

See **`README_DEV.md`** for detailed setup instructions.

## 🛠️ Tech Stack

- **Frontend**: Next.js 16, React 19, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python
- **Database**: Firebase Firestore
- **Auth**: Firebase Authentication (Google OAuth + Email/Password)
- **AI**: Google Gemini (Nano Banana)
- **3D**: Product-to-3D Pipeline

## 📁 Project Structure

```
HnR-2026-Lovelace/
├── frontend/              # Next.js app
│   ├── app/              # Pages
│   ├── components/       # React components
│   ├── lib/              # Firebase, API client, utils
│   └── hooks/            # Custom React hooks
│
├── backend/              # FastAPI server
│   ├── main.py          # Entry point
│   └── src/             # Backend modules
│       ├── WardrobeDB/  # Firestore integration
│       ├── OAuth/       # OAuth integrations
│       ├── LiveVideoCall/  # Video call feature
│       └── ProductTo3DPipeline/  # 3D conversion
│
├── README_DEV.md        # Development guide
└── INTEGRATION_COMPLETE.md  # Full integration docs
```

## 🎯 Current Status

### ✅ Implemented
- Firebase Authentication (Google OAuth + Email/Password)
- Complete REST API with token verification
- User profile management
- Clothing item CRUD operations
- Outfit management
- Collection management
- Wardrobe statistics
- Product-to-3D pipeline
- Interactive API documentation

### 🚧 In Progress
- Virtual try-on integration
- AI outfit recommendations
- Google Calendar sync
- Live video call with avatar

## 📖 Documentation

- **`README_DEV.md`** - Quick development setup
- **`frontend/DEV_SETUP.md`** - Detailed dev environment setup
- **`INTEGRATION_COMPLETE.md`** - Full backend/frontend integration
- **`QUICKSTART_INTEGRATION.md`** - Quick reference guide
- **`frontend/AUTH_SETUP_COMPLETE.md`** - Authentication setup

## 🔒 Security

- Firebase Authentication for user management
- Token-based API authorization
- User data isolation in Firestore
- Secure environment variables
- CORS protection

## 🤝 Contributing

This is a hackathon project for HnR-2026. Feel free to contribute!

## 📝 License

See LICENSE file.

## 🎨 Design Philosophy

Lovelace features a soft "otome" aesthetic with:
- Pastel color palette
- Glassmorphism effects
- Smooth animations
- Elegant typography
- Modern, clean UI

---

**Made with 💜 for HnR-2026 Hackathon**