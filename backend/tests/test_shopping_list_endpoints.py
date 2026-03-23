"""Unit tests for shopping list API endpoints."""
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


@pytest.fixture
def auth_headers(db):
    """Create a test user and return auth headers."""
    user = AuthService.create_user(db, f"testuser_{id(db)}", "password123")
    token = AuthService.create_token(user.id)
    return {"Authorization": f"Bearer {token}"}, user.id


@pytest.fixture
def test_recipe(db, auth_headers):
    """Create a test recipe."""
    headers, user_id = auth_headers
    recipe_data = RecipeCreate(
        title="Test Recipe",
        ingredients=["2 cups flour", "1 cup sugar", "3 eggs"],
        steps=["step1"]
    )
    recipe = RecipeManager.create_recipe(db, user_id, recipe_data)
    return recipe


def test_create_shopping_list_from_recipes(db, auth_headers, test_recipe):
    """Test creating a shopping list from recipe IDs."""
    headers, _ = auth_headers
    
    response = client.post(
        "/api/shopping-lists",
        json={
            "name": "My Shopping List",
            "recipe_ids": [test_recipe.id]
        },
        headers=headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My Shopping List"
    assert len(data["items"]) > 0
    assert data["user_id"] is not None


def test_get_shopping_lists(db, auth_headers, test_recipe):
    """Test retrieving all shopping lists for a user."""
    headers, _ = auth_headers
    
    # Create a shopping list first
    client.post(
        "/api/shopping-lists",
        json={
            "name": "Test List",
            "recipe_ids": [test_recipe.id]
        },
        headers=headers
    )
    
    # Get shopping lists
    response = client.get(
        "/api/shopping-lists",
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == "Test List"


def test_get_shopping_list_by_id(db, auth_headers, test_recipe):
    """Test retrieving a specific shopping list."""
    headers, _ = auth_headers
    
    # Create a shopping list
    create_response = client.post(
        "/api/shopping-lists",
        json={
            "name": "Specific List",
            "recipe_ids": [test_recipe.id]
        },
        headers=headers
    )
    
    list_id = create_response.json()["id"]
    
    # Get the specific list
    response = client.get(
        f"/api/shopping-lists/{list_id}",
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == list_id
    assert data["name"] == "Specific List"
    assert len(data["items"]) > 0


def test_delete_shopping_list(db, auth_headers, test_recipe):
    """Test deleting a shopping list."""
    headers, _ = auth_headers
    
    # Create a shopping list
    create_response = client.post(
        "/api/shopping-lists",
        json={
            "name": "To Delete",
            "recipe_ids": [test_recipe.id]
        },
        headers=headers
    )
    
    list_id = create_response.json()["id"]
    
    # Delete the list
    response = client.delete(
        f"/api/shopping-lists/{list_id}",
        headers=headers
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Shopping list deleted successfully"
    
    # Verify it's deleted
    get_response = client.get(
        f"/api/shopping-lists/{list_id}",
        headers=headers
    )
    assert get_response.status_code == 404


def test_update_item_status(db, auth_headers, test_recipe):
    """Test checking/unchecking a shopping list item."""
    headers, _ = auth_headers
    
    # Create a shopping list
    create_response = client.post(
        "/api/shopping-lists",
        json={
            "name": "Check Test",
            "recipe_ids": [test_recipe.id]
        },
        headers=headers
    )
    
    list_id = create_response.json()["id"]
    item_id = create_response.json()["items"][0]["id"]
    
    # Check the item
    response = client.patch(
        f"/api/shopping-lists/{list_id}/items/{item_id}",
        json={"is_checked": True},
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_checked"] is True
    
    # Uncheck the item
    response = client.patch(
        f"/api/shopping-lists/{list_id}/items/{item_id}",
        json={"is_checked": False},
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_checked"] is False


def test_add_custom_item(db, auth_headers, test_recipe):
    """Test adding a custom item to a shopping list."""
    headers, _ = auth_headers
    
    # Create a shopping list
    create_response = client.post(
        "/api/shopping-lists",
        json={
            "name": "Custom Item Test",
            "recipe_ids": [test_recipe.id]
        },
        headers=headers
    )
    
    list_id = create_response.json()["id"]
    initial_item_count = len(create_response.json()["items"])
    
    # Add custom item
    response = client.post(
        f"/api/shopping-lists/{list_id}/items",
        json={
            "ingredient_name": "Paper towels",
            "quantity": "1 roll",
            "category": "other"
        },
        headers=headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["ingredient_name"] == "Paper towels"
    assert data["is_custom"] is True
    assert data["category"] == "other"
    
    # Verify the list now has more items
    get_response = client.get(
        f"/api/shopping-lists/{list_id}",
        headers=headers
    )
    assert len(get_response.json()["items"]) == initial_item_count + 1


def test_delete_item(db, auth_headers, test_recipe):
    """Test deleting a shopping list item."""
    headers, _ = auth_headers
    
    # Create a shopping list
    create_response = client.post(
        "/api/shopping-lists",
        json={
            "name": "Delete Item Test",
            "recipe_ids": [test_recipe.id]
        },
        headers=headers
    )
    
    list_id = create_response.json()["id"]
    item_id = create_response.json()["items"][0]["id"]
    initial_item_count = len(create_response.json()["items"])
    
    # Delete the item
    response = client.delete(
        f"/api/shopping-lists/{list_id}/items/{item_id}",
        headers=headers
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Item deleted successfully"
    
    # Verify the list has fewer items
    get_response = client.get(
        f"/api/shopping-lists/{list_id}",
        headers=headers
    )
    assert len(get_response.json()["items"]) == initial_item_count - 1


def test_share_shopping_list(db, auth_headers, test_recipe):
    """Test generating a share link for a shopping list."""
    headers, _ = auth_headers
    
    # Create a shopping list
    create_response = client.post(
        "/api/shopping-lists",
        json={
            "name": "Shared List",
            "recipe_ids": [test_recipe.id]
        },
        headers=headers
    )
    
    list_id = create_response.json()["id"]
    
    # Generate share link
    response = client.post(
        f"/api/shopping-lists/{list_id}/share",
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "share_token" in data
    assert "share_url" in data
    assert data["share_token"] is not None


def test_get_shared_list(db, auth_headers, test_recipe):
    """Test accessing a shared shopping list without authentication."""
    headers, _ = auth_headers
    
    # Create a shopping list
    create_response = client.post(
        "/api/shopping-lists",
        json={
            "name": "Public Shared List",
            "recipe_ids": [test_recipe.id]
        },
        headers=headers
    )
    
    list_id = create_response.json()["id"]
    
    # Generate share link
    share_response = client.post(
        f"/api/shopping-lists/{list_id}/share",
        headers=headers
    )
    
    share_token = share_response.json()["share_token"]
    
    # Access shared list without authentication
    response = client.get(
        f"/api/shopping-lists/shared/{share_token}"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Public Shared List"
    assert len(data["items"]) > 0


def test_update_shared_item(db, auth_headers, test_recipe):
    """Test updating an item in a shared shopping list without authentication."""
    headers, _ = auth_headers
    
    # Create a shopping list
    create_response = client.post(
        "/api/shopping-lists",
        json={
            "name": "Shared Update Test",
            "recipe_ids": [test_recipe.id]
        },
        headers=headers
    )
    
    list_id = create_response.json()["id"]
    item_id = create_response.json()["items"][0]["id"]
    
    # Generate share link
    share_response = client.post(
        f"/api/shopping-lists/{list_id}/share",
        headers=headers
    )
    
    share_token = share_response.json()["share_token"]
    
    # Update item via shared link (no authentication)
    response = client.patch(
        f"/api/shopping-lists/shared/{share_token}/items/{item_id}",
        json={"is_checked": True}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_checked"] is True
    
    # Verify the owner sees the update
    get_response = client.get(
        f"/api/shopping-lists/{list_id}",
        headers=headers
    )
    
    updated_item = next(
        (item for item in get_response.json()["items"] if item["id"] == item_id),
        None
    )
    assert updated_item is not None
    assert updated_item["is_checked"] is True


def test_create_shopping_list_invalid_recipe(db, auth_headers):
    """Test creating a shopping list with invalid recipe ID."""
    headers, _ = auth_headers
    
    response = client.post(
        "/api/shopping-lists",
        json={
            "name": "Invalid Recipe List",
            "recipe_ids": [99999]  # Non-existent recipe
        },
        headers=headers
    )
    
    assert response.status_code == 400


def test_unauthorized_access(db, test_recipe):
    """Test accessing shopping lists without authentication."""
    response = client.get("/api/shopping-lists")
    assert response.status_code == 401


def test_access_other_user_list(db, test_recipe):
    """Test that users cannot access other users' shopping lists."""
    # Create first user and shopping list
    user1 = AuthService.create_user(db, f"user1_{id(db)}", "password123")
    token1 = AuthService.create_token(user1.id)
    headers1 = {"Authorization": f"Bearer {token1}"}
    
    recipe_data = RecipeCreate(
        title="User1 Recipe",
        ingredients=["ingredient1"],
        steps=["step1"]
    )
    recipe1 = RecipeManager.create_recipe(db, user1.id, recipe_data)
    
    create_response = client.post(
        "/api/shopping-lists",
        json={
            "name": "User1 List",
            "recipe_ids": [recipe1.id]
        },
        headers=headers1
    )
    
    list_id = create_response.json()["id"]
    
    # Create second user
    user2 = AuthService.create_user(db, f"user2_{id(db)}", "password123")
    token2 = AuthService.create_token(user2.id)
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    # Try to access first user's list
    response = client.get(
        f"/api/shopping-lists/{list_id}",
        headers=headers2
    )
    
    assert response.status_code == 404  # Should not find it
