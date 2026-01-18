"""
Product to 3D Pipeline Routes
Handles 3D model generation, storage, and serving
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
import os
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Import the pipeline
from .boyfriend_generator import BoyfriendGenerator

router = APIRouter()

# Thread pool for async boyfriend generation
executor = ThreadPoolExecutor(max_workers=3)

# Store job statuses in memory (in production, use Redis or database)
job_statuses: Dict[str, Dict[str, Any]] = {}

# Configuration - paths relative to this file
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
MODELS_DIR = BASE_DIR / "models"
TEMP_DIR = BASE_DIR / "temp"

# Ensure directories exist
UPLOAD_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

@router.post("/boyfriends/custom/generate")
async def generate_custom_boyfriend(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
    boyfriend_name: Optional[str] = None,
    async_mode: bool = True
):
    """
    Generate a custom 3D boyfriend avatar from an uploaded image

    MOCK IMPLEMENTATION: Returns fake successful response with demo model

    Parameters:
    - image: User photo to convert into 3D boyfriend
    - boyfriend_name: Optional custom name
    - async_mode: Process asynchronously (recommended, returns job ID)

    Returns:
    - If async: job_id for status polling
    - If sync: complete boyfriend data with model URL
    """
    
    # Validate input
    if not image.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        raise HTTPException(400, "Image must be PNG, JPG, JPEG, or WebP")
    
    # Generate unique boyfriend ID
    boyfriend_id = f"custom_{uuid.uuid4().hex[:8]}"
    job_id = boyfriend_id
    
    # Setup directories
    custom_dir = MODELS_DIR / "custom"
    custom_dir.mkdir(parents=True, exist_ok=True)
    
    # Save uploaded image temporarily
    temp_image_path = TEMP_DIR / f"{boyfriend_id}_input{Path(image.filename).suffix}"
    with open(temp_image_path, "wb") as f:
        content = await image.read()
        f.write(content)
    
    if async_mode:
        # Initialize job status
        job_statuses[job_id] = {
            "job_id": job_id,
            "boyfriend_id": boyfriend_id,
            "status": "processing",
            "progress": 0,
            "stage": "Uploading image...",
            "model_url": None,
            "error": None,
            "started_at": datetime.now().isoformat()
        }
        
        # Start mock background generation
        background_tasks.add_task(
            generate_boyfriend_mock_async,
            boyfriend_id,
            str(temp_image_path),
            boyfriend_name
        )
        
        return {
            "success": True,
            "job_id": job_id,
            "boyfriend_id": boyfriend_id,
            "message": "Custom boyfriend generation started",
            "status": "processing",
            "estimated_time": "5 seconds",
            "status_url": f"/3d/status/{job_id}"
        }
    else:
        # Synchronous mock generation
        return {
            "success": True,
            "boyfriend_id": boyfriend_id,
            "name": boyfriend_name or "Custom Boyfriend",
            "model_url": f"/3d/models/boyfriends/alex",  # Use existing model as demo
            "description": "Your custom virtual companion",
            "personality": "Personalized just for you",
            "generation_time": 2.5
        }


async def generate_boyfriend_async(
    boyfriend_id: str,
    image_path: str,
    boyfriend_name: Optional[str],
    output_dir: Path
):
    """
    Background task to generate custom boyfriend avatar
    Updates job_statuses dict with progress
    """
    try:
        # Update status callback
        def update_status(stage: str, progress: int):
            if boyfriend_id in job_statuses:
                job_statuses[boyfriend_id]["stage"] = stage
                job_statuses[boyfriend_id]["progress"] = progress
        
        update_status("Initializing...", 5)
        
        # Run generation in thread pool (Tripo3D calls are synchronous)
        loop = asyncio.get_event_loop()
        generator = BoyfriendGenerator()
        
        update_status("Uploading image to Tripo3D...", 10)
        
        result = await loop.run_in_executor(
            executor,
            generator.generate_boyfriend,
            image_path,
            boyfriend_id,
            output_dir
        )
        
        if result["success"]:
            # Update status with success
            job_statuses[boyfriend_id].update({
                "status": "completed",
                "progress": 100,
                "stage": "Complete!",
                "model_url": f"/3d/models/boyfriends/custom/{boyfriend_id}",
                "model_path": result["model_path"],
                "generation_time": result["generation_time"],
                "completed_at": datetime.now().isoformat()
            })
        else:
            # Update status with error
            job_statuses[boyfriend_id].update({
                "status": "failed",
                "progress": 0,
                "stage": "Failed",
                "error": result["error"],
                "failed_at": datetime.now().isoformat()
            })
    
    except Exception as e:
        print(f"Error in async boyfriend generation: {e}")
        import traceback
        traceback.print_exc()
        
        if boyfriend_id in job_statuses:
            job_statuses[boyfriend_id].update({
                "status": "failed",
                "progress": 0,
                "stage": "Failed",
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            })
    
    finally:
        # Clean up temp image
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
        except:
            pass


async def generate_boyfriend_mock_async(
    boyfriend_id: str,
    image_path: str,
    boyfriend_name: Optional[str]
):
    """
    Mock async boyfriend generation - simulates the process with fake progress
    """
    import asyncio

    try:
        # Simulate the generation process with realistic timing
        stages = [
            ("Uploading image...", 1, 10),
            ("Processing image...", 2, 20),
            ("Generating 3D model...", 3, 60),
            ("Auto-rigging for animation...", 4, 90),
            ("Finalizing model...", 5, 100)
        ]

        for stage, delay, progress in stages:
            await asyncio.sleep(delay)

            if boyfriend_id in job_statuses:
                job_statuses[boyfriend_id].update({
                    "stage": stage,
                    "progress": progress
                })

        # Complete the job
        if boyfriend_id in job_statuses:
            job_statuses[boyfriend_id].update({
                "status": "completed",
                "progress": 100,
                "stage": "Complete!",
                "model_url": f"/3d/models/boyfriends/alex",  # Use existing model as demo
                "model_path": "mock_model_path",
                "generation_time": 10.0,
                "completed_at": datetime.now().isoformat()
            })

    except Exception as e:
        print(f"Error in mock boyfriend generation: {e}")
        if boyfriend_id in job_statuses:
            job_statuses[boyfriend_id].update({
                "status": "failed",
                "progress": 0,
                "stage": "Failed",
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            })

    finally:
        # Clean up temp image
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
        except:
            pass


@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Get status of an async 3D generation job"""
    if job_id in job_statuses:
        return job_statuses[job_id]
    else:
        # For old demo purposes, return completed
        return {
            "job_id": job_id,
            "status": "completed",
            "progress": 100,
            "model_url": f"/models/{job_id}",
            "message": "3D model generation completed"
        }


