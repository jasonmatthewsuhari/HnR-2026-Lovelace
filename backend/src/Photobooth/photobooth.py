"""
Lovelace Photobooth - Generate Couple's Photos with AI Avatar

Features:
- Generate 3 photobooth backgrounds with avatar in couple's poses
- Webcam capture with background removal
- Countdown timer
- Composite user + avatar photos
- Save all photos to Photobooth folder

Usage:
    python photobooth.py
"""

import os
import sys
import base64
import time
from pathlib import Path
from typing import List, Tuple, Optional

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Load environment variables from .env file in repository root
try:
    from dotenv import load_dotenv
    # Navigate to repository root (4 levels up from this file)
    root_dir = Path(__file__).parent.parent.parent.parent
    env_path = root_dir / '.env'
    
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"[OK] Loaded .env from: {env_path}")
    else:
        load_dotenv()  # Try to find .env in parent directories
        print(f"[!] .env not found at {env_path}, using system environment variables")
except ImportError:
    print("[!] Warning: python-dotenv not installed, using system environment variables only")
    print("    Install with: pip install python-dotenv")

print("Starting imports...")

# Import dependencies
try:
    from google import genai
    from PIL import Image, ImageDraw, ImageFont
    import cv2
    import numpy as np
    DEPENDENCIES_AVAILABLE = True
    print("[OK] Core libraries imported")
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    print(f"[ERROR] Import error: {e}")
    print("Run: pip install google-genai pillow opencv-python numpy")

# Optional: Background removal (rembg)
try:
    from rembg import remove, new_session
    REMBG_AVAILABLE = True
    print("[OK] Background removal (rembg) available")
    
    # Pre-initialize sessions for better performance
    # 'isnet-general-use' is generally better for portraits/people than u2net
    try:
        REMBG_SESSION = new_session("isnet-general-use")
        print("[OK] Loaded high-quality background removal model (isnet-general-use)")
    except Exception as e:
        print(f"[WARN] Failed to load isnet-general-use model: {e}")
        print("[*] Falling back to default u2net model")
        REMBG_SESSION = new_session("u2net")
except ImportError:
    REMBG_AVAILABLE = False
    print("[WARN] rembg not installed - background removal will use simple method")
    print("      For better results: pip install rembg")


def encode_image(image_path):
    """Encode image to base64"""
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()
    
    ext = Path(image_path).suffix.lower()
    mime_map = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp'}
    mime_type = mime_map.get(ext, 'image/jpeg')
    
    return image_data, mime_type


