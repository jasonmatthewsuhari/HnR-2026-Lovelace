# Lovelace Backend

Backend API for Lovelace - AI-Powered Fashion Assistant with Virtual Boyfriend

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Up Firebase

#### Option A: Use the Setup Helper Script

```bash
python setup_firebase.py
```

#### Option B: Manual Setup

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create/select your project
3. Go to **Project Settings** > **Service Accounts**
4. Click **Generate New Private Key**
5. Save the JSON file as `firebase-credentials.json`
6. Set environment variable:

**Windows (PowerShell):**

```powershell
$env:FIREBASE_CREDENTIALS_PATH="C:\path\to\firebase-credentials.json"
```

**Linux/Mac:**

```bash
export FIREBASE_CREDENTIALS_PATH=/path/to/firebase-credentials.json
```

### 3. Run the API Server

```bash
# Option 1: Using uvicorn directly
uvicorn main:app --reload

# Option 2: Using Python
python main.py

# Option 3: Run the complete API example
python api_example.py
```

The API will be available at:

- **API Server**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 📁 Project Structure

```
backend/
├── main.py                 # Main FastAPI application
├── api_example.py          # Complete API implementation example
├── setup_firebase.py       # Firebase setup helper
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
│
└── src/
    ├── WardrobeDB/        # Firebase wardrobe management
    │   ├── wardrobe_db.py # Main database module
    │   └── README.md      # Detailed documentation
    │
    ├── ClothesRecommendation/  # AI outfit recommendations
    ├── ClothesSearch/          # Search clothes online
    ├── VirtualTryOn/           # Virtual try-on feature
    ├── GoogleCalendarSync/     # Calendar integration
    ├── LiveVideoCall/          # Video call with avatar
    ├── Photobooth/             # Photobooth feature
    └── ProductTo3DPipeline/    # Product to 3D conversion
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
FIREBASE_PROJECT_ID=your-project-id
ENVIRONMENT=development
```

### Firebase Setup

The WardrobeDB module requires Firebase Firestore. See detailed setup in:

- `src/WardrobeDB/README.md`
- Or run `python setup_firebase.py`

## 📚 API Documentation

### Available Endpoints

Once the server is running, visit http://localhost:8000/docs for interactive API documentation.

#### User Management

- `POST /api/users` - Create user profile
- `GET /api/users/{user_id}` - Get user profile
- `PUT /api/users/{user_id}` - Update user profile
- `DELETE /api/users/{user_id}` - Delete user profile

#### Clothing Items

- `POST /api/users/{user_id}/clothing` - Add clothing item
- `GET /api/users/{user_id}/clothing` - Get user's clothing items
- `GET /api/clothing/{item_id}` - Get specific item
- `PUT /api/clothing/{item_id}` - Update item
- `DELETE /api/clothing/{item_id}` - Delete item

#### Outfits

- `POST /api/users/{user_id}/outfits` - Create outfit
- `GET /api/users/{user_id}/outfits` - Get user's outfits
- `GET /api/outfits/{outfit_id}` - Get specific outfit
- `PUT /api/outfits/{outfit_id}` - Update outfit
- `POST /api/outfits/{outfit_id}/worn` - Mark as worn
- `DELETE /api/outfits/{outfit_id}` - Delete outfit

#### Collections

- `POST /api/users/{user_id}/collections` - Create collection
- `GET /api/users/{user_id}/collections` - Get user's collections
- `GET /api/collections/{collection_id}` - Get specific collection
- `PUT /api/collections/{collection_id}` - Update collection
- `DELETE /api/collections/{collection_id}` - Delete collection

#### Statistics

- `GET /api/users/{user_id}/stats` - Get wardrobe statistics

## 🧪 Testing the Database

Test the Firebase connection and basic operations:

```bash
cd src/WardrobeDB
python wardrobe_db.py
```

This will:

1. Connect to Firebase
2. Create a test user
3. Add sample clothing items
4. Create a sample outfit
5. Display wardrobe statistics

## 🔌 Integrating with Frontend

### Example: Fetch User's Clothing Items

```typescript
// frontend/lib/api.ts
const API_URL = "http://localhost:8000";

export async function getUserClothing(userId: string) {
  const response = await fetch(`${API_URL}/api/users/${userId}/clothing`);
  if (!response.ok) throw new Error("Failed to fetch clothing");
  return response.json();
}

export async function addClothingItem(userId: string, item: any) {
  const response = await fetch(`${API_URL}/api/users/${userId}/clothing`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(item),
  });
  if (!response.ok) throw new Error("Failed to add clothing item");
  return response.json();
}
```

### Updating Frontend to Use Backend

Replace localStorage calls with API calls:

```typescript
// Before (localStorage)
const clothes = localStorage.getItem("lovelace-clothing");

// After (API)
const clothes = await getUserClothing(userId);
```

## 🛠️ Development

### Running in Development Mode

```bash
uvicorn main:app --reload --log-level debug
```

### Running in Production

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

Or use Gunicorn:

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📦 Dependencies

### Core Dependencies

- **FastAPI**: Modern web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **Firebase Admin SDK**: Database & authentication
- **python-dotenv**: Environment management

### Installation

```bash
pip install -r requirements.txt
```

## 🔒 Security

### Firestore Security Rules

Add these rules in Firebase Console > Firestore Database > Rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
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

### CORS Configuration

In production, update the CORS settings in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🐛 Troubleshooting

### Firebase Connection Issues

1. **"Database not initialized"**

   - Check that `FIREBASE_CREDENTIALS_PATH` is set
   - Verify the credentials file exists and is valid

2. **"Permission denied"**

   - Check Firestore security rules
   - Ensure the service account has proper permissions

3. **Import errors**
   - Run `pip install -r requirements.txt`
   - Ensure you're in the correct virtual environment

### API Issues

1. **CORS errors**

   - Check the `allow_origins` in CORS configuration
   - Ensure frontend URL is included

2. **404 errors**
   - Check the API endpoint URLs in your frontend
   - Verify the server is running on the correct port

## 📖 Module Documentation

- **WardrobeDB**: See `src/WardrobeDB/README.md` for detailed documentation
- Other modules: Documentation coming soon

## 🎯 Roadmap

### Implemented ✅

- [x] Firebase Firestore integration
- [x] User profile management
- [x] Clothing item CRUD operations
- [x] Outfit management
- [x] Collection management
- [x] Wardrobe statistics
- [x] FastAPI REST API
- [x] Interactive API documentation

### In Progress 🚧

- [ ] Firebase Authentication
- [ ] Image upload to Firebase Storage
- [ ] AI outfit recommendations
- [ ] Clothes search integration

### Planned 📋

- [ ] Virtual try-on
- [ ] Google Calendar sync
- [ ] Live video call with avatar
- [ ] Photobooth feature
- [ ] Product to 3D pipeline
- [ ] WebSocket support for real-time updates

## 🤝 Contributing

This is a hackathon project (HnR-2026). Feel free to contribute!

## 📝 License

See LICENSE file in the root directory.

## 💡 Support

For issues or questions:

1. Check the documentation in `src/WardrobeDB/README.md`
2. Run `python setup_firebase.py` for interactive setup help
3. Check the API docs at http://localhost:8000/docs

---

Made with 💜 for HnR-2026
