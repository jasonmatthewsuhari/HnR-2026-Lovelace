"""
FastAPI Application for Lovelace Wardrobe Database

This is the main API implementation using FastAPI for the Firebase wardrobe database.

Install dependencies:
    pip install -r requirements.txt

Run:
    uvicorn api_example:app --reload
    or
    python api_example.py
"""

from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import os
import uuid
from datetime import datetime

# Import the WardrobeDB
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'WardrobeDB'))
from wardrobe_db import (
    WardrobeDB, 
    ClothingItem as DBClothingItem,
    Outfit as DBOutfit,
    Collection as DBCollection,
    UserProfile as DBUserProfile
)

# Initialize FastAPI app
app = FastAPI(
    title="Lovelace Wardrobe API",
    description="REST API for Lovelace wardrobe management system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
creds_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
db = None

@app.on_event("startup")
async def startup_event():
    """Initialize Firebase on startup"""
    global db
    if not creds_path:
        print("WARNING: FIREBASE_CREDENTIALS_PATH not set. Database will not be initialized.")
    else:
        db = WardrobeDB(credentials_path=creds_path)
        print("✓ Firebase Firestore connected successfully")


# ==================== PYDANTIC MODELS ====================

class UserProfileCreate(BaseModel):
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    gender: Optional[str] = None
    body_size_data: Optional[Dict[str, Any]] = {}
    preferences: Optional[Dict[str, Any]] = {}


class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    gender: Optional[str] = None
    body_size_data: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None


class UserProfileResponse(BaseModel):
    user_id: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    gender: Optional[str] = None
    body_size_data: Dict[str, Any] = {}
    preferences: Dict[str, Any] = {}
    created_at: str
    updated_at: str


class ClothingItemCreate(BaseModel):
    name: str
    category: str
    images: List[str] = []
    color: Optional[str] = None
    size: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[str] = None
    source: Optional[str] = None
    purchase_date: Optional[str] = None
    tags: List[str] = []


class ClothingItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    images: Optional[List[str]] = None
    color: Optional[str] = None
    size: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[str] = None
    source: Optional[str] = None
    purchase_date: Optional[str] = None
    tags: Optional[List[str]] = None


class ClothingItemResponse(BaseModel):
    id: str
    user_id: str
    name: str
    category: str
    images: List[str]
    color: Optional[str] = None
    size: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[str] = None
    source: Optional[str] = None
    purchase_date: Optional[str] = None
    tags: List[str]
    created_at: str
    updated_at: str


class OutfitCreate(BaseModel):
    name: str
    description: Optional[str] = None
    clothing_item_ids: List[str]
    occasion: Optional[str] = None
    season: Optional[str] = None
    weather: Optional[str] = None
    tags: List[str] = []


class OutfitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    clothing_item_ids: Optional[List[str]] = None
    occasion: Optional[str] = None
    season: Optional[str] = None
    weather: Optional[str] = None
    liked: Optional[bool] = None
    tags: Optional[List[str]] = None


class OutfitResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str]
    clothing_item_ids: List[str]
    occasion: Optional[str]
    season: Optional[str]
    weather: Optional[str]
    liked: bool
    times_worn: int
    last_worn: Optional[str]
    tags: List[str]
    created_at: str
    updated_at: str


class OutfitWithItemsResponse(BaseModel):
    outfit: OutfitResponse
    items: List[ClothingItemResponse]


class CollectionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    outfit_ids: List[str] = []
    is_wishlist: bool = False
    tags: List[str] = []


class CollectionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    outfit_ids: Optional[List[str]] = None
    is_wishlist: Optional[bool] = None
    tags: Optional[List[str]] = None


class CollectionResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str]
    outfit_ids: List[str]
    is_wishlist: bool
    tags: List[str]
    created_at: str
    updated_at: str


class StandardResponse(BaseModel):
    status: str = "success"
    message: str
    data: Optional[Any] = None


# ==================== HELPER FUNCTIONS ====================

