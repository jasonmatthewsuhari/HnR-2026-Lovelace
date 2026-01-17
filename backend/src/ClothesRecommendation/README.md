# Clothes Recommendation Module

AI-powered outfit recommendations and shopping suggestions using Gemini API.

## Overview

This module analyzes user's existing wardrobe and outfits to provide:

1. **Complete Outfit Recommendations** - Suggest outfit combinations from existing wardrobe items
2. **Shopping Recommendations** - Identify wardrobe gaps and suggest items to buy with real product links

## Features

- **AI-Powered Style Analysis** - Uses Gemini API to understand user's fashion preferences
- **Occasion-Based Recommendations** - Tailored suggestions for work, casual, formal, date nights, etc.
- **Wardrobe Gap Identification** - Identifies missing pieces to complete your wardrobe
- **Integrated Product Search** - Provides real shopping links via ClothesSearch module
- **Color Harmony** - Considers color matching and palettes
- **User Style Profile** - Builds and maintains understanding of user preferences

## Quick Start

### Prerequisites

```bash
# Install required packages (should already be installed in project)
pip install google-generativeai firebase-admin fastapi

# Set environment variables
export GEMINI_API_KEY=your_gemini_api_key

# Note: Firebase credentials should be at backend/firebase-credentials.json
# Alternatively, you can set: export FIREBASE_CREDENTIALS_PATH=path/to/firebase-credentials.json
```

### Basic Usage (Python)

```python
from src.ClothesRecommendation.clothes_recommendation import ClothesRecommender
from src.WardrobeDB.wardrobe_db import WardrobeDB
from src.ClothesSearch.clothes_search import ClothesSearcher

# Initialize
recommender = ClothesRecommender(
    gemini_api_key="your_key",
    wardrobe_db=WardrobeDB(),
    clothes_searcher=ClothesSearcher()
)

# Get recommendations
result = recommender.generate_recommendations(
    user_id="user123",
    user_outfits=[
        {
            "name": "Work Monday",
            "occasion": "work",
            "items": ["white shirt", "black pants", "leather shoes"]
        }
    ],
    occasion="date night"
)

# Access results
print(f"Found {len(result.existing_outfits)} outfit combinations")
print(f"Suggested {len(result.missing_items)} items to buy")
```

## API Endpoints

### 1. Generate Complete Recommendations

**POST** `/api/recommendations/analyze`

Generate both outfit and shopping recommendations.

**Request Body:**

```json
{
  "user_id": "user123",
  "existing_outfits": [
    {
      "name": "Work Monday",
      "occasion": "work",
      "clothing_item_ids": ["item1", "item2"],
      "times_worn": 3
    }
  ],
  "occasion": "date night",
  "max_outfits": 5,
  "max_shopping_items": 5
}
```

**Response:**

```json
{
  "existing_outfits": [
    {
      "outfit_items": [
        {
          "id": "item1",
          "name": "Black Dress",
          "category": "dresses",
          "color": "black"
        },
        { "id": "item2", "name": "Heels", "category": "shoes", "color": "nude" }
      ],
      "confidence_score": 92,
      "occasion": "date night",
      "reasoning": "Classic black dress with nude heels creates an elegant, sophisticated look perfect for upscale dates",
      "style_notes": "Add statement jewelry for more formal venues",
      "color_palette": ["black", "nude", "silver"]
    }
  ],
  "missing_items": [
    {
      "category": "accessories",
      "description": "Statement clutch or evening bag",
      "reason": "Would complete your date night looks and provide elegant storage",
      "search_query": "women's black clutch evening bag",
      "product_links": [
        {
          "url": "https://example.com/clutch",
          "title": "Black Satin Clutch",
          "description": "Elegant evening clutch with gold chain"
        }
      ],
      "priority": "medium"
    }
  ],
  "occasion": "date night",
  "analysis_summary": "You have great basics for date nights but could benefit from statement accessories",
  "user_style_profile": {
    "dominant_colors": ["black", "white", "navy"],
    "style_keywords": ["classic", "elegant", "minimalist"],
    "common_occasions": ["work", "casual"],
    "wardrobe_strengths": ["professional attire", "casual basics"],
    "wardrobe_gaps": ["formal accessories", "evening wear"]
  }
}
```