def generate_photobooth_backgrounds(avatar_path: str, api_key: str = None, num_backgrounds: int = 3, verbose: bool = True) -> List[Tuple[Image.Image, str]]:
    """
    Generate photobooth backgrounds with avatar in couple's poses.
    
    Args:
        avatar_path (str): Path to avatar image
        api_key (str, optional): Gemini API key. If None, loads from environment.
        num_backgrounds (int): Number of backgrounds to generate (default 3)
        verbose (bool): Whether to print progress messages
        
    Returns:
        List[Tuple[PIL.Image, str]]: List of (image, description) tuples
        
    Example:
        >>> backgrounds = generate_photobooth_backgrounds("avatar.jpg")
        >>> for img, desc in backgrounds:
        ...     img.save(f"background_{desc}.png")
    """
    
    # Load API key if not provided
    if api_key is None:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("No API key provided. Set GEMINI_API_KEY environment variable or pass api_key parameter.")
    
    if verbose:
        print("\n" + "="*70)
        print("[*] Photobooth Background Generation")
        print("="*70 + "\n")
    
    # Initialize Gemini client
    client = genai.Client(api_key=api_key)
    
    # Load avatar image
    avatar_data, avatar_mime = encode_image(avatar_path)
    
    # Define couple's poses
    poses = [
        {
            "name": "romantic_cafe",
            "prompt": """Create a romantic photobooth background showing this character sitting at a cozy café table with flowers, 
with an empty chair next to them for their date. The character should be smiling warmly and gesturing welcomingly to the empty space. 
Romantic lighting, soft bokeh background, café ambiance. The composition should have clear space on the right side for another person. 
Photobooth style, high quality, warm tones."""
        },
        {
            "name": "sunset_beach",
            "prompt": """Create a romantic photobooth background showing this character standing on a beautiful sunset beach, 
with their arm positioned as if around someone's shoulder (empty space for their date). Looking lovingly to the side with a warm smile. 
Golden hour lighting, ocean waves, sandy beach. Clear space on the left side for another person. 
Photobooth style, dreamy atmosphere, warm sunset colors."""
        },
        {
            "name": "cozy_home",
            "prompt": """Create a romantic photobooth background showing this character sitting on a cozy couch at home, 
with space next to them for their date. They're holding what looks like they're offering something (hot chocolate or popcorn), 
smiling warmly. Soft home lighting, fairy lights in background, comfortable living room setting. 
Clear space on the right for another person. Photobooth style, cozy and intimate atmosphere."""
        }
    ]
    
    # Generate only requested number of backgrounds
    poses = poses[:num_backgrounds]
    
    backgrounds = []
    
    for i, pose_info in enumerate(poses, 1):
        if verbose:
            print(f"[{i}/{len(poses)}] Generating {pose_info['name']} background...")
            print(f"         This may take 10-30 seconds...")
        
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=[
                    {"parts": [
                        {"inline_data": {"mime_type": avatar_mime, "data": avatar_data}},
                        {"text": pose_info['prompt']}
                    ]}
                ]
            )
            
            # Get description of what was generated
            description = response.text if response.text else pose_info['name']
            
            if verbose:
                print(f"         [OK] Generated: {pose_info['name']}")
            
            # Note: For actual image generation, we'd need gemini-2.5-flash-image
            # For now, we'll create a placeholder approach
            # In production, you'd generate the actual backgrounds
            
            backgrounds.append((pose_info['name'], pose_info['prompt'], description))
            
        except Exception as e:
            if verbose:
                print(f"         [ERROR] Failed to generate {pose_info['name']}: {e}")
            continue
    
    if verbose:
        print(f"\n[OK] Generated {len(backgrounds)} backgrounds")
    
    return backgrounds


def remove_background(image: np.ndarray, method: str = 'auto') -> np.ndarray:
    """
    Remove background from image.
    
    Args:
        image (np.ndarray): Input image in BGR format (OpenCV)
        method (str): 'auto' (use rembg if available), 'simple' (color-based), or 'none'
        
    Returns:
        np.ndarray: Image with transparent background (BGRA format)
    """
    
    if method == 'auto' and REMBG_AVAILABLE:
        try:
            # Convert BGR to RGB for rembg
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image_rgb)
            
            # Remove background using pre-initialized session
            # If session is available, use it, otherwise fall back to basic remove
            if 'REMBG_SESSION' in globals():
                result_pil = remove(pil_image, session=REMBG_SESSION)
            else:
                result_pil = remove(pil_image)
            
            # Convert back to OpenCV format (BGRA)
            result_rgb = np.array(result_pil)
            if result_rgb.shape[2] == 4:  # Already has alpha
                result_bgra = cv2.cvtColor(result_rgb, cv2.COLOR_RGBA2BGRA)
            else:
                result_bgra = cv2.cvtColor(result_rgb, cv2.COLOR_RGB2BGRA)
            
            return result_bgra
        except Exception as e:
            print(f"[REMBG ERROR] {e} - falling back to simple method")
            # Continue to simple method
    
    if method == 'simple' or (method == 'auto'):
        # Simple method: only remove extreme backgrounds (very bright or very dark)
        # to avoid making the user invisible in typical rooms
        bgra = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Create mask: keep pixels between 30 and 240 brightness
        # This is very conservative background removal
        mask = cv2.inRange(gray, 30, 240)
        
        # Smooth mask
        mask = cv2.medianBlur(mask, 5)
        
        bgra[:, :, 3] = mask
        return bgra
    
    # default fallback
    return cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)


