# Search Products Feature - Frontend Integration

## ✅ What Was Added

### 1. New Component: `search-products-modal.tsx`

A complete product search interface with:
- ✅ **Search Query**: Main input for what to search
- ✅ **Optional Filters**: Size, Color, Brand, Category
- ✅ **Real-time Search**: Calls backend API
- ✅ **Singapore Results**: Automatically searches Singapore stores
- ✅ **Beautiful Results**: Shows products with links
- ✅ **Loading States**: Shows spinner while searching
- ✅ **Error Handling**: Displays errors gracefully

### 2. Updated: `main-app.tsx`

- ✅ Added "Search Products" option to dropdown menu
- ✅ Positioned between Photobooth and Calendar
- ✅ Beautiful gradient icon with ShoppingBag
- ✅ Opens modal when clicked

## 🎯 User Flow

### Opening Search Products
1. Click **Menu button** (top left)
2. Select **"Search Products"**
3. Modal opens full-screen

### Searching for Products

**Step 1: Enter Search Query**
- Type what you're looking for (e.g., "red dress", "running shoes")
- Press Enter or click "Search"

**Step 2: Add Filters (Optional)**
- **Size**: e.g., "M", "32", "Large"
- **Color**: e.g., "black", "blue", "red"
- **Brand**: e.g., "Nike", "Zara", "Adidas"
- **Category**: e.g., "Tops", "Shoes", "Dresses"

**Step 3: View Results**
- See list of products from Singapore stores
- Each result shows:
  - Product title
  - Description
  - Direct product URL
- Click any product to open in new tab

## 🔧 Features

### Automatic Singapore Focus
- ✅ All searches automatically include "Singapore"
- ✅ Results from local stores (Nike.com/sg, Zalora.sg, etc.)

### Smart Filtering
- ✅ Filters are optional - use as many or as few as you want
- ✅ Filters seamlessly integrated into search
- ✅ Example: "shoes size 10 black color Nike brand Singapore"

### Backend Integration
- ✅ Calls `/api/search/clothes` endpoint
- ✅ Handles both GET and POST requests
- ✅ 10-20 second response time
- ✅ Returns real product links

## 📍 Position in Menu

Dropdown menu order:
1. **Video Call** - Live chat with fashion advisor
2. **Virtual Try-On** - See how clothes look on you
3. **Photobooth** - Take couple's photos with AI
4. **Search Products** ← NEW! 🎉
5. **Your Calendar** - Sync with Google Calendar

## 🎨 Design

- **Icon**: ShoppingBag (lucide-react)
- **Colors**: Orange to Pink to Purple gradient
- **Modal**: Full-screen with backdrop blur
- **Results**: Clean cards with hover effects
- **Responsive**: Works on all screen sizes

## 💡 Usage Examples

### Basic Search
```
Query: "summer dress"
→ Returns 10 dresses from Singapore stores
```

### With Filters
```
Query: "running shoes"
Size: "10"
Color: "black"
Brand: "Nike"
→ Returns Nike black running shoes size 10 from Singapore
```

### Category Search
```
Query: "casual"
Category: "Tops"
Color: "blue"
→ Returns casual blue tops from Singapore stores
```

## 🚀 Backend API

**Endpoint**: `http://localhost:8000/api/search/clothes`

**Parameters**:
- `query` (required): Search query
- `n` (optional): Number of results (default: 10)
- `size` (optional): Size filter
- `color` (optional): Color filter
- `brand` (optional): Brand filter
- `category` (optional): Category filter

**Response**:
```json
{
  "query": "red dress",
  "count": 10,
  "products": [
    {
      "url": "https://example.com/product",
      "title": "Red Summer Dress",
      "description": "Beautiful red dress..."
    }
  ]
}
```

## ✨ Next Steps

Users can now:
1. Open menu
2. Click "Search Products"
3. Search for anything
4. Add optional filters
5. Get real product links from Singapore stores
6. Click to buy directly

---

**Made with 💜 for Lovelace - HnR-2026 Hackathon**
