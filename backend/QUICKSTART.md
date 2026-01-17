# Lovelace Backend - Quick Reference

## 🚀 Setup (5 Minutes)

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Get Firebase credentials
# Go to: https://console.firebase.google.com/
# Project Settings > Service Accounts > Generate New Private Key
# Save as firebase-credentials.json

# 3. Set environment variable
# Windows:
$env:FIREBASE_CREDENTIALS_PATH="C:\path\to\firebase-credentials.json"
# Linux/Mac:
export FIREBASE_CREDENTIALS_PATH=/path/to/firebase-credentials.json

# 4. Test it
python usage_examples.py

# 5. Start API
python main.py
```

## 📍 Important URLs

- **API Server**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## 🔥 Common Commands

```bash
# Run main API server
python main.py

# Or with uvicorn
uvicorn main:app --reload

# Run complete API example
python api_example.py

# Test database connection
cd src/WardrobeDB
python wardrobe_db.py

# Run usage examples
python usage_examples.py

# Setup wizard
python setup_firebase.py
```

## 📦 Files Overview

| File | Purpose |
|------|---------|
| `main.py` | Main FastAPI application |
| `api_example.py` | Complete API with all endpoints |
| `usage_examples.py` | Tutorial with 8 examples |
| `setup_firebase.py` | Interactive setup wizard |
| `src/WardrobeDB/wardrobe_db.py` | Core database module |
| `requirements.txt` | Python dependencies |

## 🎯 Quick API Examples

### Create User
```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "jane_doe",
    "first_name": "Jane",
    "location": "Singapore"
  }'
```

### Add Clothing Item
```bash
curl -X POST http://localhost:8000/api/users/{user_id}/clothing \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Blue Denim Jacket",
    "category": "outerwear",
    "images": ["https://example.com/jacket.jpg"],
    "color": "blue",
    "size": "M",
    "brand": "Levis",
    "price": "$89.99"
  }'
```

### Get User's Clothing
```bash
curl http://localhost:8000/api/users/{user_id}/clothing
```

### Create Outfit
```bash
curl -X POST http://localhost:8000/api/users/{user_id}/outfits \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Casual Friday",
    "clothing_item_ids": ["item1", "item2", "item3"],
    "occasion": "work",
    "weather": "sunny"
  }'
```

### Get Wardrobe Stats
```bash
curl http://localhost:8000/api/users/{user_id}/stats
```

## 🐍 Python Usage

```python
from src.WardrobeDB.wardrobe_db import WardrobeDB, ClothingItem
import uuid

# Initialize
db = WardrobeDB(credentials_path="firebase-credentials.json")

# Add clothing
item = ClothingItem(
    id=str(uuid.uuid4()),
    user_id="user123",
    name="White T-Shirt",
    category="tops",
    images=["url"],
    color="white",
    size="M"
)
db.add_clothing_item(item)

# Get user's clothes
items = db.get_user_clothing_items("user123")

# Get stats
stats = db.get_wardrobe_stats("user123")
```

## 🔧 Environment Variables

```env
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
FIREBASE_PROJECT_ID=your-project-id
ENVIRONMENT=development
```

## 🎨 Data Models

### ClothingItem
```python
{
  "id": "uuid",
  "user_id": "user123",
  "name": "Blue Jacket",
  "category": "outerwear",  # tops, bottoms, shoes, accessories, etc.
  "images": ["url1", "url2"],
  "color": "blue",
  "size": "M",
  "brand": "Levi's",
  "price": "$89.99",
  "source": "Shopee",
  "tags": ["casual", "denim"]
}
```

### Outfit
```python
{
  "id": "uuid",
  "user_id": "user123",
  "name": "Casual Friday",
  "description": "Comfortable office look",
  "clothing_item_ids": ["item1", "item2"],
  "occasion": "work",  # work, casual, formal, etc.
  "season": "spring",
  "weather": "sunny",
  "liked": false,
  "times_worn": 0,
  "last_worn": null
}
```

## 🎓 Learning Path

1. **Start here**: `backend/README.md`
2. **Understand the database**: `backend/src/WardrobeDB/README.md`
3. **See it in action**: `python usage_examples.py`
4. **Explore API**: http://localhost:8000/docs
5. **Build something**: Integrate with frontend!

## 💡 Pro Tips

- Use `python setup_firebase.py` for first-time setup
- Check `usage_examples.py` for code samples
- API docs at `/docs` are interactive - try requests there!
- Keep `firebase-credentials.json` in `.gitignore`
- Use `uvicorn main:app --reload` for auto-reload during dev

## 📚 Documentation

- **Backend Overview**: `backend/README.md`
- **Database Module**: `backend/src/WardrobeDB/README.md`
- **Implementation Summary**: `backend/IMPLEMENTATION_SUMMARY.md`
- **This Quick Ref**: `backend/QUICKSTART.md`

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| "Database not initialized" | Set `FIREBASE_CREDENTIALS_PATH` |
| Import errors | Run `pip install -r requirements.txt` |
| CORS errors | Update `allow_origins` in API |
| 404 errors | Check endpoint URL and method |

## 🎉 You're Ready!

Everything is set up and ready to use. Start with:

```bash
python usage_examples.py
```

Then explore the API at http://localhost:8000/docs

Happy coding! 💜
