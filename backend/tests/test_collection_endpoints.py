"""Integration tests for collection API endpoints."""
import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.services.auth_service import AuthService
from app.services.recipe_service import RecipeManager
from app.schemas import RecipeCreate

client = TestClient(app)


def test_create_collection(db):
    """Test creating a collection."""
    # Create user and get token
    user = AuthService.create_user(db, "colltest1", "password123")
    token = AuthService.create_access_token(user.id)
    
    # Create collection
    response = client.post(
        "/api/collections",
        json={"name": "My Collection", "description": "Test collection"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My Collection"
    assert data["description"] == "Test collection"
    assert data["user_id"] == user.id
    assert data["nesting_level"] == 0


def test_get_collections(db):
    """Test getting user's collections."""
    # Create user and get token
    user = AuthService.create_user(db, "colltest2", "password123")
    token = AuthService.create_access_token(user.id)
    
    
    # Create multiple collections
    client.post(
        "/api/collections",
        json={"name": "Collection 1"},
        headers={"Authorization": f"Bearer {token}"}
    )
    client.post(
        "/api/collections",
        json={"name": "Collection 2"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Get collections
    response = client.get(
        "/api/collections",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(c["name"] == "Collection 1" for c in data)
    assert any(c["name"] == "Collection 2" for c in data)


def test_get_collection_by_id(db):
    """Test getting a specific collection with recipes."""
    # Create user and get token
    user = AuthService.create_user(db, "colltest3", "password123")
    token = AuthService.create_access_token(user.id)
    
    
    # Create collection
    coll_response = client.post(
        "/api/collections",
        json={"name": "Test Collection"},
        headers={"Authorization": f"Bearer {token}"}
    )
    collection_id = coll_response.json()["id"]
    
    # Create a recipe
    recipe_data = RecipeCreate(
        title="Test Recipe",
        ingredients=["ingredient1"],
        steps=["step1"]
    )
    recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
    
    # Add recipe to collection
    client.post(
        f"/api/collections/{collection_id}/recipes",
        json={"recipe_ids": [recipe.id]},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Get collection
    response = client.get(
        f"/api/collections/{collection_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Collection"
    assert "recipes" in data
    assert len(data["recipes"]) == 1
    assert data["recipes"][0]["title"] == "Test Recipe"


def test_update_collection(db):
    """Test updating a collection."""
    # Create user and get token
    user = AuthService.create_user(db, "colltest4", "password123")
    token = AuthService.create_access_token(user.id)
    
    
    # Create collection
    coll_response = client.post(
        "/api/collections",
        json={"name": "Original Name"},
        headers={"Authorization": f"Bearer {token}"}
    )
    collection_id = coll_response.json()["id"]
    
    # Update collection
    response = client.put(
        f"/api/collections/{collection_id}",
        json={"name": "Updated Name", "description": "New description"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["description"] == "New description"


def test_delete_collection(db):
    """Test deleting a collection."""
    # Create user and get token
    user = AuthService.create_user(db, "colltest5", "password123")
    token = AuthService.create_access_token(user.id)
    
    
    # Create collection
    coll_response = client.post(
        "/api/collections",
        json={"name": "To Delete"},
        headers={"Authorization": f"Bearer {token}"}
    )
    collection_id = coll_response.json()["id"]
    
    # Delete collection
    response = client.delete(
        f"/api/collections/{collection_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Collection deleted successfully"
    
    # Verify it's deleted
    get_response = client.get(
        f"/api/collections/{collection_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_response.status_code == 404


def test_add_recipes_to_collection(db):
    """Test adding recipes to a collection."""
    # Create user and get token
    user = AuthService.create_user(db, "colltest6", "password123")
    token = AuthService.create_access_token(user.id)
    
    
    # Create collection
    coll_response = client.post(
        "/api/collections",
        json={"name": "Recipe Collection"},
        headers={"Authorization": f"Bearer {token}"}
    )
    collection_id = coll_response.json()["id"]
    
    # Create recipes
    recipe1 = RecipeManager.create_recipe(
        db, user.id,
        RecipeCreate(title="Recipe 1", ingredients=["i1"], steps=["s1"])
    )
    recipe2 = RecipeManager.create_recipe(
        db, user.id,
        RecipeCreate(title="Recipe 2", ingredients=["i2"], steps=["s2"])
    )
    
    # Add recipes to collection
    response = client.post(
        f"/api/collections/{collection_id}/recipes",
        json={"recipe_ids": [recipe1.id, recipe2.id]},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["added_count"] == 2


def test_remove_recipe_from_collection(db):
    """Test removing a recipe from a collection."""
    # Create user and get token
    user = AuthService.create_user(db, "colltest7", "password123")
    token = AuthService.create_access_token(user.id)
    
    
    # Create collection
    coll_response = client.post(
        "/api/collections",
        json={"name": "Recipe Collection"},
        headers={"Authorization": f"Bearer {token}"}
    )
    collection_id = coll_response.json()["id"]
    
    # Create recipe
    recipe = RecipeManager.create_recipe(
        db, user.id,
        RecipeCreate(title="Recipe", ingredients=["i1"], steps=["s1"])
    )
    
    # Add recipe to collection
    client.post(
        f"/api/collections/{collection_id}/recipes",
        json={"recipe_ids": [recipe.id]},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Remove recipe from collection
    response = client.delete(
        f"/api/collections/{collection_id}/recipes/{recipe.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Recipe removed from collection"


def test_generate_share_link(db):
    """Test generating a share link for a collection."""
    # Create user and get token
    user = AuthService.create_user(db, "colltest8", "password123")
    token = AuthService.create_access_token(user.id)
    
    
    # Create collection
    coll_response = client.post(
        "/api/collections",
        json={"name": "Shared Collection"},
        headers={"Authorization": f"Bearer {token}"}
    )
    collection_id = coll_response.json()["id"]
    
    # Generate share link
    response = client.post(
        f"/api/collections/{collection_id}/share",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "share_url" in data
    assert "share_token" in data
    assert len(data["share_token"]) > 0


def test_revoke_sharing(db):
    """Test revoking sharing for a collection."""
    # Create user and get token
    user = AuthService.create_user(db, "colltest9", "password123")
    token = AuthService.create_access_token(user.id)
    
    
    # Create collection
    coll_response = client.post(
        "/api/collections",
        json={"name": "Shared Collection"},
        headers={"Authorization": f"Bearer {token}"}
    )
    collection_id = coll_response.json()["id"]
    
    # Generate share link
    share_response = client.post(
        f"/api/collections/{collection_id}/share",
        headers={"Authorization": f"Bearer {token}"}
    )
    share_token = share_response.json()["share_token"]
    
    # Revoke sharing
    response = client.delete(
        f"/api/collections/{collection_id}/share",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Sharing revoked"
    
    # Verify shared access is revoked
    shared_response = client.get(f"/api/collections/shared/{share_token}")
    assert shared_response.status_code == 404


def test_get_shared_collection(db):
    """Test accessing a shared collection without authentication."""
    # Create user and get token
    user = AuthService.create_user(db, "colltest10", "password123")
    token = AuthService.create_access_token(user.id)
    
    
    # Create collection
    coll_response = client.post(
        "/api/collections",
        json={"name": "Public Collection", "description": "Shared with everyone"},
        headers={"Authorization": f"Bearer {token}"}
    )
    collection_id = coll_response.json()["id"]
    
    # Generate share link
    share_response = client.post(
        f"/api/collections/{collection_id}/share",
        headers={"Authorization": f"Bearer {token}"}
    )
    share_token = share_response.json()["share_token"]
    
    # Access shared collection without authentication
    response = client.get(f"/api/collections/shared/{share_token}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Public Collection"
    assert data["description"] == "Shared with everyone"
    assert "recipes" in data
