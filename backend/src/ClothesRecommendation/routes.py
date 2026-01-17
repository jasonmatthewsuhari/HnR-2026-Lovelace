"""
FastAPI Routes for Clothes Recommendation

Provides API endpoints for AI-powered outfit recommendations and shopping suggestions
"""

from fastapi import APIRouter, HTTPException, Query, Depends, Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
from pathlib import Path as PathLib

try:
    from .clothes_recommendation import (
        ClothesRecommender,
        RecommendationResult,
        OutfitRecommendation,
        MissingItemRecommendation,
        GEMINI_AVAILABLE
    )
    from ..WardrobeDB.wardrobe_db import WardrobeDB
    from ..ClothesSearch.clothes_search import ClothesSearcher
except ImportError:
    # Fallback for direct execution
    from clothes_recommendation import (
        ClothesRecommender,
        RecommendationResult,
        OutfitRecommendation,
        MissingItemRecommendation,
        GEMINI_AVAILABLE
    )
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from WardrobeDB.wardrobe_db import WardrobeDB
    from ClothesSearch.clothes_search import ClothesSearcher

# Create router
router = APIRouter(prefix="/api/recommendations", tags=["Clothes Recommendations"])


# Request/Response Models
class OutfitDict(BaseModel):
    """Outfit information for style analysis"""
    name: Optional[str] = Field(None, description="Outfit name")
    occasion: Optional[str] = Field(None, description="Occasion (work, casual, formal, etc.)")
    clothing_item_ids: Optional[List[str]] = Field(None, description="List of clothing item IDs")
    items: Optional[List[str]] = Field(None, description="Alternative: list of item descriptions")
    times_worn: Optional[int] = Field(0, description="How many times worn")


class RecommendationRequest(BaseModel):
    """Request model for generating recommendations"""
    user_id: str = Field(..., description="User ID")
    existing_outfits: Optional[List[OutfitDict]] = Field(None, description="User's existing outfits for style analysis")
    occasion: Optional[str] = Field(None, description="Target occasion (work, casual, date, formal, etc.)")
    max_outfits: int = Field(5, ge=1, le=10, description="Maximum outfit recommendations (1-10)")
    max_shopping_items: int = Field(5, ge=1, le=10, description="Maximum shopping suggestions (1-10)")


class ProductLinkResponse(BaseModel):
    """Product link information"""
    url: str
    title: str
    description: str


class OutfitRecommendationResponse(BaseModel):
    """Outfit recommendation response"""
    outfit_items: List[Dict[str, Any]]
    confidence_score: float
    occasion: str
    reasoning: str
    style_notes: Optional[str] = None
    color_palette: Optional[List[str]] = None


class MissingItemResponse(BaseModel):
    """Missing item recommendation response"""
    category: str
    description: str
    reason: str
    search_query: str
    product_links: List[ProductLinkResponse]
    priority: str


class RecommendationResponse(BaseModel):
    """Complete recommendation response"""
    existing_outfits: List[OutfitRecommendationResponse]
    missing_items: List[MissingItemResponse]
    occasion: Optional[str]
    analysis_summary: str
    user_style_profile: Optional[Dict[str, Any]] = None


# Singleton instances
_recommender = None
_wardrobe_db = None
_clothes_searcher = None


def get_wardrobe_db() -> WardrobeDB:
    """Get or create WardrobeDB instance"""
    global _wardrobe_db
    if _wardrobe_db is None:
        try:
            # Try to find firebase-credentials.json in backend directory
            current_dir = PathLib(__file__).resolve()
            backend_dir = current_dir.parent.parent.parent
            credentials_path = backend_dir / "firebase-credentials.json"
            
            # Fallback to environment variable if file doesn't exist
            if not credentials_path.exists():
                credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
            else:
                credentials_path = str(credentials_path)
            
            _wardrobe_db = WardrobeDB(credentials_path=credentials_path)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize WardrobeDB: {str(e)}"
            )
    return _wardrobe_db


