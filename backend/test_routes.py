#!/usr/bin/env python
"""Test if boyfriend_generator imports correctly"""

try:
    from src.ProductTo3DPipeline.boyfriend_generator import BoyfriendGenerator
    print("[OK] BoyfriendGenerator imported successfully")
    
    from src.ProductTo3DPipeline.routes import router
    print("[OK] Routes imported successfully")
    
    # List all route paths
    print("\nAvailable routes:")
    for route in router.routes:
        print(f"  {list(route.methods)[0]:6} {route.path}")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
