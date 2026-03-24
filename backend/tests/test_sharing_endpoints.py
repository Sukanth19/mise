"""
Integration tests for sharing endpoints (Task 19)
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import User, Recipe
import json


client = TestClient(app)


def create_test_user_and_login(db, username="testuser"):
    """Helper to create a test user and get auth token."""
    # Register user
    response = client.post(
        "/api/auth/register",
        json={"username": username, "password": "testpass123"}
    )
    
    # Login to get token
    response = client.post(
        "/api/auth/login",
        json={"username": username, "password": "testpass123"}
    )
    
    return response.json()["access_token"]


def create_test_recipe(db, token, title="Test Recipe"):
    """Helper to create a test recipe."""
    response = client.post(
        "/api/recipes",
        json={
            "title": title,
            "ingredients": ["ingredient1", "ingredient2"],
            "steps": ["step1", "step2"],
            "tags": ["tag1"]
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()


# ============================================================================
# Subtask 19.1: Recipe URL Import Endpoint Tests
# ============================================================================

def test_import_recipe_from_url_endpoint_invalid_url(db):
    """Test importing recipe from invalid URL."""
    token = create_test_user_and_login(db, "user_import_1")
    
    # Try to import from invalid URL
    response = client.post(
        "/api/recipes/import-url",
        json={"url": "https://invalid-url-that-does-not-exist.com/recipe"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Should return 400 Bad Request
    assert response.status_code == 400
    assert "IMPORT_FAILED" in response.headers.get("error_code", "")


def test_import_recipe_from_url_endpoint_unauthorized(db):
    """Test importing recipe without authentication."""
    response = client.post(
        "/api/recipes/import-url",
        json={"url": "https://example.com/recipe"}
    )
    
    # Should return 401 Unauthorized
    assert response.status_code == 401


# ============================================================================
# Subtask 19.2: QR Code Generation Endpoint Tests
# ============================================================================

def test_get_recipe_qr_code_success(db):
    """Test generating QR code for a recipe."""
    token = create_test_user_and_login(db, "user_qr_1")
    recipe = create_test_recipe(db, token, "QR Test Recipe")
    
    # Get QR code
    response = client.get(f"/api/recipes/{recipe['id']}/qrcode")
    
    # Should return 200 OK with PNG image
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    
    # Verify it's a valid PNG
    content = response.content
    assert content[:8] == b'\x89PNG\r\n\x1a\n'


def test_get_recipe_qr_code_nonexistent_recipe(db):
    """Test generating QR code for nonexistent recipe."""
    response = client.get("/api/recipes/99999/qrcode")
    
    # Should return 404 Not Found
    assert response.status_code == 404


# ============================================================================
# Subtask 19.3: Share Metadata Endpoint Tests
# ============================================================================

def test_get_share_metadata_success(db):
    """Test getting share metadata for a recipe."""
    token = create_test_user_and_login(db, "user_meta_1")
    recipe = create_test_recipe(db, token, "Metadata Test Recipe")
    
    # Get share metadata
    response = client.get(f"/api/recipes/{recipe['id']}/share-metadata")
    
    # Should return 200 OK with metadata
    assert response.status_code == 200
    
    data = response.json()
    assert "title" in data
    assert "description" in data
    assert "url" in data
    assert data["title"] == "Metadata Test Recipe"


def test_get_share_metadata_nonexistent_recipe(db):
    """Test getting share metadata for nonexistent recipe."""
    response = client.get("/api/recipes/99999/share-metadata")
    
    # Should return 404 Not Found
    assert response.status_code == 404


def test_get_share_metadata_public_recipe_url(db):
    """Test that public recipes have correct URL in metadata."""
    token = create_test_user_and_login(db, "user_meta_2")
    recipe = create_test_recipe(db, token, "Public Recipe")
    
    # Set recipe to public
    # (This would require the visibility endpoint to be implemented)
    # For now, we just verify the metadata endpoint works
    
    # Get share metadata
    response = client.get(f"/api/recipes/{recipe['id']}/share-metadata")
    
    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    assert str(recipe['id']) in data["url"]
