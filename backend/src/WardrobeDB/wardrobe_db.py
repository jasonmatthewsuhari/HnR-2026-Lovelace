"""
Lovelace Wardrobe Database - Firebase Implementation

This module provides a comprehensive interface for managing user wardrobes,
clothing items, outfits, and collections using Google Firebase Firestore.

Main features:
- User profile management
- Clothing item CRUD operations
- Outfit creation and management
- Collection management
- Image URL storage support
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    from google.cloud.firestore_v1.base_query import FieldFilter
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("Warning: Firebase libraries not installed. Run: pip install firebase-admin")


class ClothingCategory(Enum):
    """Clothing categories"""
    TOPS = "tops"
    BOTTOMS = "bottoms"
    SHOES = "shoes"
    ACCESSORIES = "accessories"
    OUTERWEAR = "outerwear"
    DRESSES = "dresses"
    ACTIVEWEAR = "activewear"
    FORMAL = "formal"
    OTHER = "other"


@dataclass
class ClothingItem:
    """Represents a single clothing item in the wardrobe"""
    id: str
    user_id: str
    name: str
    category: str
    images: List[str]  # URLs to images
    color: Optional[str] = None
    size: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[str] = None
    source: Optional[str] = None  # Where it was purchased (e.g., "Shopee", "Zalora")
    purchase_date: Optional[str] = None
    tags: List[str] = None
    created_at: str = None
    updated_at: str = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firebase storage"""
        return asdict(self)


@dataclass
class Outfit:
    """Represents an outfit (combination of clothing items)"""
    id: str
    user_id: str
    name: str
    description: Optional[str]
    clothing_item_ids: List[str]  # References to ClothingItem IDs
    occasion: Optional[str] = None  # e.g., "work", "casual", "formal"
    season: Optional[str] = None  # e.g., "summer", "winter"
    weather: Optional[str] = None  # e.g., "sunny", "rainy"
    liked: bool = False
    times_worn: int = 0
    last_worn: Optional[str] = None
    tags: List[str] = None
    created_at: str = None
    updated_at: str = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firebase storage"""
        return asdict(self)


@dataclass
class Collection:
    """Represents a collection of outfits (e.g., wishlist, favorites)"""
    id: str
    user_id: str
    name: str
    description: Optional[str]
    outfit_ids: List[str]  # References to Outfit IDs
    is_wishlist: bool = False
    tags: List[str] = None
    created_at: str = None
    updated_at: str = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firebase storage"""
        return asdict(self)


