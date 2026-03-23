"""Unit tests for rating endpoints."""
import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"

import pytest
from fastapi import status


def test_rating_boundary_value_1(client, db):
    """Test rating with boundary value 1 (minimum valid)."""
    # Register and login
    client.post("/api/auth/register", json={"username": "ratinguser1", "password": "password123"})
    login_response = client.post("/api/auth/login", json={"username": "ratinguser1", "password": "password123"})
    token = login_response.json()["access_token"]
    
    # Create recipe
    recipe_response = client.post(
        "/api/recipes",
        json={"title": "Test Recipe", "ingredients": ["a"], "steps": ["b"]},
        headers={"Authorization": f"Bearer {token}"}
    )
    recipe_id = recipe_response.json()["id"]
    
    # Create rating with value 1
    response = client.post(
        f"/api/recipes/{recipe_id}/rating",
        json={"rating": 1},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["rating"] == 1
    assert data["recipe_id"] == recipe_id


def test_rating_boundary_value_5(client, db):
    """Test rating with boundary value 5 (maximum valid)."""
    # Register and login
    client.post("/api/auth/register", json={"username": "ratinguser2", "password": "password123"})
    login_response = client.post("/api/auth/login", json={"username": "ratinguser2", "password": "password123"})
    token = login_response.json()["access_token"]
    
    # Create recipe
    recipe_response = client.post(
        "/api/recipes",
        json={"title": "Test Recipe", "ingredients": ["a"], "steps": ["b"]},
        headers={"Authorization": f"Bearer {token}"}
    )
    recipe_id = recipe_response.json()["id"]
    
    # Create rating with value 5
    response = client.post(
        f"/api/recipes/{recipe_id}/rating",
        json={"rating": 5},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["rating"] == 5
    assert data["recipe_id"] == recipe_id


def test_rating_boundary_value_0(client, db):
    """Test rating with boundary value 0 (below minimum - invalid)."""
    # Register and login
    client.post("/api/auth/register", json={"username": "ratinguser3", "password": "password123"})
    login_response = client.post("/api/auth/login", json={"username": "ratinguser3", "password": "password123"})
    token = login_response.json()["access_token"]
    
    # Create recipe
    recipe_response = client.post(
        "/api/recipes",
        json={"title": "Test Recipe", "ingredients": ["a"], "steps": ["b"]},
        headers={"Authorization": f"Bearer {token}"}
    )
    recipe_id = recipe_response.json()["id"]
    
    # Try to create rating with value 0 (should fail validation at schema level)
    response = client.post(
        f"/api/recipes/{recipe_id}/rating",
        json={"rating": 0},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Pydantic validation should catch this
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_rating_boundary_value_6(client, db):
    """Test rating with boundary value 6 (above maximum - invalid)."""
    # Register and login
    client.post("/api/auth/register", json={"username": "ratinguser4", "password": "password123"})
    login_response = client.post("/api/auth/login", json={"username": "ratinguser4", "password": "password123"})
    token = login_response.json()["access_token"]
    
    # Create recipe
    recipe_response = client.post(
        "/api/recipes",
        json={"title": "Test Recipe", "ingredients": ["a"], "steps": ["b"]},
        headers={"Authorization": f"Bearer {token}"}
    )
    recipe_id = recipe_response.json()["id"]
    
    # Try to create rating with value 6 (should fail validation at schema level)
    response = client.post(
        f"/api/recipes/{recipe_id}/rating",
        json={"rating": 6},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Pydantic validation should catch this
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_duplicate_rating_handling(client, db):
    """Test that creating a duplicate rating returns appropriate error."""
    # Register and login
    client.post("/api/auth/register", json={"username": "duprating", "password": "password123"})
    login_response = client.post("/api/auth/login", json={"username": "duprating", "password": "password123"})
    token = login_response.json()["access_token"]
    
    # Create recipe
    recipe_response = client.post(
        "/api/recipes",
        json={"title": "Test Recipe", "ingredients": ["a"], "steps": ["b"]},
        headers={"Authorization": f"Bearer {token}"}
    )
    recipe_id = recipe_response.json()["id"]
    
    # Create first rating
    first_response = client.post(
        f"/api/recipes/{recipe_id}/rating",
        json={"rating": 3},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert first_response.status_code == status.HTTP_201_CREATED
    
    # Try to create duplicate rating (should fail)
    duplicate_response = client.post(
        f"/api/recipes/{recipe_id}/rating",
        json={"rating": 4},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert duplicate_response.status_code == status.HTTP_409_CONFLICT
    assert "already exists" in duplicate_response.json()["detail"].lower()
    
    # Verify original rating is unchanged
    get_response = client.get(
        f"/api/recipes/{recipe_id}/rating",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_response.status_code == status.HTTP_200_OK
    assert get_response.json()["rating"] == 3


def test_rating_for_nonexistent_recipe(client, db):
    """Test creating a rating for a non-existent recipe."""
    # Register and login
    client.post("/api/auth/register", json={"username": "norecipe", "password": "password123"})
    login_response = client.post("/api/auth/login", json={"username": "norecipe", "password": "password123"})
    token = login_response.json()["access_token"]
    
    # Try to create rating for non-existent recipe
    response = client.post(
        "/api/recipes/99999/rating",
        json={"rating": 4},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()


def test_update_rating_success(client, db):
    """Test successfully updating an existing rating."""
    # Register and login
    client.post("/api/auth/register", json={"username": "updaterating", "password": "password123"})
    login_response = client.post("/api/auth/login", json={"username": "updaterating", "password": "password123"})
    token = login_response.json()["access_token"]
    
    # Create recipe
    recipe_response = client.post(
        "/api/recipes",
        json={"title": "Test Recipe", "ingredients": ["a"], "steps": ["b"]},
        headers={"Authorization": f"Bearer {token}"}
    )
    recipe_id = recipe_response.json()["id"]
    
    # Create initial rating
    create_response = client.post(
        f"/api/recipes/{recipe_id}/rating",
        json={"rating": 2},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    rating_id = create_response.json()["id"]
    
    # Update rating
    update_response = client.put(
        f"/api/recipes/{recipe_id}/rating",
        json={"rating": 5},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert update_response.status_code == status.HTTP_200_OK
    data = update_response.json()
    assert data["rating"] == 5
    assert data["id"] == rating_id  # Same rating record
    
    # Verify updated rating
    get_response = client.get(
        f"/api/recipes/{recipe_id}/rating",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_response.status_code == status.HTTP_200_OK
    assert get_response.json()["rating"] == 5


def test_update_nonexistent_rating(client, db):
    """Test updating a rating that doesn't exist."""
    # Register and login
    client.post("/api/auth/register", json={"username": "noupdaterating", "password": "password123"})
    login_response = client.post("/api/auth/login", json={"username": "noupdaterating", "password": "password123"})
    token = login_response.json()["access_token"]
    
    # Create recipe
    recipe_response = client.post(
        "/api/recipes",
        json={"title": "Test Recipe", "ingredients": ["a"], "steps": ["b"]},
        headers={"Authorization": f"Bearer {token}"}
    )
    recipe_id = recipe_response.json()["id"]
    
    # Try to update rating that doesn't exist
    response = client.put(
        f"/api/recipes/{recipe_id}/rating",
        json={"rating": 4},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()


def test_get_rating_success(client, db):
    """Test successfully retrieving a rating."""
    # Register and login
    client.post("/api/auth/register", json={"username": "getrating", "password": "password123"})
    login_response = client.post("/api/auth/login", json={"username": "getrating", "password": "password123"})
    token = login_response.json()["access_token"]
    
    # Create recipe
    recipe_response = client.post(
        "/api/recipes",
        json={"title": "Test Recipe", "ingredients": ["a"], "steps": ["b"]},
        headers={"Authorization": f"Bearer {token}"}
    )
    recipe_id = recipe_response.json()["id"]
    
    # Create rating
    create_response = client.post(
        f"/api/recipes/{recipe_id}/rating",
        json={"rating": 4},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    
    # Get rating
    get_response = client.get(
        f"/api/recipes/{recipe_id}/rating",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert get_response.status_code == status.HTTP_200_OK
    data = get_response.json()
    assert data["rating"] == 4
    assert data["recipe_id"] == recipe_id


def test_get_nonexistent_rating(client, db):
    """Test retrieving a rating that doesn't exist."""
    # Register and login
    client.post("/api/auth/register", json={"username": "nogetrating", "password": "password123"})
    login_response = client.post("/api/auth/login", json={"username": "nogetrating", "password": "password123"})
    token = login_response.json()["access_token"]
    
    # Create recipe
    recipe_response = client.post(
        "/api/recipes",
        json={"title": "Test Recipe", "ingredients": ["a"], "steps": ["b"]},
        headers={"Authorization": f"Bearer {token}"}
    )
    recipe_id = recipe_response.json()["id"]
    
    # Try to get rating that doesn't exist
    response = client.get(
        f"/api/recipes/{recipe_id}/rating",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()


def test_rating_user_isolation(client, db):
    """Test that users can only see their own ratings."""
    # Register and login user1
    client.post("/api/auth/register", json={"username": "ratinguser1iso", "password": "password123"})
    login1 = client.post("/api/auth/login", json={"username": "ratinguser1iso", "password": "password123"})
    token1 = login1.json()["access_token"]
    
    # Register and login user2
    client.post("/api/auth/register", json={"username": "ratinguser2iso", "password": "password123"})
    login2 = client.post("/api/auth/login", json={"username": "ratinguser2iso", "password": "password123"})
    token2 = login2.json()["access_token"]
    
    # User1 creates recipe
    recipe_response = client.post(
        "/api/recipes",
        json={"title": "Shared Recipe", "ingredients": ["a"], "steps": ["b"]},
        headers={"Authorization": f"Bearer {token1}"}
    )
    recipe_id = recipe_response.json()["id"]
    
    # User1 creates rating
    user1_rating = client.post(
        f"/api/recipes/{recipe_id}/rating",
        json={"rating": 3},
        headers={"Authorization": f"Bearer {token1}"}
    )
    assert user1_rating.status_code == status.HTTP_201_CREATED
    
    # User2 creates different rating for same recipe
    user2_rating = client.post(
        f"/api/recipes/{recipe_id}/rating",
        json={"rating": 5},
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert user2_rating.status_code == status.HTTP_201_CREATED
    
    # User1 retrieves their rating
    user1_get = client.get(
        f"/api/recipes/{recipe_id}/rating",
        headers={"Authorization": f"Bearer {token1}"}
    )
    assert user1_get.status_code == status.HTTP_200_OK
    assert user1_get.json()["rating"] == 3
    
    # User2 retrieves their rating
    user2_get = client.get(
        f"/api/recipes/{recipe_id}/rating",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert user2_get.status_code == status.HTTP_200_OK
    assert user2_get.json()["rating"] == 5