@router.get("/models/boyfriends/custom/{boyfriend_id}")
async def serve_custom_boyfriend_model(boyfriend_id: str):
    """Serve custom boyfriend avatar models"""
    # Try custom directory first
    custom_model_path = MODELS_DIR / "custom" / f"{boyfriend_id}.glb"
    
    if custom_model_path.exists():
        return FileResponse(
            path=custom_model_path,
            filename=f"{boyfriend_id}.glb",
            media_type="model/gltf-binary"
        )
    
    # Fall back to base custom model path
    base_custom_path = MODELS_DIR / "custom" / f"{boyfriend_id}_base.glb"
    if base_custom_path.exists():
        return FileResponse(
            path=base_custom_path,
            filename=f"{boyfriend_id}.glb",
            media_type="model/gltf-binary"
        )
    
    raise HTTPException(404, f"Custom boyfriend model {boyfriend_id} not found")


@router.get("/boyfriends/custom")
async def list_custom_boyfriends():
    """List all custom boyfriend models"""
    custom_dir = MODELS_DIR / "custom"
    
    if not custom_dir.exists():
        return {
            "boyfriends": [],
            "count": 0
        }
    
    boyfriends = []
    for model_file in custom_dir.glob("*.glb"):
        # Skip base models, only include final rigged models
        if "_base" in model_file.stem:
            continue
        
        boyfriend_id = model_file.stem
        stat = model_file.stat()
        
        boyfriends.append({
            "id": boyfriend_id,
            "name": f"Custom {boyfriend_id.split('_')[-1][:4].upper()}",
            "model_url": f"/3d/models/boyfriends/custom/{boyfriend_id}",
            "description": "Your custom virtual boyfriend",
            "personality": "Personalized companion",
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "size": stat.st_size
        })
    
    # Sort by creation date (newest first)
    boyfriends.sort(key=lambda x: x["created"], reverse=True)
    
    return {
        "boyfriends": boyfriends,
        "count": len(boyfriends)
    }