### 2. Get Outfit Recommendations Only

**GET** `/api/recommendations/outfits?user_id=user123&occasion=work&max_results=5`

Returns only outfit combinations from existing wardrobe.

**Response:**

```json
[
  {
    "outfit_items": [...],
    "confidence_score": 88,
    "occasion": "work",
    "reasoning": "Professional yet comfortable combination",
    "style_notes": "Pair with a belt for added polish",
    "color_palette": ["navy", "white", "brown"]
  }
]
```

### 3. Get Shopping Recommendations Only

**GET** `/api/recommendations/shopping?user_id=user123&occasion=formal&max_suggestions=3`

Returns only shopping suggestions with product links.

**Response:**

```json
[
  {
    "category": "outerwear",
    "description": "Tailored blazer in navy or charcoal",
    "reason": "Essential for formal occasions, missing from wardrobe",
    "search_query": "men's navy blazer tailored fit",
    "product_links": [
      {
        "url": "https://example.com/blazer",
        "title": "Navy Blazer",
        "description": "Slim fit wool blazer"
      }
    ],
    "priority": "high"
  }
]
```

### 4. Get User Style Profile

**GET** `/api/recommendations/style-profile/user123`

Analyzes and returns user's fashion preferences.

**Response:**

```json
{
  "user_id": "user123",
  "style_profile": {
    "dominant_colors": ["black", "white", "navy", "gray"],
    "style_keywords": ["minimalist", "modern", "professional"],
    "common_occasions": ["work", "casual"],
    "favorite_brands": ["Uniqlo", "Zara"],
    "wardrobe_strengths": ["professional attire", "basics"],
    "wardrobe_gaps": ["formal shoes", "statement pieces"],
    "style_summary": "Modern minimalist with focus on professional wear"
  },
  "analyzed_outfits": 15,
  "wardrobe_items": 42
}
```

### 5. Health Check

**GET** `/api/recommendations/health`

Check service status.

**Response:**

```json
{
  "status": "operational",
  "components": {
    "gemini": {
      "status": "operational",
      "model": "gemini-2.0-flash-exp"
    },
    "wardrobe_db": {
      "status": "operational"
    },
    "clothes_search": {
      "status": "operational"
    }
  }
}
```

## Testing via Swagger UI

1. Start the server:

   ```bash
   cd backend
   python main.py
   ```

2. Open http://localhost:8000/docs

3. Navigate to the "Recommendations" section

4. Try the `/api/recommendations/analyze` endpoint with sample data

## Integration Examples

### Frontend (React/TypeScript)

```typescript
// Generate recommendations
async function getRecommendations(userId: string, occasion?: string) {
  const response = await fetch(
    "http://localhost:8000/api/recommendations/analyze",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: userId,
        occasion: occasion,
        max_outfits: 5,
        max_shopping_items: 3,
      }),
    }
  );

  const data = await response.json();
  return data;
}

// Use in component
const recommendations = await getRecommendations("user123", "date night");
console.log(`Found ${recommendations.existing_outfits.length} outfits`);
console.log(`Suggested ${recommendations.missing_items.length} items to buy`);
```

### Command Line Testing

```bash
# Get outfit recommendations
curl "http://localhost:8000/api/recommendations/outfits?user_id=user123&occasion=work"

# Get shopping suggestions
curl "http://localhost:8000/api/recommendations/shopping?user_id=user123&max_suggestions=3"

# Complete analysis
curl -X POST "http://localhost:8000/api/recommendations/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "occasion": "date night",
    "max_outfits": 3,
    "max_shopping_items": 3
  }'
```

## How It Works

### 1. Style Analysis

