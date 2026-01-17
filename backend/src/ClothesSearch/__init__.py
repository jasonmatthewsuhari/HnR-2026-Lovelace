"""
Clothes Search Module

AI-powered clothing product search using Google Gemini API with Google Search grounding.

Quick Usage:
    from ClothesSearch import search_clothes
    
    results = search_clothes("red dress", n=10)
    for product in results:
        print(f"{product['title']}: {product['url']}")
"""

from .clothes_search import (
    ClothesSearcher,
    search_clothes,
    GEMINI_AVAILABLE
)

from .routes import router

__all__ = [
    'ClothesSearcher',
    'search_clothes',
    'router',
    'GEMINI_AVAILABLE'
]

__version__ = '1.0.0'
