#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FULL PIPELINE DEMO
Takes model.jpg → Generates 3D → Auto-rigs it → Saves both files

Usage: python demo_full_pipeline.py
"""

import os
import sys
import time
from pathlib import Path

print("=" * 80)
print("LOVELACE FULL PIPELINE DEMO")
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

# Import Tripo3D functions
import requests
from product_to_3d_pipeline import ProductTo3DPipeline, Provider, QualityLevel

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

    # Upload image
    with open(input_image, "rb") as f:
        files = {
            "file": ("model.jpg", f, "image/jpeg")
        }

    upload_headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.post(
        f"{API_BASE}/upload",
        headers=upload_headers,
        files=files,
        timeout=30
    )

    if response.status_code != 200:
        print(f"[ERROR] Upload failed: {response.status_code}")
        print(f"Response: {response.text}")
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
    print(f"Uploading {model_file} for rigging...")

    # Upload GLB for rigging
    with open(model_file, "rb") as f:
        files = {
            "file": (model_file, f, "model/gltf-binary")
        }

    response = requests.post(
        f"{API_BASE}/upload",
        headers={"Authorization": f"Bearer {api_key}"},
        files=files,
        timeout=60
    )

    if response.status_code != 200:
        print(f"[ERROR] GLB upload failed: {response.status_code}")
        print(f"Response: {response.text}")
        sys.exit(1)

    upload_result = response.json()

    # Extract file token
    if "data" in upload_result and "file_token" in upload_result["data"]:
        file_token = upload_result["data"]["file_token"]
    elif "file_token" in upload_result:
        file_token = upload_result["file_token"]
    else:
        print(f"[ERROR] No file_token: {upload_result}")
        sys.exit(1)

    print(f"[OK] GLB uploaded! Token: {file_token[:20]}...")

    # Create rigging task
    print("Starting auto-rigging...")
    payload = {
        "type": "rigging",
        "file": {
            "type": "glb",
            "file_token": file_token
        },
        "rigging_type": "auto",
        "target_format": "glb"
    }

    response = requests.post(
        f"{API_BASE}/task",
        headers=HEADERS,
        json=payload,
        timeout=30
    )

    if response.status_code != 200:
        print(f"[ERROR] Rigging task failed: {response.status_code}")
        print(f"Response: {response.text}")
        sys.exit(1)

    task_result = response.json()

    if "data" in task_result and "task_id" in task_result["data"]:
        rig_task_id = task_result["data"]["task_id"]
    elif "task_id" in task_result:
        rig_task_id = task_result["task_id"]
    else:
        print(f"[ERROR] No rigging task_id: {task_result}")
        sys.exit(1)

    print(f"[OK] Auto-rigging started! Task: {rig_task_id}")

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