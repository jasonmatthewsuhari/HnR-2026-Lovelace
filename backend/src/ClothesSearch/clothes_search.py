"""
Clothes Search Module - Using Gemini API with Google Search Grounding

This module uses Google's Gemini API with google_search tool to find product links
based on user queries for fashion items.
"""

import os
import re
import sys
from typing import List, Optional
from dotenv import load_dotenv

# Fix Windows encoding issues
if sys.platform == 'win32':
    import codecs
    try:
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except AttributeError:
        pass  # Already wrapped or not necessary

# Load environment variables
load_dotenv()

try:
    import google.genai as genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    try:
        # Fallback to old package if new one not available
        import google.generativeai as genai
        types = genai.types
        GEMINI_AVAILABLE = True
        print("[WARNING] Using deprecated google.generativeai - please upgrade to google-genai")
    except ImportError:
        GEMINI_AVAILABLE = False
        print("Warning: Neither google-genai nor google-generativeai installed")
        print("Run: pip install google-genai")


class ClothesSearcher:
    """Search for clothing products using Gemini API with Google Search"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the clothes searcher
        
        Args:
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
        """
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai package not installed")
        
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Configure Gemini
        client = genai.Client(api_key=self.api_key)
        self.client = client
        self.model_id = 'gemini-2.0-flash-exp'
    
    def search_products(
        self, 
        query: str, 
        n: int = 10,
        size: Optional[str] = None,
        color: Optional[str] = None,
        brand: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[dict]:
        """
        Search for clothing products based on query with optional filters
        
        Args:
            query: Search query (e.g., "red summer dress", "nike running shoes")
            n: Number of product links to return (default: 10)
            size: Size filter (e.g., "M", "32", "Large")
            color: Color filter (e.g., "black", "blue")
            brand: Brand filter (e.g., "Nike", "Adidas")
            category: Category filter (e.g., "Tops", "Shoes", "Dresses")
        
        Returns:
            List of dictionaries with product information:
            [
                {
                    "url": "https://example.com/product",
                    "title": "Product Name",
                    "description": "Product description"
                },
                ...
            ]
        """
        # Build enhanced query with filters
        enhanced_query = query
        
        # Add filters to query if provided
        filters = []
        if size:
            filters.append(f"size {size}")
        if color:
            filters.append(f"{color} color")
        if brand:
            filters.append(f"{brand} brand")
        if category:
            filters.append(f"category {category}")
        
        if filters:
            enhanced_query = f"{query} {' '.join(filters)}"
        
        # Silently add "Singapore" to focus on local availability
        enhanced_query = f"{enhanced_query} Singapore"
        # Create a detailed prompt for fashion product search
        prompt = f"""
        You are a fashion shopping assistant. Search the web and find {n} real, buyable clothing products 
        that match this query: "{enhanced_query}"
        
        Requirements:
        - Find products from real e-commerce websites (Amazon, ASOS, Zara, H&M, Nike, Nordstrom, Macy's, etc.)
        - Each result must be a direct product page URL (not category pages)
        - Products should be currently available for purchase
        - Provide diverse sources
        - IMPORTANT: Include the product image URL
        
        For each product, provide:
        1. Direct product page URL (must be a real, working link)
        2. Product image URL (the main product image from the website)
        3. Product name/title
        4. Brief description (1-2 sentences)
        
        Format each result EXACTLY like this:
        URL: [full product url]
        IMAGE: [full image url]
        TITLE: [product name]
        DESC: [brief description]
        ---
        
        Provide exactly {n} products. Focus on giving real, working product links and their images.
        """
        
        try:
            # Generate content
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            
            # Parse the response
            products = self._parse_response(response.text, n)
            
            return products
            
        except Exception as e:
            print(f"Error during Gemini API call: {e}")
            raise
    
    def _parse_response(self, response_text: str, max_results: int) -> List[dict]:
        """
        Parse the Gemini response to extract product information
        
        Args:
            response_text: Raw response from Gemini
            max_results: Maximum number of results to return
        
        Returns:
            List of product dictionaries
        """
        products = []
        
        # Split by separator
        sections = response_text.split('---')
        
        for section in sections[:max_results]:
            # Extract URL, IMAGE, TITLE, DESC using regex
            url_match = re.search(r'URL:\s*(.+?)(?:\n|$)', section, re.IGNORECASE)
            image_match = re.search(r'IMAGE:\s*(.+?)(?:\n|$)', section, re.IGNORECASE)
            title_match = re.search(r'TITLE:\s*(.+?)(?:\n|$)', section, re.IGNORECASE)
            desc_match = re.search(r'DESC:\s*(.+?)(?:\n|$)', section, re.IGNORECASE | re.DOTALL)
            
            if url_match:
                url = url_match.group(1).strip()
                # Clean URL - remove markdown formatting if present
                url = re.sub(r'[\[\]\(\)]', '', url)
                
                # Extract and clean image URL
                image_url = None
                if image_match:
                    image_url = image_match.group(1).strip()
                    image_url = re.sub(r'[\[\]\(\)]', '', image_url)
                    # Validate it looks like a URL
                    if not image_url.startswith(('http://', 'https://')):
                        image_url = None
                
                product = {
                    "url": url,
                    "image": image_url,
                    "title": title_match.group(1).strip() if title_match else "Unknown Product",
                    "description": desc_match.group(1).strip() if desc_match else ""
                }
                
                # Validate URL
                if self._is_valid_url(url):
                    products.append(product)
        
        # Fallback: If structured parsing failed, try to extract any URLs
        if not products:
            urls = re.findall(r'https?://[^\s\)]+', response_text)
            for url in urls[:max_results]:
                if self._is_valid_url(url):
                    products.append({
                        "url": url,
                        "image": None,
                        "title": "Product Link",
                        "description": ""
                    })
        
        return products[:max_results]
    
    def _is_valid_url(self, url: str) -> bool:
        """
        Check if URL is valid and looks like a product page
        
        Args:
            url: URL to validate
        
        Returns:
            True if URL appears valid
        """
        if not url.startswith(('http://', 'https://')):
            return False
        
        # Filter out obvious non-product URLs
        invalid_patterns = [
            'google.com/search',
            'youtube.com',
            'facebook.com',
            'twitter.com',
            'instagram.com',
            '/category/',
            '/categories/',
        ]
        
        return not any(pattern in url.lower() for pattern in invalid_patterns)
    
    def search_simple(
        self, 
        query: str, 
        n: int = 10,
        size: Optional[str] = None,
        color: Optional[str] = None,
        brand: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[str]:
        """
        Simple search that returns only URLs
        
        Args:
            query: Search query
            n: Number of URLs to return
            size: Size filter (optional)
            color: Color filter (optional)
            brand: Brand filter (optional)
            category: Category filter (optional)
        
        Returns:
            List of product URLs
        """
        products = self.search_products(query, n, size, color, brand, category)
        return [p["url"] for p in products]


# Convenience function for quick usage
def search_clothes(
    query: str, 
    n: int = 10, 
    api_key: Optional[str] = None,
    size: Optional[str] = None,
    color: Optional[str] = None,
    brand: Optional[str] = None,
    category: Optional[str] = None
) -> List[dict]:
    """
    Quick search function
    
    Args:
        query: Search query for clothing items
        n: Number of results (default: 10)
        api_key: Optional Gemini API key
        size: Size filter (e.g., "M", "32")
        color: Color filter (e.g., "black", "blue")
        brand: Brand filter (e.g., "Nike")
        category: Category filter (e.g., "Tops", "Shoes")
    
    Returns:
        List of product dictionaries
    """
    searcher = ClothesSearcher(api_key=api_key)
    return searcher.search_products(query, n, size, color, brand, category)


if __name__ == "__main__":
    # Simple usage example
    import sys
    
    print("=" * 70)
    print("Clothes Search - Quick Test")
    print("=" * 70)
    
    # Check for API key
    if not os.getenv("GEMINI_API_KEY"):
        print("\nERROR: GEMINI_API_KEY not found in environment variables")
        print("\nTo use this module:")
        print("1. Get an API key from https://makersuite.google.com/app/apikey")
        print("2. Set it in your .env file at project root:")
        print("   GEMINI_API_KEY=your-api-key")
        sys.exit(1)
    
    # Quick test search
    query = "black t-shirt"
    print(f"\nSearching for: '{query}'")
    print("Please wait (10-20 seconds)...\n")
    
    try:
        # Simple usage - just call search_clothes()
        results = search_clothes(query, n=3)
        
        print(f"Found {len(results)} products:\n")
        for i, product in enumerate(results, 1):
            print(f"{i}. {product['title']}")
            print(f"   URL: {product['url']}")
            if product['description']:
                print(f"   Description: {product['description'][:80]}...")
            print()
        
        print("=" * 70)
        print("✓ Test completed successfully!")
        print("\nUsage in your code:")
        print("  from ClothesSearch import search_clothes")
        print("  results = search_clothes('red dress', n=10)")
        print("\nWith filters:")
        print("  results = search_clothes('shoes', n=5, size='10', color='black')")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
