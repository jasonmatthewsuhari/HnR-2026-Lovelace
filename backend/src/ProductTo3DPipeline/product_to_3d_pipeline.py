"""
Product-to-3D Pipeline Service

Converts product images (especially fashion/clothing) into 3D models using various APIs.
Supports multiple providers with fallback options for speed vs quality trade-offs.
"""

import os
import io
import time
import base64
import requests
from typing import Optional, Dict, Any, Literal, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import json
import asyncio
import aiohttp
from PIL import Image


class QualityLevel(str, Enum):
    """Quality levels for 3D generation"""
    PREVIEW = "preview"      # < 5 seconds, lower quality
    STANDARD = "standard"    # < 30 seconds, good quality
    HIGH = "high"           # < 2 minutes, high quality
    PREMIUM = "premium"     # < 5 minutes, best quality


class Provider(str, Enum):
    """Available 3D generation providers"""
    TRIPO_3D = "tripo_3d"          # Tripo3D Direct API (recommended)
    STABLE_FAST_3D = "stable_fast_3d"
    TRIPO_SR = "tripo_sr"
    SUDO_AI = "sudo_ai"
    SAM_3D = "sam_3d"
    INSTANT_3D = "instant_3d"
    REALI3 = "reali3"


@dataclass
class GenerationResult:
    """Result from 3D generation"""
    success: bool
    model_url: Optional[str] = None
    model_data: Optional[bytes] = None
    format: Optional[str] = None  # glb, obj, fbx
    generation_time: Optional[float] = None
    provider: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ProductTo3DPipeline:
    """
    Main pipeline class for converting product images to 3D models.

    Features:
    - Multiple API provider support
    - Quality level selection
    - Automatic preprocessing
    - Mesh post-processing
    - Auto-rigging support
    - Async job handling
    """

    def __init__(
        self,
        default_provider: Provider = Provider.TRIPO_3D,  # Changed default to Tripo3D
        api_keys: Optional[Dict[str, str]] = None
    ):
        """
        Initialize pipeline with provider and API keys.

        Args:
            default_provider: Default 3D generation provider
            api_keys: Dictionary of API keys for different providers
                      e.g. {"stable_fast_3d": "key", "sudo_ai": "key"}
        """
        self.default_provider = default_provider
        self.api_keys = api_keys or {}

        # Load from environment if not provided
        if not self.api_keys:
            self.api_keys = {
                "tripo_3d": os.getenv("TRIPO_API_KEY", ""),
                "stable_fast_3d": os.getenv("STABLE_FAST_3D_API_KEY", ""),
                "tripo_sr": os.getenv("TRIPO_SR_API_KEY", ""),
                "sudo_ai": os.getenv("SUDO_AI_API_KEY", ""),
                "sam_3d": os.getenv("SAM_3D_API_KEY", ""),
                "instant_3d": os.getenv("INSTANT_3D_API_KEY", ""),
                "reali3": os.getenv("REALI3_API_KEY", ""),
            }

    def preprocess_image(
        self,
        image_path: str,
        remove_background: bool = True,
        target_size: Tuple[int, int] = (1024, 1024)
    ) -> Image.Image:
        """
        Preprocess input image for optimal 3D generation.

        Args:
            image_path: Path to input image
            remove_background: Whether to remove background
            target_size: Target image size (width, height)

        Returns:
            Preprocessed PIL Image
        """
        # Load image
        img = Image.open(image_path)

        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Resize maintaining aspect ratio
        img.thumbnail(target_size, Image.Resampling.LANCZOS)

        # Optional: Remove background using rembg
        if remove_background:
            try:
                from rembg import remove
                img = remove(img)
            except ImportError:
                print("Warning: rembg not installed. Skipping background removal.")
                print("Install with: pip install rembg")

        return img

    def generate_3d(
        self,
        image_path: str,
        quality: QualityLevel = QualityLevel.STANDARD,
        provider: Optional[Provider] = None,
        output_format: str = "glb",
        **kwargs
    ) -> GenerationResult:
        """
        Generate 3D model from image.

        Args:
            image_path: Path to input image
            quality: Quality level for generation
            provider: Override default provider
            output_format: Desired output format (glb, obj, fbx)
            **kwargs: Additional provider-specific parameters

        Returns:
            GenerationResult with model data or URL
        """
        provider = provider or self.default_provider
        start_time = time.time()

        # Preprocess image
        try:
            img = self.preprocess_image(
                image_path,
                remove_background=kwargs.get('remove_background', True)
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                error=f"Preprocessing failed: {str(e)}"
            )

        # Route to appropriate provider
        try:
            if provider == Provider.TRIPO_3D:
                result = self._generate_tripo_3d(img, quality, output_format, **kwargs)
            elif provider == Provider.STABLE_FAST_3D:
                result = self._generate_stable_fast_3d(img, quality, output_format, **kwargs)
            elif provider == Provider.TRIPO_SR:
                result = self._generate_tripo_sr(img, quality, output_format, **kwargs)
            elif provider == Provider.SUDO_AI:
                result = self._generate_sudo_ai(img, quality, output_format, **kwargs)
            elif provider == Provider.SAM_3D:
                result = self._generate_sam_3d(img, quality, output_format, **kwargs)
            elif provider == Provider.INSTANT_3D:
                result = self._generate_instant_3d(img, quality, output_format, **kwargs)
            elif provider == Provider.REALI3:
                result = self._generate_reali3(img, quality, output_format, **kwargs)
            else:
                return GenerationResult(
                    success=False,
                    error=f"Unknown provider: {provider}"
                )

            result.generation_time = time.time() - start_time
            result.provider = provider.value
            return result

        except Exception as e:
            return GenerationResult(
                success=False,
                error=f"Generation failed: {str(e)}",
                generation_time=time.time() - start_time,
                provider=provider.value
            )

    def rig_model(
        self,
        glb_path: str,
        output_path: Optional[str] = None,
        rigging_type: str = "auto"
    ) -> GenerationResult:
        """
        Auto-rig a GLB model using Tripo3D.

        Args:
            glb_path: Path to input GLB file
            output_path: Optional output path, defaults to input_rigged.glb
            rigging_type: Type of rigging ("auto" or "manual")

        Returns:
            GenerationResult with rigged model
        """
        if not output_path:
            base_name = Path(glb_path).stem
            output_path = f"{base_name}_rigged.glb"

        api_key = self.api_keys.get("tripo_3d")
        if not api_key:
            return GenerationResult(
                success=False,
                error="Tripo3D API key not configured. Get it from https://platform.tripo3d.ai"
            )

        API_BASE = "https://api.tripo3d.ai/v2/openapi"
        HEADERS = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        try:
            # Step 1: Upload GLB file
            with open(glb_path, "rb") as f:
                files = {
                    "file": (Path(glb_path).name, f, "model/gltf-binary")
                }

            upload_headers = {"Authorization": f"Bearer {api_key}"}

            response = requests.post(
                f"{API_BASE}/upload",
                headers=upload_headers,
                files=files,
                timeout=60
            )

            if response.status_code != 200:
                return GenerationResult(
                    success=False,
                    error=f"Upload failed: {response.status_code} - {response.text}"
                )

            upload_result = response.json()

            # Extract file token
            if "data" in upload_result and "file_token" in upload_result["data"]:
                file_token = upload_result["data"]["file_token"]
            elif "file_token" in upload_result:
                file_token = upload_result["file_token"]
            else:
                return GenerationResult(
                    success=False,
                    error=f"No file_token in upload response: {upload_result}"
                )

            # Step 2: Create rigging task
            # Create rigging task - EXACT format from Tripo3D Animation API docs
            # Note: Rigging requires original_model_task_id from previous generation
            # This assumes the generation and rigging happen in sequence
            # In practice, you'd need to store task_ids and chain operations

            payload = {
                "type": "animate_rig",
                "original_model_task_id": "placeholder_task_id",  # Would need actual task_id
                "out_format": "glb",
                "model_version": "v2.0-20250506",
                "rig_type": "biped",
                "spec": "tripo"
            }

            response = requests.post(
                f"{API_BASE}/task",
                headers=HEADERS,
                json=payload,
                timeout=30
            )

            if response.status_code != 200:
                return GenerationResult(
                    success=False,
                    error=f"Task creation failed: {response.status_code} - {response.text}"
                )

            task_result = response.json()

            if "data" in task_result and "task_id" in task_result["data"]:
                task_id = task_result["data"]["task_id"]
            elif "task_id" in task_result:
                task_id = task_result["task_id"]
            else:
                return GenerationResult(
                    success=False,
                    error=f"No task_id in response: {task_result}"
                )

            # Step 3: Monitor progress (up to 5 minutes)
            max_attempts = 60
            attempt = 0

            while attempt < max_attempts:
                response = requests.get(
                    f"{API_BASE}/task/{task_id}",
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

                if status == "success":
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
                        return GenerationResult(
                            success=False,
                            error=f"No rigged model URL in success response: {status_data}"
                        )

                    # Download rigged model
                    model_response = requests.get(rigged_url, timeout=120)

                    if model_response.status_code != 200:
                        return GenerationResult(
                            success=False,
                            error=f"Model download failed: {model_response.status_code}"
                        )

                    return GenerationResult(
                        success=True,
                        model_url=rigged_url,
                        model_data=model_response.content,
                        format="glb",
                        metadata=status_data
                    )

                elif status in ["failed", "error"]:
                    return GenerationResult(
                        success=False,
                        error=f"Rigging failed with status: {status}"
                    )
                elif status in ["pending", "processing", "running"]:
                    time.sleep(5)
                else:
                    time.sleep(5)

                attempt += 1

            return GenerationResult(
                success=False,
                error="Timeout waiting for rigging to complete"
            )

        except Exception as e:
            return GenerationResult(
                success=False,
                error=f"Tripo3D rigging error: {str(e)}"
            )

    # ... existing provider methods ...

    def save_model(
        self,
        result: GenerationResult,
        output_path: str
    ) -> bool:
        """
        Save generated model to file.

        Args:
            result: GenerationResult from generate_3d or rig_model
            output_path: Path to save model

        Returns:
            Success status
        """
        if not result.success or not result.model_data:
            return False

        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(result.model_data)
            return True
        except Exception as e:
            print(f"Error saving model: {e}")
            return False


# Example usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "rig":
        # Rig a GLB file
        glb_file = sys.argv[2] if len(sys.argv) > 2 else "product_3d.glb"

        print(f"Rigging GLB file: {glb_file}")
        pipeline = ProductTo3DPipeline()
        result = pipeline.rig_model(glb_file)

        if result.success:
            output_path = f"{Path(glb_file).stem}_rigged.glb"
            if pipeline.save_model(result, output_path):
                print(f"[SUCCESS] Rigged model saved: {output_path}")
            else:
                print("[ERROR] Failed to save rigged model")
        else:
            print(f"[ERROR] Rigging failed: {result.error}")

    else:
        # Generate 3D from image
        pipeline = ProductTo3DPipeline(
            default_provider=Provider.TRIPO_3D,
            api_keys={
                "tripo_3d": os.getenv("TRIPO_API_KEY", "your-tripo-key-here"),
                "stable_fast_3d": "your-key-here",
                "tripo_sr": "your-replicate-key-here",
                "sudo_ai": "your-sudo-key-here",
            }
        )

        test_image = "product.jpg"

        if os.path.exists(test_image):
            print("Generating 3D model with Tripo3D...")
            result = pipeline.generate_3d(
                image_path=test_image,
                quality=QualityLevel.STANDARD,
                output_format="glb"
            )

            if result.success:
                print(f"[OK] Success! Generated in {result.generation_time:.2f}s")
                print(f"  Provider: {result.provider}")
                print(f"  Format: {result.format}")

                # Save to file
                if result.model_data:
                    output_path = "product_3d.glb"
                    if pipeline.save_model(result, output_path):
                        print(f"  Saved to: {output_path}")
                        print(f"  Size: {len(result.model_data) / 1024:.1f} KB")
            else:
                print(f"[ERROR] Failed: {result.error}")
        else:
            print(f"Test image not found: {test_image}")
            print("\nTo test:")
            print("1. Add TRIPO_API_KEY to your .env file")
            print("2. Place product image as 'product.jpg'")
            print("3. Run: python product_to_3d_pipeline.py")
            print("\nTo rig a GLB file:")
            print("python product_to_3d_pipeline.py rig product_3d.glb")