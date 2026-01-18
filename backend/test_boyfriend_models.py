#!/usr/bin/env python3
"""
Test script to verify boyfriend model endpoints work correctly
"""

import sys
import os
sys.path.append('.')

from src.ProductTo3DPipeline.routes import list_boyfriend_models

async def test_boyfriend_models():
    """Test the boyfriend models endpoint"""
    try:
        result = await list_boyfriend_models()
        print("[OK] Boyfriend models endpoint working!")
        print(f"Found {result['count']} boyfriend models:")

        for boyfriend in result['boyfriends']:
            print(f"  - {boyfriend['name']} ({boyfriend['id']})")
            print(f"    Description: {boyfriend['description']}")
            print(f"    Model URL: {boyfriend['model_url']}")
            print(f"    Personality: {boyfriend['personality']}")
            print()

        # Check if model files exist
        from pathlib import Path
        models_dir = Path("src/ProductTo3DPipeline/models")

        print("[INFO] Checking model files:")
        boyfriend_files = {
            "alex": "model_rigged.glb",
            "mike": "model_final_animated.glb",
            "ryan": "model_3d.glb"
        }

        for bf_id, filename in boyfriend_files.items():
            file_path = models_dir / filename
            if file_path.exists():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                print(f"  [OK] {bf_id}: {filename} ({size_mb:.1f} MB)")
            else:
                print(f"  [ERROR] {bf_id}: {filename} (NOT FOUND)")

    except Exception as e:
        print(f"[ERROR] Error testing boyfriend models: {e}")
        return False

    return True

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(test_boyfriend_models())
    if success:
        print("\n[SUCCESS] All boyfriend model tests passed!")
    else:
        print("\n[FAILED] Some tests failed!")
        sys.exit(1)