The system analyzes user's existing outfits to understand:

- Color preferences
- Style patterns (casual, formal, sporty, etc.)
- Common occasions
- Favorite brands
- Wardrobe strengths and gaps

### 2. Outfit Recommendation

For each recommendation request:

1. Fetches user's clothing items from WardrobeDB
2. Uses Gemini AI to generate outfit combinations
3. Considers occasion, color harmony, style consistency
4. Ranks by confidence score
5. Provides reasoning and styling tips

### 3. Gap Analysis & Shopping

To identify missing items:

1. Analyzes wardrobe by category and occasion coverage
2. Identifies gaps based on user's lifestyle and style
3. Generates specific search queries
4. Calls ClothesSearch to find real products
5. Returns recommendations with direct shopping links

## Architecture

```
┌─────────────┐
│   User      │
│  Request    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│  ClothesRecommender         │
│  ┌────────────────────┐     │
│  │ Style Analysis     │     │
│  │ (Gemini AI)        │     │
│  └────────────────────┘     │
│           │                 │
│           ▼                 │
│  ┌────────────────────┐     │
│  │ Outfit Generator   │◄────┤─── WardrobeDB
│  └────────────────────┘     │
│           │                 │
│           ▼                 │
│  ┌────────────────────┐     │
│  │ Gap Analysis       │     │
│  └────────────────────┘     │
│           │                 │
│           ▼                 │
│  ┌────────────────────┐     │
│  │ Product Search     │◄────┤─── ClothesSearch
│  └────────────────────┘     │
└──────────┬──────────────────┘
           │
           ▼
    ┌─────────────┐
    │  Response   │
    └─────────────┘
```

## Configuration

### Environment Variables

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional - Firebase credentials (defaults to backend/firebase-credentials.json)
# FIREBASE_CREDENTIALS_PATH=/path/to/firebase-credentials.json

# Note: GEMINI_API_KEY is used for both recommendation and search
```

### API Keys

- **Gemini API**: Get from https://makersuite.google.com/app/apikey
- **Firebase**: Download credentials from Firebase Console

## Performance

- **Typical Response Time**: 3-5 seconds
- **Style Analysis**: ~1-2 seconds
- **Outfit Recommendations**: ~1-2 seconds
- **Shopping Search**: ~2-3 seconds (includes product search)

### Optimization Tips

1. Cache user style profiles (implemented with 1-hour TTL)
2. Batch product searches for multiple missing items
3. Limit max_outfits and max_shopping_items for faster responses
4. Pre-compute style profiles during low-traffic periods

## Error Handling

Common errors and solutions:

### "GEMINI_API_KEY not configured"

- Set the environment variable or pass it to the constructor

### "WardrobeDB not initialized"

- Ensure firebase-credentials.json exists in backend/ directory
- Or set FIREBASE_CREDENTIALS_PATH environment variable

### "No clothing items found"

- User needs to add items to their wardrobe first
- Use WardrobeDB endpoints to add items

### "Search failed"

- ClothesSearch integration is optional
- Recommendations will still work without product links

## Development

### Running Tests

```bash
cd backend/src/ClothesRecommendation
python clothes_recommendation.py  # Test core module
```

### Adding New Features

1. **Custom Occasions**: Modify prompts to include new occasion types
2. **Style Filters**: Add filters for specific styles (bohemian, streetwear, etc.)
3. **Budget Constraints**: Filter product searches by price range
4. **Brand Preferences**: Prioritize specific brands in searches

## Related Modules

- **WardrobeDB** - Stores user's clothing items and outfits
- **ClothesSearch** - Finds product links for shopping recommendations
- **VirtualTryOn** - Visual try-on for recommended outfits

## Support

For issues or questions:

1. Check health endpoint: `/api/recommendations/health`
2. Review API logs for detailed error messages
3. Verify API keys are configured correctly
4. Test with sample data via Swagger UI

## License

Part of the Lovelace - AI-Powered Fashion Assistant project.
