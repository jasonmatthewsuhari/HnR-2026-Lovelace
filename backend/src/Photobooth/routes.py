"""
FastAPI routes for Photobooth feature

Provides endpoints for:
- Generating photobooth backgrounds with avatar
- Regenerating specific backgrounds
- Compositing user photos with backgrounds
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from pathlib import Path
import os
import base64
import tempfile
import time
from typing import List
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    # Use full path for robust importing regardless of working directory
    from src.Photobooth.photobooth import (
        generate_photobooth_backgrounds,
        create_composite_photo,
        remove_background
    )
    import cv2
    import numpy as np
    PHOTOBOOTH_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Photobooth module imports failed: {e}")
    # Try alternative relative import if above fails
    try:
        from .photobooth import generate_photobooth_backgrounds, create_composite_photo, remove_background
        import cv2
        import numpy as np
        PHOTOBOOTH_AVAILABLE = True
    except ImportError as e2:
        print(f"Error: Fallback import also failed: {e2}")
        PHOTOBOOTH_AVAILABLE = False

router = APIRouter(prefix="/api/photobooth", tags=["Photobooth"])


@router.post("/generate-background")
async def generate_single_background(
    description: str = Form(..., description="User's description of the background scene"),
    pose: str = Form("", description="User's description of the avatar's pose"),
    avatar: UploadFile = File(..., description="Avatar image file")
):
    """
    Generate a single photobooth background with avatar based on user description and pose
    
    Args:
        description: User's description of the background scene
        avatar: Avatar image file
        
    Returns:
        Background image URL
    """
    try:
        print(f"[DEBUG] Received request - description: {description}, avatar: {avatar.filename}")
        
        # Save uploaded avatar temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_avatar:
            content = await avatar.read()
            temp_avatar.write(content)
            avatar_path = temp_avatar.name
        
        from PIL import Image
        import hashlib
        import google.genai as genai
        import base64
        
        output_dir = Path(__file__).parent / "temp_backgrounds"
        output_dir.mkdir(exist_ok=True)
        
        # Create a unique ID for this background
        bg_id = hashlib.md5(f"{description}{time.time()}".encode()).hexdigest()[:8]
        
        # Load API key
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY not set")
        
        print(f"[*] Generating AI photobooth background...")
        
        # Initialize Gemini client
        client = genai.Client(api_key=api_key)
        
        # Load and encode avatar image
        avatar_img = Image.open(avatar_path)
        
        # Convert avatar to base64
        from io import BytesIO
        buffer = BytesIO()
        avatar_img.save(buffer, format='PNG')
        avatar_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        avatar_mime = 'image/png'
        
        # Create prompt for photobooth background
        pose_prompt = f"The avatar should be {pose}." if pose else "The avatar should be naturally integrated into the scene, posing for a photo."
        
        prompt = f"""Create a romantic photobooth background scene: {description}

Requirements:
- The person from the provided image (the avatar) should be naturally integrated into the scene.
- {pose_prompt}
- IMPORTANT: The avatar person MUST be positioned on the LEFT side of the composition.
- IMPORTANT: Leave the RIGHT side of the scene empty/open for another person to be added later.
- Create a couple's photobooth aesthetic - romantic, cute, fun.
- The scene should look like a real high-end photobooth background with professional lighting.
- Resolution: 1280x720 pixels (landscape).
- High quality, photorealistic style.
- The avatar should look like they are waiting for their partner to join them in the photo.

