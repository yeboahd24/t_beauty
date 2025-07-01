"""
File upload utilities for handling image uploads.
"""
import os
import uuid
import shutil
from typing import Optional, List
from pathlib import Path
from PIL import Image
from fastapi import UploadFile, HTTPException, status
import aiofiles


class FileUploadService:
    """Service for handling file uploads."""
    
    # Supported image formats
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Image size configurations
    THUMBNAIL_SIZE = (200, 200)
    MEDIUM_SIZE = (800, 800)
    
    def __init__(self, upload_dir: str = "uploads"):
        """Initialize the file upload service."""
        self.upload_dir = Path(upload_dir)
        self.images_dir = self.upload_dir / "images"
        self.products_dir = self.images_dir / "products"
        
        # Create directories if they don't exist
        self.products_dir.mkdir(parents=True, exist_ok=True)
    
    def _validate_image_file(self, file: UploadFile) -> None:
        """Validate uploaded image file."""
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No filename provided"
            )
        
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_ext} not allowed. Allowed types: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )
        
        # Check file size (if available)
        if hasattr(file, 'size') and file.size and file.size > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size too large. Maximum size: {self.MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
    
    def _generate_filename(self, original_filename: str, prefix: str = "") -> str:
        """Generate a unique filename."""
        file_ext = Path(original_filename).suffix.lower()
        unique_id = str(uuid.uuid4())
        if prefix:
            return f"{prefix}_{unique_id}{file_ext}"
        return f"{unique_id}{file_ext}"
    
    async def save_image(
        self, 
        file: UploadFile, 
        user_id: int, 
        product_id: Optional[int] = None,
        image_type: str = "primary"
    ) -> dict:
        """Save uploaded image and create variants."""
        self._validate_image_file(file)
        
        # Create user-specific directory
        user_dir = self.products_dir / str(user_id)
        if product_id:
            user_dir = user_dir / str(product_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        prefix = f"{image_type}" if image_type else "image"
        filename = self._generate_filename(file.filename, prefix)
        
        # Save original file
        original_path = user_dir / filename
        
        try:
            # Save uploaded file
            async with aiofiles.open(original_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Create image variants
            variants = await self._create_image_variants(original_path, user_dir)
            
            # Generate URLs (relative to upload directory)
            base_url = f"/uploads/images/products/{user_id}"
            if product_id:
                base_url += f"/{product_id}"
            
            return {
                "original_url": f"{base_url}/{filename}",
                "thumbnail_url": f"{base_url}/{variants['thumbnail']}",
                "medium_url": f"{base_url}/{variants['medium']}",
                "filename": filename,
                "file_size": len(content),
                "image_type": image_type
            }
            
        except Exception as e:
            # Clean up on error
            if original_path.exists():
                original_path.unlink()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save image: {str(e)}"
            )
    
    async def _create_image_variants(self, original_path: Path, output_dir: Path) -> dict:
        """Create thumbnail and medium-sized variants of the image."""
        try:
            with Image.open(original_path) as img:
                # Convert to RGB if necessary (for JPEG compatibility)
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Create thumbnail
                thumbnail = img.copy()
                thumbnail.thumbnail(self.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
                thumbnail_filename = f"thumb_{original_path.name}"
                thumbnail_path = output_dir / thumbnail_filename
                thumbnail.save(thumbnail_path, 'JPEG', quality=85)
                
                # Create medium size
                medium = img.copy()
                medium.thumbnail(self.MEDIUM_SIZE, Image.Resampling.LANCZOS)
                medium_filename = f"medium_{original_path.name}"
                medium_path = output_dir / medium_filename
                medium.save(medium_path, 'JPEG', quality=90)
                
                return {
                    "thumbnail": thumbnail_filename,
                    "medium": medium_filename
                }
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process image: {str(e)}"
            )
    
    async def save_multiple_images(
        self, 
        files: List[UploadFile], 
        user_id: int, 
        product_id: Optional[int] = None
    ) -> List[dict]:
        """Save multiple images."""
        results = []
        
        for i, file in enumerate(files):
            image_type = "primary" if i == 0 else f"additional_{i}"
            try:
                result = await self.save_image(file, user_id, product_id, image_type)
                results.append(result)
            except HTTPException:
                # Continue with other files if one fails
                continue
        
        return results
    
    def delete_image(self, file_path: str) -> bool:
        """Delete an image file and its variants."""
        try:
            # Convert URL back to file path
            if file_path.startswith('/uploads/'):
                file_path = file_path[1:]  # Remove leading slash
            
            full_path = Path(file_path)
            
            if full_path.exists():
                # Delete original
                full_path.unlink()
                
                # Delete variants
                thumb_path = full_path.parent / f"thumb_{full_path.name}"
                medium_path = full_path.parent / f"medium_{full_path.name}"
                
                if thumb_path.exists():
                    thumb_path.unlink()
                if medium_path.exists():
                    medium_path.unlink()
                
                return True
            
            return False
            
        except Exception:
            return False
    
    def get_file_info(self, file_path: str) -> Optional[dict]:
        """Get information about an uploaded file."""
        try:
            if file_path.startswith('/uploads/'):
                file_path = file_path[1:]
            
            full_path = Path(file_path)
            
            if full_path.exists():
                stat = full_path.stat()
                return {
                    "filename": full_path.name,
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "exists": True
                }
            
            return {"exists": False}
            
        except Exception:
            return {"exists": False}


# Global instance
file_upload_service = FileUploadService()