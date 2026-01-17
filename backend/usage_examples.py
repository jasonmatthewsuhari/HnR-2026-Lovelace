"""
Example Usage of Lovelace Wardrobe Database

This script demonstrates how to use the WardrobeDB module with practical examples.
"""

import os
import uuid
from datetime import datetime

# Import the WardrobeDB module
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'WardrobeDB'))
from wardrobe_db import (
    WardrobeDB,
    ClothingItem,
    Outfit,
    Collection,
    UserProfile,
    ClothingCategory
)


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def example_1_create_user():
    """Example 1: Create a user profile"""
    print_section("Example 1: Creating a User Profile")
    
    user_id = str(uuid.uuid4())
    profile = UserProfile(
        user_id=user_id,
        username="fashionista_jane",
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        location="Singapore",
        gender="female",
        body_size_data={
            "height_cm": 165,
            "weight_kg": 55,
            "bust_cm": 86,
            "waist_cm": 66,
            "hips_cm": 92,
            "shoe_size_us": 7
        },
        preferences={
            "style": ["casual", "minimalist", "modern"],
            "colors": ["black", "white", "beige", "navy"],
            "budget": "mid-range",
            "sustainable": True
        }
    )
    
    db.create_user_profile(profile)
    print(f"✓ Created user: {profile.username} ({user_id})")
    
    return user_id


