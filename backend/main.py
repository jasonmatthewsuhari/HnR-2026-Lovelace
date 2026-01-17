"""
Lovelace Backend - Main Application Entry Point

This is the main FastAPI application for the Lovelace wardrobe management system.
It integrates all backend modules and provides a unified API.

Run with:
    uvicorn main:app --reload
    or
    python main.py
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import API routes
try:
    from src.WardrobeDB.routes import router as wardrobe_router
    WARDROBE_ROUTES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import wardrobe routes: {e}")
    WARDROBE_ROUTES_AVAILABLE = False

try:
    print("[*] Loading Photobooth routes...")
    from src.Photobooth.routes import router as photobooth_router
    PHOTOBOOTH_ROUTES_AVAILABLE = True
    print("[OK] Photobooth routes loaded successfully")
except Exception as e:
    print(f"[ERROR] Could not import photobooth routes: {e}")
    import traceback
    traceback.print_exc()
    PHOTOBOOTH_ROUTES_AVAILABLE = False

try:
    from src.ClothesSearch.routes import router as search_router
    SEARCH_ROUTES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import clothes search routes: {e}")
    SEARCH_ROUTES_AVAILABLE = False

try:
    from src.ClothesRecommendation.routes import router as recommendation_router
    RECOMMENDATION_ROUTES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import recommendation routes: {e}")
    RECOMMENDATION_ROUTES_AVAILABLE = False

try:
    from src.LiveVideoCall.routes import router as video_call_router
    VIDEO_CALL_ROUTES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import video call routes: {e}")
    VIDEO_CALL_ROUTES_AVAILABLE = False

try:
    from src.OAuth.calendar_routes import router as calendar_router
    CALENDAR_ROUTES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import calendar routes: {e}")
    CALENDAR_ROUTES_AVAILABLE = False

try:
    from src.VirtualTryOn.routes import router as virtual_tryon_router
    VIRTUAL_TRYON_ROUTES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import virtual try-on routes: {e}")
    VIRTUAL_TRYON_ROUTES_AVAILABLE = False

# Initialize FastAPI app
app = FastAPI(
    title="Lovelace API",
    description="Complete API for Lovelace - AI-Powered Fashion Assistant",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for frontend integration
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:8000').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
if WARDROBE_ROUTES_AVAILABLE:
    app.include_router(wardrobe_router, tags=["Wardrobe & Clothing"])

if PHOTOBOOTH_ROUTES_AVAILABLE:
    app.include_router(photobooth_router, tags=["Photobooth"])

if SEARCH_ROUTES_AVAILABLE:
    app.include_router(search_router, tags=["Clothes Search"])

if RECOMMENDATION_ROUTES_AVAILABLE:
    app.include_router(recommendation_router, tags=["Recommendations"])

if VIDEO_CALL_ROUTES_AVAILABLE:
    app.include_router(video_call_router, tags=["Video Call"])

if CALENDAR_ROUTES_AVAILABLE:
    app.include_router(calendar_router, tags=["Google Calendar"])

if VIRTUAL_TRYON_ROUTES_AVAILABLE:
    app.include_router(virtual_tryon_router, tags=["Virtual Try-On"])


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Lovelace API",
        "version": "1.0.0",
        "description": "AI-Powered Fashion Assistant with Virtual Boyfriend",
        "features": [
            "Wardrobe Management",
            "Outfit Recommendations",
            "Virtual Try-On",
            "Clothes Search",
            "Google Calendar Sync",
            "Live Video Call",
            "Photobooth",
            "Product to 3D Pipeline"
        ],
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Lovelace API",
        "modules": {
            "wardrobe_db": "active" if WARDROBE_ROUTES_AVAILABLE else "unavailable",
            "clothes_search": "active" if SEARCH_ROUTES_AVAILABLE else "unavailable",
            "recommendation": "active" if RECOMMENDATION_ROUTES_AVAILABLE else "unavailable",
            "photobooth": "active" if PHOTOBOOTH_ROUTES_AVAILABLE else "unavailable",
            "video_call": "active" if VIDEO_CALL_ROUTES_AVAILABLE else "unavailable",
            "calendar_sync": "active" if CALENDAR_ROUTES_AVAILABLE else "unavailable",
            "virtual_try_on": "active" if VIRTUAL_TRYON_ROUTES_AVAILABLE else "unavailable",
            "product_3d": "pending"
        }
    }


# Include routers for different modules
# app.include_router(wardrobe_router, prefix="/api/wardrobe", tags=["Wardrobe"])
# app.include_router(recommendation_router, prefix="/api/recommendations", tags=["Recommendations"])
# ... etc


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 70)
    print("LOVELACE - AI-Powered Fashion Assistant")
    print("=" * 70)
    print()
    print("Starting Lovelace Backend API Server...")
    print()
    print("Server: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("ReDoc: http://localhost:8000/redoc")
    print()
    
    # Check environment variables
    if not os.getenv('FIREBASE_CREDENTIALS_PATH'):
        print("WARNING: FIREBASE_CREDENTIALS_PATH not set")
        print("Some features may not work correctly.")
        print()
    
    print("=" * 70)
    print()
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
