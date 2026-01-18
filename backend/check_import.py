#!/usr/bin/env python
try:
    from src.ProductTo3DPipeline.routes import router as product_3d_router
    print('[OK] Import successful')
    print(f'Routes: {len(product_3d_router.routes)}')
    custom_routes = [r.path for r in product_3d_router.routes if 'custom' in r.path]
    print(f'Custom routes: {len(custom_routes)}')
    for route in custom_routes:
        print(f'  - {route}')
except Exception as e:
    print('[ERROR] Import error:', e)
    import traceback
    traceback.print_exc()