def example_2_add_clothing(user_id):
    """Example 2: Add clothing items to wardrobe"""
    print_section("Example 2: Adding Clothing Items")
    
    items = []
    
    # Item 1: White T-shirt
    item1 = ClothingItem(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name="Classic White T-Shirt",
        category=ClothingCategory.TOPS.value,
        images=["https://example.com/white-tshirt.jpg"],
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
    print(f"✓ Added: {item1.name}")
    
    # Item 2: Blue Jeans
    item2 = ClothingItem(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name="Slim Fit Blue Jeans",
        category=ClothingCategory.BOTTOMS.value,
        images=["https://example.com/blue-jeans.jpg"],
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
    print(f"✓ Added: {item2.name}")
    
    # Item 3: Sneakers
    item3 = ClothingItem(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name="White Canvas Sneakers",
        category=ClothingCategory.SHOES.value,
        images=["https://example.com/sneakers.jpg"],
        color="white",
        size="US 7",
        brand="Converse",
        price="$65.00",
        source="Zalora",
        purchase_date="2024-02-01",
        tags=["casual", "comfortable", "canvas"]
    )
    db.add_clothing_item(item3)
    items.append(item3)
    print(f"✓ Added: {item3.name}")
    
    # Item 4: Black Blazer
    item4 = ClothingItem(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name="Tailored Black Blazer",
        category=ClothingCategory.OUTERWEAR.value,
        images=["https://example.com/blazer.jpg"],
        color="black",
        size="M",
        brand="Zara",
        price="$129.90",
        source="Zara",
        purchase_date="2024-02-10",
        tags=["formal", "work", "tailored"]
    )
    db.add_clothing_item(item4)
    items.append(item4)
    print(f"✓ Added: {item4.name}")
    
    # Item 5: Sunglasses
    item5 = ClothingItem(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name="Classic Aviator Sunglasses",
        category=ClothingCategory.ACCESSORIES.value,
        images=["https://example.com/sunglasses.jpg"],
        color="gold",
        size="Standard",
        brand="Ray-Ban",
        price="$189.00",
        source="Ray-Ban Store",
        tags=["accessory", "summer", "classic"]
    )
    db.add_clothing_item(item5)
    items.append(item5)
    print(f"✓ Added: {item5.name}")
    
    print(f"\n✓ Total items added: {len(items)}")
    return items


def example_3_create_outfits(user_id, items):
    """Example 3: Create outfits from clothing items"""
    print_section("Example 3: Creating Outfits")
    
    outfits = []
    
    # Outfit 1: Casual Weekend Look
    outfit1 = Outfit(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name="Casual Weekend Look",
        description="Perfect for a relaxed Saturday brunch with friends",
        clothing_item_ids=[items[0].id, items[1].id, items[2].id],  # T-shirt, jeans, sneakers
        occasion="casual",
        season="spring",
        weather="sunny",
        tags=["weekend", "brunch", "comfortable"]
    )
    db.create_outfit(outfit1)
    outfits.append(outfit1)
    print(f"✓ Created: {outfit1.name}")
    
    # Outfit 2: Smart Casual Work
    outfit2 = Outfit(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name="Smart Casual Office",
        description="Professional yet comfortable office outfit",
        clothing_item_ids=[items[0].id, items[1].id, items[3].id],  # T-shirt, jeans, blazer
        occasion="work",
        season="all",
        weather="any",
        tags=["office", "smart-casual", "professional"]
    )
    db.create_outfit(outfit2)
    outfits.append(outfit2)
    print(f"✓ Created: {outfit2.name}")
    
    print(f"\n✓ Total outfits created: {len(outfits)}")
    return outfits


def example_4_create_collection(user_id, outfits):
    """Example 4: Create a collection"""
    print_section("Example 4: Creating a Collection")
    
    collection = Collection(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name="Spring 2024 Favorites",
        description="My go-to outfits for spring season",
        outfit_ids=[outfit.id for outfit in outfits],
        is_wishlist=False,
        tags=["spring", "favorites", "2024"]
    )
    
    db.create_collection(collection)
    print(f"✓ Created collection: {collection.name}")
    print(f"  Contains {len(collection.outfit_ids)} outfits")
    
    return collection


def example_5_query_wardrobe(user_id):
    """Example 5: Query and filter wardrobe"""
    print_section("Example 5: Querying the Wardrobe")
    
    # Get all clothing items
    all_items = db.get_user_clothing_items(user_id)
    print(f"✓ Total clothing items: {len(all_items)}")
    
    # Filter by category
    tops = db.get_user_clothing_items(user_id, category=ClothingCategory.TOPS.value)
    print(f"✓ Tops: {len(tops)}")
    
    shoes = db.get_user_clothing_items(user_id, category=ClothingCategory.SHOES.value)
    print(f"✓ Shoes: {len(shoes)}")
    
    # Get all outfits
    all_outfits = db.get_user_outfits(user_id)
    print(f"✓ Total outfits: {len(all_outfits)}")
    
    # Filter by occasion
    casual_outfits = db.get_user_outfits(user_id, occasion="casual")
    print(f"✓ Casual outfits: {len(casual_outfits)}")


def example_6_outfit_with_items(outfits):
    """Example 6: Get outfit with clothing items"""
    print_section("Example 6: Getting Outfit with Items")
    
    outfit = outfits[0]
    result = db.get_outfit_with_items(outfit.id)
    
    print(f"Outfit: {result['outfit'].name}")
    print(f"Description: {result['outfit'].description}")
    print(f"\nClothing items in this outfit:")
    for item in result['items']:
        print(f"  - {item.name} ({item.category})")


def example_7_mark_worn(outfits):
    """Example 7: Track outfit usage"""
    print_section("Example 7: Tracking Outfit Usage")
    
    outfit = outfits[0]
    print(f"Marking '{outfit.name}' as worn...")
    
    # Mark as worn
    db.mark_outfit_worn(outfit.id)
    
    # Retrieve updated outfit
    updated = db.get_outfit(outfit.id)
    print(f"✓ Times worn: {updated.times_worn}")
    print(f"✓ Last worn: {updated.last_worn}")


def example_8_wardrobe_stats(user_id):
    """Example 8: Get wardrobe statistics"""
    print_section("Example 8: Wardrobe Statistics")
    
    stats = db.get_wardrobe_stats(user_id)
    
    print(f"User: {stats['user_id']}")
    print(f"Total clothing items: {stats['total_clothing_items']}")
    print(f"Total outfits: {stats['total_outfits']}")
    print(f"Total collections: {stats['total_collections']}")
    print(f"Estimated wardrobe value: {stats['estimated_wardrobe_value']}")
    print(f"Most common category: {stats['most_common_category']}")
    
    print("\nCategory breakdown:")
    for category, count in stats['category_breakdown'].items():
        print(f"  - {category}: {count} items")


def main():
    """Run all examples"""
    print("=" * 70)
    print("  LOVELACE WARDROBE DATABASE - USAGE EXAMPLES")
    print("=" * 70)
    
    # Check for credentials
    creds_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
    if not creds_path:
        print("\n❌ ERROR: FIREBASE_CREDENTIALS_PATH not set!")
        print("\nPlease set the environment variable:")
        print("  Windows: $env:FIREBASE_CREDENTIALS_PATH=\"path\\to\\credentials.json\"")
        print("  Linux/Mac: export FIREBASE_CREDENTIALS_PATH=/path/to/credentials.json")
        return
    
    # Initialize database
    global db
    db = WardrobeDB(credentials_path=creds_path)
    
    # Run examples
    user_id = example_1_create_user()
    items = example_2_add_clothing(user_id)
    outfits = example_3_create_outfits(user_id, items)
    collection = example_4_create_collection(user_id, outfits)
    example_5_query_wardrobe(user_id)
    example_6_outfit_with_items(outfits)
    example_7_mark_worn(outfits)
    example_8_wardrobe_stats(user_id)
    
    # Final summary
    print_section("Summary")
    print("✓ All examples completed successfully!")
    print(f"\nTest user ID: {user_id}")
    print(f"You can view this data in your Firebase Console:")
    print(f"https://console.firebase.google.com/")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExamples cancelled by user.")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