Scene description: {description}"""
        
        # Generate image using Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[
                {"parts": [
                    {"inline_data": {"mime_type": avatar_mime, "data": avatar_data}},
                    {"text": prompt}
                ]}
            ]
        )
        
        # Extract result image
        result_image = None
        for part in response.parts:
            if part.inline_data:
                result_image = part.as_image()
                break
        
        if not result_image:
            raise Exception("No image in response from Gemini")
        
        # Convert to PIL Image
        if hasattr(result_image, '_pil_image'):
            bg_img = result_image._pil_image
        else:
            bg_img = result_image
        
        # Save background
        bg_filename = f"{bg_id}_ai_scene.png"
        bg_path = output_dir / bg_filename
        bg_img.save(bg_path)
        
        print(f"[OK] Generated background: {bg_filename}")
        
        # Cleanup
        os.unlink(avatar_path)
        
        return {
            "success": True,
            "background": {
                "id": bg_id,
                "name": description,
                "url": f"/api/photobooth/backgrounds/{bg_filename}"
            }
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate background: {str(e)}")


@router.post("/regenerate-background/{background_index}")
async def regenerate_background(background_index: int, avatar: UploadFile = File(...)):
    """
    Regenerate a specific background
    
    Args:
        background_index: Index of background to regenerate (0-2)
        avatar: Avatar image file
        
    Returns:
        New background image URL
    """
    if not PHOTOBOOTH_AVAILABLE:
        raise HTTPException(status_code=503, detail="Photobooth module not available")
    
    if background_index < 0 or background_index > 2:
        raise HTTPException(status_code=400, detail="Invalid background index")
    
    # Get API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
    
    try:
        # Similar to generate_backgrounds but for one background
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_avatar:
            content = await avatar.read()
            temp_avatar.write(content)
            avatar_path = temp_avatar.name
        
        from PIL import Image
        
        output_dir = Path(__file__).parent / "temp_backgrounds"
        output_dir.mkdir(exist_ok=True)
        
        avatar_img = Image.open(avatar_path)
        
        bg_colors = [
            ((255, 192, 203), "romantic_cafe"),
            ((255, 223, 186), "sunset_beach"),
            ((200, 220, 255), "cozy_home")
        ]
        
        color, name = bg_colors[background_index]
        
        # Create new background
        bg = Image.new('RGB', (1280, 720), color)
        avatar_resized = avatar_img.copy()
        avatar_resized.thumbnail((400, 600))
        
        x_pos = 150
        y_pos = (720 - avatar_resized.height) // 2
        
        if avatar_resized.mode == 'RGBA':
            bg.paste(avatar_resized, (x_pos, y_pos), avatar_resized)
        else:
            bg.paste(avatar_resized, (x_pos, y_pos))
        
        bg_path = output_dir / f"background_{background_index+1}_{name}.png"
        bg.save(bg_path)
        
        os.unlink(avatar_path)
        
        return {
            "success": True,
            "background": {
                "id": str(background_index + 1),
                "name": name.replace("_", " ").title(),
                "url": f"/api/photobooth/backgrounds/{background_index+1}_{name}.png?t={int(time.time() * 1000)}"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to regenerate background: {str(e)}")


@router.get("/backgrounds/{filename}")
async def get_background_image(filename: str):
    """
    Serve generated background images from the temp_backgrounds directory.
    """
    bg_path = Path(__file__).parent / "temp_backgrounds" / filename
    if not bg_path.exists():
        print(f"[ERROR] Background file not found: {bg_path}")
        raise HTTPException(status_code=404, detail="Background not found")
    return FileResponse(bg_path, media_type="image/png")


@router.post("/remove-background")
async def remove_bg(image: UploadFile = File(...)):
    """
    Remove background from user image
    
    Args:
        image: User image with background
        
    Returns:
        Image with transparent background (base64)
    """
    if not PHOTOBOOTH_AVAILABLE:
        raise HTTPException(status_code=503, detail="Photobooth module not available")
    
    try:
        # Read uploaded image
        content = await image.read()
        nparr = np.frombuffer(content, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Remove background
        img_no_bg = remove_background(img, method='auto')
        
        # Encode to PNG with transparency
        _, buffer = cv2.imencode('.png', img_no_bg)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return {
            "success": True,
            "image": f"data:image/png;base64,{img_base64}"
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[ERROR] Background removal failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to remove background: {str(e)}")



@router.post("/composite")
async def create_composite(
    background_url: str = Form(..., description="URL/path to background image"),
    user_image: UploadFile = File(..., description="User photo with background removed")
):
    """
    Create composite photo of user + background
    """
    if not PHOTOBOOTH_AVAILABLE:
        raise HTTPException(status_code=503, detail="Photobooth module not available")
    
    try:
        print(f"\n[DEBUG] COMPOSITE START")
        print(f"[DEBUG] background_url: {background_url}")
        print(f"[DEBUG] user_image filename: {user_image.filename}")
        
        # Read user image
        content = await user_image.read()
        print(f"[DEBUG] Read {len(content)} bytes from user_image")
        
        nparr = np.frombuffer(content, np.uint8)
        user_img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
        
        if user_img is None:
            print("[ERROR] Failed to decode user image")
            raise HTTPException(status_code=400, detail="Failed to decode user image")
        
        print(f"[DEBUG] User image shape: {user_img.shape}")
        
        # Get background file - handle various URL formats
        # Check if it has query params first
        clean_url = background_url.split('?')[0]
        # Then get the last part
        filename = clean_url.split('/')[-1]
        
        print(f"[DEBUG] Raw URL: {background_url}")
        print(f"[DEBUG] Extracted filename: {filename}")
        
        output_dir = Path(__file__).parent / "temp_backgrounds"
        bg_path = output_dir / filename
        
        # Fallback: if filename doesn't exist, try to find a match in the directory
        if not bg_path.exists():
            print(f"[DEBUG] Exact path not found, searching in {output_dir}")
            for existing_file in output_dir.glob("*"):
                if existing_file.name in filename or filename in existing_file.name:
                    bg_path = existing_file
                    print(f"[DEBUG] Found potential match: {bg_path.name}")
                    break
        
        print(f"[DEBUG] Using background path: {bg_path}")
        
        if not bg_path.exists():
            print(f"[ERROR] Background file not found: {bg_path}")
            raise HTTPException(status_code=404, detail=f"Background not found: {filename}")
        
        # Create composite
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_output:
            output_path = temp_output.name
        
        print(f"[DEBUG] Using temp output: {output_path}")
        
        try:
            result_path = create_composite_photo(
                background_path=str(bg_path),
                user_photo=user_img,
                output_path=output_path,
                user_position='right',
                verbose=True
            )
            
            print(f"[DEBUG] create_composite_photo returned: {result_path}")
            
            # Read and encode result
            if os.path.exists(result_path):
                with open(result_path, 'rb') as f:
                    img_data = f.read()
                    print(f"[DEBUG] Read {len(img_data)} bytes from result")
                    img_base64 = base64.b64encode(img_data).decode('utf-8')
                
                # Cleanup
                os.unlink(result_path)
                print(f"[DEBUG] COMPOSITE SUCCESS")
                
                return {
                    "success": True,
                    "image": f"data:image/png;base64,{img_base64}"
                }
            else:
                print(f"[ERROR] Result path does not exist: {result_path}")
                raise Exception("Composite creation failed to produce a file")
                
        except Exception as e:
            print(f"[ERROR] Inner composite failure: {str(e)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Inner composite failed: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Outer composite failure: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Composite failed: {str(e)}")


@router.get("/saved-backgrounds")
async def list_saved_backgrounds():
    """
    List all generated backgrounds in the temp directory
    """
    output_dir = Path(__file__).parent / "temp_backgrounds"
    if not output_dir.exists():
        return {"success": True, "backgrounds": []}
    
    backgrounds = []
    # Sort files by modification time (newest first)
    files = sorted(output_dir.glob("*.png"), key=os.path.getmtime, reverse=True)
    
    for bg_file in files:
        backgrounds.append({
            "id": bg_file.stem,
            "url": f"/api/photobooth/backgrounds/{bg_file.name}",
            "name": bg_file.stem.replace("_", " ").title()
        })
    
    return {"success": True, "backgrounds": backgrounds}


@router.get("/avatar")
async def get_photobooth_avatar():
    """
    Serve the default avatar image for the photobooth.
    """
    avatar_path = Path(__file__).parent / "avatar.jpg"
    if not avatar_path.exists():
        # Check if it was renamed to something else
        for ext in ['.png', '.jpeg', '.webp']:
            alt_path = avatar_path.with_suffix(ext)
            if alt_path.exists():
                return FileResponse(alt_path)
        raise HTTPException(status_code=404, detail="Avatar not found")
    return FileResponse(avatar_path, media_type="image/jpeg")

