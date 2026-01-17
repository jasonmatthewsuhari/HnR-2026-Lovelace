"""
Clothes Recommendation Module - AI-Powered Outfit & Shopping Recommendations

This module uses Gemini API to analyze user's wardrobe and provide:
1. Complete outfit recommendations from existing wardrobe items
2. Missing piece recommendations with integrated product search

Features:
- AI-powered style analysis
- Occasion-based outfit suggestions
- Wardrobe gap identification
- Integrated product search for missing items
"""

import os
import json
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not installed. Run: pip install google-generativeai")

try:
    from ..WardrobeDB.wardrobe_db import WardrobeDB, ClothingItem, Outfit
    from ..ClothesSearch.clothes_search import ClothesSearcher
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from WardrobeDB.wardrobe_db import WardrobeDB, ClothingItem, Outfit
    from ClothesSearch.clothes_search import ClothesSearcher


@dataclass
class OutfitRecommendation:
    """Represents a recommended outfit from existing wardrobe"""
    outfit_items: List[Dict[str, Any]]  # List of ClothingItem dicts
    confidence_score: float  # 0-100
    occasion: str
    reasoning: str
    style_notes: Optional[str] = None
    color_palette: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class ProductLink:
    """Product link from search"""
    url: str
    title: str
    description: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MissingItemRecommendation:
    """Represents a wardrobe gap with product suggestions"""
    category: str
    description: str
    reason: str
    search_query: str
    product_links: List[ProductLink] = field(default_factory=list)
    priority: str = "medium"  # low, medium, high
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['product_links'] = [p.to_dict() for p in self.product_links]
        return data


@dataclass
class RecommendationResult:
    """Complete recommendation response"""
    existing_outfits: List[OutfitRecommendation]
    missing_items: List[MissingItemRecommendation]
    occasion: Optional[str]
    analysis_summary: str
    user_style_profile: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'existing_outfits': [o.to_dict() for o in self.existing_outfits],
            'missing_items': [m.to_dict() for m in self.missing_items],
            'occasion': self.occasion,
            'analysis_summary': self.analysis_summary,
            'user_style_profile': self.user_style_profile
        }


