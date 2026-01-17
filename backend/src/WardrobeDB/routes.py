"""
API Routes for Wardrobe Management

This module provides RESTful API endpoints for managing:
- User profiles
- Clothing items
- Outfits
- Collections
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

# Firebase Admin for token verification
try:
    from firebase_admin import auth as firebase_auth
    FIREBASE_AUTH_AVAILABLE = True
except ImportError:
    FIREBASE_AUTH_AVAILABLE = False

from .wardrobe_db import (
    WardrobeDB,
    ClothingItem,
    Outfit,
    Collection,
    UserProfile
)
import os

# Initialize router
router = APIRouter(prefix="/api")

# Initialize WardrobeDB
try:
    creds_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
    wardrobe_db = WardrobeDB(credentials_path=creds_path)
except Exception as e:
    print(f"Warning: Could not initialize WardrobeDB: {e}")
    wardrobe_db = None


# ==================== REQUEST/RESPONSE MODELS ====================

class ClothingItemCreate(BaseModel):
    name: str
    category: str
    images: List[str]
    color: Optional[str] = None
    size: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[str] = None
    source: Optional[str] = None
    tags: Optional[List[str]] = []


class ClothingItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    images: Optional[List[str]] = None
    color: Optional[str] = None
    size: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[str] = None
    source: Optional[str] = None
    tags: Optional[List[str]] = None


class OutfitCreate(BaseModel):
    name: str
    description: Optional[str] = None
    clothing_item_ids: List[str]
    occasion: Optional[str] = None
    season: Optional[str] = None
    weather: Optional[str] = None
    tags: Optional[List[str]] = []


class OutfitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    clothing_item_ids: Optional[List[str]] = None
    occasion: Optional[str] = None
    season: Optional[str] = None
    weather: Optional[str] = None
    liked: Optional[bool] = None
    tags: Optional[List[str]] = None


class CollectionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    outfit_ids: Optional[List[str]] = []
    is_wishlist: bool = False
    tags: Optional[List[str]] = []


class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    location: Optional[str] = None
    gender: Optional[str] = None
    body_size_data: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None


# ==================== AUTHENTICATION ====================

async def verify_firebase_token(authorization: Optional[str] = Header(None)) -> str:
    """Verify Firebase ID token and return user ID"""
    if not FIREBASE_AUTH_AVAILABLE:
        # Development mode - allow without auth
        if os.getenv('ENVIRONMENT') == 'development':
            return "dev_user"
        raise HTTPException(status_code=500, detail="Firebase auth not available")
    
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization header")
    
    try:
        # Extract token from "Bearer <token>"
        token = authorization.replace('Bearer ', '')
        decoded_token = firebase_auth.verify_id_token(token)
        return decoded_token['uid']
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


# ==================== USER PROFILE ROUTES ====================

@router.get("/users/{user_id}")
async def get_user_profile(user_id: str, current_user: str = Depends(verify_firebase_token)):
    """Get user profile"""
    if not wardrobe_db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    # Users can only access their own profile
    if current_user != user_id and os.getenv('ENVIRONMENT') != 'development':
        raise HTTPException(status_code=403, detail="Access denied")
    
    profile = wardrobe_db.get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    
    return profile.to_dict()


@router.put("/users/{user_id}")
async def update_user_profile(
    user_id: str,
    updates: UserProfileUpdate,
    current_user: str = Depends(verify_firebase_token)
):
    """Update user profile"""
    if not wardrobe_db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    if current_user != user_id and os.getenv('ENVIRONMENT') != 'development':
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Filter out None values
    update_dict = {k: v for k, v in updates.dict().items() if v is not None}
    
    wardrobe_db.update_user_profile(user_id, update_dict)
    return {"message": "Profile updated", "user_id": user_id}


# ==================== CLOTHING ITEM ROUTES ====================

@router.post("/users/{user_id}/clothing")
async def add_clothing_item(
    user_id: str,
    item: ClothingItemCreate,
    current_user: str = Depends(verify_firebase_token)
):
    """Add a new clothing item"""
    if not wardrobe_db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    if current_user != user_id and os.getenv('ENVIRONMENT') != 'development':
        raise HTTPException(status_code=403, detail="Access denied")
    
    clothing_item = ClothingItem(
        id=str(uuid.uuid4()),
        user_id=user_id,
        **item.dict()
    )
    
    item_id = wardrobe_db.add_clothing_item(clothing_item)
    return {"message": "Item added", "item_id": item_id, "item": clothing_item.to_dict()}


@router.get("/users/{user_id}/clothing")
async def get_user_clothing(
    user_id: str,
    category: Optional[str] = None,
    current_user: str = Depends(verify_firebase_token)
):
    """Get all clothing items for a user"""
    if not wardrobe_db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    if current_user != user_id and os.getenv('ENVIRONMENT') != 'development':
        raise HTTPException(status_code=403, detail="Access denied")
    
    items = wardrobe_db.get_user_clothing_items(user_id, category)
    return {"items": [item.to_dict() for item in items], "count": len(items)}


@router.get("/clothing/{item_id}")
async def get_clothing_item(item_id: str, current_user: str = Depends(verify_firebase_token)):
    """Get a specific clothing item"""
    if not wardrobe_db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    item = wardrobe_db.get_clothing_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Verify user owns this item
    if current_user != item.user_id and os.getenv('ENVIRONMENT') != 'development':
        raise HTTPException(status_code=403, detail="Access denied")
    
    return item.to_dict()


@router.put("/clothing/{item_id}")
async def update_clothing_item(
    item_id: str,
    updates: ClothingItemUpdate,
    current_user: str = Depends(verify_firebase_token)
):
    """Update a clothing item"""
    if not wardrobe_db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    # Verify ownership
    item = wardrobe_db.get_clothing_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if current_user != item.user_id and os.getenv('ENVIRONMENT') != 'development':
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Filter out None values
    update_dict = {k: v for k, v in updates.dict().items() if v is not None}
    
    wardrobe_db.update_clothing_item(item_id, update_dict)
    return {"message": "Item updated", "item_id": item_id}


@router.delete("/clothing/{item_id}")
async def delete_clothing_item(item_id: str, current_user: str = Depends(verify_firebase_token)):
    """Delete a clothing item"""
    if not wardrobe_db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    # Verify ownership
    item = wardrobe_db.get_clothing_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if current_user != item.user_id and os.getenv('ENVIRONMENT') != 'development':
        raise HTTPException(status_code=403, detail="Access denied")
    
    wardrobe_db.delete_clothing_item(item_id)
    return {"message": "Item deleted", "item_id": item_id}


# ==================== OUTFIT ROUTES ====================

@router.post("/users/{user_id}/outfits")
async def create_outfit(
    user_id: str,
    outfit: OutfitCreate,
    current_user: str = Depends(verify_firebase_token)
):
    """Create a new outfit"""
    if not wardrobe_db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    if current_user != user_id and os.getenv('ENVIRONMENT') != 'development':
        raise HTTPException(status_code=403, detail="Access denied")
    
    outfit_obj = Outfit(
        id=str(uuid.uuid4()),
        user_id=user_id,
        **outfit.dict()
    )
    
    outfit_id = wardrobe_db.create_outfit(outfit_obj)
    return {"message": "Outfit created", "outfit_id": outfit_id, "outfit": outfit_obj.to_dict()}


@router.get("/users/{user_id}/outfits")
async def get_user_outfits(
    user_id: str,
    occasion: Optional[str] = None,
    current_user: str = Depends(verify_firebase_token)
):
    """Get all outfits for a user"""
    if not wardrobe_db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    if current_user != user_id and os.getenv('ENVIRONMENT') != 'development':
        raise HTTPException(status_code=403, detail="Access denied")
    
    outfits = wardrobe_db.get_user_outfits(user_id, occasion)
    return {"outfits": [outfit.to_dict() for outfit in outfits], "count": len(outfits)}


@router.get("/outfits/{outfit_id}")
async def get_outfit(outfit_id: str, current_user: str = Depends(verify_firebase_token)):
    """Get a specific outfit with populated items"""
    if not wardrobe_db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    outfit_with_items = wardrobe_db.get_outfit_with_items(outfit_id)
    if not outfit_with_items:
        raise HTTPException(status_code=404, detail="Outfit not found")
    
    outfit = outfit_with_items['outfit']
    if current_user != outfit.user_id and os.getenv('ENVIRONMENT') != 'development':
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "outfit": outfit.to_dict(),
        "items": [item.to_dict() for item in outfit_with_items['items']]
    }


@router.put("/outfits/{outfit_id}")
async def update_outfit(
    outfit_id: str,
    updates: OutfitUpdate,
    current_user: str = Depends(verify_firebase_token)
):
    """Update an outfit"""
    if not wardrobe_db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    outfit = wardrobe_db.get_outfit(outfit_id)
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    
    if current_user != outfit.user_id and os.getenv('ENVIRONMENT') != 'development':
        raise HTTPException(status_code=403, detail="Access denied")
    
    update_dict = {k: v for k, v in updates.dict().items() if v is not None}
    wardrobe_db.update_outfit(outfit_id, update_dict)
    return {"message": "Outfit updated", "outfit_id": outfit_id}


@router.post("/outfits/{outfit_id}/worn")
async def mark_outfit_worn(outfit_id: str, current_user: str = Depends(verify_firebase_token)):
    """Mark an outfit as worn"""
    if not wardrobe_db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    outfit = wardrobe_db.get_outfit(outfit_id)
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    
    if current_user != outfit.user_id and os.getenv('ENVIRONMENT') != 'development':
        raise HTTPException(status_code=403, detail="Access denied")
    
    wardrobe_db.mark_outfit_worn(outfit_id)
    return {"message": "Outfit marked as worn", "outfit_id": outfit_id}


@router.delete("/outfits/{outfit_id}")
async def delete_outfit(outfit_id: str, current_user: str = Depends(verify_firebase_token)):
    """Delete an outfit"""
    if not wardrobe_db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    outfit = wardrobe_db.get_outfit(outfit_id)
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    
    if current_user != outfit.user_id and os.getenv('ENVIRONMENT') != 'development':
        raise HTTPException(status_code=403, detail="Access denied")
    
    wardrobe_db.delete_outfit(outfit_id)
    return {"message": "Outfit deleted", "outfit_id": outfit_id}


# ==================== COLLECTION ROUTES ====================

@router.post("/users/{user_id}/collections")
async def create_collection(
    user_id: str,
    collection: CollectionCreate,
    current_user: str = Depends(verify_firebase_token)
):
    """Create a new collection"""
    if not wardrobe_db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    if current_user != user_id and os.getenv('ENVIRONMENT') != 'development':
        raise HTTPException(status_code=403, detail="Access denied")
    
    collection_obj = Collection(
        id=str(uuid.uuid4()),
        user_id=user_id,
        **collection.dict()
    )
    
    collection_id = wardrobe_db.create_collection(collection_obj)
    return {"message": "Collection created", "collection_id": collection_id}


@router.get("/users/{user_id}/collections")
async def get_user_collections(user_id: str, current_user: str = Depends(verify_firebase_token)):
    """Get all collections for a user"""
    if not wardrobe_db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    if current_user != user_id and os.getenv('ENVIRONMENT') != 'development':
        raise HTTPException(status_code=403, detail="Access denied")
    
    collections = wardrobe_db.get_user_collections(user_id)
    return {"collections": [col.to_dict() for col in collections], "count": len(collections)}


# ==================== STATISTICS ====================

@router.get("/users/{user_id}/stats")
async def get_wardrobe_stats(user_id: str, current_user: str = Depends(verify_firebase_token)):
    """Get wardrobe statistics"""
    if not wardrobe_db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    if current_user != user_id and os.getenv('ENVIRONMENT') != 'development':
        raise HTTPException(status_code=403, detail="Access denied")
    
    stats = wardrobe_db.get_wardrobe_stats(user_id)
    return stats
