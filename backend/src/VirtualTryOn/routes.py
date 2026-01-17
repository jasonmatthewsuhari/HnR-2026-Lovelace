"""
FastAPI routes for Virtual Try-On feature in Lovelace

Provides endpoints for:
- Virtual try-on processing
- Image upload and processing
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional
import base64
import os
from pathlib import Path
import tempfile
from PIL import Image
import io

from .virtual_try_on import apply_virtual_tryon

# Initialize router
router = APIRouter(prefix="/api/virtual-tryon", tags=["Virtual Try-On"])


@router.post("")
async def process_virtual_tryon(
    person_image: UploadFile = File(..., description="Person image file"),
    clothing_image: UploadFile = File(..., description="Clothing image file"),
):
    """
    Process virtual try-on with person and clothing images
    
    Args:
        person_image: Image of the person
        clothing_image: Image of the clothing item
        
    Returns:
        JSON with base64 encoded result image
    """
    try:
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Save uploaded images
            person_path = temp_path / f"person_{person_image.filename}"
            clothing_path = temp_path / f"clothing_{clothing_image.filename}"
            
            # Read and save person image
            person_content = await person_image.read()
            with open(person_path, "wb") as f:
                f.write(person_content)
            
            # Read and save clothing image
            clothing_content = await clothing_image.read()
            with open(clothing_path, "wb") as f:
                f.write(clothing_content)
            
            # Process virtual try-on
            result_image, _ = apply_virtual_tryon(
                person_path=str(person_path),
                clothing_path=str(clothing_path),
                api_key=os.getenv('GEMINI_API_KEY'),
                output_path=None,  # Don't save to disk
                verbose=False
            )
            
            # Convert PIL Image to base64
            buffered = io.BytesIO()
            result_image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            return {
                "success": True,
                "image": f"data:image/png;base64,{img_base64}",
                "message": "Virtual try-on completed successfully"
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Virtual try-on failed: {str(e)}"
        )


@router.post("/base64")
async def process_virtual_tryon_base64(
    person_image_base64: str = Form(..., description="Base64 encoded person image"),
    clothing_image_base64: str = Form(..., description="Base64 encoded clothing image"),
):
    """
    Process virtual try-on with base64 encoded images
    
    Args:
        person_image_base64: Base64 encoded person image
        clothing_image_base64: Base64 encoded clothing image
        
    Returns:
        JSON with base64 encoded result image
    """
    try:
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Decode base64 images
            person_path = temp_path / "person.png"
            clothing_path = temp_path / "clothing.png"
            
            # Remove data URL prefix if present
            if "base64," in person_image_base64:
                person_image_base64 = person_image_base64.split("base64,")[1]
            if "base64," in clothing_image_base64:
                clothing_image_base64 = clothing_image_base64.split("base64,")[1]
            
            # Decode and save person image
            person_data = base64.b64decode(person_image_base64)
            person_img = Image.open(io.BytesIO(person_data))
            person_img.save(person_path)
            
            # Decode and save clothing image
            clothing_data = base64.b64decode(clothing_image_base64)
            clothing_img = Image.open(io.BytesIO(clothing_data))
            clothing_img.save(clothing_path)
            
            # Process virtual try-on
            result_image, _ = apply_virtual_tryon(
                person_path=str(person_path),
                clothing_path=str(clothing_path),
                api_key=os.getenv('GEMINI_API_KEY'),
                output_path=None,
                verbose=False
            )
            
            # Convert PIL Image to base64
            buffered = io.BytesIO()
            result_image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            return {
                "success": True,
                "image": f"data:image/png;base64,{img_base64}",
                "message": "Virtual try-on completed successfully"
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Virtual try-on failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    api_key = os.getenv('GEMINI_API_KEY')
    return {
        "status": "healthy",
        "service": "Virtual Try-On",
        "api_key_configured": bool(api_key)
    }
