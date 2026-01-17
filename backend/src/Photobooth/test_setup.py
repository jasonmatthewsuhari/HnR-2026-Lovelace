"""
Quick test script for Photobooth setup verification.

Checks:
- Dependencies installed
- API key configured
- Avatar image present
- Webcam accessible
"""

import os
import sys
from pathlib import Path

def test_dependencies():
    """Test if all dependencies are installed"""
    print("[1] Checking dependencies...")
    
    missing = []
    
    try:
        import google.genai
        print("   ✓ google-genai")
    except ImportError:
        print("   ✗ google-genai")
        missing.append("google-genai")
    
    try:
        from PIL import Image
        print("   ✓ pillow")
    except ImportError:
        print("   ✗ pillow")
        missing.append("pillow")
    
    try:
        import cv2
        print("   ✓ opencv-python")
    except ImportError:
        print("   ✗ opencv-python")
        missing.append("opencv-python")
    
    try:
        import numpy
        print("   ✓ numpy")
    except ImportError:
        print("   ✗ numpy")
        missing.append("numpy")
    
    # Optional dependency
    try:
        import rembg
        print("   ✓ rembg (optional - AI background removal)")
    except ImportError:
        print("   ⚠ rembg (optional - for better background removal)")
        print("     Install with: pip install rembg")
    
    if missing:
        print(f"\n   ❌ Missing dependencies: {', '.join(missing)}")
        print(f"   Install with: pip install {' '.join(missing)}")
        return False
    
    print("   ✅ All core dependencies installed!")
    return True


def test_api_key():
    """Test if API key is configured"""
    print("\n[2] Checking API key...")
    
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("   ❌ GEMINI_API_KEY not set")
        print("\n   Set it with:")
        print("   PowerShell: $env:GEMINI_API_KEY='your-key-here'")
        print("   Bash: export GEMINI_API_KEY='your-key-here'")
        print("\n   Get your key at: https://ai.google.dev/")
        return False
    
    print(f"   ✅ API key configured ({api_key[:8]}...)")
    return True


def test_avatar():
    """Test if avatar image exists"""
    print("\n[3] Checking avatar image...")
    
    script_dir = Path(__file__).parent
    avatar_path = script_dir / "avatar.jpg"
    
    if not avatar_path.exists():
        print(f"   ❌ avatar.jpg not found")
        print(f"   Place it in: {script_dir}")
        return False
    
    print(f"   ✅ avatar.jpg found")
    
    # Check if it's a valid image
    try:
        from PIL import Image
        img = Image.open(avatar_path)
        print(f"   ✅ Valid image ({img.size[0]}x{img.size[1]})")
    except Exception as e:
        print(f"   ⚠ Warning: Could not open image: {e}")
    
    return True


def test_webcam():
    """Test if webcam is accessible"""
    print("\n[4] Checking webcam...")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("   ❌ Could not open webcam")
            print("   Make sure:")
            print("     - Webcam is connected")
            print("     - No other app is using it")
            print("     - Camera permissions granted")
            return False
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            print("   ❌ Could not read from webcam")
            return False
        
        print(f"   ✅ Webcam accessible ({frame.shape[1]}x{frame.shape[0]})")
        return True
        
    except Exception as e:
        print(f"   ❌ Webcam test failed: {e}")
        return False


def test_output_dir():
    """Test if output directory is writable"""
    print("\n[5] Checking output directory...")
    
    script_dir = Path(__file__).parent
    test_file = script_dir / ".test_write"
    
    try:
        test_file.write_text("test")
        test_file.unlink()
        print(f"   ✅ Output directory writable")
        print(f"   📁 {script_dir}")
        return True
    except Exception as e:
        print(f"   ❌ Cannot write to output directory: {e}")
        return False


def main():
    """Run all tests"""
    print("="*70)
    print("🎀 Photobooth Setup Verification")
    print("="*70)
    print()
    
    results = {
        "Dependencies": test_dependencies(),
        "API Key": test_api_key(),
        "Avatar": test_avatar(),
        "Webcam": test_webcam(),
        "Output Dir": test_output_dir()
    }
    
    print("\n" + "="*70)
    print("📋 Test Results")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    all_passed = all(results.values())
    
    print()
    
    if all_passed:
        print("="*70)
        print("✨ All tests passed! You're ready to use Photobooth!")
        print("="*70)
        print("\nRun: python photobooth.py")
    else:
        print("="*70)
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("="*70)
    
    print()
    input("Press Enter to exit...")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