def get_clothes_searcher() -> Optional[ClothesSearcher]:
    """Get or create ClothesSearcher instance (optional)"""
    global _clothes_searcher
    if _clothes_searcher is None:
        try:
            if os.getenv("GEMINI_API_KEY"):
                _clothes_searcher = ClothesSearcher()
                print("ClothesSearcher initialized successfully")
            else:
                print("Warning: GEMINI_API_KEY not set, product search will be disabled")
        except Exception as e:
            print(f"Warning: Could not initialize ClothesSearcher: {e}")
            return None
    return _clothes_searcher


def get_recommender() -> ClothesRecommender:
    """Get or create ClothesRecommender instance"""
    global _recommender
    if _recommender is None:
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
            _recommender = ClothesRecommender(
                gemini_api_key=api_key,
                wardrobe_db=get_wardrobe_db(),
                clothes_searcher=get_clothes_searcher()
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize recommender: {str(e)}"
            )
    
    return _recommender


# API Endpoints
@router.post("/analyze", response_model=RecommendationResponse)
async def analyze_and_recommend(request: RecommendationRequest):
    """
    Generate complete recommendations including outfits and shopping suggestions
    
    This endpoint analyzes the user's wardrobe and existing outfits to provide:
    1. Complete outfit recommendations from existing wardrobe items
    2. Shopping suggestions for missing pieces with product links
    
    **Example request:**
    ```json
    {
      "user_id": "user123",
      "existing_outfits": [
        {
          "name": "Work Monday",
          "occasion": "work",
          "items": ["white shirt", "black pants"]
        }
      ],
      "occasion": "date night",
      "max_outfits": 5,
      "max_shopping_items": 3
    }
    ```
    """
    try:
        recommender = get_recommender()
        
        # Convert Pydantic models to dicts
        outfits_data = None
        if request.existing_outfits:
            outfits_data = [outfit.dict() for outfit in request.existing_outfits]
        
        # Generate recommendations
        result = recommender.generate_recommendations(
            user_id=request.user_id,
            user_outfits=outfits_data,
            occasion=request.occasion,
            max_outfits=request.max_outfits,
            max_shopping_items=request.max_shopping_items
        )
        
        # Convert to response format
        return RecommendationResponse(
            existing_outfits=[
                OutfitRecommendationResponse(**outfit.to_dict())
                for outfit in result.existing_outfits
            ],
            missing_items=[
                MissingItemResponse(
                    category=item.category,
                    description=item.description,
                    reason=item.reason,
                    search_query=item.search_query,
                    product_links=[
                        ProductLinkResponse(**link.to_dict())
                        for link in item.product_links
                    ],
                    priority=item.priority
                )
                for item in result.missing_items
            ],
            occasion=result.occasion,
            analysis_summary=result.analysis_summary,
            user_style_profile=result.user_style_profile
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Recommendation generation failed: {str(e)}"
        )


@router.get("/outfits", response_model=List[OutfitRecommendationResponse])
async def get_outfit_recommendations(
    user_id: str = Query(..., description="User ID"),
    occasion: Optional[str] = Query(None, description="Target occasion (work, casual, date, formal, etc.)"),
    max_results: int = Query(5, ge=1, le=10, description="Maximum number of outfit recommendations")
):
    """
    Get outfit recommendations from user's existing wardrobe
    
    Returns complete outfit combinations that can be worn with items
    already in the user's wardrobe.
    
    **Example:** `/api/recommendations/outfits?user_id=user123&occasion=work&max_results=3`
    """
    try:
        recommender = get_recommender()
        
        # Generate outfit recommendations
        outfits = recommender.recommend_outfits(
            user_id=user_id,
            occasion=occasion,
            max_outfits=max_results
        )
        
        return [
            OutfitRecommendationResponse(**outfit.to_dict())
            for outfit in outfits
        ]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Outfit recommendation failed: {str(e)}"
        )


