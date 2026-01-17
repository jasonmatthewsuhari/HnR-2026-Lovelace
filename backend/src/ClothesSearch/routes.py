"""
FastAPI Routes for Clothes Search

Provides API endpoints for searching clothing products using Gemini API
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
import os

try:
    from .clothes_search import ClothesSearcher, GEMINI_AVAILABLE
except ImportError:
    from clothes_search import ClothesSearcher, GEMINI_AVAILABLE

# Create router
router = APIRouter(prefix="/api/search", tags=["Clothes Search"])


# Request/Response Models
class SearchRequest(BaseModel):
    """Request model for clothes search"""
    query: str = Field(..., description="Search query for clothing items", example="red summer dress")
    n: int = Field(10, ge=1, le=50, description="Number of results to return (1-50)")
    size: Optional[str] = Field(None, description="Size filter (e.g., 'M', '32', 'Large')", example="M")
    color: Optional[str] = Field(None, description="Color filter (e.g., 'black', 'blue')", example="black")
    brand: Optional[str] = Field(None, description="Brand filter (e.g., 'Nike', 'Adidas')", example="Nike")
    category: Optional[str] = Field(None, description="Category filter (e.g., 'Tops', 'Shoes')", example="Tops")


class ProductResult(BaseModel):
    """Product information from search"""
    url: str = Field(..., description="Product page URL")
    image: Optional[str] = Field(None, description="Product image URL")
    title: str = Field(..., description="Product name/title")
    description: Optional[str] = Field("", description="Product description")


class SearchResponse(BaseModel):
    """Response model for clothes search"""
    query: str = Field(..., description="Original search query")
    count: int = Field(..., description="Number of results returned")
    products: List[ProductResult] = Field(..., description="List of product results")


# Initialize searcher (singleton)
_searcher = None

def get_searcher() -> ClothesSearcher:
    """Get or create the ClothesSearcher instance"""
    global _searcher
    if _searcher is None:
        if not GEMINI_AVAILABLE:
            raise HTTPException(
                status_code=500,
                detail="Gemini API not available. Install: pip install google-generativeai"
            )
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="GEMINI_API_KEY not configured in environment"
            )
        
        try:
            _searcher = ClothesSearcher(api_key=api_key)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize Gemini API: {str(e)}"
            )
    
    return _searcher


# API Endpoints
@router.post("/clothes", response_model=SearchResponse)
async def search_clothes(request: SearchRequest):
    """
    Search for clothing products using AI-powered search
    
    Uses Gemini API to find real product links from e-commerce websites.
    Automatically focuses on Singapore availability.
    
    **Optional Filters:**
    - `size`: Filter by size (e.g., "M", "32", "Large")
    - `color`: Filter by color (e.g., "black", "blue")
    - `brand`: Filter by brand (e.g., "Nike", "Adidas")
    - `category`: Filter by category (e.g., "Tops", "Shoes", "Dresses")
    
    **Example queries:**
    - "red summer dress"
    - "nike running shoes"
    - "vintage leather jacket"
    
    **Example with filters:**
    ```json
    {
      "query": "running shoes",
      "n": 5,
      "size": "10",
      "color": "black",
      "brand": "Nike"
    }
    ```
    """
    try:
        searcher = get_searcher()
        products = searcher.search_products(
            query=request.query,
            n=request.n,
            size=request.size,
            color=request.color,
            brand=request.brand,
            category=request.category
        )
        
        return SearchResponse(
            query=request.query,
            count=len(products),
            products=[ProductResult(**p) for p in products]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/clothes", response_model=SearchResponse)
async def search_clothes_get(
    query: str = Query(..., description="Search query for clothing items", example="blue jeans"),
    n: int = Query(10, ge=1, le=50, description="Number of results (1-50)"),
    size: Optional[str] = Query(None, description="Size filter (e.g., 'M', '32')"),
    color: Optional[str] = Query(None, description="Color filter (e.g., 'black', 'blue')"),
    brand: Optional[str] = Query(None, description="Brand filter (e.g., 'Nike')"),
    category: Optional[str] = Query(None, description="Category filter (e.g., 'Tops', 'Shoes')")
):
    """
    Search for clothing products (GET version)
    
    Same as POST /api/search/clothes but accepts query parameters.
    Useful for simple browser-based testing.
    
    **Example:**
    ```
    /api/search/clothes?query=sneakers&n=5&color=white&brand=Nike
    ```
    """
    request = SearchRequest(
        query=query,
        n=n,
        size=size,
        color=color,
        brand=brand,
        category=category
    )
    return await search_clothes(request)


@router.get("/health")
async def search_health_check():
    """Check if the clothes search service is operational"""
    try:
        if not GEMINI_AVAILABLE:
            return {
                "status": "unavailable",
                "message": "google-generativeai package not installed"
            }
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return {
                "status": "not_configured",
                "message": "GEMINI_API_KEY not set in environment"
            }
        
        # Try to initialize searcher
        get_searcher()
        
        return {
            "status": "operational",
            "message": "Clothes search service is ready",
            "model": "gemini-2.0-flash-exp with google_search_retrieval"
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# For backwards compatibility
@router.post("/")
async def search_clothes_root(request: SearchRequest):
    """Legacy endpoint - redirects to /api/search/clothes"""
    return await search_clothes(request)
