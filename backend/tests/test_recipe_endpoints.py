"""Unit tests for recipe endpoints."""
import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"

import pytest
from fastapi import status


def test_create_recipe_with_title(client, db):
    """Test recipe creation with valid title."""
    # Register and login
    client.post("/api/auth/register", json={"username": "testuser", "password": "password123"})
    login_response = client.post("/api/auth/login", json={"username": "testuser", "password": "password123"})
    token = login_response.json()["access_token"]
    
    # Create recipe
    recipe_data = {
        "title": "Test Recipe",
        "ingredients": ["flour", "sugar", "eggs"],
        "steps": ["Mix ingredients", "Bake at 350F"],
        "tags": ["dessert", "easy"],
        "reference_link": "https://example.com/recipe"
    }
    
    response = client.post(
        "/api/recipes",
        json=recipe_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "Test Recipe"
    assert data["ingredients"] == ["flour", "sugar", "eggs"]
    assert data["steps"] == ["Mix ingredients", "Bake at 350F"]
    assert data["tags"] == ["dessert", "easy"]
    assert data["reference_link"] == "https://example.com/recipe"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_recipe_without_title(client, db):
    """Test recipe creation without title fails validation."""
    # Register and login
    client.post("/api/auth/register", json={"username": "testuser2", "password": "password123"})
    login_response = client.post("/api/auth/login", json={"username": "testuser2", "password": "password123"})
    token = login_response.json()["access_token"]
    
    # Try to create recipe without title
    recipe_data = {
        "ingredients": ["flour", "sugar"],
        "steps": ["Mix", "Bake"]
    }
    
    response = client.post(
        "/api/recipes",
        json=recipe_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_user_recipes(client, db):
    """Test retrieving user's recipes with filtering."""
    # Register and login user1
    client.post("/api/auth/register", json={"username": "user1", "password": "password123"})
    login1 = client.post("/api/auth/login", json={"username": "user1", "password": "password123"})
    token1 = login1.json()["access_token"]
    
    # Register and login user2
    client.post("/api/auth/register", json={"username": "user2", "password": "password123"})
    login2 = client.post("/api/auth/login", json={"username": "user2", "password": "password123"})
    token2 = login2.json()["access_token"]
    
    # User1 creates recipes
    client.post(
        "/api/recipes",
        json={"title": "User1 Recipe 1", "ingredients": ["a"], "steps": ["b"]},
        headers={"Authorization": f"Bearer {token1}"}
    )
    client.post(
        "/api/recipes",
        json={"title": "User1 Recipe 2", "ingredients": ["c"], "steps": ["d"]},
        headers={"Authorization": f"Bearer {token1}"}
    )
    
    # User2 creates recipe
    client.post(
        "/api/recipes",
        json={"title": "User2 Recipe", "ingredients": ["e"], "steps": ["f"]},
        headers={"Authorization": f"Bearer {token2}"}
    )
    
    # User1 retrieves their recipes
    response1 = client.get("/api/recipes", headers={"Authorization": f"Bearer {token1}"})
    assert response1.status_code == status.HTTP_200_OK
    recipes1 = response1.json()
    assert len(recipes1) == 2
    assert all(r["title"].startswith("User1") for r in recipes1)
    
    # User2 retrieves their recipes
    response2 = client.get("/api/recipes", headers={"Authorization": f"Bearer {token2}"})
    assert response2.status_code == status.HTTP_200_OK
    recipes2 = response2.json()
    assert len(recipes2) == 1
    assert recipes2[0]["title"] == "User2 Recipe"


def test_get_recipe_by_id(client, db):
    """Test retrieving a specific recipe by ID."""
    # Register and login
    client.post("/api/auth/register", json={"username": "testuser3", "password": "password123"})
    login_response = client.post("/api/auth/login", json={"username": "testuser3", "password": "password123"})
    token = login_response.json()["access_token"]
    
    # Create recipe
    create_response = client.post(
        "/api/recipes",
        json={"title": "Specific Recipe", "ingredients": ["a"], "steps": ["b"]},
        headers={"Authorization": f"Bearer {token}"}
    )
    recipe_id = create_response.json()["id"]
    
    # Get recipe by ID
    response = client.get(f"/api/recipes/{recipe_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == recipe_id
    assert data["title"] == "Specific Recipe"


def test_update_recipe_with_ownership(client, db):
    """Test updating a recipe with ownership validation."""
    # Register and login owner
    client.post("/api/auth/register", json={"username": "owner", "password": "password123"})
    login_owner = client.post("/api/auth/login", json={"username": "owner", "password": "password123"})
    token_owner = login_owner.json()["access_token"]
    
    # Register and login other user
    client.post("/api/auth/register", json={"username": "other", "password": "password123"})
    login_other = client.post("/api/auth/login", json={"username": "other", "password": "password123"})
    token_other = login_other.json()["access_token"]
    
    # Owner creates recipe
    create_response = client.post(
        "/api/recipes",
        json={"title": "Original Title", "ingredients": ["a"], "steps": ["b"]},
        headers={"Authorization": f"Bearer {token_owner}"}
    )
    recipe_id = create_response.json()["id"]
    
    # Other user tries to update (should fail)
    update_response = client.put(
        f"/api/recipes/{recipe_id}",
        json={"title": "Hacked Title"},
        headers={"Authorization": f"Bearer {token_other}"}
    )
    assert update_response.status_code == status.HTTP_403_FORBIDDEN
    
    # Owner updates successfully
    owner_update = client.put(
        f"/api/recipes/{recipe_id}",
        json={"title": "Updated Title"},
        headers={"Authorization": f"Bearer {token_owner}"}
    )
    assert owner_update.status_code == status.HTTP_200_OK
    assert owner_update.json()["title"] == "Updated Title"


def test_delete_recipe_with_ownership(client, db):
    """Test deleting a recipe with ownership validation."""
    # Register and login owner
    client.post("/api/auth/register", json={"username": "owner2", "password": "password123"})
    login_owner = client.post("/api/auth/login", json={"username": "owner2", "password": "password123"})
    token_owner = login_owner.json()["access_token"]
    
    # Register and login other user
    client.post("/api/auth/register", json={"username": "other2", "password": "password123"})
    login_other = client.post("/api/auth/login", json={"username": "other2", "password": "password123"})
    token_other = login_other.json()["access_token"]
    
    # Owner creates recipe
    create_response = client.post(
        "/api/recipes",
        json={"title": "To Delete", "ingredients": ["a"], "steps": ["b"]},
        headers={"Authorization": f"Bearer {token_owner}"}
    )
    recipe_id = create_response.json()["id"]
    
    # Other user tries to delete (should fail)
    delete_response = client.delete(
        f"/api/recipes/{recipe_id}",
        headers={"Authorization": f"Bearer {token_other}"}
    )
    assert delete_response.status_code == status.HTTP_403_FORBIDDEN
    
    # Verify recipe still exists
    get_response = client.get(f"/api/recipes/{recipe_id}", headers={"Authorization": f"Bearer {token_owner}"})
    assert get_response.status_code == status.HTTP_200_OK
    
    # Owner deletes successfully
    owner_delete = client.delete(
        f"/api/recipes/{recipe_id}",
        headers={"Authorization": f"Bearer {token_owner}"}
    )
    assert owner_delete.status_code == status.HTTP_200_OK
    assert owner_delete.json()["message"] == "Recipe deleted successfully"
    
    # Verify recipe is deleted
    get_deleted = client.get(f"/api/recipes/{recipe_id}", headers={"Authorization": f"Bearer {token_owner}"})
    assert get_deleted.status_code == status.HTTP_404_NOT_FOUND


def test_recipe_not_found(client, db):
    """Test 404 error for non-existent recipes."""
    # Register and login
    client.post("/api/auth/register", json={"username": "testuser4", "password": "password123"})
    login_response = client.post("/api/auth/login", json={"username": "testuser4", "password": "password123"})
    token = login_response.json()["access_token"]
    
    # Try to get non-existent recipe
    response = client.get("/api/recipes/99999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    # Try to update non-existent recipe
    update_response = client.put(
        "/api/recipes/99999",
        json={"title": "New Title"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert update_response.status_code == status.HTTP_404_NOT_FOUND
    
    # Try to delete non-existent recipe
    delete_response = client.delete("/api/recipes/99999", headers={"Authorization": f"Bearer {token}"})
    assert delete_response.status_code == status.HTTP_404_NOT_FOUND


def test_unauthorized_access(client, db):
    """Test that endpoints require authentication."""
    # Try to create recipe without token
    response = client.post(
        "/api/recipes",
        json={"title": "Test", "ingredients": ["a"], "steps": ["b"]}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Try to get recipes without token
    response = client.get("/api/recipes")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY



def test_search_recipes_with_query(client, db):
    """Test searching recipes with various queries."""
    # Register and login
    client.post("/api/auth/register", json={"username": "searchuser", "password": "password123"})
    login_response = client.post("/api/auth/login", json={"username": "searchuser", "password": "password123"})
    token = login_response.json()["access_token"]
    
    # Create multiple recipes
    client.post(
        "/api/recipes",
        json={"title": "Chocolate Cake", "ingredients": ["chocolate"], "steps": ["bake"]},
        headers={"Authorization": f"Bearer {token}"}
    )
    client.post(
        "/api/recipes",
        json={"title": "Vanilla Cake", "ingredients": ["vanilla"], "steps": ["bake"]},
        headers={"Authorization": f"Bearer {token}"}
    )
    client.post(
        "/api/recipes",
        json={"title": "Chocolate Cookies", "ingredients": ["chocolate"], "steps": ["bake"]},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Search for "chocolate"
    response = client.get("/api/recipes?search=chocolate", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()
    assert len(results) == 2
    assert all("chocolate" in r["title"].lower() for r in results)
    
    # Search for "cake"
    response = client.get("/api/recipes?search=cake", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()
    assert len(results) == 2
    assert all("cake" in r["title"].lower() for r in results)
    
    # Search for "vanilla"
    response = client.get("/api/recipes?search=vanilla", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()
    assert len(results) == 1
    assert results[0]["title"] == "Vanilla Cake"


def test_search_case_insensitive(client, db):
    """Test that search is case-insensitive."""
    # Register and login
    client.post("/api/auth/register", json={"username": "caseuser", "password": "password123"})
    login_response = client.post("/api/auth/login", json={"username": "caseuser", "password": "password123"})
    token = login_response.json()["access_token"]
    
    # Create recipe with mixed case title
    client.post(
        "/api/recipes",
        json={"title": "Spaghetti Carbonara", "ingredients": ["pasta"], "steps": ["cook"]},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Search with lowercase
    response = client.get("/api/recipes?search=spaghetti", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    
    # Search with uppercase
    response = client.get("/api/recipes?search=CARBONARA", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    
    # Search with mixed case
    response = client.get("/api/recipes?search=SpAgHeTtI", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


def test_search_empty_results(client, db):
    """Test search returns empty results when no matches."""
    # Register and login
    client.post("/api/auth/register", json={"username": "emptyuser", "password": "password123"})
    login_response = client.post("/api/auth/login", json={"username": "emptyuser", "password": "password123"})
    token = login_response.json()["access_token"]
    
    # Create recipe
    client.post(
        "/api/recipes",
        json={"title": "Apple Pie", "ingredients": ["apples"], "steps": ["bake"]},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Search for non-existent term
    response = client.get("/api/recipes?search=banana", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()
    assert len(results) == 0


def test_search_user_isolation(client, db):
    """Test that search respects user boundaries."""
    # Register and login user1
    client.post("/api/auth/register", json={"username": "searchuser1", "password": "password123"})
    login1 = client.post("/api/auth/login", json={"username": "searchuser1", "password": "password123"})
    token1 = login1.json()["access_token"]
    
    # Register and login user2
    client.post("/api/auth/register", json={"username": "searchuser2", "password": "password123"})
    login2 = client.post("/api/auth/login", json={"username": "searchuser2", "password": "password123"})
    token2 = login2.json()["access_token"]
    
    # User1 creates recipe with "pasta"
    client.post(
        "/api/recipes",
        json={"title": "User1 Pasta Recipe", "ingredients": ["pasta"], "steps": ["cook"]},
        headers={"Authorization": f"Bearer {token1}"}
    )
    
    # User2 creates recipe with "pasta"
    client.post(
        "/api/recipes",
        json={"title": "User2 Pasta Recipe", "ingredients": ["pasta"], "steps": ["cook"]},
        headers={"Authorization": f"Bearer {token2}"}
    )
    
    # User1 searches for "pasta"
    response1 = client.get("/api/recipes?search=pasta", headers={"Authorization": f"Bearer {token1}"})
    assert response1.status_code == status.HTTP_200_OK
    results1 = response1.json()
    assert len(results1) == 1
    assert results1[0]["title"] == "User1 Pasta Recipe"
    
    # User2 searches for "pasta"
    response2 = client.get("/api/recipes?search=pasta", headers={"Authorization": f"Bearer {token2}"})
    assert response2.status_code == status.HTTP_200_OK
    results2 = response2.json()
    assert len(results2) == 1
    assert results2[0]["title"] == "User2 Pasta Recipe"


def test_search_without_query_returns_all(client, db):
    """Test that omitting search query returns all user recipes."""
    # Register and login
    client.post("/api/auth/register", json={"username": "alluser", "password": "password123"})
    login_response = client.post("/api/auth/login", json={"username": "alluser", "password": "password123"})
    token = login_response.json()["access_token"]
    
    # Create multiple recipes
    client.post(
        "/api/recipes",
        json={"title": "Recipe 1", "ingredients": ["a"], "steps": ["b"]},
        headers={"Authorization": f"Bearer {token}"}
    )
    client.post(
        "/api/recipes",
        json={"title": "Recipe 2", "ingredients": ["c"], "steps": ["d"]},
        headers={"Authorization": f"Bearer {token}"}
    )
    client.post(
        "/api/recipes",
        json={"title": "Recipe 3", "ingredients": ["e"], "steps": ["f"]},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Get all recipes without search query
    response = client.get("/api/recipes", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()
    assert len(results) == 3
