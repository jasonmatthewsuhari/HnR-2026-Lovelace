# Lovelace Wardrobe Database (Firebase)

This module provides a comprehensive Firebase Firestore implementation for managing user wardrobes, clothing items, outfits, and collections.

## Features

- **User Profile Management**: Store user information, preferences, and body measurements
- **Clothing Items**: Full CRUD operations for managing individual clothing pieces
- **Outfits**: Create and manage outfit combinations from clothing items
- **Collections**: Organize outfits into collections (e.g., wishlists, favorites)
- **Search & Filter**: Query clothing items by category, color, brand, etc.
- **Statistics**: Get wardrobe analytics and insights

## Setup

### 1. Install Dependencies

```bash
pip install firebase-admin
```

### 2. Set Up Firebase

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select existing project
3. Go to **Project Settings** > **Service Accounts**
4. Click **Generate New Private Key** to download credentials JSON file
5. Save the file securely (e.g., `firebase-credentials.json`)

### 3. Configure Credentials

Set the environment variable to point to your credentials file:

**Windows:**

```bash
set FIREBASE_CREDENTIALS_PATH=C:\path\to\firebase-credentials.json
```

**Linux/Mac:**

```bash
export FIREBASE_CREDENTIALS_PATH=/path/to/firebase-credentials.json
```

Or use the `GOOGLE_APPLICATION_CREDENTIALS` environment variable:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/firebase-credentials.json
```

## Usage

### Running the Main Script

```bash
cd backend/src/WardrobeDB
python wardrobe_db.py
```

This will test the Firebase connection and demonstrate basic operations.

### Using in Your Code

```python
from backend.src.WardrobeDB.wardrobe_db import (
    WardrobeDB,
    ClothingItem,
    Outfit,
    Collection,
    UserProfile
)
import uuid

# Initialize database
db = WardrobeDB(credentials_path="path/to/credentials.json")

# Create user profile
profile = UserProfile(
    user_id="user_123",
    username="fashionista",
    first_name="Jane",
    last_name="Doe",
    location="Singapore"
)
db.create_user_profile(profile)

# Add clothing item
item = ClothingItem(
    id=str(uuid.uuid4()),
    user_id="user_123",
    name="Blue Denim Jacket",
    category="outerwear",
    images=["https://example.com/image.jpg"],
    color="blue",
    size="M",
    brand="Levi's",
    price="$89.99"
)
db.add_clothing_item(item)

# Get user's clothing
items = db.get_user_clothing_items("user_123")

# Create outfit
outfit = Outfit(
    id=str(uuid.uuid4()),
    user_id="user_123",
    name="Casual Friday",
    description="Comfortable office look",
    clothing_item_ids=[item.id],
    occasion="work",
    weather="cool"
)
db.create_outfit(outfit)

# Get statistics
stats = db.get_wardrobe_stats("user_123")
print(stats)
```

## Data Models

### ClothingItem

- `id`: Unique identifier
- `user_id`: Owner's user ID
- `name`: Item name
- `category`: Category (tops, bottoms, shoes, etc.)
- `images`: List of image URLs
- `color`, `size`, `brand`, `price`, `source`: Optional metadata
- `tags`: Custom tags for organization
- `created_at`, `updated_at`: Timestamps

### Outfit

- `id`: Unique identifier
- `user_id`: Owner's user ID
- `name`: Outfit name
- `description`: Optional description
- `clothing_item_ids`: List of clothing item IDs
- `occasion`, `season`, `weather`: Context metadata
- `liked`: Boolean flag
- `times_worn`: Usage counter
- `last_worn`: Last worn timestamp
- `tags`: Custom tags

### Collection

- `id`: Unique identifier
- `user_id`: Owner's user ID
- `name`: Collection name
- `description`: Optional description
- `outfit_ids`: List of outfit IDs
- `is_wishlist`: Boolean flag for wishlists
- `tags`: Custom tags

### UserProfile

- `user_id`: Unique identifier
- `username`: Display username
- `first_name`, `last_name`: Full name
- `email`: Email address
- `location`: User location
- `gender`: Gender preference
- `body_size_data`: Body measurements dict
- `preferences`: User preferences dict

## API Methods

### User Operations

- `create_user_profile(profile)`: Create new user
- `get_user_profile(user_id)`: Get user profile
- `update_user_profile(user_id, updates)`: Update user
- `delete_user_profile(user_id)`: Delete user

### Clothing Operations

- `add_clothing_item(item)`: Add new item
- `get_clothing_item(item_id)`: Get specific item
- `get_user_clothing_items(user_id, category=None)`: Get user's items
- `update_clothing_item(item_id, updates)`: Update item
- `delete_clothing_item(item_id)`: Delete item
- `search_clothing_items(user_id, **filters)`: Search with filters

### Outfit Operations

- `create_outfit(outfit)`: Create new outfit
- `get_outfit(outfit_id)`: Get specific outfit
- `get_user_outfits(user_id, occasion=None)`: Get user's outfits
- `update_outfit(outfit_id, updates)`: Update outfit
- `delete_outfit(outfit_id)`: Delete outfit
- `get_outfit_with_items(outfit_id)`: Get outfit with populated items
- `mark_outfit_worn(outfit_id)`: Record outfit usage

### Collection Operations

- `create_collection(collection)`: Create new collection
- `get_collection(collection_id)`: Get specific collection
- `get_user_collections(user_id)`: Get user's collections
- `update_collection(collection_id, updates)`: Update collection
- `delete_collection(collection_id)`: Delete collection
- `add_outfit_to_collection(collection_id, outfit_id)`: Add outfit to collection
- `remove_outfit_from_collection(collection_id, outfit_id)`: Remove outfit from collection

### Utility Operations

- `get_wardrobe_stats(user_id)`: Get wardrobe statistics and analytics

## Firestore Collections Structure

```
users/
  {user_id}/
    - username
    - first_name
    - last_name
    - email
    - location
    - gender
    - body_size_data
    - preferences
    - created_at
    - updated_at

clothing_items/
  {item_id}/
    - user_id
    - name
    - category
    - images[]
    - color
    - size
    - brand
    - price
    - source
    - tags[]
    - created_at
    - updated_at

outfits/
  {outfit_id}/
    - user_id
    - name
    - description
    - clothing_item_ids[]
    - occasion
    - season
    - weather
    - liked
    - times_worn
    - last_worn
    - tags[]
    - created_at
    - updated_at

collections/
  {collection_id}/
    - user_id
    - name
    - description
    - outfit_ids[]
    - is_wishlist
    - tags[]
    - created_at
    - updated_at
```

## Security Rules (Firestore)

Add these rules in Firebase Console > Firestore Database > Rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only read/write their own data
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

## Error Handling

The module includes comprehensive error handling. Common errors:

- **ImportError**: Firebase libraries not installed
- **ValueError**: No credentials provided
- **Firebase errors**: Network issues, permission denied, etc.

## Integration with Frontend

The frontend currently uses localStorage. To integrate with this backend:

1. Set up Firebase Authentication for users
2. Create API endpoints using Flask/FastAPI
3. Update frontend to call backend APIs instead of localStorage
4. Handle image uploads to Firebase Storage

## Next Steps

- [ ] Add API endpoints (Flask/FastAPI)
- [ ] Integrate Firebase Storage for images
- [ ] Add Firebase Authentication
- [ ] Implement caching for performance
- [ ] Add batch operations for bulk updates
- [ ] Create backup/export functionality
