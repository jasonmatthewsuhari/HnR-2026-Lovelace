"""
Lovelace Backend - Main Application Entry Point

This is the main FastAPI application for the Lovelace wardrobe management system.
It integrates all backend modules and provides a unified API.

Run with:
    uvicorn main:app --reload
    or
    python main.py
"""

from fastapi import FastAPI, UploadFile, File
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
    # Temporarily disable photobooth routes to fix server startup
    # from src.Photobooth.routes import router as photobooth_router
    photobooth_router = None
    PHOTOBOOTH_ROUTES_AVAILABLE = False
    print("[WARN] Photobooth routes temporarily disabled")
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

try:
    from src.ProductTo3DPipeline.routes import router as product_3d_router
    PRODUCT_3D_ROUTES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import product 3D routes: {e}")
    PRODUCT_3D_ROUTES_AVAILABLE = False

try:
    from src.PaymentAgent.routes import router as payment_agent_router
    PAYMENT_AGENT_ROUTES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import payment agent routes: {e}")
    PAYMENT_AGENT_ROUTES_AVAILABLE = False

try:
    from src.VoiceAgent.routes import router as voice_agent_router
    VOICE_AGENT_ROUTES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import voice agent routes: {e}")
    VOICE_AGENT_ROUTES_AVAILABLE = False

# Initialize FastAPI app
app = FastAPI(
    title="Lovelace API",
    description="Complete API for Lovelace - AI-Powered Fashion Assistant",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    # Configure WebSocket settings to accept all origins
    websocket_ping_interval=20,
    websocket_ping_timeout=20,
)

# Configure CORS for frontend integration
# NOTE: CORSMiddleware blocks WebSocket connections in some versions
# We'll add CORS headers manually where needed instead
# 
# Temporarily disabled to fix WebSocket 403 issue:
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=False,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Custom CORS handling for HTTP endpoints only
@app.middleware("http")
async def add_cors_and_debug(request, call_next):
    """Add CORS headers to HTTP responses and debug WebSocket upgrades"""
    # Log ALL requests including WebSocket upgrade attempts
    print(f"[DEBUG] Request: {request.method} {request.url.path}")
    print(f"[DEBUG] Headers: {dict(request.headers)}")
    
    response = await call_next(request)
    
    # Add CORS headers for non-WebSocket responses
    if not request.headers.get("upgrade") == "websocket":
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
    
    print(f"[DEBUG] Response status: {response.status_code}")
    return response

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

if PRODUCT_3D_ROUTES_AVAILABLE:
    app.include_router(product_3d_router, prefix="/3d", tags=["Product to 3D"])
    print("[OK] Product to 3D routes loaded successfully")
else:
    print("[ERROR] Product to 3D routes not available")

if PAYMENT_AGENT_ROUTES_AVAILABLE:
    app.include_router(payment_agent_router, tags=["Payment Agent"])
    print("[OK] Payment Agent routes loaded successfully")
else:
    print("[ERROR] Payment Agent routes not available")

if VOICE_AGENT_ROUTES_AVAILABLE:
    app.include_router(voice_agent_router, tags=["Voice Agent"])
    print("[OK] Voice Agent routes loaded successfully")
else:
    print("[ERROR] Voice Agent routes not available")

# Add direct WebSocket endpoint to bypass router issues
@app.websocket("/voice-agent/ws")
async def direct_voice_agent_websocket(websocket):
    """
    Direct WebSocket endpoint to bypass router origin validation issues
    """
    print(f"[Direct Voice Agent] WebSocket connection attempt from: {websocket.client}")
    print(f"[Direct Voice Agent] Origin: {websocket.headers.get('origin')}")

    try:
        # Accept WebSocket connection
        await websocket.accept()
        print("[Direct Voice Agent] WebSocket accepted")

        # Send welcome message
        await websocket.send_json({
            "type": "text",
            "content": "Direct WebSocket connection successful!"
        })

        # Echo messages back
        while True:
            try:
                data = await websocket.receive_json()
                print(f"[Direct Voice Agent] Received: {data}")
                await websocket.send_json({
                    "type": "text",
                    "content": f"Echo: {data}"
                })
            except Exception as e:
                print(f"[Direct Voice Agent] Message error: {e}")
                break

    except Exception as e:
        print(f"[Direct Voice Agent] Accept failed: {e}")
        try:
            await websocket.close(code=1008, reason=str(e))
        except:
            pass


@app.post("/3d/boyfriends/custom/generate")
async def mock_custom_boyfriend_generation(
    image: UploadFile = File(...),
    boyfriend_name: str = None,
    async_mode: bool = True
):
    """
    MOCK: Generate custom boyfriend from image
    Returns fake successful response immediately
    """
    from uuid import uuid4
    from datetime import datetime

    # Generate fake boyfriend ID
    boyfriend_id = f"custom_{uuid4().hex[:8]}"

    if async_mode:
        # Return fake job info
        return {
            "success": True,
            "job_id": boyfriend_id,
            "boyfriend_id": boyfriend_id,
            "message": "Custom boyfriend generation started",
            "status": "processing",
            "estimated_time": "5 seconds",
            "status_url": f"/3d/status/{boyfriend_id}"
        }
    else:
        # Return immediate success
        return {
            "success": True,
            "boyfriend_id": boyfriend_id,
            "name": boyfriend_name or "Custom Boyfriend",
            "model_url": "/3d/models/boyfriends/alex",  # Use existing demo model
            "description": "Your custom virtual companion",
            "personality": "Personalized just for you",
            "generation_time": 2.5
        }


@app.get("/3d/status/{job_id}")
async def mock_job_status(job_id: str):
    """MOCK: Always return completed status"""
    return {
        "job_id": job_id,
        "status": "completed",
        "progress": 100,
        "stage": "Complete!",
        "model_url": "/3d/models/boyfriends/alex",  # Use existing demo model
        "generation_time": 2.5
    }


@app.get("/3d/boyfriends/custom")
async def mock_list_custom_boyfriends():
    """MOCK: Return empty list"""
    return {
        "boyfriends": [],
        "count": 0
    }


@app.get("/3d/models/demo/product_3d.glb")
async def serve_glb_file():
    """Serve the demo GLB file"""
    from pathlib import Path
    glb_path = Path("src/ProductTo3DPipeline/models/product_3d.glb")
    if glb_path.exists():
        from fastapi.responses import FileResponse
        return FileResponse(
            path=glb_path,
            media_type="model/gltf-binary",
            filename="product_3d.glb"
        )
    else:
        return {"error": "GLB file not found"}

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
            "Product to 3D Pipeline",
            "Agentic Commerce Payment"
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
            "product_3d": "active" if PRODUCT_3D_ROUTES_AVAILABLE else "unavailable",
            "payment_agent": "active" if PAYMENT_AGENT_ROUTES_AVAILABLE else "unavailable",
            "voice_agent": "active" if VOICE_AGENT_ROUTES_AVAILABLE else "unavailable"
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
        log_level="info",
        access_log=True,
        # Remove ws parameter - let uvicorn auto-detect
    )
