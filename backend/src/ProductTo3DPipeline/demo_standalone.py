#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FULL PIPELINE DEMO - STANDALONE VERSION
Takes model.jpg → Generates 3D → Auto-rigs it → Saves both files

Usage: python demo_standalone.py
"""

import os
import sys
import time
from pathlib import Path
import requests

print("=" * 80)
print("LOVELACE FULL PIPELINE DEMO - STANDALONE")
print("model.jpg → 3D Model → Rigged Model")
print("=" * 80)

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
    print("\nPlease add to your .env file:")
    print("TRIPO_API_KEY=your_key_from_tripo3d_ai")
    print("\nGet your key at: https://platform.tripo3d.ai")
    sys.exit(1)

print(f"[OK] API key loaded: {api_key[:10]}...{api_key[-4:]}")

# Check for input image
input_image = "model.jpeg"  # User's image
if not os.path.exists(input_image):
    print(f"[ERROR] {input_image} not found!")
    print("Please place your model image as 'model.jpg' in this directory")
    sys.exit(1)

from PIL import Image
img = Image.open(input_image)
print(f"[OK] Found {input_image}: {img.size[0]}x{img.size[1]} pixels")

API_BASE = "https://api.tripo3d.ai/v2/openapi"
HEADERS = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Step 1: Generate 3D Model
print(f"\n{'='*50}")
print("STEP 1: Generating 3D Model from Image")
print(f"{'='*50}")

try:
    print(f"Uploading {input_image} to Tripo3D...")

    # Try uploading as-is first (JPEG)
    print("Trying original format...")
    with open(input_image, "rb") as f:
        original_data = f.read()

    # Determine MIME type based on file extension
    filename = input_image.lower()
    if filename.endswith('.jpg') or filename.endswith('.jpeg'):
        mime_type = "image/jpeg"
        upload_filename = "image.jpg"
    elif filename.endswith('.png'):
        mime_type = "image/png"
        upload_filename = "image.png"
    else:
        mime_type = "image/jpeg"  # fallback
        upload_filename = "image.jpg"

    files = {
        "file": (upload_filename, original_data, mime_type)
    }

    upload_headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.post(
        f"{API_BASE}/upload",
        headers=upload_headers,
        files=files,
        timeout=30
    )

    # If original format fails, try PNG conversion
    if response.status_code != 200:
        print(f"Original format failed ({response.status_code}), trying PNG conversion...")

        # Convert image to PNG format
        import io

        img = Image.open(input_image)
        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGB')

        # Save as PNG in memory
        png_buffer = io.BytesIO()
        img.save(png_buffer, format='PNG')
        png_data = png_buffer.getvalue()

        files = {
            "file": ("image.png", png_data, "image/png")
        }

        response = requests.post(
            f"{API_BASE}/upload",
            headers=upload_headers,
            files=files,
            timeout=30
        )

    if response.status_code != 200:
        print(f"[ERROR] Upload failed: {response.status_code}")
        print(f"Response: {response.text}")
        print("\n[DEBUG] Supported image formats (try PNG, JPG, JPEG)")
        print(f"[DEBUG] Original file: {input_image}")
        print(f"[DEBUG] Converted to: PNG format")
        sys.exit(1)

    upload_result = response.json()

    # Extract image token
    if "data" in upload_result and "image_token" in upload_result["data"]:
        image_token = upload_result["data"]["image_token"]
    elif "image_token" in upload_result:
        image_token = upload_result["image_token"]
    else:
        print(f"[ERROR] No image_token: {upload_result}")
        sys.exit(1)

    print(f"[OK] Image uploaded! Token: {image_token[:20]}...")

    # Create 3D generation task
    print("Starting 3D generation...")
    payload = {
        "type": "image_to_model",
        "file": {
            "type": "png",  # We always convert to PNG now
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

    if response.status_code != 200:
        print(f"[ERROR] 3D generation failed: {response.status_code}")
        print(f"Response: {response.text}")
        sys.exit(1)

    task_result = response.json()

    if "data" in task_result and "task_id" in task_result["data"]:
        gen_task_id = task_result["data"]["task_id"]
    elif "task_id" in task_result:
        gen_task_id = task_result["task_id"]
    else:
        print(f"[ERROR] No task_id: {task_result}")
        sys.exit(1)

    print(f"[OK] 3D generation started! Task: {gen_task_id}")

    # Monitor 3D generation
    print("Waiting for 3D model (1-3 minutes)...")
    max_attempts = 60
    attempt = 0

    while attempt < max_attempts:
        response = requests.get(
            f"{API_BASE}/task/{gen_task_id}",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30
        )

        if response.status_code != 200:
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

        print(f"Status: {status} ({progress}%) - {attempt+1}/{max_attempts}")

        if status == "success":
            print("[SUCCESS] 3D model generated!")

            # Extract model URL
            model_url = None
            if "output" in status_data:
                output = status_data["output"]
                model_url = (output.get("model") or
                           output.get("pbr_model") or
                           output.get("glb"))
            elif "result" in status_data:
                result = status_data["result"]
                model_url = (result.get("model") or
                           result.get("pbr_model") or
                           result.get("glb"))

            if not model_url:
                print(f"[ERROR] No model URL: {status_data}")
                sys.exit(1)

            # Download 3D model
            print("Downloading 3D model...")
            response = requests.get(model_url, timeout=120)

            if response.status_code != 200:
                print(f"[ERROR] Download failed: {response.status_code}")
                sys.exit(1)

            # Save as GLB
            model_file = "model_3d.glb"
            with open(model_file, "wb") as f:
                f.write(response.content)

            model_size = len(response.content)
            print(f"[OK] Saved 3D model: {model_file} ({model_size/1024:.1f} KB)")
            break

        elif status in ["failed", "error"]:
            print(f"[ERROR] Generation failed: {status}")
            sys.exit(1)
        elif status in ["pending", "processing", "running"]:
            time.sleep(5)
        else:
            time.sleep(5)

        attempt += 1

    if attempt >= max_attempts:
        print("[ERROR] Timeout waiting for 3D generation")
        sys.exit(1)

except Exception as e:
    print(f"[ERROR] 3D generation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 2: Auto-rig the 3D model
print(f"\n{'='*50}")
print("STEP 2: Auto-Rigging the 3D Model")
print(f"{'='*50}")

try:
    # We use the gen_task_id from Step 1 as the input for rigging
    print(f"Starting auto-rigging for Task ID: {gen_task_id}")

    rig_payload = {
        "type": "animate_rig",
        "original_model_task_id": gen_task_id,  # Points to your newly generated 3D model
        "out_format": "glb",
        "model_version": "v2.0-20250506",
        "rig_type": "biped",
        "spec": "tripo"
    }

    response = requests.post(
        f"{API_BASE}/task",
        headers=HEADERS,
        json=rig_payload,
        timeout=30
    )

    if response.status_code != 200:
        print(f"[ERROR] Rigging task failed: {response.text}")
        sys.exit(1)

    rig_task_id = response.json()["data"]["task_id"]
    print(f"[OK] Auto-rigging started! Task: {rig_task_id}")

    # ... (Keep your existing monitoring loop here)

    # Monitor rigging
    print("Waiting for rigging completion (2-5 minutes)...")
    attempt = 0

    while attempt < max_attempts:
        response = requests.get(
            f"{API_BASE}/task/{rig_task_id}",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30
        )

        if response.status_code != 200:
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

        print(f"Status: {status} ({progress}%) - {attempt+1}/{max_attempts}")

        if status == "success":
            print("[SUCCESS] Auto-rigging completed!")

            # Extract rigged model URL
            rigged_url = None
            if "output" in status_data:
                output = status_data["output"]
                rigged_url = (output.get("rigged_model") or
                             output.get("model") or
                             output.get("glb"))
            elif "result" in status_data:
                result = status_data["result"]
                rigged_url = (result.get("rigged_model") or
                             result.get("model") or
                             result.get("glb"))

            if not rigged_url:
                print(f"[ERROR] No rigged model URL: {status_data}")
                sys.exit(1)

            # Download rigged model
            print("Downloading rigged model...")
            response = requests.get(rigged_url, timeout=120)

            if response.status_code != 200:
                print(f"[ERROR] Download failed: {response.status_code}")
                sys.exit(1)

            # Save rigged model
            rigged_file = "model_rigged.glb"
            with open(rigged_file, "wb") as f:
                f.write(response.content)

            rigged_size = len(response.content)
            print(f"[OK] Saved rigged model: {rigged_file} ({rigged_size/1024:.1f} KB)")
            break

        elif status in ["failed", "error"]:
            print(f"[ERROR] Rigging failed: {status}")
            sys.exit(1)
        elif status in ["pending", "processing", "running"]:
            time.sleep(5)
        else:
            time.sleep(5)

        attempt += 1

    if attempt >= max_attempts:
        print("[ERROR] Timeout waiting for rigging")
        sys.exit(1)

except Exception as e:
    print(f"[ERROR] Rigging failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Final success message
print(f"\n{'='*80}")
print("🎉 DEMO COMPLETE! Both files generated successfully!")
print(f"{'='*80}")

print(f"\n📁 Files created:")
print(f"  • 3D Model: {model_file} ({model_size/1024:.1f} KB)")
print(f"  • Rigged:  {rigged_file} ({rigged_size/1024:.1f} KB)")

print(f"\n🌐 View your models:")
print(f"  • 3D Model: https://gltf-viewer.donmccurdy.com/")
print(f"  • Rigged:   https://gltf-viewer.donmccurdy.com/")

print(f"\n🎮 Game Engine Ready:")
print(f"  • Import {rigged_file} into Unity/Unreal")
print(f"  • Add animations and use in virtual try-on")
print(f"  • Bone structure automatically detected")

print(f"\n💡 What happened:")
print(f"  1. {input_image} → AI analysis → 3D mesh generation")
print(f"  2. {model_file} → Auto-rigging → Bone structure added")
print(f"  3. {rigged_file} → Ready for animation!")

print(f"\n{'='*80}")
print("🚀 Your virtual try-on pipeline is ready!")
print(f"{'='*80}")