@dataclass
class UserProfile:
    """User profile information"""
    user_id: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    gender: Optional[str] = None
    body_size_data: Dict[str, Any] = None
    preferences: Dict[str, Any] = None
    created_at: str = None
    updated_at: str = None

    def __post_init__(self):
        if self.body_size_data is None:
            self.body_size_data = {}
        if self.preferences is None:
            self.preferences = {}
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firebase storage"""
        return asdict(self)


class WardrobeDB:
    """
    Main class for interacting with Firebase Firestore for wardrobe management
    """

    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize Firebase connection
        
        Args:
            credentials_path: Path to Firebase service account credentials JSON file
                            If None, will look for GOOGLE_APPLICATION_CREDENTIALS env var
        """
        if not FIREBASE_AVAILABLE:
            raise ImportError("Firebase libraries not installed. Run: pip install firebase-admin")

        self.db = None
        self._initialize_firebase(credentials_path)

    def _initialize_firebase(self, credentials_path: Optional[str] = None):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if already initialized
            firebase_admin.get_app()
            print("Firebase already initialized")
        except ValueError:
            # Not initialized, so initialize now
            if credentials_path:
                cred = credentials.Certificate(credentials_path)
                firebase_admin.initialize_app(cred)
            elif os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
                # Use default credentials from environment
                cred = credentials.ApplicationDefault()
                firebase_admin.initialize_app(cred)
            else:
                raise ValueError(
                    "No Firebase credentials provided. Either pass credentials_path "
                    "or set GOOGLE_APPLICATION_CREDENTIALS environment variable"
                )
        
        self.db = firestore.client()
        print("Firebase Firestore connected successfully")

    # ==================== USER PROFILE OPERATIONS ====================

    def create_user_profile(self, profile: UserProfile) -> str:
        """Create a new user profile"""
        doc_ref = self.db.collection('users').document(profile.user_id)
        doc_ref.set(profile.to_dict())
        print(f"User profile created: {profile.user_id}")
        return profile.user_id

    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by ID"""
        doc = self.db.collection('users').document(user_id).get()
        if doc.exists:
            return UserProfile(**doc.to_dict())
        return None

    def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user profile"""
        updates['updated_at'] = datetime.utcnow().isoformat()
        self.db.collection('users').document(user_id).update(updates)
        print(f"User profile updated: {user_id}")
        return True

    def delete_user_profile(self, user_id: str) -> bool:
        """Delete user profile"""
        self.db.collection('users').document(user_id).delete()
        print(f"User profile deleted: {user_id}")
        return True

    # ==================== CLOTHING ITEM OPERATIONS ====================

    def add_clothing_item(self, item: ClothingItem) -> str:
        """Add a new clothing item to the wardrobe"""
        doc_ref = self.db.collection('clothing_items').document(item.id)
        doc_ref.set(item.to_dict())
        print(f"Clothing item added: {item.name} ({item.id})")
        return item.id

    def get_clothing_item(self, item_id: str) -> Optional[ClothingItem]:
        """Get a specific clothing item by ID"""
        doc = self.db.collection('clothing_items').document(item_id).get()
        if doc.exists:
            return ClothingItem(**doc.to_dict())
        return None

    def get_user_clothing_items(self, user_id: str, category: Optional[str] = None) -> List[ClothingItem]:
        """Get all clothing items for a user, optionally filtered by category"""
        query = self.db.collection('clothing_items').where(filter=FieldFilter('user_id', '==', user_id))
        
        if category:
            query = query.where(filter=FieldFilter('category', '==', category))
        
        items = []
        for doc in query.stream():
            items.append(ClothingItem(**doc.to_dict()))
        
        print(f"Retrieved {len(items)} clothing items for user {user_id}")
        return items

    def update_clothing_item(self, item_id: str, updates: Dict[str, Any]) -> bool:
        """Update a clothing item"""
        updates['updated_at'] = datetime.utcnow().isoformat()
        self.db.collection('clothing_items').document(item_id).update(updates)
        print(f"Clothing item updated: {item_id}")
        return True

    def delete_clothing_item(self, item_id: str) -> bool:
        """Delete a clothing item"""
        self.db.collection('clothing_items').document(item_id).delete()
        print(f"Clothing item deleted: {item_id}")
        return True

    def search_clothing_items(self, user_id: str, **filters) -> List[ClothingItem]:
        """
        Search clothing items with various filters
        
        Args:
            user_id: User ID
            **filters: Keyword arguments for filtering (e.g., color="red", category="tops")
        """
        query = self.db.collection('clothing_items').where(filter=FieldFilter('user_id', '==', user_id))
        
        for field, value in filters.items():
            query = query.where(filter=FieldFilter(field, '==', value))
        
        items = []
        for doc in query.stream():
            items.append(ClothingItem(**doc.to_dict()))
        
        return items

    # ==================== OUTFIT OPERATIONS ====================

    def create_outfit(self, outfit: Outfit) -> str:
        """Create a new outfit"""
        doc_ref = self.db.collection('outfits').document(outfit.id)
        doc_ref.set(outfit.to_dict())
        print(f"Outfit created: {outfit.name} ({outfit.id})")
        return outfit.id

    def get_outfit(self, outfit_id: str) -> Optional[Outfit]:
        """Get a specific outfit by ID"""
        doc = self.db.collection('outfits').document(outfit_id).get()
        if doc.exists:
            return Outfit(**doc.to_dict())
        return None

    def get_user_outfits(self, user_id: str, occasion: Optional[str] = None) -> List[Outfit]:
        """Get all outfits for a user, optionally filtered by occasion"""
        query = self.db.collection('outfits').where(filter=FieldFilter('user_id', '==', user_id))
        
        if occasion:
            query = query.where(filter=FieldFilter('occasion', '==', occasion))
        
        outfits = []
        for doc in query.stream():
            outfits.append(Outfit(**doc.to_dict()))
        
        print(f"Retrieved {len(outfits)} outfits for user {user_id}")
        return outfits

    def update_outfit(self, outfit_id: str, updates: Dict[str, Any]) -> bool:
        """Update an outfit"""
        updates['updated_at'] = datetime.utcnow().isoformat()
        self.db.collection('outfits').document(outfit_id).update(updates)
        print(f"Outfit updated: {outfit_id}")
        return True

    def delete_outfit(self, outfit_id: str) -> bool:
        """Delete an outfit"""
        self.db.collection('outfits').document(outfit_id).delete()
        print(f"Outfit deleted: {outfit_id}")
        return True

    def get_outfit_with_items(self, outfit_id: str) -> Optional[Dict[str, Any]]:
        """Get an outfit with all its clothing items populated"""
        outfit = self.get_outfit(outfit_id)
        if not outfit:
            return None
        
        items = []
        for item_id in outfit.clothing_item_ids:
            item = self.get_clothing_item(item_id)
            if item:
                items.append(item)
        
        return {
            'outfit': outfit,
            'items': items
        }

    def mark_outfit_worn(self, outfit_id: str) -> bool:
        """Mark an outfit as worn (increment times_worn, update last_worn)"""
        outfit = self.get_outfit(outfit_id)
        if not outfit:
            return False
        
        updates = {
            'times_worn': outfit.times_worn + 1,
            'last_worn': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        self.db.collection('outfits').document(outfit_id).update(updates)
        print(f"Outfit marked as worn: {outfit_id}")
        return True

    # ==================== COLLECTION OPERATIONS ====================

    def create_collection(self, collection: Collection) -> str:
        """Create a new collection"""
        doc_ref = self.db.collection('collections').document(collection.id)
        doc_ref.set(collection.to_dict())
        print(f"Collection created: {collection.name} ({collection.id})")
        return collection.id

    def get_collection(self, collection_id: str) -> Optional[Collection]:
        """Get a specific collection by ID"""
        doc = self.db.collection('collections').document(collection_id).get()
        if doc.exists:
            return Collection(**doc.to_dict())
        return None

    def get_user_collections(self, user_id: str) -> List[Collection]:
        """Get all collections for a user"""
        query = self.db.collection('collections').where(filter=FieldFilter('user_id', '==', user_id))
        
        collections = []
        for doc in query.stream():
            collections.append(Collection(**doc.to_dict()))
        
        print(f"Retrieved {len(collections)} collections for user {user_id}")
        return collections

    def update_collection(self, collection_id: str, updates: Dict[str, Any]) -> bool:
        """Update a collection"""
        updates['updated_at'] = datetime.utcnow().isoformat()
        self.db.collection('collections').document(collection_id).update(updates)
        print(f"Collection updated: {collection_id}")
        return True

    def delete_collection(self, collection_id: str) -> bool:
        """Delete a collection"""
        self.db.collection('collections').document(collection_id).delete()
        print(f"Collection deleted: {collection_id}")
        return True

    def add_outfit_to_collection(self, collection_id: str, outfit_id: str) -> bool:
        """Add an outfit to a collection"""
        collection = self.get_collection(collection_id)
        if not collection:
            return False
        
        if outfit_id not in collection.outfit_ids:
            collection.outfit_ids.append(outfit_id)
            self.update_collection(collection_id, {'outfit_ids': collection.outfit_ids})
            print(f"Outfit {outfit_id} added to collection {collection_id}")
        return True

    def remove_outfit_from_collection(self, collection_id: str, outfit_id: str) -> bool:
        """Remove an outfit from a collection"""
        collection = self.get_collection(collection_id)
        if not collection:
            return False
        
        if outfit_id in collection.outfit_ids:
            collection.outfit_ids.remove(outfit_id)
            self.update_collection(collection_id, {'outfit_ids': collection.outfit_ids})
            print(f"Outfit {outfit_id} removed from collection {collection_id}")
        return True

    # ==================== UTILITY OPERATIONS ====================

    def get_wardrobe_stats(self, user_id: str) -> Dict[str, Any]:
        """Get statistics about a user's wardrobe"""
        clothing_items = self.get_user_clothing_items(user_id)
        outfits = self.get_user_outfits(user_id)
        collections = self.get_user_collections(user_id)
        
        # Category breakdown
        category_counts = {}
        for item in clothing_items:
            category_counts[item.category] = category_counts.get(item.category, 0) + 1
        
        # Calculate total value if prices are available
        total_value = 0
        for item in clothing_items:
            if item.price:
                try:
                    # Extract numeric value from price string
                    price_str = item.price.replace('$', '').replace(',', '')
                    total_value += float(price_str)
                except:
                    pass
        
        return {
            'user_id': user_id,
            'total_clothing_items': len(clothing_items),
            'total_outfits': len(outfits),
            'total_collections': len(collections),
            'category_breakdown': category_counts,
            'estimated_wardrobe_value': f"${total_value:.2f}",
            'most_common_category': max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else None
        }


def main():
    """
    Main function for testing and demonstrating the WardrobeDB functionality
    """
    print("=" * 60)
    print("Lovelace Wardrobe Database - Firebase Implementation")
    print("=" * 60)
    print()
    
    if not FIREBASE_AVAILABLE:
        print("ERROR: Firebase libraries not installed!")
        print("Please run: pip install firebase-admin")
        return
    
    # Check for credentials
    creds_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
    if not creds_path and not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        print("ERROR: No Firebase credentials found!")
        print("Please set either:")
        print("  - FIREBASE_CREDENTIALS_PATH environment variable")
        print("  - GOOGLE_APPLICATION_CREDENTIALS environment variable")
        print()
        print("Or download your Firebase service account key from:")
        print("  Firebase Console > Project Settings > Service Accounts")
        return
    
    try:
        # Initialize database
        print("Initializing Firebase connection...")
        db = WardrobeDB(credentials_path=creds_path)
        print("✓ Connected to Firebase Firestore")
        print()
        
        # Example usage
        print("Example Operations:")
        print("-" * 60)
        
        # 1. Create a test user profile
        test_user_id = "test_user_123"
        print(f"1. Creating user profile for {test_user_id}...")
        
        profile = UserProfile(
            user_id=test_user_id,
            username="fashionista_test",
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
            location="Singapore",
            gender="female"
        )
        db.create_user_profile(profile)
        print("   ✓ User profile created")
        print()
        
        # 2. Add clothing items
        print("2. Adding clothing items...")
        import uuid
        
        item1 = ClothingItem(
            id=str(uuid.uuid4()),
            user_id=test_user_id,
            name="Blue Denim Jacket",
            category="outerwear",
            images=["https://example.com/jacket.jpg"],
            color="blue",
            size="M",
            brand="Levi's",
            price="$89.99",
            source="Shopee"
        )
        db.add_clothing_item(item1)
        
        item2 = ClothingItem(
            id=str(uuid.uuid4()),
            user_id=test_user_id,
            name="Black Skinny Jeans",
            category="bottoms",
            images=["https://example.com/jeans.jpg"],
            color="black",
            size="28",
            brand="H&M",
            price="$49.99"
        )
        db.add_clothing_item(item2)
        print("   ✓ Added 2 clothing items")
        print()
        
        # 3. Create an outfit
        print("3. Creating an outfit...")
        outfit = Outfit(
            id=str(uuid.uuid4()),
            user_id=test_user_id,
            name="Casual Friday Look",
            description="Comfortable outfit for casual office day",
            clothing_item_ids=[item1.id, item2.id],
            occasion="work",
            season="fall",
            weather="cool"
        )
        db.create_outfit(outfit)
        print("   ✓ Outfit created")
        print()
        
        # 4. Get wardrobe stats
        print("4. Getting wardrobe statistics...")
        stats = db.get_wardrobe_stats(test_user_id)
        print(f"   Statistics for {test_user_id}:")
        print(f"   - Total clothing items: {stats['total_clothing_items']}")
        print(f"   - Total outfits: {stats['total_outfits']}")
        print(f"   - Total collections: {stats['total_collections']}")
        print(f"   - Estimated value: {stats['estimated_wardrobe_value']}")
        print()
        
        print("=" * 60)
        print("✓ All operations completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