@router.delete("/boyfriends/custom/{boyfriend_id}")
async def delete_custom_boyfriend(boyfriend_id: str):
    """Delete a custom boyfriend model"""
    custom_dir = MODELS_DIR / "custom"
    
    deleted_files = []
    
    # Delete both base and rigged models
    for suffix in ["", "_base"]:
        model_path = custom_dir / f"{boyfriend_id}{suffix}.glb"
        if model_path.exists():
            model_path.unlink()
            deleted_files.append(model_path.name)
    
    if not deleted_files:
        raise HTTPException(404, f"Custom boyfriend {boyfriend_id} not found")
    
    # Clean up job status if exists
    if boyfriend_id in job_statuses:
        del job_statuses[boyfriend_id]
    
    return {
        "success": True,
        "boyfriend_id": boyfriend_id,
        "deleted_files": deleted_files,
        "message": f"Deleted custom boyfriend {boyfriend_id}"
    }


@router.get("/")
async def get_3d_pipeline_info():
    """Get information about the 3D pipeline service"""
    return {
        "service": "Product to 3D Pipeline",
        "version": "1.0.0",
        "features": [
            "Image to 3D conversion",
            "GLB model serving",
            "Model storage and retrieval",
            "Multiple 3D providers support"
        ],
        "supported_formats": ["glb", "obj", "fbx"],
        "endpoints": {
            "generate": "/generate - Convert image to 3D",
            "models": "/models - List stored models",
            "model": "/models/{model_id} - Get specific model",
            "download": "/download/{model_id} - Download model file"
        }
    }

@router.post("/generate")
async def generate_3d_model(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
    quality: str = "standard",
    output_format: str = "glb",
    remove_background: bool = True,
    async_mode: bool = False
):
    """
    Generate 3D model from product image

    Parameters:
    - image: Product image file
    - quality: preview/standard/high/premium
    - output_format: glb/obj/fbx
    - remove_background: Remove background from image
    - async_mode: Process asynchronously (returns job ID)
    """

    # Validate inputs
    if not image.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        raise HTTPException(400, "Image must be PNG, JPG, JPEG, or WebP")

    if quality not in ["preview", "standard", "high", "premium"]:
        raise HTTPException(400, "Quality must be: preview, standard, high, premium")

    if output_format not in ["glb", "obj", "fbx"]:
        raise HTTPException(400, f"Output format must be: glb, obj, fbx")

    # Generate unique ID for this job
    job_id = str(uuid.uuid4())

    # Save uploaded image
    image_path = UPLOAD_DIR / f"{job_id}_input{Path(image.filename).suffix}"
    with open(image_path, "wb") as f:
        content = await image.read()
        f.write(content)

        # For now, return mock response since pipeline isn't fully implemented
        # In production, this would call the actual 3D generation pipeline

        if async_mode:
            # Async mode - return job ID immediately
            background_tasks.add_task(process_3d_generation_async, job_id, image_path, quality, output_format, remove_background)

            return {
                "success": True,
                "job_id": job_id,
                "message": "3D generation started asynchronously",
                "status": "processing",
                "estimated_time": get_estimated_time(quality)
            }
        else:
            # Sync mode - process immediately (for demo, return existing model)
            model_url = f"/models/demo/product_3d.glb"
            model_path = MODELS_DIR / "product_3d.glb"

            if not model_path.exists():
                # Copy the existing demo model
                demo_model = BASE_DIR / "product_3d.glb"
                if demo_model.exists():
                    import shutil
                    shutil.copy(demo_model, model_path)

        return {
            "success": True,
            "job_id": job_id,
            "message": "3D model generated successfully",
            "model_url": model_url,
            "generation_time": 2.5,
            "provider": "demo",
            "format": output_format,
            "quality": quality
        }

@router.get("/models")
async def list_models():
    """List all stored 3D models"""
    models = []
    for model_file in MODELS_DIR.glob("*.glb"):
        model_id = model_file.stem
        models.append({
            "id": model_id,
            "filename": model_file.name,
            "size": model_file.stat().st_size,
            "created": datetime.fromtimestamp(model_file.stat().st_ctime).isoformat(),
            "url": f"/models/{model_id}"
        })

    return {
        "models": models,
        "count": len(models)
    }

@router.get("/models/boyfriends/{boyfriend_id}")
async def serve_boyfriend_model(boyfriend_id: str):
    """Serve boyfriend avatar models"""
    # Map boyfriend IDs to available GLB models
    boyfriend_models = {
        "alex": "model_rigged.glb",  # Elegant gentleman
        "mike": "model_final_animated.glb",  # Athletic adventurer
        "ryan": "model_3d.glb",  # Creative artist
    }

    model_filename = boyfriend_models.get(boyfriend_id)
    if not model_filename:
        raise HTTPException(404, f"Boyfriend model {boyfriend_id} not found")

    model_path = MODELS_DIR / model_filename

    # If model doesn't exist in models dir, try to copy from the source
    if not model_path.exists():
        source_path = BASE_DIR / model_filename
        if source_path.exists():
            import shutil
            shutil.copy(source_path, model_path)
        else:
            raise HTTPException(404, f"Boyfriend model {boyfriend_id} not available")

    return FileResponse(
        path=model_path,
        filename=model_filename,
        media_type="model/gltf-binary"
    )

