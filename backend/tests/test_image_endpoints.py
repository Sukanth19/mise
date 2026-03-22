"""Unit tests for image upload endpoints."""
import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"
os.environ["UPLOAD_DIR"] = "test_uploads"

import pytest
import io
from PIL import Image
from pathlib import Path
import shutil


def create_test_image(format='JPEG', size=(100, 100), color=(255, 0, 0)):
    """Helper function to create a test image."""
    img = Image.new('RGB', size, color=color)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format=format)
    img_bytes.seek(0)
    
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
    
    return img_bytes, mime_types[format], f'test{extensions[format]}'


def test_successful_image_upload_jpeg(client, db):
    """Test successful upload with valid JPEG image."""
    from app.services.auth_service import AuthService
    from app.config import settings
    
    # Create a test user and get token
    user = AuthService.create_user(db, "testuser", "password123")
    token = AuthService.create_access_token(user.id)
    
    # Create test image
    img_bytes, content_type, filename = create_test_image('JPEG')
    
    # Upload image
    response = client.post(
        "/api/images/upload",
        files={"file": (filename, img_bytes, content_type)},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Verify response
    assert response.status_code == 201
    data = response.json()
    assert "url" in data
    assert data["url"].startswith(f"/{settings.upload_dir}/")
    
    # Verify file exists
    url = data["url"]
    file_path = Path(url.lstrip('/'))
    assert file_path.exists()
    
    # Clean up
    file_path.unlink()
    upload_dir = Path(settings.upload_dir)
    if upload_dir.exists():
        shutil.rmtree(upload_dir, ignore_errors=True)


def test_successful_image_upload_png(client, db):
    """Test successful upload with valid PNG image."""
    from app.services.auth_service import AuthService
    from app.config import settings
    
    # Create a test user and get token
    user = AuthService.create_user(db, "testuser", "password123")
    token = AuthService.create_access_token(user.id)
    
    # Create test image
    img_bytes, content_type, filename = create_test_image('PNG')
    
    # Upload image
    response = client.post(
        "/api/images/upload",
        files={"file": (filename, img_bytes, content_type)},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Verify response
    assert response.status_code == 201
    data = response.json()
    assert "url" in data
    
    # Clean up
    url = data["url"]
    file_path = Path(url.lstrip('/'))
    if file_path.exists():
        file_path.unlink()
    upload_dir = Path(settings.upload_dir)
    if upload_dir.exists():
        shutil.rmtree(upload_dir, ignore_errors=True)


def test_successful_image_upload_webp(client, db):
    """Test successful upload with valid WebP image."""
    from app.services.auth_service import AuthService
    from app.config import settings
    
    # Create a test user and get token
    user = AuthService.create_user(db, "testuser", "password123")
    token = AuthService.create_access_token(user.id)
    
    # Create test image
    img_bytes, content_type, filename = create_test_image('WEBP')
    
    # Upload image
    response = client.post(
        "/api/images/upload",
        files={"file": (filename, img_bytes, content_type)},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Verify response
    assert response.status_code == 201
    data = response.json()
    assert "url" in data
    
    # Clean up
    url = data["url"]
    file_path = Path(url.lstrip('/'))
    if file_path.exists():
        file_path.unlink()
    upload_dir = Path(settings.upload_dir)
    if upload_dir.exists():
        shutil.rmtree(upload_dir, ignore_errors=True)


def test_reject_invalid_file_type(client, db):
    """Test rejection of invalid file types (not JPEG, PNG, or WebP)."""
    from app.services.auth_service import AuthService
    from app.config import settings
    
    # Create a test user and get token
    user = AuthService.create_user(db, "testuser", "password123")
    token = AuthService.create_access_token(user.id)
    
    # Create a text file (invalid type)
    text_content = io.BytesIO(b"This is not an image")
    
    # Try to upload
    response = client.post(
        "/api/images/upload",
        files={"file": ("test.txt", text_content, "text/plain")},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Verify rejection
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Invalid file type" in data["detail"]
    
    # Clean up
    upload_dir = Path(settings.upload_dir)
    if upload_dir.exists():
        shutil.rmtree(upload_dir, ignore_errors=True)


def test_reject_oversized_file(client, db):
    """Test rejection of files larger than 5MB."""
    from app.services.auth_service import AuthService
    from app.config import settings
    
    # Create a test user and get token
    user = AuthService.create_user(db, "testuser", "password123")
    token = AuthService.create_access_token(user.id)
    
    # Create a file that's definitely over 5MB
    # Use a large uncompressed format to ensure size
    large_data = b'\x00' * (6 * 1024 * 1024)  # 6MB of zeros
    img_bytes = io.BytesIO(large_data)
    
    # Try to upload (will fail validation before size check due to invalid format)
    # So let's create a valid but large image
    # Create a large BMP-like structure that won't compress well
    large_img = Image.new('RGB', (2500, 2500))
    # Fill with random-ish data that won't compress well
    import random
    pixels = large_img.load()
    for i in range(0, 2500, 10):
        for j in range(0, 2500, 10):
            pixels[i, j] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    
    img_bytes = io.BytesIO()
    large_img.save(img_bytes, format='PNG', compress_level=0)  # No compression
    img_bytes.seek(0)
    
    # Verify size
    actual_size = len(img_bytes.getvalue())
    print(f"Image size: {actual_size / (1024*1024):.2f} MB")
    
    # If still not large enough, just create raw data
    if actual_size <= 5 * 1024 * 1024:
        # Create a minimal valid PNG header + large data
        # For testing purposes, we'll just verify the logic works with a mock
        # by creating a truly oversized file
        img_bytes = io.BytesIO(b'\x89PNG\r\n\x1a\n' + b'\x00' * (6 * 1024 * 1024))
    
    # Try to upload
    response = client.post(
        "/api/images/upload",
        files={"file": ("large.png", img_bytes, "image/png")},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Verify rejection
    assert response.status_code == 413
    data = response.json()
    assert "detail" in data
    assert "5MB" in data["detail"]
    
    # Clean up
    upload_dir = Path(settings.upload_dir)
    if upload_dir.exists():
        shutil.rmtree(upload_dir, ignore_errors=True)


def test_upload_requires_authentication(client, db):
    """Test that image upload requires authentication."""
    from app.config import settings
    
    # Create test image
    img_bytes, content_type, filename = create_test_image('JPEG')
    
    # Try to upload without token
    response = client.post(
        "/api/images/upload",
        files={"file": (filename, img_bytes, content_type)}
    )
    
    # Verify rejection
    assert response.status_code == 422  # Missing required header
    
    # Clean up
    upload_dir = Path(settings.upload_dir)
    if upload_dir.exists():
        shutil.rmtree(upload_dir, ignore_errors=True)


def test_upload_with_invalid_token(client, db):
    """Test that image upload rejects invalid tokens."""
    from app.config import settings
    
    # Create test image
    img_bytes, content_type, filename = create_test_image('JPEG')
    
    # Try to upload with invalid token
    response = client.post(
        "/api/images/upload",
        files={"file": (filename, img_bytes, content_type)},
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    # Verify rejection
    assert response.status_code == 401
    
    # Clean up
    upload_dir = Path(settings.upload_dir)
    if upload_dir.exists():
        shutil.rmtree(upload_dir, ignore_errors=True)
