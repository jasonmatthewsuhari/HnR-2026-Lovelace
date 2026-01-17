# Clothes Search Module

AI-powered clothing search using Google Gemini API with Google Search grounding.

## Features

- 🔍 Natural language search for clothing products
- 🛍️ Returns real product links from e-commerce sites
- 🤖 Powered by Gemini 2.0 with Google Search integration
- 📦 Easy REST API integration
- ⚡ Fast and accurate results

## Setup

### 1. Install Dependencies

```bash
pip install google-generativeai python-dotenv fastapi
```

### 2. Get Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### 3. Configure Environment

Add to your `.env` file (in `backend/` directory):

```env
GEMINI_API_KEY=your_api_key_here
```

Or set as environment variable:

**Windows (PowerShell):**

```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```

**Linux/Mac:**

```bash
export GEMINI_API_KEY="your_api_key_here"
```

## Usage

### As a Python Module

**Simple usage - just one function:**

```python
from ClothesSearch import search_clothes

# Basic search (automatically includes Singapore)
results = search_clothes("red summer dress", n=10)

for product in results:
    print(f"{product['title']}: {product['url']}")
```

**With filters:**

```python
# Search with size, color, brand, and category filters
results = search_clothes(
    query="running shoes",
    n=5,
    size="10",
    color="black",
    brand="Nike",
    category="Shoes"
)

for product in results:
    print(f"{product['title']}")
    print(f"URL: {product['url']}")
    print(f"Description: {product['description']}")
    print()
```

**All parameters:**

```python
search_clothes(
    query="dress",           # Required: what to search for
    n=10,                    # Optional: number of results (default: 10)
    size="M",                # Optional: size filter
    color="blue",            # Optional: color filter
    brand="Zara",            # Optional: brand filter
    category="Dresses",      # Optional: category filter
    api_key=None             # Optional: custom API key
)
```

### Using the ClothesSearcher Class

For more control:

```python
from ClothesSearch import ClothesSearcher

# Initialize once
searcher = ClothesSearcher()

# Search multiple times
products = searcher.search_products("nike shoes", n=5, color="white")
urls_only = searcher.search_simple("adidas tracksuit", n=10)
```

### Test the Module

```bash
cd backend/src/ClothesSearch
python clothes_search.py
```

This will run a quick test to verify everything works.

## API Endpoints

Once integrated into the main FastAPI app, the following endpoints are available:

### POST /api/search/clothes

Search for clothing products.

**Request Body:**

```json
{
  "query": "red summer dress",
  "n": 10
}
```

**Response:**

```json
{
  "query": "red summer dress",
  "count": 10,
  "products": [
    {
      "url": "https://example.com/product/red-dress",
      "title": "Red Summer Dress",
      "description": "Beautiful red summer dress..."
    }
  ]
}
```

**Example with curl:**

```bash
curl -X POST "http://localhost:8000/api/search/clothes" \
  -H "Content-Type: application/json" \
  -d '{"query": "blue jeans", "n": 5}'
```

### GET /api/search/clothes

Same as POST but with query parameters (easier for browser testing).

**Example:**

```
http://localhost:8000/api/search/clothes?query=vintage+leather+jacket&n=5
```

### GET /api/search/health

Check if the search service is operational.

**Response:**

```json
{
  "status": "operational",
  "message": "Clothes search service is ready",
  "model": "gemini-2.0-flash-exp with google_search_retrieval"
}
```

## Integration with Main App

The routes are automatically registered when you import them in `backend/main.py`:

```python
from src.ClothesSearch.routes import router as search_router

app.include_router(search_router, tags=["Clothes Search"])
```

## Example Queries

Good search queries for testing:

- **General**: "summer dresses", "running shoes", "winter coats"
- **Specific**: "red nike air max size 10", "vintage leather jacket men"
- **Style-based**: "bohemian maxi dress", "minimalist white sneakers"
- **Brand**: "adidas tracksuit", "levi's 501 jeans"
- **Occasion**: "wedding guest dress", "office casual blazer"

## Response Format

Each product result contains:

- `url` (string): Direct link to the product page
- `title` (string): Product name/title
- `description` (string): Brief description of the product

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Invalid request (bad query or parameters)
- `500`: Server error (API key missing, Gemini API failure, etc.)

**Common errors:**

1. **GEMINI_API_KEY not configured**

   - Solution: Set the API key in your environment

2. **google-generativeai not installed**

   - Solution: `pip install google-generativeai`

3. **No results found**
   - Solution: Try a more general query or different keywords

## How It Works

1. **Query Processing**: Your search query is enhanced with instructions for product search
2. **Gemini API**: Calls Gemini 2.0 with Google Search grounding tool
3. **Web Search**: Gemini searches the web using Google Search
4. **Result Parsing**: Extracts product URLs, titles, and descriptions
5. **Filtering**: Validates URLs and removes non-product pages
6. **Response**: Returns structured JSON with product information

## Configuration

### Adjustable Parameters

In `clothes_search.py`, you can modify:

- **Model**: Change `gemini-2.0-flash-exp` to `gemini-1.5-pro` for different performance
- **Max Results**: Adjust the maximum `n` value in routes (currently limited to 50)
- **URL Filters**: Add/remove patterns in `_is_valid_url()` to filter results

### Supported E-commerce Sites

The search typically returns results from:

- Amazon
- ASOS
- Zara
- H&M
- Nike
- Adidas
- Nordstrom
- Target
- Macy's
- And many more...

## Rate Limits & Costs

- **Gemini API**: Free tier includes 60 requests per minute
- **Google Search Tool**: Included in Gemini API usage
- **Costs**: Check [Google AI Pricing](https://ai.google.dev/pricing) for details

## Troubleshooting

### "Module not found" error

Make sure you're running from the correct directory:

```bash
cd backend
python -m src.ClothesSearch.clothes_search
```

### API key not working

1. Verify the key is correct
2. Check if it's properly set in environment
3. Try regenerating a new key from Google AI Studio

### No results returned

1. Try a more general query
2. Check your internet connection
3. Verify Gemini API is accessible in your region

## Development

### Running Tests

```bash
# Test the module directly
python clothes_search.py

# Test via API (with server running)
curl http://localhost:8000/api/search/health
```

### Adding New Features

Ideas for enhancement:

- Price filtering
- Brand filtering
- Size/color preferences
- Multi-language support
- Image search integration
- Caching popular queries

## API Documentation

When the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## License

Part of the Lovelace project for HnR-2026 Hackathon.

---

**Made with 💜 by the Lovelace Team**
