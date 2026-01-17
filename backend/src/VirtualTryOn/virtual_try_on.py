"""
Lovelace Virtual Try-On Demo

Uses Google's Nano Banana API to apply clothing onto a person.
Place person.jpg and clothing.jpg in the LiveVideoCall folder.
"""

import os
import sys
import base64
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Find the root directory (where .env is located)
    root_dir = Path(__file__).parent.parent.parent.parent
    env_path = root_dir / '.env'
    load_dotenv(dotenv_path=env_path)
    print(f"Loading .env from: {env_path}")
except ImportError:
    print("Warning: python-dotenv not installed, using system environment variables only")

print("Starting imports...")

try:
    from google import genai
    from PIL import Image
    GENAI_AVAILABLE = True
    print("[OK] Libraries imported successfully")
except ImportError as e:
    GENAI_AVAILABLE = False
    print(f"[ERROR] Import error: {e}")
    print("Run: pip install google-genai pillow")


def encode_image(image_path):
    """Encode image to base64"""
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()
    
    ext = Path(image_path).suffix.lower()
    mime_map = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp'}
    mime_type = mime_map.get(ext, 'image/jpeg')
    
    return image_data, mime_type


def analyze_clothing(client, clothing_path):
    """Analyze clothing image"""
    print("[*] Analyzing clothing...")
    
    try:
        clothing_data, mime_type = encode_image(clothing_path)
        
        prompt = """Analyze this clothing item briefly: type, color, style, material."""
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=[
                {"parts": [
                    {"inline_data": {"mime_type": mime_type, "data": clothing_data}},
                    {"text": prompt}
                ]}
            ]
        )
        
        description = response.text
        print(f"[OK] Analysis: {description[:100]}...")
        return {'description': description, 'image_path': clothing_path}
    
    except Exception as e:
        print(f"[WARN] Analysis failed: {e}")
        return {'description': "clothing item from image", 'image_path': clothing_path}


def apply_virtual_tryon(person_path, clothing_path, api_key=None, output_path=None, verbose=True):
    """
    Apply virtual try-on to a person image with clothing.
    
    Args:
        person_path (str): Path to person image
        clothing_path (str): Path to clothing image
        api_key (str, optional): Gemini API key. If None, loads from environment.
        output_path (str, optional): Path to save result. If None, saves in VirtualTryOn folder.
        verbose (bool): Whether to print progress messages
        
    Returns:
        tuple: (PIL.Image, str) - The result image object and the saved file path
        
    Example:
        >>> from virtual_try_on import apply_virtual_tryon
        >>> result_image, result_path = apply_virtual_tryon("person.jpg", "clothing.jpg")
        >>> print(f"Saved to: {result_path}")
    """
    
    # Load API key if not provided
    if api_key is None:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("No API key provided. Set GEMINI_API_KEY environment variable or pass api_key parameter.")
    
    if verbose:
        print("\n" + "="*70)
        print("[*] Virtual Try-On Process")
        print("="*70 + "\n")
    
    # Initialize
    if verbose:
        print("[*] Connecting to Gemini API...")
    client = genai.Client(api_key=api_key)
    
    # Analyze clothing
    if verbose:
        print("[*] Analyzing clothing...")
    clothing_info = analyze_clothing(client, clothing_path) if verbose else {
        'description': 'clothing item from image',
        'image_path': clothing_path
    }
    
    # Load images
    if verbose:
        print("[*] Loading person image...")
    person_data, person_mime = encode_image(person_path)
    
    if verbose:
        print("[*] Loading clothing image...")
    clothing_data, clothing_mime = encode_image(clothing_path)
    
    # Create prompt
    prompt = f"""Perform virtual try-on: Apply the clothing from the second image onto the person in the first image.

Clothing: {clothing_info['description']}

Requirements:
- Keep person's pose, face, body EXACTLY the same
- Keep background unchanged
- Make clothing fit naturally
- Match lighting and shadows
- Photorealistic quality
- Only change the clothing

Result should look like the person naturally wearing the clothing."""
    
    if verbose:
        print("[*] Generating virtual try-on (this takes 10-30 seconds)...")
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[
                {"parts": [
                    {"inline_data": {"mime_type": person_mime, "data": person_data}},
                    {"inline_data": {"mime_type": clothing_mime, "data": clothing_data}},
                    {"text": prompt}
                ]}
            ]
        )
        
        # Extract result
        result_image = None
        for part in response.parts:
            if part.inline_data:
                result_image = part.as_image()
                break
        
        if not result_image:
            raise Exception("No image in response")
        
        # Convert to PIL Image for consistency
        if hasattr(result_image, '_pil_image'):
            pil_image = result_image._pil_image
        else:
            pil_image = result_image
        
        # Determine output path
        if output_path is None:
            output_path = Path(__file__).parent / "virtual_tryon_result.png"
        else:
            output_path = Path(output_path)
        
        # Save the image
        pil_image.save(str(output_path))
        
        if verbose:
            print(f"\n[OK] Success!")
            print(f"[OK] Saved to: {output_path.name}")
            print(f"[OK] Full path: {output_path.absolute()}")
        
        return pil_image, str(output_path)
        
    except Exception as e:
        if verbose:
            print(f"\n[ERROR] Error: {e}")
        raise


def main():
    """Main function"""
    
    print("\n" + "="*70)
    print("Lovelace Virtual Try-On Demo")
    print("="*70 + "\n")
    
    # Check dependencies
    print("[1] Checking dependencies...")
    if not GENAI_AVAILABLE:
        print("   [ERROR] Libraries not installed!")
        print("   Run: pip install google-genai pillow")
        input("\n   Press Enter to exit...")
        return
    print("   [OK]")
    
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
    print(f"   [OK] ({api_key[:8]}...)")
    
    # Find images
    print("\n[3] Looking for images...")
    script_dir = Path(__file__).parent
    
    person_path = script_dir / "person.jpg"
    clothing_path = script_dir / "clothing.jpg"
    
    print(f"   Location: {script_dir}")
    
    if not person_path.exists():
        print(f"   [ERROR] person.jpg not found!")
        print(f"   Place it in: {script_dir}")
        input("\n   Press Enter to exit...")
        return
    
    if not clothing_path.exists():
        print(f"   [ERROR] clothing.jpg not found!")
        print(f"   Place it in: {script_dir}")
        input("\n   Press Enter to exit...")
        return
    
    print(f"   [OK] Found person.jpg")
    print(f"   [OK] Found clothing.jpg")
    
    # Run try-on
    try:
        print("\n[4] Starting virtual try-on...\n")
        
        result_image, result_path = apply_virtual_tryon(
            person_path=str(person_path),
            clothing_path=str(clothing_path),
            api_key=api_key,
            verbose=True
        )
        
        print("\n" + "="*70)
        print("[SUCCESS] Complete!")
        print("="*70)
        print(f"\nResult: {Path(result_path).name}")
        print(f"Location: {script_dir}")
        
        # Try to open
        try:
            print("\n[*] Opening image...")
            result_image.show()
        except Exception as e:
            print(f"\n[WARN] Could not open: {e}")
        
        input("\nPress Enter to exit...")
        
    except Exception as e:
        print(f"\n[ERROR] Failed: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
