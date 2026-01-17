"""
Add Sample Clothing Data to Firestore

This script adds sample clothing items to your Firestore database
so you can see the data structure in Firebase Console.
"""

import os
import sys
import uuid
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.WardrobeDB.wardrobe_db import (
    WardrobeDB,
    ClothingItem,
    Outfit,
    Collection,
    UserProfile,
    ClothingCategory
)


def create_sample_user(db: WardrobeDB) -> str:
    """Create a sample user"""
    user_id = "sample_user_" + str(uuid.uuid4())[:8]
    
    profile = UserProfile(
        user_id=user_id,
        username="fashionista_demo",
        first_name="Demo",
        last_name="User",
        email="demo@lovelace.app",
        location="Singapore",
        gender="female",
        body_size_data={
            "height_cm": 165,
            "weight_kg": 55,
            "bust_cm": 86,
            "waist_cm": 66,
            "hips_cm": 92
        },
        preferences={
            "style": ["casual", "minimalist"],
            "colors": ["black", "white", "blue"],
            "budget": "mid-range"
        }
    )
    
    db.create_user_profile(profile)
    print(f"✓ Created user: {profile.username} (ID: {user_id})")
    return user_id


def add_sample_clothing(db: WardrobeDB, user_id: str):
    """Add sample clothing items"""
    print("\nAdding sample clothing items...")
    
    items = []
    
    # Item 1: White T-shirt
    item1 = ClothingItem(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name="Classic White T-Shirt",
        category=ClothingCategory.TOPS.value,
        images=[
            "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400",
        ],
        color="white",
        size="M",
        brand="Uniqlo",
        price="$19.90",
        source="Uniqlo Store",
        purchase_date="2024-01-15",
        tags=["basic", "casual", "cotton"]
    )
    db.add_clothing_item(item1)
    items.append(item1)
    print(f"  ✓ {item1.name}")
    
    # Item 2: Blue Jeans
    item2 = ClothingItem(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name="Slim Fit Blue Jeans",
        category=ClothingCategory.BOTTOMS.value,
        images=[
            "https://images.unsplash.com/photo-1542272454315-7f6d5c489e01?w=400",
        ],
        color="blue",
        size="28",
        brand="Levi's",
        price="$89.90",
        source="Shopee",
        purchase_date="2024-01-20",
        tags=["denim", "casual", "slim-fit"]
    )
    db.add_clothing_item(item2)
    items.append(item2)
    print(f"  ✓ {item2.name}")
    
    # Item 3: Black Leather Jacket
    item3 = ClothingItem(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name="Black Leather Jacket",
        category=ClothingCategory.OUTERWEAR.value,
        images=[
            "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400",
        ],
        color="black",
        size="M",
        brand="Zara",
        price="$199.00",
        source="Zara",
        purchase_date="2024-02-01",
        tags=["leather", "edgy", "winter"]
    )
    db.add_clothing_item(item3)
    items.append(item3)
    print(f"  ✓ {item3.name}")
    
    # Item 4: White Sneakers
    item4 = ClothingItem(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name="Classic White Sneakers",
        category=ClothingCategory.SHOES.value,
        images=[
            "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400",
        ],
        color="white",
        size="US 7",
        brand="Converse",
        price="$65.00",
        source="Zalora",
        purchase_date="2024-02-05",
        tags=["sneakers", "casual", "comfortable"]
    )
    db.add_clothing_item(item4)
    items.append(item4)
    print(f"  ✓ {item4.name}")
    
    # Item 5: Black Dress
    item5 = ClothingItem(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name="Little Black Dress",
        category=ClothingCategory.DRESSES.value,
        images=[
            "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400",
        ],
        color="black",
        size="S",
        brand="H&M",
        price="$49.90",
        source="H&M",
        purchase_date="2024-02-10",
        tags=["formal", "elegant", "cocktail"]
    )
    db.add_clothing_item(item5)
    items.append(item5)
    print(f"  ✓ {item5.name}")
    
    print(f"\n✓ Added {len(items)} clothing items")
    return items


def create_sample_outfit(db: WardrobeDB, user_id: str, items):
    """Create a sample outfit"""
    print("\nCreating sample outfit...")
    
    # Casual outfit with first 3 items
    outfit = Outfit(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name="Casual Weekend Look",
        description="Perfect for a relaxed Saturday brunch with friends",
        clothing_item_ids=[items[0].id, items[1].id, items[3].id],
        occasion="casual",
        season="spring",
        weather="sunny",
        liked=True,
        tags=["weekend", "brunch", "comfortable"]
    )
    
    db.create_outfit(outfit)
    print(f"  ✓ {outfit.name}")
    return outfit


def create_sample_collection(db: WardrobeDB, user_id: str, outfit):
    """Create a sample collection"""
    print("\nCreating sample collection...")
    
    collection = Collection(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name="Spring 2024 Favorites",
        description="My favorite looks for spring season",
        outfit_ids=[outfit.id],
        is_wishlist=False,
        tags=["spring", "favorites", "2024"]
    )
    
    db.create_collection(collection)
    print(f"  ✓ {collection.name}")
    return collection


def main():
    """Add sample data to Firestore"""
    print("=" * 70)
    print("  📦 ADDING SAMPLE DATA TO FIRESTORE")
    print("=" * 70)
    print()
    
    # Initialize database
    try:
        creds_path = os.getenv('FIREBASE_CREDENTIALS_PATH', './firebase-credentials.json')
        db = WardrobeDB(credentials_path=creds_path)
        print("✓ Connected to Firestore")
        print()
    except Exception as e:
        print(f"❌ Error connecting to Firestore: {e}")
        print("\nMake sure:")
        print("  1. Firestore is enabled in Firebase Console")
        print("  2. firebase-credentials.json exists")
        print("  3. FIREBASE_CREDENTIALS_PATH is set")
        return
    
    try:
        # Create sample user
        user_id = create_sample_user(db)
        
        # Add clothing items
        items = add_sample_clothing(db, user_id)
        
        # Create outfit
        outfit = create_sample_outfit(db, user_id, items)
        
        # Create collection
        collection = create_sample_collection(db, user_id, outfit)
        
        # Get statistics
        print("\n" + "=" * 70)
        print("  📊 WARDROBE STATISTICS")
        print("=" * 70)
        stats = db.get_wardrobe_stats(user_id)
        print(f"\nUser: {user_id}")
        print(f"Total clothing items: {stats['total_clothing_items']}")
        print(f"Total outfits: {stats['total_outfits']}")
        print(f"Total collections: {stats['total_collections']}")
        print(f"Estimated wardrobe value: {stats['estimated_wardrobe_value']}")
        
        print("\nCategory breakdown:")
        for category, count in stats['category_breakdown'].items():
            print(f"  - {category}: {count} items")
        
        # Final instructions
        print("\n" + "=" * 70)
        print("  ✅ SAMPLE DATA ADDED SUCCESSFULLY!")
        print("=" * 70)
        print()
        print("Now check your Firebase Console:")
        print("  1. Go to: https://console.firebase.google.com/")
        print("  2. Select project: lovelace-b8ef5")
        print("  3. Click 'Firestore Database' in left menu")
        print("  4. You should see collections:")
        print("     - users")
        print("     - clothing_items")
        print("     - outfits")
        print("     - collections")
        print()
        print(f"Sample user ID: {user_id}")
        print("(Save this if you want to query this user's data via API)")
        print()
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error adding sample data: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user.")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