@router.get("/shopping", response_model=List[MissingItemResponse])
async def get_shopping_recommendations(
    user_id: str = Query(..., description="User ID"),
    occasion: Optional[str] = Query(None, description="Target occasion to focus on"),
    max_suggestions: int = Query(5, ge=1, le=10, description="Maximum shopping suggestions")
):
    """
    Get shopping recommendations for missing wardrobe items
    
    Analyzes wardrobe gaps and suggests items to purchase with
    direct product links from online retailers.
    
    **Example:** `/api/recommendations/shopping?user_id=user123&occasion=formal&max_suggestions=3`
    """
    try:
        recommender = get_recommender()
        
        # Find wardrobe gaps
        missing_items = recommender.find_wardrobe_gaps(
            user_id=user_id,
            occasion=occasion,
            max_suggestions=max_suggestions
        )
        
        return [
            MissingItemResponse(
                category=item.category,
                description=item.description,
                reason=item.reason,
                search_query=item.search_query,
                product_links=[
                    ProductLinkResponse(**link.to_dict())
                    for link in item.product_links
                ],
                priority=item.priority
            )
            for item in missing_items
        ]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Shopping recommendation failed: {str(e)}"
        )


@router.get("/style-profile/{user_id}")
async def get_user_style_profile(
    user_id: str = Path(..., description="User ID")
):
    """
    Analyze and return user's style profile
    
    Extracts style preferences, color choices, and fashion patterns
    from the user's existing outfits and wardrobe.
    """
    try:
        recommender = get_recommender()
        wardrobe_db = get_wardrobe_db()
        
        # Get user's outfits
        user_outfits = wardrobe_db.get_user_outfits(user_id)
        if not user_outfits:
            return {
                "message": "No outfits found for style analysis",
                "style_profile": None
            }
        
        # Convert to dict format
        outfits_data = [
            {
                'name': o.name,
                'occasion': o.occasion,
                'clothing_item_ids': o.clothing_item_ids,
                'times_worn': o.times_worn
            }
            for o in user_outfits
        ]
        
        # Get clothing items
        clothing_items = wardrobe_db.get_user_clothing_items(user_id)
        
        # Analyze style
        style_profile = recommender.analyze_user_style(outfits_data, clothing_items)
        
        return {
            "user_id": user_id,
            "style_profile": style_profile,
            "analyzed_outfits": len(user_outfits),
            "wardrobe_items": len(clothing_items)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Style analysis failed: {str(e)}"
        )


@router.get("/health")
async def recommendation_health_check():
    """Check if the recommendation service is operational"""
    try:
        health_status = {
            "status": "operational",
            "components": {}
        }
        
        # Check Gemini API
        if not GEMINI_AVAILABLE:
            health_status["components"]["gemini"] = {
                "status": "unavailable",
                "message": "google-generativeai package not installed"
            }
            health_status["status"] = "degraded"
        elif not os.getenv("GEMINI_API_KEY"):
            health_status["components"]["gemini"] = {
                "status": "not_configured",
                "message": "GEMINI_API_KEY not set"
            }
            health_status["status"] = "degraded"
        else:
            health_status["components"]["gemini"] = {
                "status": "operational",
                "model": "gemini-2.0-flash-exp"
            }
        
        # Check WardrobeDB
        try:
            get_wardrobe_db()
            health_status["components"]["wardrobe_db"] = {
                "status": "operational"
            }
        except Exception as e:
            health_status["components"]["wardrobe_db"] = {
                "status": "error",
                "message": str(e)
            }
            health_status["status"] = "degraded"
        
        # Check ClothesSearcher (optional)
        searcher = get_clothes_searcher()
        if searcher:
            health_status["components"]["clothes_search"] = {
                "status": "operational"
            }
        else:
            health_status["components"]["clothes_search"] = {
                "status": "unavailable",
                "message": "ClothesSearcher not configured (optional)"
            }
        
        return health_status
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# Legacy/convenience endpoints
@router.post("/", response_model=RecommendationResponse)
async def generate_recommendations_legacy(request: RecommendationRequest):
    """Legacy endpoint - redirects to /api/recommendations/analyze"""
    return await analyze_and_recommend(request)
