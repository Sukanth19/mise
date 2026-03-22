import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException
from app.config import settings


class ImageHandler:
    """Service for handling image uploads and storage."""
    
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
    ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes
    
    @staticmethod
    def validate_image(file: UploadFile) -> bool:
        """
        Validate image file type.
        
        Args:
            file: The uploaded file to validate
            
        Returns:
            True if valid, raises HTTPException otherwise
        """
        # Check MIME type
        if file.content_type not in ImageHandler.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: JPEG, PNG, WebP"
            )
        
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ImageHandler.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file extension. Allowed extensions: {', '.join(ImageHandler.ALLOWED_EXTENSIONS)}"
            )
        
        return True
    
    @staticmethod
    async def save_image(file: UploadFile) -> str:
        """
        Save uploaded image to filesystem with unique filename.
        
        Args:
            file: The uploaded file to save
            
        Returns:
            URL path to the saved image
            
        Raises:
            HTTPException: If file is invalid or too large
        """
        # Validate file type
        ImageHandler.validate_image(file)
        
        # Read file content to check size
        content = await file.read()
        file_size = len(content)
        
        if file_size > ImageHandler.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds maximum limit of 5MB"
            )
        
        # Generate unique filename
        file_ext = Path(file.filename).suffix.lower()
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        
        # Create upload directory if it doesn't exist
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = upload_dir / unique_filename
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Return URL path
        return f"/{settings.upload_dir}/{unique_filename}"
    
    @staticmethod
    def delete_image(url: str) -> None:
        """
        Delete image file from filesystem.
        
        Args:
            url: The URL path of the image to delete
        """
        if not url:
            return
        
        # Extract filename from URL
        # URL format: /uploads/filename.ext
        try:
            filename = Path(url).name
            file_path = Path(settings.upload_dir) / filename
            
            if file_path.exists():
                file_path.unlink()
        except Exception:
            # Silently fail if file doesn't exist or can't be deleted
            pass