def check_db():
    """Check if database is initialized"""
    if db is None:
        raise HTTPException(
            status_code=503,
            detail="Database not initialized. Check FIREBASE_CREDENTIALS_PATH environment variable."
        )


# ==================== ROOT & HEALTH ====================

@app.get("/", response_model=Dict[str, Any])
async def root():
    """API information"""
    return {
        "name": "Lovelace Wardrobe API",
        "version": "1.0.0",
        "description": "REST API for Lovelace wardrobe management system using FastAPI",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "users": "/api/users",
            "clothing": "/api/users/{user_id}/clothing",
            "outfits": "/api/users/{user_id}/outfits",
            "collections": "/api/users/{user_id}/collections",
            "stats": "/api/users/{user_id}/stats",
            "health": "/api/health"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Lovelace Wardrobe API",
        "version": "1.0.0",
        "database": "connected" if db is not None else "not initialized"
    }


# ==================== USER ENDPOINTS ====================

@app.post("/api/users", response_model=StandardResponse, status_code=201)
async def create_user(profile_data: UserProfileCreate):
    """Create a new user profile"""
    check_db()
    try:
        user_id = str(uuid.uuid4())
        profile = DBUserProfile(
            user_id=user_id,
            username=profile_data.username,
            first_name=profile_data.first_name,
            last_name=profile_data.last_name,
            email=profile_data.email,
            location=profile_data.location,
            gender=profile_data.gender,
            body_size_data=profile_data.body_size_data,
            preferences=profile_data.preferences
        )
        db.create_user_profile(profile)
        return StandardResponse(
            message="User created successfully",
            data={"user_id": user_id}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/users/{user_id}", response_model=UserProfileResponse)
async def get_user(user_id: str = Path(..., description="User ID")):
    """Get user profile"""
    check_db()
    try:
        profile = db.get_user_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User not found")
        return UserProfileResponse(**profile.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/api/users/{user_id}", response_model=StandardResponse)
async def update_user(
    user_id: str = Path(..., description="User ID"),
    updates: UserProfileUpdate = None
):
    """Update user profile"""
    check_db()
    try:
        update_dict = {k: v for k, v in updates.dict().items() if v is not None}
        db.update_user_profile(user_id, update_dict)
        return StandardResponse(message="User updated successfully")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/users/{user_id}", response_model=StandardResponse)
async def delete_user(user_id: str = Path(..., description="User ID")):
    """Delete user profile"""
    check_db()
    try:
        db.delete_user_profile(user_id)
        return StandardResponse(message="User deleted successfully")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== CLOTHING ITEM ENDPOINTS ====================

@app.post("/api/users/{user_id}/clothing", response_model=StandardResponse, status_code=201)
async def add_clothing_item(
    user_id: str = Path(..., description="User ID"),
    item_data: ClothingItemCreate = None
):
    """Add a new clothing item"""
    check_db()
    try:
        item_id = str(uuid.uuid4())
        item = DBClothingItem(
            id=item_id,
            user_id=user_id,
            name=item_data.name,
            category=item_data.category,
            images=item_data.images,
            color=item_data.color,
            size=item_data.size,
            brand=item_data.brand,
            price=item_data.price,
            source=item_data.source,
            purchase_date=item_data.purchase_date,
            tags=item_data.tags
        )
        db.add_clothing_item(item)
        return StandardResponse(
            message="Clothing item added successfully",
            data={"item_id": item_id}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/users/{user_id}/clothing", response_model=List[ClothingItemResponse])
async def get_user_clothing(
    user_id: str = Path(..., description="User ID"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """Get all clothing items for a user"""
    check_db()
    try:
        items = db.get_user_clothing_items(user_id, category)
        return [ClothingItemResponse(**item.to_dict()) for item in items]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/clothing/{item_id}", response_model=ClothingItemResponse)
async def get_clothing_item(item_id: str = Path(..., description="Clothing item ID")):
    """Get a specific clothing item"""
    check_db()
    try:
        item = db.get_clothing_item(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Clothing item not found")
        return ClothingItemResponse(**item.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/api/clothing/{item_id}", response_model=StandardResponse)
async def update_clothing_item(
    item_id: str = Path(..., description="Clothing item ID"),
    updates: ClothingItemUpdate = None
):
    """Update a clothing item"""
    check_db()
    try:
        update_dict = {k: v for k, v in updates.dict().items() if v is not None}
        db.update_clothing_item(item_id, update_dict)
        return StandardResponse(message="Clothing item updated successfully")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/clothing/{item_id}", response_model=StandardResponse)
async def delete_clothing_item(item_id: str = Path(..., description="Clothing item ID")):
    """Delete a clothing item"""
    check_db()
    try:
        db.delete_clothing_item(item_id)
        return StandardResponse(message="Clothing item deleted successfully")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== OUTFIT ENDPOINTS ====================

@app.post("/api/users/{user_id}/outfits", response_model=StandardResponse, status_code=201)
async def create_outfit(
    user_id: str = Path(..., description="User ID"),
    outfit_data: OutfitCreate = None
):
    """Create a new outfit"""
    check_db()
    try:
        outfit_id = str(uuid.uuid4())
        outfit = DBOutfit(
            id=outfit_id,
            user_id=user_id,
            name=outfit_data.name,
            description=outfit_data.description,
            clothing_item_ids=outfit_data.clothing_item_ids,
            occasion=outfit_data.occasion,
            season=outfit_data.season,
            weather=outfit_data.weather,
            tags=outfit_data.tags
        )
        db.create_outfit(outfit)
        return StandardResponse(
            message="Outfit created successfully",
            data={"outfit_id": outfit_id}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/users/{user_id}/outfits", response_model=List[OutfitResponse])
async def get_user_outfits(
    user_id: str = Path(..., description="User ID"),
    occasion: Optional[str] = Query(None, description="Filter by occasion")
):
    """Get all outfits for a user"""
    check_db()
    try:
        outfits = db.get_user_outfits(user_id, occasion)
        return [OutfitResponse(**outfit.to_dict()) for outfit in outfits]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/outfits/{outfit_id}")
async def get_outfit(
    outfit_id: str = Path(..., description="Outfit ID"),
    include_items: bool = Query(False, description="Include clothing items")
):
    """Get a specific outfit, optionally with clothing items"""
    check_db()
    try:
        if include_items:
            result = db.get_outfit_with_items(outfit_id)
            if not result:
                raise HTTPException(status_code=404, detail="Outfit not found")
            return OutfitWithItemsResponse(
                outfit=OutfitResponse(**result['outfit'].to_dict()),
                items=[ClothingItemResponse(**item.to_dict()) for item in result['items']]
            )
        else:
            outfit = db.get_outfit(outfit_id)
            if not outfit:
                raise HTTPException(status_code=404, detail="Outfit not found")
            return OutfitResponse(**outfit.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/api/outfits/{outfit_id}", response_model=StandardResponse)
async def update_outfit(
    outfit_id: str = Path(..., description="Outfit ID"),
    updates: OutfitUpdate = None
):
    """Update an outfit"""
    check_db()
    try:
        update_dict = {k: v for k, v in updates.dict().items() if v is not None}
        db.update_outfit(outfit_id, update_dict)
        return StandardResponse(message="Outfit updated successfully")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/outfits/{outfit_id}/worn", response_model=StandardResponse)
async def mark_outfit_worn(outfit_id: str = Path(..., description="Outfit ID")):
    """Mark an outfit as worn"""
    check_db()
    try:
        success = db.mark_outfit_worn(outfit_id)
        if not success:
            raise HTTPException(status_code=404, detail="Outfit not found")
        return StandardResponse(message="Outfit marked as worn")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/outfits/{outfit_id}", response_model=StandardResponse)
async def delete_outfit(outfit_id: str = Path(..., description="Outfit ID")):
    """Delete an outfit"""
    check_db()
    try:
        db.delete_outfit(outfit_id)
        return StandardResponse(message="Outfit deleted successfully")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== COLLECTION ENDPOINTS ====================

@app.post("/api/users/{user_id}/collections", response_model=StandardResponse, status_code=201)
async def create_collection(
    user_id: str = Path(..., description="User ID"),
    collection_data: CollectionCreate = None
):
    """Create a new collection"""
    check_db()
    try:
        collection_id = str(uuid.uuid4())
        collection = DBCollection(
            id=collection_id,
            user_id=user_id,
            name=collection_data.name,
            description=collection_data.description,
            outfit_ids=collection_data.outfit_ids,
            is_wishlist=collection_data.is_wishlist,
            tags=collection_data.tags
        )
        db.create_collection(collection)
        return StandardResponse(
            message="Collection created successfully",
            data={"collection_id": collection_id}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/users/{user_id}/collections", response_model=List[CollectionResponse])
async def get_user_collections(user_id: str = Path(..., description="User ID")):
    """Get all collections for a user"""
    check_db()
    try:
        collections = db.get_user_collections(user_id)
        return [CollectionResponse(**col.to_dict()) for col in collections]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/collections/{collection_id}", response_model=CollectionResponse)
async def get_collection(collection_id: str = Path(..., description="Collection ID")):
    """Get a specific collection"""
    check_db()
    try:
        collection = db.get_collection(collection_id)
        if not collection:
            raise HTTPException(status_code=404, detail="Collection not found")
        return CollectionResponse(**collection.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/api/collections/{collection_id}", response_model=StandardResponse)
async def update_collection(
    collection_id: str = Path(..., description="Collection ID"),
    updates: CollectionUpdate = None
):
    """Update a collection"""
    check_db()
    try:
        update_dict = {k: v for k, v in updates.dict().items() if v is not None}
        db.update_collection(collection_id, update_dict)
        return StandardResponse(message="Collection updated successfully")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/collections/{collection_id}", response_model=StandardResponse)
async def delete_collection(collection_id: str = Path(..., description="Collection ID")):
    """Delete a collection"""
    check_db()
    try:
        db.delete_collection(collection_id)
        return StandardResponse(message="Collection deleted successfully")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/collections/{collection_id}/outfits/{outfit_id}", response_model=StandardResponse)
async def add_outfit_to_collection(
    collection_id: str = Path(..., description="Collection ID"),
    outfit_id: str = Path(..., description="Outfit ID")
):
    """Add an outfit to a collection"""
    check_db()
    try:
        success = db.add_outfit_to_collection(collection_id, outfit_id)
        if not success:
            raise HTTPException(status_code=404, detail="Collection not found")
        return StandardResponse(message="Outfit added to collection")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/collections/{collection_id}/outfits/{outfit_id}", response_model=StandardResponse)
async def remove_outfit_from_collection(
    collection_id: str = Path(..., description="Collection ID"),
    outfit_id: str = Path(..., description="Outfit ID")
):
    """Remove an outfit from a collection"""
    check_db()
    try:
        success = db.remove_outfit_from_collection(collection_id, outfit_id)
        if not success:
            raise HTTPException(status_code=404, detail="Collection not found")
        return StandardResponse(message="Outfit removed from collection")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== STATS ENDPOINTS ====================

@app.get("/api/users/{user_id}/stats")
async def get_wardrobe_stats(user_id: str = Path(..., description="User ID")):
    """Get wardrobe statistics for a user"""
    check_db()
    try:
        stats = db.get_wardrobe_stats(user_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("Lovelace Wardrobe API Server (FastAPI)")
    print("=" * 60)
    print()
    
    if not creds_path:
        print("WARNING: FIREBASE_CREDENTIALS_PATH environment variable not set!")
        print("The API will start but database operations will fail.")
        print()
    else:
        print(f"Firebase credentials: {creds_path}")
    
    print("Starting server on http://localhost:8000")
    print()
    print("API Documentation: http://localhost:8000/docs")
    print("Alternative Docs: http://localhost:8000/redoc")
    print("Health Check: http://localhost:8000/api/health")
    print()
    print("=" * 60)
    
    uvicorn.run("api_example:app", host="0.0.0.0", port=8000, reload=True)
