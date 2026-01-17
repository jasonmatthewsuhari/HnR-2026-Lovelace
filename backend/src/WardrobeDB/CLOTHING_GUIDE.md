# 👕 Clothing Items Database - Complete Guide

## Overview

Your clothing database now supports:
- ✅ **Image uploads** with automatic processing
- ✅ **Multiple images** per item
- ✅ **Background removal** (optional)
- ✅ **Metadata storage** (name, category, price, tags, etc.)
- ✅ **Search & filter** by category, color, brand, tags
- ✅ **Statistics** for your wardrobe

## Data Structure

Each clothing item contains:

```json
{
  "id": "uuid",
  "user_id": "user123",
  "name": "Blue Denim Jacket",
  "category": "outerwear",
  "images": [
    "https://storage.googleapis.com/lovelace-b8ef5.appspot.com/clothing/user123/20240117_120000_abc123.jpg"
  ],
  "color": "blue",
  "size": "M",
  "brand": "Levi's",
  "price": "$89.99",
  "source": "Shopee",
  "purchase_link": "https://shopee.sg/product/123",
  "purchase_date": "2024-01-15",
  "tags": ["casual", "denim", "winter"],
  "created_at": "2024-01-17T12:00:00",
  "updated_at": "2024-01-17T12:00:00"
}
```

## Categories

Standard categories:
- `tops` - T-shirts, shirts, blouses, sweaters
- `bottoms` - Jeans, pants, skirts, shorts
- `shoes` - Sneakers, boots, sandals, heels
- `accessories` - Bags, belts, jewelry, hats, scarves
- `outerwear` - Jackets, coats, cardigans
- `dresses` - Dresses, jumpsuits, rompers
- `activewear` - Gym clothes, sportswear
- `formal` - Suits, formal dresses
- `other` - Anything else

## API Endpoints

### 1. Upload New Clothing Item

**POST** `/api/clothing/upload`

Upload a clothing item with images.

**Form Data:**
- `user_id` (required) - User ID
- `name` (required) - Item name
- `category` (required) - Category
- `images` (required) - One or more image files
- `color` (optional) - Color
- `size` (optional) - Size
- `brand` (optional) - Brand name
- `price` (optional) - Price (e.g., "$89.99")
- `source` (optional) - Where purchased (e.g., "Shopee")
- `purchase_link` (optional) - Link to product
- `purchase_date` (optional) - Date purchased (YYYY-MM-DD)
- `tags` (optional) - Comma-separated tags
- `remove_background` (optional) - Boolean, remove image background

**Example (cURL):**
```bash
curl -X POST "http://localhost:8000/api/clothing/upload" \
  -F "user_id=user123" \
  -F "name=Blue Denim Jacket" \
  -F "category=outerwear" \
  -F "images=@/path/to/jacket.jpg" \
  -F "images=@/path/to/jacket2.jpg" \
  -F "color=blue" \
  -F "size=M" \
  -F "brand=Levi's" \
  -F "price=$89.99" \
  -F "source=Shopee" \
  -F "tags=casual,denim,winter" \
  -F "remove_background=false"
```

**Example (Python):**
```python
import requests

url = "http://localhost:8000/api/clothing/upload"

with open("jacket.jpg", "rb") as f:
    files = [("images", f)]
    data = {
        "user_id": "user123",
        "name": "Blue Denim Jacket",
        "category": "outerwear",
        "color": "blue",
        "size": "M",
        "brand": "Levi's",
        "price": "$89.99",
        "tags": "casual,denim,winter"
    }
    
    response = requests.post(url, files=files, data=data)
    print(response.json())
```

### 2. Get User's Clothing Items

**GET** `/api/clothing/user/{user_id}`

Get all clothing items for a user with optional filters.

**Query Parameters:**
- `category` - Filter by category
- `color` - Filter by color
- `brand` - Filter by brand
- `tags` - Filter by tags (comma-separated)

**Examples:**
```bash
# Get all items
GET /api/clothing/user/user123

# Get only tops
GET /api/clothing/user/user123?category=tops

# Get blue items
GET /api/clothing/user/user123?color=blue

# Get items with specific tags
GET /api/clothing/user/user123?tags=casual,winter
```

### 3. Get Specific Item

**GET** `/api/clothing/{item_id}`

Get details of a specific clothing item.

### 4. Update Item

**PUT** `/api/clothing/{item_id}`

Update item metadata (not images).

**Body:**
```json
{
  "name": "Updated Name",
  "price": "$99.99",
  "tags": ["new", "tag"]
}
```

### 5. Add More Images

**POST** `/api/clothing/{item_id}/images`

Add additional images to an existing item.

**Form Data:**
- `user_id` - User ID
- `images` - Image files
- `remove_background` - Boolean

### 6. Delete Item

**DELETE** `/api/clothing/{item_id}?delete_images=true`

Delete a clothing item (and optionally its images).

### 7. Get Statistics

**GET** `/api/clothing/stats/{user_id}`

Get statistics about the user's wardrobe.

**Returns:**
```json
{
  "total_items": 25,
  "by_category": {
    "tops": 10,
    "bottoms": 8,
    "shoes": 5,
    "accessories": 2
  },
  "by_color": {
    "blue": 8,
    "black": 7,
    "white": 5
  },
  "by_brand": {
    "Uniqlo": 6,
    "H&M": 4,
    "Levi's": 3
  },
  "total_value": "$1,250.00",
  "recent_additions": [...]
}
```

## Frontend Integration

### React/Next.js Example

