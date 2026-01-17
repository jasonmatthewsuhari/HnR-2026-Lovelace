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
            "wardrobe_db": "active",
            "clothes_search": "pending",
            "virtual_try_on": "pending",
            "recommendation": "pending",
            "calendar_sync": "pending",
            "video_call": "pending",
            "photobooth": "pending",
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