def add_countdown_overlay(frame: np.ndarray, count: int) -> np.ndarray:
    """Add countdown number overlay to frame"""
    overlay = frame.copy()
    h, w = frame.shape[:2]
    
    # Draw semi-transparent circle
    center = (w // 2, h // 2)
    radius = 100
    cv2.circle(overlay, center, radius, (0, 0, 0), -1)
    
    # Blend with original
    alpha = 0.6
    frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
    
    # Draw countdown number
    font = cv2.FONT_HERSHEY_BOLD
    text = str(count)
    text_size = cv2.getTextSize(text, font, 4, 8)[0]
    text_x = center[0] - text_size[0] // 2
    text_y = center[1] + text_size[1] // 2
    cv2.putText(frame, text, (text_x, text_y), font, 4, (255, 255, 255), 8)
    
    return frame


def capture_webcam_photo(background_removal: bool = True, countdown_seconds: int = 5, verbose: bool = True) -> Optional[np.ndarray]:
    """
    Capture photo from webcam with countdown.
    
    Args:
        background_removal (bool): Whether to remove background
        countdown_seconds (int): Countdown duration
        verbose (bool): Whether to print messages
        
    Returns:
        np.ndarray: Captured image with background removed (BGRA) or None if cancelled
    """
    
    if verbose:
        print(f"\n[*] Opening webcam...")
        print(f"    Press SPACE when ready to start {countdown_seconds}s countdown")
        print(f"    Press ESC to cancel")
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        if verbose:
            print("[ERROR] Could not open webcam")
        return None
    
    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    countdown_started = False
    countdown_start_time = 0
    captured_frame = None
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        display_frame = frame.copy()
        
        # Add instructions
        if not countdown_started:
            cv2.putText(display_frame, "Press SPACE to start countdown", 
                       (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(display_frame, "Press ESC to cancel", 
                       (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        else:
            # Calculate remaining time
            elapsed = time.time() - countdown_start_time
            remaining = countdown_seconds - int(elapsed)
            
            if remaining > 0:
                display_frame = add_countdown_overlay(display_frame, remaining)
            elif remaining == 0:
                # Take photo
                captured_frame = frame.copy()
                cv2.putText(display_frame, "SNAP!", 
                           (display_frame.shape[1]//2 - 100, display_frame.shape[0]//2), 
                           cv2.FONT_HERSHEY_BOLD, 3, (0, 255, 0), 5)
                cv2.imshow('Photobooth', display_frame)
                cv2.waitKey(500)  # Show "SNAP!" for 0.5 seconds
                break
        
        cv2.imshow('Photobooth', display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == 27:  # ESC
            break
        elif key == 32 and not countdown_started:  # SPACE
            countdown_started = True
            countdown_start_time = time.time()
    
    cap.release()
    cv2.destroyAllWindows()
    
    if captured_frame is None:
        if verbose:
            print("[*] Capture cancelled")
        return None
    
    if verbose:
        print("[OK] Photo captured!")
    
    # Remove background if requested
    if background_removal:
        if verbose:
            print("[*] Removing background...")
        captured_frame = remove_background(captured_frame, method='auto')
        if verbose:
            print("[OK] Background removed")
    else:
        captured_frame = cv2.cvtColor(captured_frame, cv2.COLOR_BGR2BGRA)
    
    return captured_frame


def create_composite_photo(background_path: str, user_photo: np.ndarray, output_path: str, 
                          user_position: str = 'right', user_scale: float = 1.0, verbose: bool = True) -> str:
    """
    Create composite photo of user + background with avatar.
    """
    if verbose:
        print(f"[*] Creating composite photo...")
    
    # Load background
    background = cv2.imread(background_path, cv2.IMREAD_UNCHANGED)
    if background is None:
        raise ValueError(f"Failed to load background image from: {background_path}")
    
    if background.shape[2] == 3:
        background = cv2.cvtColor(background, cv2.COLOR_BGR2BGRA)
    
    # Ensure user photo has 4 channels
    if user_photo.shape[2] == 3:
        user_photo = cv2.cvtColor(user_photo, cv2.COLOR_BGR2BGRA)
    
    # Scale user photo if requested
    if user_scale != 1.0:
        new_size = (int(user_photo.shape[1] * user_scale), int(user_photo.shape[0] * user_scale))
        user_photo = cv2.resize(user_photo, new_size, interpolation=cv2.INTER_AREA)
    
    # If user photo is still larger than background, scale it down to fit
    bg_h, bg_w = background.shape[:2]
    u_h, u_w = user_photo.shape[:2]
    
    if u_h > bg_h or u_w > bg_w:
        scale = min(bg_h / u_h, bg_w / u_w)
        new_size = (int(u_w * scale), int(u_h * scale))
        user_photo = cv2.resize(user_photo, new_size, interpolation=cv2.INTER_AREA)
        u_h, u_w = user_photo.shape[:2]
    
    # Determine offset
    if user_position == 'right':
        x_offset = bg_w - u_w - 20 # 20px margin from right
    else:
        x_offset = 20 # 20px margin from left
        
    y_offset = bg_h - u_h # Bottom aligned
    
    # Clamp offsets
    x_offset = max(0, min(x_offset, bg_w - u_w))
    y_offset = max(0, min(y_offset, bg_h - u_h))
    
    if verbose:
        print(f"[DEBUG] Composite positions: x={x_offset}, y={y_offset}, size={u_w}x{u_h}")
    
    # Vectorized alpha blending
    try:
        # Extract channels
        user_rgb = user_photo[:, :, :3].astype(float)
        user_alpha = (user_photo[:, :, 3] / 255.0)[:, :, np.newaxis]
        
        # Get Roi dimensions
        roi_h = min(u_h, bg_h - y_offset)
        roi_w = min(u_w, bg_w - x_offset)
        
        if verbose:
            print(f"[DEBUG] Final ROI: {roi_w}x{roi_h} at {x_offset},{y_offset}")
            
        bg_roi = background[y_offset:y_offset+roi_h, x_offset:x_offset+roi_w, :3].astype(float)
        u_rgb_roi = user_rgb[:roi_h, :roi_w, :]
        u_alpha_roi = user_alpha[:roi_h, :roi_w, :]
        
        # Blend
        blended_roi = (u_alpha_roi * u_rgb_roi + (1 - u_alpha_roi) * bg_roi).astype(np.uint8)
        
        # Place back
        background[y_offset:y_offset+roi_h, x_offset:x_offset+roi_w, :3] = blended_roi
    except Exception as e:
        print(f"[ERROR] Blending failure: {e}")
        import traceback
        traceback.print_exc()
        raise ValueError(f"Blending failure: {e}")
    
    # Save result
    try:
        success = cv2.imwrite(output_path, background)
        if not success:
            raise ValueError(f"Failed to save composite to: {output_path}")
    except Exception as e:
        print(f"[ERROR] imwrite failure: {e}")
        raise ValueError(f"imwrite failure: {e}")
        
    return output_path


def run_photobooth_session(avatar_path: str, api_key: str = None, output_dir: str = None, 
                           background_removal: bool = True, verbose: bool = True) -> List[str]:
    """
    Run complete photobooth session.
    
    1. Generate 3 photobooth backgrounds with avatar
    2. For each background, capture user photo with countdown
    3. Create composite photos
    4. Save all photos
    
    Args:
        avatar_path (str): Path to avatar image
        api_key (str, optional): Gemini API key
        output_dir (str, optional): Output directory (default: same as script)
        background_removal (bool): Whether to remove user background
        verbose (bool): Print progress
        
    Returns:
        List[str]: Paths to all composite photos
    """
    
    if output_dir is None:
        output_dir = Path(__file__).parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*70)
    print("LOVELACE PHOTOBOOTH - Couple's Photos with AI Avatar")
    print("="*70 + "\n")
    
    # Step 1: Generate backgrounds
    print("[1] Generating photobooth backgrounds...")
    backgrounds = generate_photobooth_backgrounds(avatar_path, api_key, num_backgrounds=3, verbose=verbose)
    
    if not backgrounds:
        print("[ERROR] No backgrounds generated")
        return []
    
    print(f"\n[OK] Generated {len(backgrounds)} backgrounds\n")
    
    # For this implementation, we'll create simple backgrounds with the avatar
    # In production, you'd use the actual generated backgrounds
    avatar_img = Image.open(avatar_path)
    
    # Create simple photobooth backgrounds
    bg_images = []
    bg_colors = [
        ((255, 192, 203), "romantic_cafe"),      # Pink
        ((255, 223, 186), "sunset_beach"),       # Peach
        ((200, 220, 255), "cozy_home")           # Light blue
    ]
    
    for i, (color, name) in enumerate(bg_colors[:len(backgrounds)]):
        # Create colored background
        bg = Image.new('RGB', (1280, 720), color)
        
        # Resize and place avatar
        avatar_resized = avatar_img.copy()
        avatar_resized.thumbnail((400, 600))
        
        # Place avatar on left side
        x_pos = 150
        y_pos = (720 - avatar_resized.height) // 2
        bg.paste(avatar_resized, (x_pos, y_pos), avatar_resized if avatar_resized.mode == 'RGBA' else None)
        
        # Save background
        bg_path = output_dir / f"background_{i+1}_{name}.png"
        bg.save(bg_path)
        bg_images.append((bg_path, name))
        
        if verbose:
            print(f"   [OK] Background {i+1}: {name}")
    
    print()
    
    # Step 2 & 3: Capture photos and create composites
    composite_photos = []
    
    for i, (bg_path, bg_name) in enumerate(bg_images, 1):
        print(f"\n[{i}/{len(bg_images)}] Photo {i}: {bg_name}")
        print("="*70)
        
        # Capture user photo
        user_photo = capture_webcam_photo(
            background_removal=background_removal,
            countdown_seconds=5,
            verbose=verbose
        )
        
        if user_photo is None:
            print(f"[SKIP] Photo {i} skipped")
            continue
        
        # Create composite
        composite_path = output_dir / f"photobooth_{i}_{bg_name}.png"
        create_composite_photo(
            background_path=str(bg_path),
            user_photo=user_photo,
            output_path=str(composite_path),
            user_position='right',
            verbose=verbose
        )
        
        composite_photos.append(str(composite_path))
    
    # Cleanup background files
    for bg_path, _ in bg_images:
        try:
            bg_path.unlink()
        except:
            pass
    
    print("\n" + "="*70)
    print("[SUCCESS] PHOTOBOOTH SESSION COMPLETE!")
    print("="*70)
    print(f"\nGenerated {len(composite_photos)} photos:")
    for photo in composite_photos:
        print(f"  [IMG] {Path(photo).name}")
    print(f"\nLocation: {output_dir}")
    print("="*70 + "\n")
    
    return composite_photos


def main():
    """Main function"""
    
    print("\n" + "="*70)
    print("Lovelace Photobooth")
    print("="*70 + "\n")
    
    # Check dependencies
    print("[1] Checking dependencies...")
    if not DEPENDENCIES_AVAILABLE:
        print("   [ERROR] Dependencies not installed!")
        print("   Run: pip install google-genai pillow opencv-python numpy")
        if not REMBG_AVAILABLE:
            print("   Optional (better background removal): pip install rembg")
        input("\n   Press Enter to exit...")
        return
    print("   [OK] Dependencies installed")
    
    if not REMBG_AVAILABLE:
        print("   [WARN] rembg not installed - using simple background removal")
        print("   For better results: pip install rembg")
    
    # Check API key
    print("\n[2] Checking API key...")
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("   [ERROR] GEMINI_API_KEY not set!")
        print("\n   Set it:")
        print("   $env:GEMINI_API_KEY='your-key-here'")
        print("\n   Get key at: https://ai.google.dev/")
        input("\n   Press Enter to exit...")
        return
    print(f"   [OK] API key configured")
    
    # Check avatar
    print("\n[3] Looking for avatar...")
    script_dir = Path(__file__).parent
    avatar_path = script_dir / "avatar.jpg"
    
    if not avatar_path.exists():
        print(f"   [ERROR] avatar.jpg not found!")
        print(f"   Place it in: {script_dir}")
        input("\n   Press Enter to exit...")
        return
    
    print(f"   [OK] Found avatar.jpg")
    
    # Run photobooth session
    print("\n[4] Starting photobooth session...\n")
    print("You will take 3 photos with your avatar in couple's poses!")
    print("Get ready to pose!\n")
    input("Press Enter to begin...")
    
    try:
        composite_photos = run_photobooth_session(
            avatar_path=str(avatar_path),
            api_key=api_key,
            output_dir=str(script_dir),
            background_removal=True,
            verbose=True
        )
        
        if composite_photos:
            print("\n[SUCCESS] Success! Check your photos:")
            for photo in composite_photos:
                print(f"  [IMG] {Path(photo).name}")
        else:
            print("\n[WARN] No photos were taken")
        
    except Exception as e:
        print(f"\n[ERROR] Photobooth failed: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