```typescript
// lib/api/clothing.ts

const API_URL = 'http://localhost:8000';

export interface ClothingItem {
  id: string;
  user_id: string;
  name: string;
  category: string;
  images: string[];
  color?: string;
  size?: string;
  brand?: string;
  price?: string;
  source?: string;
  purchase_date?: string;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export async function uploadClothingItem(
  userId: string,
  data: {
    name: string;
    category: string;
    images: File[];
    color?: string;
    size?: string;
    brand?: string;
    price?: string;
    source?: string;
    tags?: string[];
  }
): Promise<ClothingItem> {
  const formData = new FormData();
  
  formData.append('user_id', userId);
  formData.append('name', data.name);
  formData.append('category', data.category);
  
  // Add images
  data.images.forEach(image => {
    formData.append('images', image);
  });
  
  // Add optional fields
  if (data.color) formData.append('color', data.color);
  if (data.size) formData.append('size', data.size);
  if (data.brand) formData.append('brand', data.brand);
  if (data.price) formData.append('price', data.price);
  if (data.source) formData.append('source', data.source);
  if (data.tags) formData.append('tags', data.tags.join(','));
  
  const response = await fetch(`${API_URL}/api/clothing/upload`, {
    method: 'POST',
    body: formData
  });
  
  if (!response.ok) {
    throw new Error('Failed to upload clothing item');
  }
  
  const result = await response.json();
  return result.data.item;
}

export async function getUserClothing(
  userId: string,
  filters?: {
    category?: string;
    color?: string;
    brand?: string;
    tags?: string[];
  }
): Promise<ClothingItem[]> {
  const params = new URLSearchParams();
  
  if (filters?.category) params.append('category', filters.category);
  if (filters?.color) params.append('color', filters.color);
  if (filters?.brand) params.append('brand', filters.brand);
  if (filters?.tags) params.append('tags', filters.tags.join(','));
  
  const url = `${API_URL}/api/clothing/user/${userId}?${params}`;
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error('Failed to fetch clothing items');
  }
  
  const result = await response.json();
  return result.data;
}

export async function deleteClothingItem(itemId: string): Promise<void> {
  const response = await fetch(`${API_URL}/api/clothing/${itemId}`, {
    method: 'DELETE'
  });
  
  if (!response.ok) {
    throw new Error('Failed to delete clothing item');
  }
}
```

### Usage in Component

```typescript
// components/AddClothingForm.tsx
'use client';

import { useState } from 'react';
import { uploadClothingItem } from '@/lib/api/clothing';

export function AddClothingForm({ userId }: { userId: string }) {
  const [uploading, setUploading] = useState(false);
  
  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setUploading(true);
    
    const formData = new FormData(e.currentTarget);
    const images = formData.getAll('images') as File[];
    
    try {
      await uploadClothingItem(userId, {
        name: formData.get('name') as string,
        category: formData.get('category') as string,
        images: images,
        color: formData.get('color') as string,
        size: formData.get('size') as string,
        brand: formData.get('brand') as string,
        price: formData.get('price') as string,
        source: formData.get('source') as string,
        tags: (formData.get('tags') as string)?.split(',') || []
      });
      
      alert('Clothing item added successfully!');
    } catch (error) {
      console.error('Error uploading:', error);
      alert('Failed to upload clothing item');
    } finally {
      setUploading(false);
    }
  }
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <input name="name" placeholder="Item name" required />
      <select name="category" required>
        <option value="">Select category</option>
        <option value="tops">Tops</option>
        <option value="bottoms">Bottoms</option>
        <option value="shoes">Shoes</option>
        {/* ... more options */}
      </select>
      <input name="images" type="file" accept="image/*" multiple required />
      <input name="color" placeholder="Color" />
      <input name="size" placeholder="Size" />
      <input name="brand" placeholder="Brand" />
      <input name="price" placeholder="Price (e.g., $89.99)" />
      <input name="source" placeholder="Source (e.g., Shopee)" />
      <input name="tags" placeholder="Tags (comma-separated)" />
      
      <button type="submit" disabled={uploading}>
        {uploading ? 'Uploading...' : 'Add Item'}
      </button>
    </form>
  );
}
```

## Image Processing Features

### Automatic Processing
- **Resizing**: Images automatically resized to max 1200x1200px
- **Optimization**: JPEG quality set to 85 for optimal size/quality balance
- **Format conversion**: Supports JPEG, PNG, WebP input

### Background Removal (Optional)
Set `remove_background=true` to remove background from clothing images.

**Requirements:**
```bash
pip install rembg
```

**Use cases:**
- Product photos with distracting backgrounds
- Creating clean product catalogs
- Virtual try-on preparation

## Testing

### Start the API Server
```bash
cd backend
python main.py
```

Visit: http://localhost:8000/docs for interactive API testing

### Test with cURL
```bash
# Upload an item
curl -X POST "http://localhost:8000/api/clothing/upload" \
  -F "user_id=test_user" \
  -F "name=Test Jacket" \
  -F "category=outerwear" \
  -F "images=@test_jacket.jpg"

# Get all items
curl "http://localhost:8000/api/clothing/user/test_user"

# Get statistics
curl "http://localhost:8000/api/clothing/stats/test_user"
```

## Next Steps

1. **Enable Firestore** (if not done):
   - Visit the link from the test output
   - Click "Enable"

2. **Start uploading**:
   - Use the API directly
   - Integrate with your frontend
   - Test with Postman or cURL

3. **Optional enhancements**:
   - Add AI tagging (automatic color/style detection)
   - Implement duplicate detection
   - Add outfit creation from items

## Troubleshooting

### "Firebase Storage not initialized"
→ Check `FIREBASE_STORAGE_BUCKET` in `.env`

### "Image upload failed"
→ Check file size (max 10MB by default)
→ Check file format (JPEG, PNG, WebP only)

### "Background removal not working"
→ Install rembg: `pip install rembg`
→ First run downloads AI model (~100MB)

---

Your clothing database is now fully functional! 🎉