class ClothesRecommender:
    """
    Main class for AI-powered clothes recommendations
    
    Uses Gemini API to analyze user's wardrobe and provide intelligent
    outfit recommendations and shopping suggestions.
    """
    
    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        wardrobe_db: Optional[WardrobeDB] = None,
        clothes_searcher: Optional[ClothesSearcher] = None
    ):
        """
        Initialize the recommender
        
        Args:
            gemini_api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
            wardrobe_db: WardrobeDB instance (will create if None)
            clothes_searcher: ClothesSearcher instance (will create if None)
        """
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai package not installed")
        
        self.api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Use Gemini 2.0 Flash for fast, high-quality responses
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Initialize integrations
        self.wardrobe_db = wardrobe_db
        self.clothes_searcher = clothes_searcher
        
        # Cache for user style profiles (simple in-memory cache)
        self._style_cache: Dict[str, Dict[str, Any]] = {}
    
    def analyze_user_style(
        self,
        user_outfits: List[Dict[str, Any]],
        user_clothing_items: Optional[List[ClothingItem]] = None
    ) -> Dict[str, Any]:
        """
        Analyze user's existing outfits to understand their style preferences
        
        Args:
            user_outfits: List of outfit dictionaries
            user_clothing_items: Optional list of user's clothing items
        
        Returns:
            Dictionary with style profile and insights
        """
        # Prepare data for analysis
        outfits_summary = []
        for outfit in user_outfits:
            outfits_summary.append({
                'name': outfit.get('name', 'Unnamed'),
                'occasion': outfit.get('occasion', 'casual'),
                'items': outfit.get('clothing_item_ids', []) or outfit.get('items', [])
            })
        
        # Prepare clothing items summary if available
        items_summary = []
        if user_clothing_items:
            for item in user_clothing_items:
                items_summary.append({
                    'name': item.name,
                    'category': item.category,
                    'color': item.color,
                    'brand': item.brand
                })
        
        # Create prompt for style analysis
        prompt = f"""
Analyze this user's fashion style based on their wardrobe and outfits.

EXISTING OUTFITS:
{json.dumps(outfits_summary, indent=2)}

WARDROBE ITEMS:
{json.dumps(items_summary[:30], indent=2) if items_summary else "Not provided"}

Please analyze and return a JSON object with the following structure:
{{
  "dominant_colors": ["color1", "color2", "color3"],
  "style_keywords": ["style1", "style2", "style3"],
  "common_occasions": ["occasion1", "occasion2"],
  "favorite_brands": ["brand1", "brand2"],
  "wardrobe_strengths": ["strength1", "strength2"],
  "wardrobe_gaps": ["gap1", "gap2", "gap3"],
  "style_summary": "Brief summary of user's overall style"
}}

Focus on being specific and actionable. Return ONLY the JSON object, no additional text.
"""
        
        try:
            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            response_text = response.text.strip()
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            style_profile = json.loads(response_text)
            return style_profile
            
        except Exception as e:
            print(f"Error analyzing user style: {e}")
            # Return default profile
            return {
                "dominant_colors": [],
                "style_keywords": ["casual"],
                "common_occasions": ["casual"],
                "favorite_brands": [],
                "wardrobe_strengths": [],
                "wardrobe_gaps": [],
                "style_summary": "Unable to analyze style at this time"
            }
    
    def recommend_outfits(
        self,
        user_id: str,
        occasion: Optional[str] = None,
        max_outfits: int = 5,
        style_profile: Optional[Dict[str, Any]] = None
    ) -> List[OutfitRecommendation]:
        """
        Recommend complete outfits from user's existing wardrobe
        
        Args:
            user_id: User ID
            occasion: Optional occasion filter
            max_outfits: Maximum number of outfits to recommend
            style_profile: Optional pre-computed style profile
        
        Returns:
            List of outfit recommendations
        """
        if not self.wardrobe_db:
            raise ValueError("WardrobeDB not initialized")
        
        # Get user's clothing items
        clothing_items = self.wardrobe_db.get_user_clothing_items(user_id)
        
        if not clothing_items:
            return []
        
        # Convert to dict format for AI processing
        items_data = []
        for item in clothing_items:
            items_data.append({
                'id': item.id,
                'name': item.name,
                'category': item.category,
                'color': item.color,
                'brand': item.brand,
                'tags': item.tags
            })
        
        # Create prompt for outfit recommendations
        style_context = ""
        if style_profile:
            style_context = f"\nUser Style Profile: {json.dumps(style_profile, indent=2)}"
        
        occasion_context = ""
        if occasion:
            occasion_context = f"\nTarget Occasion: {occasion}"
        
        prompt = f"""
You are a professional fashion stylist. Create {max_outfits} complete outfit recommendations from these wardrobe items.

AVAILABLE ITEMS:
{json.dumps(items_data, indent=2)}
{style_context}
{occasion_context}

Create outfit combinations that:
1. Match the occasion (if specified)
2. Have good color harmony
3. Include items from different categories (tops, bottoms, shoes, etc.)
4. Are stylish and wearable
5. Consider the user's style preferences

Return a JSON array with this structure:
[
  {{
    "outfit_items": ["item_id_1", "item_id_2", "item_id_3"],
    "confidence_score": 85,
    "occasion": "casual",
    "reasoning": "Why this outfit works well",
    "style_notes": "Additional styling tips",
    "color_palette": ["blue", "white", "black"]
  }}
]

Return ONLY the JSON array, no additional text. Make sure outfit_items contains valid item IDs from the available items.
"""
        
        try:
            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            response_text = response.text.strip()
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            outfits_data = json.loads(response_text)
            
            # Convert to OutfitRecommendation objects
            recommendations = []
            for outfit_data in outfits_data[:max_outfits]:
                # Get full item details
                item_ids = outfit_data.get('outfit_items', [])
                full_items = []
                for item_id in item_ids:
                    item = next((i for i in clothing_items if i.id == item_id), None)
                    if item:
                        full_items.append({
                            'id': item.id,
                            'name': item.name,
                            'category': item.category,
                            'color': item.color,
                            'images': item.images
                        })
                
                if full_items:  # Only add if we found valid items
                    recommendations.append(OutfitRecommendation(
                        outfit_items=full_items,
                        confidence_score=outfit_data.get('confidence_score', 70),
                        occasion=outfit_data.get('occasion', occasion or 'casual'),
                        reasoning=outfit_data.get('reasoning', ''),
                        style_notes=outfit_data.get('style_notes'),
                        color_palette=outfit_data.get('color_palette', [])
                    ))
            
            return recommendations
            
        except Exception as e:
            print(f"Error recommending outfits: {e}")
            return []
    
    def find_wardrobe_gaps(
        self,
        user_id: str,
        occasion: Optional[str] = None,
        style_profile: Optional[Dict[str, Any]] = None,
        max_suggestions: int = 5
    ) -> List[MissingItemRecommendation]:
        """
        Identify wardrobe gaps and recommend items to purchase
        
        Args:
            user_id: User ID
            occasion: Optional occasion focus
            style_profile: Optional pre-computed style profile
            max_suggestions: Maximum number of suggestions
        
        Returns:
            List of missing item recommendations with product links
        """
        if not self.wardrobe_db:
            raise ValueError("WardrobeDB not initialized")
        
        # Get user's wardrobe
        clothing_items = self.wardrobe_db.get_user_clothing_items(user_id)
        
        # Analyze what they have
        category_counts = {}
        for item in clothing_items:
            category_counts[item.category] = category_counts.get(item.category, 0) + 1
        
        # Get user's outfits to understand usage patterns
        user_outfits = self.wardrobe_db.get_user_outfits(user_id)
        outfits_summary = [
            {
                'name': o.name,
                'occasion': o.occasion,
                'times_worn': o.times_worn
            }
            for o in user_outfits[:10]  # Recent outfits
        ]
        
        # Create prompt for gap analysis
        style_context = ""
        if style_profile:
            style_context = f"\nUser Style Profile: {json.dumps(style_profile, indent=2)}"
        
        occasion_context = ""
        if occasion:
            occasion_context = f"\nTarget Occasion: {occasion}"
        
        prompt = f"""
You are a personal shopping assistant. Analyze this user's wardrobe and identify missing items they should buy.

WARDROBE SUMMARY:
{json.dumps(category_counts, indent=2)}

OUTFIT USAGE:
{json.dumps(outfits_summary, indent=2)}
{style_context}
{occasion_context}

Identify {max_suggestions} missing wardrobe items that would:
1. Fill important gaps in their wardrobe
2. Match their style preferences
3. Be suitable for their common occasions
4. Create new outfit possibilities

Return a JSON array with this structure:
[
  {{
    "category": "tops",
    "description": "White button-down dress shirt",
    "reason": "Essential for formal and business occasions, missing from wardrobe",
    "search_query": "men's white dress shirt slim fit",
    "priority": "high"
  }}
]

Priority levels: high, medium, low
Return ONLY the JSON array, no additional text.
"""
        
        try:
            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            response_text = response.text.strip()
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            gaps_data = json.loads(response_text)
            
            # Convert to MissingItemRecommendation objects
            recommendations = []
            for gap in gaps_data[:max_suggestions]:
                search_query = gap.get('search_query', '')
                
                # Get product links if clothes searcher is available
                product_links = []
                if self.clothes_searcher and search_query:
                    try:
                        print(f"Searching for products: {search_query}")
                        products = self.clothes_searcher.search_products(search_query, n=5)
                        print(f"Found {len(products)} products")
                        product_links = [
                            ProductLink(
                                url=p['url'],
                                title=p['title'],
                                description=p.get('description', '')
                            )
                            for p in products
                        ]
                    except Exception as e:
                        print(f"Error searching for products '{search_query}': {e}")
                        # Continue without product links instead of failing
                else:
                    print(f"ClothesSearcher not available for query: {search_query}")
                
                recommendations.append(MissingItemRecommendation(
                    category=gap.get('category', 'other'),
                    description=gap.get('description', ''),
                    reason=gap.get('reason', ''),
                    search_query=search_query,
                    product_links=product_links,
                    priority=gap.get('priority', 'medium')
                ))
            
            return recommendations
            
        except Exception as e:
            print(f"Error finding wardrobe gaps: {e}")
            return []
    
    def generate_recommendations(
        self,
        user_id: str,
        user_outfits: Optional[List[Dict[str, Any]]] = None,
        occasion: Optional[str] = None,
        max_outfits: int = 5,
        max_shopping_items: int = 5
    ) -> RecommendationResult:
        """
        Main entry point - generates complete recommendations
        
        Args:
            user_id: User ID
            user_outfits: Optional list of user's existing outfits for style analysis
            occasion: Optional occasion filter
            max_outfits: Maximum outfit recommendations
            max_shopping_items: Maximum shopping suggestions
        
        Returns:
            Complete RecommendationResult with outfits and shopping suggestions
        """
        # Get user's clothing items if wardrobe_db is available
        user_clothing_items = []
        if self.wardrobe_db:
            user_clothing_items = self.wardrobe_db.get_user_clothing_items(user_id)
            
            # If user_outfits not provided, get from database
            if not user_outfits and self.wardrobe_db:
                db_outfits = self.wardrobe_db.get_user_outfits(user_id)
                user_outfits = [
                    {
                        'name': o.name,
                        'occasion': o.occasion,
                        'clothing_item_ids': o.clothing_item_ids,
                        'times_worn': o.times_worn
                    }
                    for o in db_outfits
                ]
        
        # Analyze user style
        style_profile = None
        if user_outfits:
            style_profile = self.analyze_user_style(user_outfits, user_clothing_items)
        
        # Generate outfit recommendations
        outfit_recommendations = []
        if user_clothing_items:
            outfit_recommendations = self.recommend_outfits(
                user_id=user_id,
                occasion=occasion,
                max_outfits=max_outfits,
                style_profile=style_profile
            )
        
        # Find wardrobe gaps and generate shopping suggestions
        shopping_recommendations = self.find_wardrobe_gaps(
            user_id=user_id,
            occasion=occasion,
            style_profile=style_profile,
            max_suggestions=max_shopping_items
        )
        
        # Generate analysis summary
        summary_parts = []
        if style_profile:
            summary_parts.append(style_profile.get('style_summary', ''))
        
        if outfit_recommendations:
            summary_parts.append(f"Found {len(outfit_recommendations)} outfit combinations from your wardrobe.")
        else:
            summary_parts.append("Your wardrobe needs more items to create complete outfits.")
        
        if shopping_recommendations:
            summary_parts.append(f"Identified {len(shopping_recommendations)} items to enhance your wardrobe.")
        
        analysis_summary = " ".join(summary_parts) or "Analysis complete."
        
        return RecommendationResult(
            existing_outfits=outfit_recommendations,
            missing_items=shopping_recommendations,
            occasion=occasion,
            analysis_summary=analysis_summary,
            user_style_profile=style_profile
        )


