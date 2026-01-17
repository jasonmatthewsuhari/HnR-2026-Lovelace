#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tripo3D API - Correct Implementation
Based on: https://platform.tripo3d.ai/docs/generation
"""

import os
import sys
import time
import base64
from pathlib import Path
import requests

print("=" * 70)
print("TRIPO3D API - 3D Model Converter")
print("=" * 70)

# Load .env
root_dir = Path(__file__).resolve().parents[3]
env_file = root_dir / ".env"

if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

api_key = os.getenv("TRIPO_API_KEY")
if not api_key:
    print("[ERROR] TRIPO_API_KEY not found in .env")
    print("Get your key from: https://platform.tripo3d.ai")
    sys.exit(1)

print(f"[OK] API key loaded: {api_key[:10]}...{api_key[-4:]}")

# Check image
if not os.path.exists("product.jpg"):
    print("[ERROR] product.jpg not found")
    sys.exit(1)

print("[OK] product.jpg found")

# Tripo3D API configuration
API_BASE = "https://api.tripo3d.ai/v2/openapi"
HEADERS = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Step 1: Upload image file
print("\n[1] Uploading image...")

try:
    # Read and encode image as base64
    with open("product.jpg", "rb") as f:
        image_data = f.read()
    
    # Tripo3D expects multipart form upload
    files = {
        "file": ("product.jpg", image_data, "image/jpeg")
    }
    
    upload_headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    response = requests.post(
        f"{API_BASE}/upload",
        headers=upload_headers,
        files=files,
        timeout=30
    )
    
    print(f"Upload response status: {response.status_code}")
    print(f"Upload response: {response.text[:200]}")
    
    if response.status_code != 200:
        print(f"[ERROR] Upload failed: {response.status_code}")
        print(f"Response: {response.text}")
        sys.exit(1)
    
    upload_result = response.json()
    
    # Extract image token from response
    if "data" in upload_result and "image_token" in upload_result["data"]:
        image_token = upload_result["data"]["image_token"]
    elif "image_token" in upload_result:
        image_token = upload_result["image_token"]
    else:
        print(f"[ERROR] No image_token in response: {upload_result}")
        sys.exit(1)
    
    print(f"[OK] Image uploaded! Token: {image_token[:20]}...")

except Exception as e:
    print(f"[ERROR] Upload failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 2: Create generation task
print(f"\n[2] Creating 3D generation task...")

try:
    payload = {
        "type": "image_to_model",
        "file": {
            "type": "jpg",
            "file_token": image_token
        },
        "model_version": "default"
    }
    
    response = requests.post(
        f"{API_BASE}/task",
        headers=HEADERS,
        json=payload,
        timeout=30
    )
    
    print(f"Task creation status: {response.status_code}")
    print(f"Task response: {response.text[:200]}")
    
    if response.status_code != 200:
        print(f"[ERROR] Task creation failed: {response.status_code}")
        print(f"Response: {response.text}")
        sys.exit(1)
    
    task_result = response.json()
    
    if "data" in task_result and "task_id" in task_result["data"]:
        task_id = task_result["data"]["task_id"]
    elif "task_id" in task_result:
        task_id = task_result["task_id"]
    else:
        print(f"[ERROR] No task_id in response: {task_result}")
        sys.exit(1)
    
    print(f"[OK] Task created! ID: {task_id}")

except Exception as e:
    print(f"[ERROR] Task creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 3: Monitor progress
print(f"\n[3] Monitoring progress...")
print("This may take 1-5 minutes...")

max_attempts = 60
attempt = 0

while attempt < max_attempts:
    try:
        response = requests.get(
            f"{API_BASE}/task/{task_id}",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"[WARN] Status check failed: {response.status_code}")
            time.sleep(5)
            attempt += 1
            continue
        
        status_result = response.json()
        
        if "data" in status_result:
            status_data = status_result["data"]
        else:
            status_data = status_result
        
        status = status_data.get("status", "unknown")
        progress = status_data.get("progress", 0)
        
        print(f"Status: {status} - Progress: {progress}% (attempt {attempt + 1}/{max_attempts})")
        
        if status == "success":
            print("[SUCCESS] 3D model completed!")
            final_data = status_data
            break
        elif status in ["failed", "error"]:
            print(f"[ERROR] Generation failed!")
            print(f"Details: {status_data}")
            sys.exit(1)
        elif status in ["pending", "processing", "running"]:
            print(f"Still processing... waiting 5 seconds")
            time.sleep(5)
        else:
            print(f"Unknown status: {status}")
            time.sleep(5)
        
        attempt += 1
    
    except Exception as e:
        print(f"[WARN] Status check error: {e}")
        time.sleep(5)
        attempt += 1

if attempt >= max_attempts:
    print("[ERROR] Timeout waiting for completion")
    sys.exit(1)

# Step 4: Download result
print(f"\n[4] Downloading 3D model...")

try:
    # Find model URL in response
    model_url = None
    
    if "output" in final_data:
        output = final_data["output"]
        # Try different possible fields
        model_url = (output.get("model") or 
                    output.get("pbr_model") or 
                    output.get("rendered_image") or
                    output.get("glb"))
    elif "result" in final_data:
        result = final_data["result"]
        model_url = (result.get("model") or 
                    result.get("pbr_model") or
                    result.get("glb"))
    
    if not model_url:
        print("[ERROR] No model URL in response")
        print(f"Full response: {final_data}")
        sys.exit(1)
    
    print(f"[OK] Model URL: {model_url}")
    
    # Download the model
    print("Downloading...")
    response = requests.get(model_url, timeout=120)
    
    if response.status_code != 200:
        print(f"[ERROR] Download failed: {response.status_code}")
        sys.exit(1)
    
    # Save as GLB
    with open("product_3d.glb", "wb") as f:
        f.write(response.content)
    
    file_size = len(response.content)
    print(f"[SUCCESS] Saved: product_3d.glb ({file_size / 1024:.1f} KB)")

except Exception as e:
    print(f"[ERROR] Download failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Success!
print("\n" + "=" * 70)
print("🎉 SUCCESS! Your 3D model is ready!")
print("=" * 70)
print(f"\nModel: product_3d.glb")
print(f"Size: {file_size / 1024:.1f} KB")
print(f"Format: GLB (WebGL compatible)")
print("\nView your model at:")
print("- https://gltf-viewer.donmccurdy.com/")
print("- https://modelviewer.dev/editor/")
print("\nUse in your Lovelace app for virtual try-on!")
print("=" * 70)
