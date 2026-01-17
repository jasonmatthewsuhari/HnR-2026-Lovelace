"""
Simple demo script to test individual photobooth functions.

Run this to test each feature separately without full session.
"""

import os
import sys
from pathlib import Path

# Load environment variables from .env file in repository root
try:
    from dotenv import load_dotenv
    # Navigate to repository root (4 levels up from this file)
    root_dir = Path(__file__).parent.parent.parent.parent
    env_path = root_dir / '.env'
    
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv()  # Try to find .env in parent directories
except ImportError:
    pass

from photobooth import (
    capture_webcam_photo,
    remove_background,
    generate_photobooth_backgrounds
)


def demo_webcam_capture():
    """Demo: Capture a photo with countdown"""
    print("\n" + "="*70)
    print("DEMO 1: Webcam Capture with Countdown")
    print("="*70)
    print("\nThis will open your webcam.")
    print("Press SPACE to start 3-second countdown")
    print("Press ESC to cancel\n")
    
    input("Press Enter to start demo...")
    
    photo = capture_webcam_photo(
        background_removal=False,  # Don't remove background yet
        countdown_seconds=3,
        verbose=True
    )
    
    if photo is not None:
        import cv2
        output_path = Path(__file__).parent / "demo_capture.png"
        cv2.imwrite(str(output_path), photo)
        print(f"\n✅ Demo photo saved: {output_path.name}")
    else:
        print("\n❌ Demo cancelled")


def demo_background_removal():
    """Demo: Remove background from an image"""
    print("\n" + "="*70)
    print("DEMO 2: Background Removal")
    print("="*70)
    
    import cv2
    
    # Check if demo capture exists
    demo_img = Path(__file__).parent / "demo_capture.png"
    
    if not demo_img.exists():
        # Use avatar instead
        demo_img = Path(__file__).parent / "avatar.jpg"
        if not demo_img.exists():
            print("\n❌ No test image found")
            print("   Run Demo 1 first or add avatar.jpg")
            return
    
    print(f"\nRemoving background from: {demo_img.name}")
    
    # Load image
    image = cv2.imread(str(demo_img))
    
    # Remove background
    print("Processing... (this may take a few seconds)")
    result = remove_background(image, method='auto')
    
    # Save result
    output_path = Path(__file__).parent / "demo_no_bg.png"
    cv2.imwrite(str(output_path), result)
    
    print(f"✅ Result saved: {output_path.name}")


def demo_background_generation():
    """Demo: Generate photobooth backgrounds"""
    print("\n" + "="*70)
    print("DEMO 3: Background Generation")
    print("="*70)
    
    avatar_path = Path(__file__).parent / "avatar.jpg"
    
    if not avatar_path.exists():
        print("\n❌ avatar.jpg not found")
        print(f"   Place it in: {Path(__file__).parent}")
        return
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("\n❌ GEMINI_API_KEY not set")
        return
    
    print("\nGenerating 1 background for demo...")
    print("This will take ~10-30 seconds\n")
    
    backgrounds = generate_photobooth_backgrounds(
        avatar_path=str(avatar_path),
        api_key=api_key,
        num_backgrounds=1,
        verbose=True
    )
    
    print(f"\n✅ Generated {len(backgrounds)} background(s)")


def demo_full_workflow():
    """Demo: Complete workflow - capture, remove bg, composite"""
    print("\n" + "="*70)
    print("DEMO 4: Full Workflow")
    print("="*70)
    print("\nThis demos the complete photobooth workflow:")
    print("  1. Capture photo with countdown")
    print("  2. Remove background")
    print("  3. (Would composite with avatar background)")
    print()
    
    input("Press Enter to start...")
    
    # Capture
    print("\n[1/2] Capturing photo...")
    photo = capture_webcam_photo(
        background_removal=True,  # Remove bg immediately
        countdown_seconds=3,
        verbose=True
    )
    
    if photo is None:
        print("\n❌ Demo cancelled")
        return
    
    # Save result
    print("\n[2/2] Saving result...")
    import cv2
    output_path = Path(__file__).parent / "demo_workflow_result.png"
    cv2.imwrite(str(output_path), photo)
    
    print(f"\n✅ Workflow complete!")
    print(f"   Result: {output_path.name}")
    print("\nIn the full photobooth, this would be composited")
    print("with a background containing your avatar.")


def main():
    """Main demo menu"""
    print("="*70)
    print("🎀 Photobooth - Interactive Demo")
    print("="*70)
    
    while True:
        print("\n" + "="*70)
        print("Select a demo:")
        print("="*70)
        print("  1. Webcam Capture with Countdown")
        print("  2. Background Removal")
        print("  3. Background Generation (requires API key)")
        print("  4. Full Workflow")
        print("  0. Exit")
        print()
        
        choice = input("Enter choice (0-4): ").strip()
        
        if choice == '0':
            print("\n👋 Goodbye!")
            break
        elif choice == '1':
            demo_webcam_capture()
        elif choice == '2':
            demo_background_removal()
        elif choice == '3':
            demo_background_generation()
        elif choice == '4':
            demo_full_workflow()
        else:
            print("\n❌ Invalid choice. Please enter 0-4.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