# Convenience function for quick usage
def get_recommendations(
    user_id: str,
    user_outfits: Optional[List[Dict[str, Any]]] = None,
    occasion: Optional[str] = None,
    gemini_api_key: Optional[str] = None,
    wardrobe_db: Optional[WardrobeDB] = None,
    clothes_searcher: Optional[ClothesSearcher] = None
) -> RecommendationResult:
    """
    Quick function to get recommendations
    
    Args:
        user_id: User ID
        user_outfits: Optional list of existing outfits
        occasion: Optional occasion filter
        gemini_api_key: Optional Gemini API key
        wardrobe_db: Optional WardrobeDB instance
        clothes_searcher: Optional ClothesSearcher instance
    
    Returns:
        RecommendationResult
    """
    recommender = ClothesRecommender(
        gemini_api_key=gemini_api_key,
        wardrobe_db=wardrobe_db,
        clothes_searcher=clothes_searcher
    )
    
    return recommender.generate_recommendations(
        user_id=user_id,
        user_outfits=user_outfits,
        occasion=occasion
    )


if __name__ == "__main__":
    # Test the module
    print("=" * 70)
    print("Clothes Recommendation - Testing")
    print("=" * 70)
    
    # Check for API key
    if not os.getenv("GEMINI_API_KEY"):
        print("\nERROR: GEMINI_API_KEY not found in environment variables")
        print("\nTo use this module:")
        print("1. Get an API key from https://makersuite.google.com/app/apikey")
        print("2. Set it in your environment or .env file")
        import sys
        sys.exit(1)
    
    print("\n✓ Gemini API key found")
    print("✓ Module loaded successfully")
    print("\nReady to generate recommendations!")
    print("=" * 70)
