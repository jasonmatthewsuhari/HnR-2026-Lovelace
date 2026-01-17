"""
Clothes Recommendation Demo - Interactive Showcase

This demo showcases the AI-powered recommendation system with sample data
and interactive examples.

Run with: python demo.py
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import json

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Note: python-dotenv not installed, using system environment only")

# Import recommendation system
try:
    from src.ClothesRecommendation.clothes_recommendation import (
        ClothesRecommender,
        RecommendationResult,
        OutfitRecommendation,
        MissingItemRecommendation,
        ProductLink,
        GEMINI_AVAILABLE
    )
except ImportError:
    try:
        # Try relative import
        from clothes_recommendation import (
            ClothesRecommender,
            RecommendationResult,
            OutfitRecommendation,
            MissingItemRecommendation,
            ProductLink,
            GEMINI_AVAILABLE
        )
    except ImportError as e:
        print(f"Error importing modules: {e}")
        print("\nPlease run from backend directory:")
        print("  cd backend")
        print("  python -m src.ClothesRecommendation.demo")
        sys.exit(1)


# Sample Data for Demo
SAMPLE_OUTFITS = [
    {
        "name": "Work Monday",
        "occasion": "work",
        "items": ["white button-down shirt", "navy blue pants", "black leather shoes"],
        "times_worn": 5
    },
    {
        "name": "Casual Weekend",
        "occasion": "casual",
        "items": ["gray t-shirt", "blue jeans", "white sneakers"],
        "times_worn": 12
    },
    {
        "name": "Friday Office",
        "occasion": "work",
        "items": ["light blue shirt", "khaki chinos", "brown loafers"],
        "times_worn": 3
    },
    {
        "name": "Coffee Meetup",
        "occasion": "casual",
        "items": ["black turtleneck", "dark jeans", "chelsea boots"],
        "times_worn": 4
    }
]

SAMPLE_WARDROBE = {
    "tops": ["white button-down", "light blue shirt", "gray t-shirt", "black turtleneck", "polo shirt"],
    "bottoms": ["navy pants", "khaki chinos", "blue jeans", "dark jeans"],
    "shoes": ["black leather shoes", "brown loafers", "white sneakers", "chelsea boots"],
    "accessories": ["leather belt", "watch"]
}


def print_header(text: str, char: str = "="):
    """Print a formatted header"""
    width = 70
    print()
    print(char * width)
    print(text.center(width))
    print(char * width)
    print()


def print_section(text: str):
    """Print a section header"""
    print()
    print("-" * 70)
    print(f"  {text}")
    print("-" * 70)


def print_outfit(outfit: OutfitRecommendation, index: int):
    """Pretty print an outfit recommendation"""
    print(f"\n  Outfit #{index + 1} - {outfit.occasion.upper()}")
    print(f"  Confidence: {outfit.confidence_score:.0f}%")
    print(f"\n  Items:")
    for item in outfit.outfit_items:
        print(f"    - {item.get('name', 'Unknown')} ({item.get('category', 'N/A')})")
    
    if outfit.color_palette:
        print(f"\n  Color Palette: {', '.join(outfit.color_palette)}")
    
    print(f"\n  Why this works:")
    print(f"    {outfit.reasoning}")
    
    if outfit.style_notes:
        print(f"\n  Styling Tip:")
        print(f"    {outfit.style_notes}")


def print_missing_item(item: MissingItemRecommendation, index: int):
    """Pretty print a shopping recommendation"""
    priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
    emoji = priority_emoji.get(item.priority, "⚪")
    
    print(f"\n  {emoji} Item #{index + 1} - {item.category.upper()} [{item.priority} priority]")
    print(f"\n  What to buy: {item.description}")
    print(f"\n  Why you need it:")
    print(f"    {item.reason}")
    
    if item.product_links:
        print(f"\n  Where to shop:")
        for i, link in enumerate(item.product_links[:3], 1):
            print(f"    {i}. {link.title}")
            print(f"       {link.url}")


def demo_style_analysis():
    """Demo: Style Analysis"""
    print_section("DEMO 1: Style Analysis")
    
    print("Analyzing user's style from their existing outfits...")
    print()
    print("Sample outfits:")
    for outfit in SAMPLE_OUTFITS[:3]:
        print(f"  - {outfit['name']}: {', '.join(outfit['items'])}")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\n❌ GEMINI_API_KEY not set - skipping AI analysis")
        print("   Set your API key to see real style analysis")
        print("   Get one at: https://makersuite.google.com/app/apikey")
        return
    
    if not GEMINI_AVAILABLE:
        print("\n❌ Gemini API not available")
        print("   Install with: pip install google-generativeai")
        return
    
    try:
        # Import using the already imported classes at the top
        from src.ClothesRecommendation.clothes_recommendation import ClothesRecommender
        
        recommender = ClothesRecommender(gemini_api_key=api_key, wardrobe_db=None, clothes_searcher=None)
        
        print("\n🔄 Analyzing with Gemini AI...")
        style_profile = recommender.analyze_user_style(SAMPLE_OUTFITS)
        
        print("\n✅ Style Profile Generated:")
        print(f"\n  Dominant Colors: {', '.join(style_profile.get('dominant_colors', []))}")
        print(f"  Style Keywords: {', '.join(style_profile.get('style_keywords', []))}")
        print(f"  Common Occasions: {', '.join(style_profile.get('common_occasions', []))}")
        
        if style_profile.get('wardrobe_strengths'):
            print(f"\n  Wardrobe Strengths:")
            for strength in style_profile['wardrobe_strengths']:
                print(f"    ✓ {strength}")
        
        if style_profile.get('wardrobe_gaps'):
            print(f"\n  Wardrobe Gaps:")
            for gap in style_profile['wardrobe_gaps']:
                print(f"    ⚠ {gap}")
        
        print(f"\n  Overall Style:")
        print(f"    {style_profile.get('style_summary', 'N/A')}")
        
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("   Make sure to run from the backend directory: cd backend && python -m src.ClothesRecommendation.demo")
    except Exception as e:
        print(f"\n❌ Error during style analysis: {e}")
        import traceback
        traceback.print_exc()


def demo_mock_outfit_recommendations():
    """Demo: Mock Outfit Recommendations (without API)"""
    print_section("DEMO 2: Outfit Recommendations (Mock Data)")
    
    print("This shows what outfit recommendations would look like:")
    print()
    
    # Create mock recommendations
    mock_outfits = [
        OutfitRecommendation(
            outfit_items=[
                {"id": "1", "name": "White Button-Down", "category": "tops", "color": "white"},
                {"id": "2", "name": "Navy Chinos", "category": "bottoms", "color": "navy"},
                {"id": "3", "name": "Brown Leather Loafers", "category": "shoes", "color": "brown"}
            ],
            confidence_score=92,
            occasion="work",
            reasoning="Classic business casual combination with complementary colors. Navy and brown create a sophisticated, professional look.",
            style_notes="Add a leather belt to match the shoes for a polished finish",
            color_palette=["white", "navy", "brown"]
        ),
        OutfitRecommendation(
            outfit_items=[
                {"id": "4", "name": "Black Turtleneck", "category": "tops", "color": "black"},
                {"id": "5", "name": "Dark Jeans", "category": "bottoms", "color": "dark blue"},
                {"id": "6", "name": "Chelsea Boots", "category": "shoes", "color": "black"}
            ],
            confidence_score=88,
            occasion="date night",
            reasoning="Modern, stylish look perfect for evening dates. Black turtleneck adds sophistication while remaining approachable.",
            style_notes="This outfit works for both casual cafes and upscale restaurants",
            color_palette=["black", "dark blue"]
        )
    ]
    
    for i, outfit in enumerate(mock_outfits):
        print_outfit(outfit, i)


def demo_mock_shopping_recommendations():
    """Demo: Mock Shopping Recommendations (without API)"""
    print_section("DEMO 3: Shopping Recommendations (Mock Data)")
    
    print("Based on wardrobe analysis, here are suggested items to buy:")
    print()
    
    # Use already imported ProductLink from top of file
    # ProductLink is already imported at the top
    
    mock_shopping = [
        MissingItemRecommendation(
            category="outerwear",
            description="Navy blazer or sport coat",
            reason="Essential for formal occasions and business meetings. Your wardrobe has great basics but lacks a proper jacket for elevated looks.",
            search_query="men's navy blazer slim fit",
            product_links=[
                ProductLink(
                    url="https://example.com/blazer1",
                    title="J.Crew Ludlow Slim-Fit Blazer",
                    description="Classic navy blazer in Italian wool"
                ),
                ProductLink(
                    url="https://example.com/blazer2",
                    title="Bonobos Foundation Blazer",
                    description="Versatile navy sport coat"
                )
            ],
            priority="high"
        ),
        MissingItemRecommendation(
            category="accessories",
            description="Leather dress belt in brown",
            reason="You have brown shoes but no matching belt. A coordinated belt completes professional looks.",
            search_query="men's brown leather dress belt",
            product_links=[
                ProductLink(
                    url="https://example.com/belt1",
                    title="Allen Edmonds Wide Basic Belt",
                    description="Premium leather belt in multiple sizes"
                )
            ],
            priority="medium"
        ),
        MissingItemRecommendation(
            category="tops",
            description="Neutral sweater (gray or navy)",
            reason="Perfect for layering in cooler weather and adds versatility to your work wardrobe.",
            search_query="men's merino wool sweater v-neck",
            product_links=[
                ProductLink(
                    url="https://example.com/sweater1",
                    title="Uniqlo Extra Fine Merino V-Neck",
                    description="Soft merino wool sweater"
                )
            ],
            priority="medium"
        )
    ]
    
    for i, item in enumerate(mock_shopping):
        print_missing_item(item, i)


def demo_json_output():
    """Demo: JSON Output Format"""
    print_section("DEMO 4: JSON API Response Format")
    
    print("This is how recommendations are returned from the API:")
    print()
    
    # Use already imported classes from top of file
    
    result = RecommendationResult(
        existing_outfits=[
            OutfitRecommendation(
                outfit_items=[
                    {"id": "1", "name": "White Shirt", "category": "tops"},
                    {"id": "2", "name": "Navy Pants", "category": "bottoms"}
                ],
                confidence_score=90,
                occasion="work",
                reasoning="Professional combination",
                style_notes="Add a belt",
                color_palette=["white", "navy"]
            )
        ],
        missing_items=[
            MissingItemRecommendation(
                category="outerwear",
                description="Navy blazer",
                reason="Essential for formal occasions",
                search_query="navy blazer",
                product_links=[
                    ProductLink(url="https://example.com", title="Blazer", description="Navy blazer")
                ],
                priority="high"
            )
        ],
        occasion="work",
        analysis_summary="You have solid basics but need formal pieces",
        user_style_profile={
            "dominant_colors": ["navy", "white"],
            "style_keywords": ["professional", "classic"]
        }
    )
    
    # Convert to JSON
    json_output = json.dumps(result.to_dict(), indent=2)
    
    # Print truncated version
    lines = json_output.split('\n')
    if len(lines) > 30:
        print('\n'.join(lines[:30]))
        print(f"\n  ... ({len(lines) - 30} more lines)")
    else:
        print(json_output)


def demo_api_endpoints():
    """Demo: API Endpoint Examples"""
    print_section("DEMO 5: API Endpoint Examples")
    
    print("Once the server is running, you can use these endpoints:")
    print()
    
    print("1. Generate Complete Recommendations:")
    print("   POST http://localhost:8000/api/recommendations/analyze")
    print()
    print("   Example request:")
    print(json.dumps({
        "user_id": "user123",
        "occasion": "date night",
        "max_outfits": 5,
        "max_shopping_items": 3
    }, indent=4))
    
    print("\n2. Get Outfit Recommendations:")
    print("   GET http://localhost:8000/api/recommendations/outfits")
    print("       ?user_id=user123&occasion=work&max_results=3")
    
    print("\n3. Get Shopping Suggestions:")
    print("   GET http://localhost:8000/api/recommendations/shopping")
    print("       ?user_id=user123&max_suggestions=5")
    
    print("\n4. Get User Style Profile:")
    print("   GET http://localhost:8000/api/recommendations/style-profile/user123")
    
    print("\n5. Health Check:")
    print("   GET http://localhost:8000/api/recommendations/health")


def demo_curl_examples():
    """Demo: cURL Command Examples"""
    print_section("DEMO 6: cURL Command Examples")
    
    print("Copy and paste these commands to test the API:")
    print()
    
    print("# Test health check")
    print("curl http://localhost:8000/api/recommendations/health")
    print()
    
    print("# Get outfit recommendations")
    print("curl 'http://localhost:8000/api/recommendations/outfits?user_id=user123&occasion=work'")
    print()
    
    print("# Generate complete recommendations")
    print("curl -X POST http://localhost:8000/api/recommendations/analyze \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print('    "user_id": "user123",')
    print('    "occasion": "date night",')
    print('    "max_outfits": 3,')
    print('    "max_shopping_items": 3')
    print("  }'")


def check_prerequisites():
    """Check if prerequisites are met"""
    print_section("Prerequisites Check")
    
    # Check for firebase credentials file
    backend_dir = Path(__file__).resolve().parent.parent.parent
    firebase_creds = backend_dir / "firebase-credentials.json"
    firebase_available = firebase_creds.exists() or bool(os.getenv("FIREBASE_CREDENTIALS_PATH"))
    
    checks = {
        "Gemini API Available": GEMINI_AVAILABLE,
        "GEMINI_API_KEY Set": bool(os.getenv("GEMINI_API_KEY")),
        "Firebase Credentials": firebase_available
    }
    
    for check, status in checks.items():
        symbol = "✓" if status else "✗"
        status_text = "OK" if status else "NOT FOUND"
        print(f"  {symbol} {check}: {status_text}")
    
    if firebase_available and firebase_creds.exists():
        print(f"\n  📄 Firebase credentials found at:")
        print(f"     {firebase_creds}")
    
    if not checks["GEMINI_API_KEY Set"]:
        print("\n⚠ Note: Some demos will be limited without GEMINI_API_KEY")
        print("  Get one at: https://makersuite.google.com/app/apikey")
    
    print()


def interactive_menu():
    """Interactive demo menu"""
    while True:
        print_header("Clothes Recommendation System - Interactive Demo", "=")
        print("Select a demo to run:")
        print()
        print("  1. Prerequisites Check")
        print("  2. Style Analysis (AI-powered)")
        print("  3. Outfit Recommendations (Mock Data)")
        print("  4. Shopping Recommendations (Mock Data)")
        print("  5. JSON Output Format")
        print("  6. API Endpoint Examples")
        print("  7. cURL Command Examples")
        print("  8. Run All Demos")
        print("  0. Exit")
        print()
        
        choice = input("Enter your choice (0-8): ").strip()
        
        if choice == "0":
            print("\nThank you for trying the Clothes Recommendation Demo!")
            break
        elif choice == "1":
            check_prerequisites()
        elif choice == "2":
            demo_style_analysis()
        elif choice == "3":
            demo_mock_outfit_recommendations()
        elif choice == "4":
            demo_mock_shopping_recommendations()
        elif choice == "5":
            demo_json_output()
        elif choice == "6":
            demo_api_endpoints()
        elif choice == "7":
            demo_curl_examples()
        elif choice == "8":
            check_prerequisites()
            demo_style_analysis()
            demo_mock_outfit_recommendations()
            demo_mock_shopping_recommendations()
            demo_json_output()
            demo_api_endpoints()
            demo_curl_examples()
        else:
            print("\n❌ Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")


def main():
    """Main demo function"""
    print_header("LOVELACE - Clothes Recommendation System", "=")
    print("Welcome to the interactive demo!")
    print()
    print("This demo showcases the AI-powered recommendation system that:")
    print("  • Analyzes your style from existing outfits")
    print("  • Recommends outfit combinations from your wardrobe")
    print("  • Suggests items to buy with real product links")
    print("  • Provides fashion advice and styling tips")
    
    interactive_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
