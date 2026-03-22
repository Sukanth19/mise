"""Property-based tests for image upload service."""
import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"
os.environ["UPLOAD_DIR"] = "test_uploads"

from hypothesis import given, strategies as st, settings as hyp_settings
from datetime import timedelta
import io
from PIL import Image
from pathlib import Path
import shutil


# Strategy for generating valid image formats
@st.composite
def valid_image_file(draw):
    """Generate a valid image file with random format and size."""
    # Choose format
    format_choice = draw(st.sampled_from(['JPEG', 'PNG', 'WEBP']))
    
    # Generate small image dimensions (to keep file size reasonable)
    width = draw(st.integers(min_value=10, max_value=200))
    height = draw(st.integers(min_value=10, max_value=200))
    
    # Generate random color
    color = (
        draw(st.integers(min_value=0, max_value=255)),
        draw(st.integers(min_value=0, max_value=255)),
        draw(st.integers(min_value=0, max_value=255))
    )
    
    # Create image
    img = Image.new('RGB', (width, height), color=color)
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format=format_choice)
    img_bytes.seek(0)
    
    # Determine MIME type and extension
    mime_types = {
        'JPEG': 'image/jpeg',
        'PNG': 'image/png',
        'WEBP': 'image/webp'
    }
    extensions = {
        'JPEG': '.jpg',
        'PNG': '.png',
        'WEBP': '.webp'
    }
    
    return {
        'content': img_bytes.getvalue(),
        'content_type': mime_types[format_choice],
        'filename': f'test_image{extensions[format_choice]}',
        'size': len(img_bytes.getvalue())
    }


# Feature: recipe-saver, Property 11: Valid images are accepted and stored
@given(image_data=valid_image_file())
@hyp_settings(max_examples=100, deadline=timedelta(milliseconds=2000))
def test_valid_image_upload_property(image_data):
    """
    Property 11: Valid images are accepted and stored
    
    For any valid image file (JPEG, PNG, or WebP under 5MB), uploading 
    should succeed and return a URL that points to an accessible file.
    
    **Validates: Requirements 4.1, 4.2, 4.4**
    """
    from fastapi import UploadFile
    from app.services.image_service import ImageHandler
    from app.config import settings
    import asyncio
    
    # Skip if image is too large (over 5MB)
    if image_data['size'] > 5 * 1024 * 1024:
        return
    
    # Create upload directory
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Create UploadFile object with headers
        file_obj = io.BytesIO(image_data['content'])
        from starlette.datastructures import Headers
        headers = Headers({'content-type': image_data['content_type']})
        upload_file = UploadFile(
            filename=image_data['filename'],
            file=file_obj,
            headers=headers
        )
        
        # Upload image
        url = asyncio.run(ImageHandler.save_image(upload_file))
        
        # Verify URL is returned
        assert url is not None, "Upload should return a URL"
        assert isinstance(url, str), "URL should be a string"
        assert len(url) > 0, "URL should not be empty"
        
        # Verify URL format
        assert url.startswith(f"/{settings.upload_dir}/"), f"URL should start with /{settings.upload_dir}/"
        
        # Extract filename from URL
        filename = Path(url).name
        file_path = upload_dir / filename
        
        # Verify file exists
        assert file_path.exists(), f"Uploaded file should exist at {file_path}"
        
        # Verify file is readable
        with open(file_path, 'rb') as f:
            saved_content = f.read()
            assert len(saved_content) > 0, "Saved file should not be empty"
            assert len(saved_content) == image_data['size'], "Saved file size should match uploaded size"
        
        # Clean up
        file_path.unlink()
        
    finally:
        # Clean up test upload directory
        if upload_dir.exists():
            shutil.rmtree(upload_dir, ignore_errors=True)
