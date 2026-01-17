"""
Firebase Storage Manager for Lovelace

Handles image uploads to Firebase Storage for clothing items, avatars, and other media.
Supports image processing, resizing, and background removal.
"""

import os
import io
import uuid
from pathlib import Path
from typing import Optional, List, Tuple
from datetime import datetime, timedelta
from PIL import Image

try:
    import firebase_admin
    from firebase_admin import credentials, storage
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("Warning: Firebase libraries not installed. Run: pip install firebase-admin")

try:
    from rembg import remove
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False
    print("Info: rembg not available. Background removal disabled. Run: pip install rembg")


class FirebaseStorageManager:
    """
    Manages file uploads to Firebase Storage with image processing capabilities
    """
    
    def __init__(self, bucket_name: Optional[str] = None):
        """
        Initialize Firebase Storage Manager
        
        Args:
            bucket_name: Firebase Storage bucket name (default from Firebase config)
        """
        if not FIREBASE_AVAILABLE:
            raise ImportError("Firebase Admin SDK not installed")
        
        # Get or use default bucket
        self.bucket_name = bucket_name or os.getenv('FIREBASE_STORAGE_BUCKET')
        
        # Initialize Firebase if needed
        try:
            firebase_admin.get_app()
        except ValueError:
            creds_path = os.getenv('FIREBASE_CREDENTIALS_PATH', './firebase-credentials.json')
            cred = credentials.Certificate(creds_path)
            firebase_admin.initialize_app(cred, {
                'storageBucket': self.bucket_name
            })
        
        self.bucket = storage.bucket(self.bucket_name)
        print(f"✓ Firebase Storage initialized: {self.bucket_name}")
    
    def _process_image(self, 
                       image_data: bytes,
                       max_size: Tuple[int, int] = (1200, 1200),
                       quality: int = 85,
                       remove_background: bool = False) -> bytes:
        """
        Process image: resize and optionally remove background
        
        Args:
            image_data: Raw image bytes
            max_size: Maximum dimensions (width, height)
            quality: JPEG quality (1-100)
            remove_background: Whether to remove background
            
        Returns:
            Processed image bytes
        """
        # Open image
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if needed
        if image.mode in ('RGBA', 'LA', 'P'):
            if remove_background:
                # Keep alpha channel for background removal
                pass
            else:
                # Convert to RGB
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
        
        # Resize if needed
        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Remove background if requested
        if remove_background and REMBG_AVAILABLE:
            try:
                output_buffer = io.BytesIO()
                image.save(output_buffer, format='PNG')
                image_data = output_buffer.getvalue()
                
                # Remove background
                image_data = remove(image_data)
                return image_data
            except Exception as e:
                print(f"Warning: Background removal failed: {e}")
                # Continue with original image
        
        # Save to bytes
        output_buffer = io.BytesIO()
        format_to_save = 'PNG' if remove_background else 'JPEG'
        
        if format_to_save == 'JPEG' and image.mode != 'RGB':
            image = image.convert('RGB')
        
        image.save(output_buffer, format=format_to_save, quality=quality, optimize=True)
        return output_buffer.getvalue()
    
    def upload_clothing_image(self,
                             user_id: str,
                             image_data: bytes,
                             filename: Optional[str] = None,
                             remove_background: bool = False) -> str:
        """
        Upload a clothing item image
        
        Args:
            user_id: User ID who owns this clothing
            image_data: Raw image bytes
            filename: Original filename (optional)
            remove_background: Whether to remove background
            
        Returns:
            Public URL of uploaded image
        """
        # Generate unique filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        
        if filename:
            ext = Path(filename).suffix.lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
                ext = '.jpg'
        else:
            ext = '.png' if remove_background else '.jpg'
        
        blob_name = f"clothing/{user_id}/{timestamp}_{unique_id}{ext}"
        
        # Process image
        processed_data = self._process_image(
            image_data,
            remove_background=remove_background
        )
        
        # Upload to Firebase Storage
        blob = self.bucket.blob(blob_name)
        
        content_type = 'image/png' if remove_background else 'image/jpeg'
        blob.upload_from_string(processed_data, content_type=content_type)
        
        # Make publicly accessible
        blob.make_public()
        
        print(f"✓ Uploaded clothing image: {blob_name}")
        return blob.public_url
    
    def upload_multiple_images(self,
                              user_id: str,
                              images_data: List[bytes],
                              filenames: Optional[List[str]] = None,
                              remove_background: bool = False) -> List[str]:
        """
        Upload multiple clothing images
        
        Args:
            user_id: User ID
            images_data: List of image bytes
            filenames: List of original filenames
            remove_background: Whether to remove backgrounds
            
        Returns:
            List of public URLs
        """
        urls = []
        filenames = filenames or [None] * len(images_data)
        
        for i, (image_data, filename) in enumerate(zip(images_data, filenames)):
            try:
                url = self.upload_clothing_image(
                    user_id=user_id,
                    image_data=image_data,
                    filename=filename,
                    remove_background=remove_background
                )
                urls.append(url)
            except Exception as e:
                print(f"Error uploading image {i}: {e}")
                continue
        
        return urls
    
    def upload_avatar(self, user_id: str, image_data: bytes) -> str:
        """
        Upload user avatar/profile picture
        
        Args:
            user_id: User ID
            image_data: Raw image bytes
            
        Returns:
            Public URL of uploaded avatar
        """
        blob_name = f"avatars/{user_id}/profile.jpg"
        
        # Process avatar (smaller size, square crop)
        image = Image.open(io.BytesIO(image_data))
        
        # Make square
        size = min(image.size)
        left = (image.width - size) // 2
        top = (image.height - size) // 2
        image = image.crop((left, top, left + size, top + size))
        
        # Resize to 400x400
        image = image.resize((400, 400), Image.Resampling.LANCZOS)
        
        # Convert to RGB
        if image.mode != 'RGB':
            rgb_image = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'RGBA':
                rgb_image.paste(image, mask=image.split()[-1])
            else:
                rgb_image.paste(image)
            image = rgb_image
        
        # Save to bytes
        output_buffer = io.BytesIO()
        image.save(output_buffer, format='JPEG', quality=90, optimize=True)
        processed_data = output_buffer.getvalue()
        
        # Upload
        blob = self.bucket.blob(blob_name)
        blob.upload_from_string(processed_data, content_type='image/jpeg')
        blob.make_public()
        
        print(f"✓ Uploaded avatar: {blob_name}")
        return blob.public_url
    
    def delete_image(self, image_url: str) -> bool:
        """
        Delete an image from Firebase Storage
        
        Args:
            image_url: Public URL of the image
            
        Returns:
            True if deleted successfully
        """
        try:
            # Extract blob name from URL
            # URL format: https://storage.googleapis.com/{bucket}/{blob_name}
            if self.bucket_name in image_url:
                parts = image_url.split(self.bucket_name + '/')
                if len(parts) > 1:
                    blob_name = parts[1].split('?')[0]  # Remove query params
                    
                    blob = self.bucket.blob(blob_name)
                    blob.delete()
                    print(f"✓ Deleted image: {blob_name}")
                    return True
        except Exception as e:
            print(f"Error deleting image: {e}")
        
        return False
    
    def get_signed_url(self, blob_name: str, expiration_hours: int = 24) -> str:
        """
        Generate a signed URL for private access
        
        Args:
            blob_name: Name of the blob in storage
            expiration_hours: Hours until URL expires
            
        Returns:
            Signed URL
        """
        blob = self.bucket.blob(blob_name)
        url = blob.generate_signed_url(
            expiration=timedelta(hours=expiration_hours)
        )
        return url


def main():
    """Test Firebase Storage functionality"""
    print("=" * 70)
    print("  Firebase Storage Manager Test")
    print("=" * 70)
    
    try:
        storage_mgr = FirebaseStorageManager()
        print("\n✓ Firebase Storage initialized successfully")
        print(f"  Bucket: {storage_mgr.bucket_name}")
        print("\nReady to upload images!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("  1. Firebase is initialized")
        print("  2. FIREBASE_STORAGE_BUCKET is set in .env")
        print("  3. firebase-credentials.json exists")


if __name__ == "__main__":
    main()
