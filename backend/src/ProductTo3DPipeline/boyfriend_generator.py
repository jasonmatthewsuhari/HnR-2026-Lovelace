"""
Boyfriend 3D Model Generator
Converts uploaded images into rigged 3D boyfriend avatars using Tripo3D
"""

import os
import sys
import time
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
import requests


class BoyfriendGenerator:
    """
    Generates custom 3D boyfriend avatars from images using Tripo3D pipeline:
    1. Upload image
    2. Generate 3D model
    3. Auto-rig for animation
    4. Save to models directory
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize generator with Tripo3D API key
        
        Args:
            api_key: Tripo3D API key (or will load from env)
        """
        self.api_key = api_key or os.getenv("TRIPO_API_KEY")
        if not self.api_key:
            raise ValueError("TRIPO_API_KEY not found. Set it in .env or pass as parameter")
        
        self.api_base = "https://api.tripo3d.ai/v2/openapi"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_boyfriend(
        self,
        image_path: str,
        boyfriend_id: Optional[str] = None,
        output_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Complete pipeline: image → 3D → rigged model
        
        Args:
            image_path: Path to input image
            boyfriend_id: Optional custom ID (or will generate UUID)
            output_dir: Directory to save model (default: models/custom)
        
        Returns:
            Dict with model info:
            {
                "success": bool,
                "boyfriend_id": str,
                "model_path": str,
                "model_url": str,
                "generation_time": float,
                "error": Optional[str]
            }
        """
        start_time = time.time()
        
        # Generate ID if not provided
        if not boyfriend_id:
            boyfriend_id = f"custom_{uuid.uuid4().hex[:8]}"
        
        # Setup output directory
        if not output_dir:
            output_dir = Path(__file__).parent / "models" / "custom"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🎨 Generating boyfriend avatar: {boyfriend_id}")
        print(f"📁 Output directory: {output_dir}")
        
        try:
            # Step 1: Upload image
            print("\n[1/4] Uploading image...")
            image_token = self._upload_image(image_path)
            print(f"✓ Image uploaded: {image_token[:20]}...")
            
            # Step 2: Generate 3D model
            print("\n[2/4] Generating 3D model...")
            task_id, model_url = self._generate_3d_model(image_token)
            print(f"✓ 3D model generated: {task_id}")
            
            # Step 3: Download base model
            print("\n[3/4] Downloading base model...")
            base_model_path = output_dir / f"{boyfriend_id}_base.glb"
            self._download_model(model_url, base_model_path)
            print(f"✓ Base model saved: {base_model_path.name}")
            
            # Step 4: Auto-rig the model
            print("\n[4/4] Auto-rigging for animation...")
            rigged_model_url = self._rig_model(task_id)
            
            # Download rigged model
            rigged_model_path = output_dir / f"{boyfriend_id}.glb"
            self._download_model(rigged_model_url, rigged_model_path)
            print(f"✓ Rigged model saved: {rigged_model_path.name}")
            
            generation_time = time.time() - start_time
            
            print(f"\n✅ Boyfriend avatar generated in {generation_time:.1f}s!")
            
            return {
                "success": True,
                "boyfriend_id": boyfriend_id,
                "model_path": str(rigged_model_path),
                "model_url": f"/3d/models/boyfriends/custom/{boyfriend_id}",
                "generation_time": generation_time,
                "error": None
            }
            
        except Exception as e:
            print(f"\n❌ Error generating boyfriend: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "boyfriend_id": boyfriend_id,
                "model_path": None,
                "model_url": None,
                "generation_time": time.time() - start_time,
                "error": str(e)
            }
    
    def _upload_image(self, image_path: str) -> str:
        """Upload image to Tripo3D and return image token"""
        with open(image_path, "rb") as f:
            image_data = f.read()
        
        files = {
            "file": (os.path.basename(image_path), image_data, "image/jpeg")
        }
        
        upload_headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        response = requests.post(
            f"{self.api_base}/upload",
            headers=upload_headers,
            files=files,
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"Upload failed: {response.status_code} - {response.text}")
        
        result = response.json()
        
        # Extract token
        if "data" in result and "image_token" in result["data"]:
            return result["data"]["image_token"]
        elif "image_token" in result:
            return result["image_token"]
        else:
            raise Exception(f"No image_token in response: {result}")
    
    def _generate_3d_model(self, image_token: str) -> tuple[str, str]:
        """Generate 3D model from image token. Returns (task_id, model_url)"""
        payload = {
            "type": "image_to_model",
            "file": {
                "type": "jpg",
                "file_token": image_token
            },
            "model_version": "default"
        }
        
        response = requests.post(
            f"{self.api_base}/task",
            headers=self.headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"Task creation failed: {response.status_code} - {response.text}")
        
        result = response.json()
        
        # Extract task ID
        if "data" in result and "task_id" in result["data"]:
            task_id = result["data"]["task_id"]
        elif "task_id" in result:
            task_id = result["task_id"]
        else:
            raise Exception(f"No task_id in response: {result}")
        
        # Poll for completion
        print("   Waiting for model generation (this may take 1-5 minutes)...")
        max_attempts = 60
        
        for attempt in range(max_attempts):
            time.sleep(5)
            
            response = requests.get(
                f"{self.api_base}/task/{task_id}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30
            )
            
            if response.status_code != 200:
                continue
            
            status_result = response.json()
            status_data = status_result.get("data", status_result)
            
            status = status_data.get("status", "unknown")
            progress = status_data.get("progress", 0)
            
            print(f"   Progress: {progress}% ({status})")
            
            if status == "success":
                # Extract model URL
                output = status_data.get("output", {})
                model_url = (
                    output.get("model") or 
                    output.get("pbr_model") or 
                    output.get("glb")
                )
                
                if not model_url:
                    raise Exception(f"No model URL in success response: {status_data}")
                
                return task_id, model_url
            
            elif status in ["failed", "error"]:
                raise Exception(f"Generation failed: {status_data}")
        
        raise Exception("Timeout waiting for model generation")
    
    def _rig_model(self, original_task_id: str) -> str:
        """Auto-rig the generated model. Returns rigged model URL"""
        payload = {
            "type": "animate_rig",
            "original_model_task_id": original_task_id,
            "out_format": "glb",
            "model_version": "v2.0-20250506",
            "rig_type": "biped",
            "spec": "tripo"
        }
        
        response = requests.post(
            f"{self.api_base}/task",
            headers=self.headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"Rigging task creation failed: {response.status_code} - {response.text}")
        
        result = response.json()
        
        # Extract rigging task ID
        if "data" in result and "task_id" in result["data"]:
            rig_task_id = result["data"]["task_id"]
        elif "task_id" in result:
            rig_task_id = result["task_id"]
        else:
            raise Exception(f"No task_id in rigging response: {result}")
        
        # Poll for completion
        print("   Waiting for auto-rigging (this may take 2-5 minutes)...")
        max_attempts = 60
        
        for attempt in range(max_attempts):
            time.sleep(5)
            
            response = requests.get(
                f"{self.api_base}/task/{rig_task_id}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30
            )
            
            if response.status_code != 200:
                continue
            
            status_result = response.json()
            status_data = status_result.get("data", status_result)
            
            status = status_data.get("status", "unknown")
            progress = status_data.get("progress", 0)
            
            print(f"   Progress: {progress}% ({status})")
            
            if status == "success":
                # Extract rigged model URL
                output = status_data.get("output", {})
                rigged_url = (
                    output.get("rigged_model") or
                    output.get("model") or
                    output.get("pbr_model") or
                    output.get("glb")
                )
                
                if not rigged_url:
                    raise Exception(f"No rigged model URL in success response: {status_data}")
                
                return rigged_url
            
            elif status in ["failed", "error"]:
                raise Exception(f"Rigging failed: {status_data}")
        
        raise Exception("Timeout waiting for rigging")
    
    def _download_model(self, url: str, output_path: Path):
        """Download model from URL to file"""
        response = requests.get(url, timeout=120)
        
        if response.status_code != 200:
            raise Exception(f"Download failed: {response.status_code}")
        
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        file_size = len(response.content) / 1024  # KB
        print(f"   Downloaded: {file_size:.1f} KB")


# CLI interface
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python boyfriend_generator.py <image_path> [boyfriend_id]")
        print("Example: python boyfriend_generator.py photo.jpg custom_boyfriend_1")
        sys.exit(1)
    
    image_path = sys.argv[1]
    boyfriend_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(image_path):
        print(f"Error: Image not found: {image_path}")
        sys.exit(1)
    
    generator = BoyfriendGenerator()
    result = generator.generate_boyfriend(image_path, boyfriend_id)
    
    if result["success"]:
        print("\n" + "="*70)
        print("🎉 SUCCESS!")
        print("="*70)
        print(f"Boyfriend ID: {result['boyfriend_id']}")
        print(f"Model saved: {result['model_path']}")
        print(f"API URL: {result['model_url']}")
        print(f"Time: {result['generation_time']:.1f}s")
        print("="*70)
    else:
        print(f"\n❌ Failed: {result['error']}")
        sys.exit(1)