@router.get("/models/boyfriends")
async def list_boyfriend_models():
    """List available boyfriend avatar models"""
    boyfriend_models = {
        "alex": {
            "id": "alex",
            "name": "Alex",
            "model_url": "/3d/models/boyfriends/alex",
            "description": "The charming gentleman",
            "personality": "Elegant, sophisticated, and always knows the right thing to say"
        },
        "mike": {
            "id": "mike",
            "name": "Mike",
            "model_url": "/3d/models/boyfriends/mike",
            "description": "The athletic adventurer",
            "personality": "Energetic, outgoing, and loves outdoor activities"
        },
        "ryan": {
            "id": "ryan",
            "name": "Ryan",
            "model_url": "/3d/models/boyfriends/ryan",
            "description": "The creative artist",
            "personality": "Imaginative, artistic, and appreciates beauty in all forms"
        }
    }

    return {
        "boyfriends": list(boyfriend_models.values()),
        "count": len(boyfriend_models)
    }

@router.get("/models/{model_id}")
async def get_model_info(model_id: str):
    """Get information about a specific 3D model"""
    model_path = MODELS_DIR / f"{model_id}.glb"

    if not model_path.exists():
        raise HTTPException(404, f"Model {model_id} not found")

    stat = model_path.stat()
    return {
        "id": model_id,
        "filename": f"{model_id}.glb",
        "size": stat.st_size,
        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "url": f"/models/{model_id}",
        "download_url": f"/download/{model_id}"
    }

@router.get("/download/{model_id}")
async def download_model(model_id: str):
    """Download a 3D model file"""
    model_path = MODELS_DIR / f"{model_id}.glb"

    if not model_path.exists():
        raise HTTPException(404, f"Model {model_id} not found")

    return FileResponse(
        path=model_path,
        filename=f"{model_id}.glb",
        media_type="model/gltf-binary"
    )

@router.get("/models/demo/{filename}")
async def serve_demo_model(filename: str):
    """Serve demo 3D models for testing"""
    model_path = MODELS_DIR / filename

    if not model_path.exists():
        # Try to copy from the default demo model
        if filename == "product_3d.glb":
            demo_path = BASE_DIR / "product_3d.glb"
            if demo_path.exists():
                import shutil
                shutil.copy(demo_path, model_path)
            else:
                raise HTTPException(404, f"Demo model {filename} not found")
        else:
            raise HTTPException(404, f"Model {filename} not found")

    return FileResponse(
        path=model_path,
        filename=filename,
        media_type="model/gltf-binary"
    )

@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Get status of an async 3D generation job"""
    # For demo purposes, return completed status
    return {
        "job_id": job_id,
        "status": "completed",
        "progress": 100,
        "model_url": f"/models/{job_id}",
        "message": "3D model generation completed"
    }

# Helper functions

def get_estimated_time(quality: str) -> str:
    """Get estimated processing time based on quality"""
    times = {
        "preview": "5-10 seconds",
        "standard": "30-60 seconds",
        "high": "2-5 minutes",
        "premium": "5-15 minutes"
    }
    return times.get(quality, "Unknown")

async def process_3d_generation_async(
    job_id: str,
    image_path: Path,
    quality: str,
    output_format: str,
    remove_background: bool
):
    """
    Process 3D generation asynchronously
    This is a placeholder - implement actual 3D generation logic here
    """
    try:
        # Placeholder for actual 3D generation
        # In production, this would:
        # 1. Preprocess image (background removal if needed)
        # 2. Call 3D generation API (Stable Fast 3D, TripoSR, etc.)
        # 3. Save the resulting model
        # 4. Update job status

        print(f"Processing 3D generation for job {job_id}")
        print(f"Image: {image_path}")
        print(f"Quality: {quality}, Format: {output_format}")

        # For demo, just copy the existing model
        demo_model = BASE_DIR / "product_3d.glb"
        if demo_model.exists():
            import shutil
            output_path = MODELS_DIR / f"{job_id}.glb"
            shutil.copy(demo_model, output_path)
            print(f"Demo model copied to {output_path}")

    except Exception as e:
        print(f"Error processing job {job_id}: {e}")
        # In production, update job status to failed