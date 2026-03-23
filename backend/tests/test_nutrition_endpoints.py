"""Unit tests for nutrition endpoints."""
import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"

import pytest
from fastapi import status


# ============================================================================
# Task 16.1: Nutrition Facts Endpoints Tests
# ============================================================================

def test_add_nutrition_facts(client, db):
    """Test adding nutrition facts to a recipe."""
    # Register and login
    client.post("/api/auth/register", json={"username": "nutritionuser1", "password": "password123"})
    login_response = client.post("/api/auth/login", json={"username": "nutritionuser1", "password": "password123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create recipe
    recipe_response = client.post(
        "/api/recipes",
        json={"title": "Healthy Salad", "ingredients": ["lettuce"], "steps": ["mix"]},
        headers=headers
    )
    recipe_id = recipe_response.json()["id"]
    
    # Add nutrition facts
    response = client.post(
        f"/api/recipes/{recipe_id}/nutrition",
        json={
            "calories": 150.0,
            "protein_g": 5.0,
            "carbs_g": 20.0,
            "fat_g": 3.0,
            "fiber_g": 4.0
        },
        headers=headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["recipe_id"] == recipe_id
    assert data["calories"] == 150.0
    assert data["protein_g"] == 5.0


def test_update_nutrition_facts(client, db):
    """Test updating nutrition facts for a recipe."""
    # Register and login
    client.post("/api/auth/register", json={"username": "nutritionuser2", "password": "password123"})
    login_response = client.post("/api/auth/login", json={"username": "nutritionuser2", "password": "password123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create recipe
    recipe_response = client.post(
        "/api/recipes",
        json={"title": "Pasta", "ingredients": ["pasta"], "steps": ["cook"]},
        headers=headers
    )
    recipe_id = recipe_response.json()["id"]
    
    # Add nutrition facts
    client.post(
        f"/api/recipes/{recipe_id}/nutrition",
        json={"calories": 300.0, "protein_g": 10.0},
        headers=headers
    )
    
    # Update nutrition facts
    response = client.put(
        f"/api/recipes/{recipe_id}/nutrition",
        json={"calories": 350.0, "protein_g": 12.0},
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["calories"] == 350.0
    assert data["protein_g"] == 12.0


def test_get_nutrition_facts_with_per_serving(client, db):
    """Test getting nutrition facts with per-serving calculation."""
    # Register and login
    client.post("/api/auth/register", json={"username": "nutritionuser3", "password": "password123"})
    login_response = client.post("/api/auth/login", json={"username": "nutritionuser3", "password": "password123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create recipe with servings
    recipe_response = client.post(
        "/api/recipes",
        json={"title": "Pizza", "ingredients": ["dough"], "steps": ["bake"]},
        headers=headers
    )
    recipe_id = recipe_response.json()["id"]
    
    # Add nutrition facts
    client.post(
        f"/api/recipes/{recipe_id}/nutrition",
        json={"calories": 800.0, "protein_g": 40.0, "carbs_g": 100.0},
        headers=headers
    )
    
    # Get nutrition facts
    response = client.get(
        f"/api/recipes/{recipe_id}/nutrition",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["nutrition_facts"] is not None
    assert data["per_serving"] is not None
    # Default servings is 1, so per_serving should equal total
    assert data["per_serving"]["calories"] == 800.0


def test_nutrition_facts_negative_values_rejected(client, db):
    """Test that negative nutrition values are rejected."""
    # Register and login
    client.post("/api/auth/register", json={"username": "nutritionuser4", "password": "password123"})
    login_response = client.post("/api/auth/login", json={"username": "nutritionuser4", "password": "password123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create recipe
    recipe_response = client.post(
        "/api/recipes",
        json={"title": "Test", "ingredients": ["a"], "steps": ["b"]},
        headers=headers
    )
    recipe_id = recipe_response.json()["id"]
    
    # Try to add nutrition with negative values (should be caught by Pydantic)
    response = client.post(
        f"/api/recipes/{recipe_id}/nutrition",
        json={"calories": -100.0},
        headers=headers
    )
    
    # Pydantic validation should reject this
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ============================================================================
# Task 16.2: Dietary Labels and Allergen Endpoints Tests
# ============================================================================

def test_set_dietary_labels(client, db):
    """Test setting dietary labels for a recipe."""
    # Register and login
    client.post("/api/auth/register", json={"username": "nutritionuser5", "password": "password123"})
    login_response = client.post("/api/auth/login", json={"username": "nutritionuser5", "password": "password123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create recipe
    recipe_response = client.post(
        "/api/recipes",
        json={"title": "Vegan Bowl", "ingredients": ["quinoa"], "steps": ["cook"]},
        headers=headers
    )
    recipe_id = recipe_response.json()["id"]
    
    # Set dietary labels
    response = client.post(
        f"/api/recipes/{recipe_id}/dietary-labels",
        json={"labels": ["vegan", "gluten-free"]},
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert set(data["labels"]) == {"vegan", "gluten-free"}


def test_set_invalid_dietary_label(client, db):
    """Test that invalid dietary labels are rejected."""
    # Register and login
    client.post("/api/auth/register", json={"username": "nutritionuser6", "password": "password123"})
    login_response = client.post("/api/auth/login", json={"username": "nutritionuser6", "password": "password123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create recipe
    recipe_response = client.post(
        "/api/recipes",
        json={"title": "Test", "ingredients": ["a"], "steps": ["b"]},
        headers=headers
    )
    recipe_id = recipe_response.json()["id"]
    
    # Try to set invalid label
    response = client.post(
        f"/api/recipes/{recipe_id}/dietary-labels",
        json={"labels": ["invalid-label"]},
        headers=headers
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_set_allergen_warnings(client, db):
    """Test setting allergen warnings for a recipe."""
    # Register and login
    client.post("/api/auth/register", json={"username": "nutritionuser7", "password": "password123"})
    login_response = client.post("/api/auth/login", json={"username": "nutritionuser7", "password": "password123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create recipe
    recipe_response = client.post(
        "/api/recipes",
        json={"title": "Peanut Butter Cookies", "ingredients": ["peanuts"], "steps": ["bake"]},
        headers=headers
    )
    recipe_id = recipe_response.json()["id"]
    
    # Set allergen warnings
    response = client.post(
        f"/api/recipes/{recipe_id}/allergens",
        json={"allergens": ["nuts", "eggs"]},
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert set(data["allergens"]) == {"nuts", "eggs"}


def test_set_invalid_allergen(client, db):
    """Test that invalid allergens are rejected."""
    # Register and login
    client.post("/api/auth/register", json={"username": "nutritionuser8", "password": "password123"})
    login_response = client.post("/api/auth/login", json={"username": "nutritionuser8", "password": "password123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create recipe
    recipe_response = client.post(
        "/api/recipes",
        json={"title": "Test", "ingredients": ["a"], "steps": ["b"]},
        headers=headers
    )
    recipe_id = recipe_response.json()["id"]
    
    # Try to set invalid allergen
    response = client.post(
        f"/api/recipes/{recipe_id}/allergens",
        json={"allergens": ["invalid-allergen"]},
        headers=headers
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# ============================================================================
# Task 16.3: Meal Plan Nutrition Summary Endpoint Tests
# ============================================================================

def test_meal_plan_nutrition_summary(client, db):
    """Test getting nutrition summary for a meal plan date range."""
    # Register and login
    client.post("/api/auth/register", json={"username": "nutritionuser9", "password": "password123"})
    login_response = client.post("/api/auth/login", json={"username": "nutritionuser9", "password": "password123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create recipe with nutrition
    recipe_response = client.post(
        "/api/recipes",
        json={"title": "Breakfast", "ingredients": ["eggs"], "steps": ["cook"]},
        headers=headers
    )
    recipe_id = recipe_response.json()["id"]
    
    client.post(
        f"/api/recipes/{recipe_id}/nutrition",
        json={"calories": 300.0, "protein_g": 20.0, "carbs_g": 10.0},
        headers=headers
    )
    
    # Create meal plan
    client.post(
        "/api/meal-plans",
        json={"recipe_id": recipe_id, "meal_date": "2024-01-15", "meal_time": "breakfast"},
        headers=headers
    )
    
    # Get nutrition summary
    response = client.get(
        "/api/meal-plans/nutrition-summary?start_date=2024-01-15&end_date=2024-01-15",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "daily_totals" in data
    assert "weekly_total" in data
    assert "missing_nutrition_count" in data
    assert len(data["daily_totals"]) == 1
    assert data["daily_totals"][0]["calories"] == 300.0
    assert data["weekly_total"]["calories"] == 300.0


def test_meal_plan_nutrition_summary_missing_nutrition(client, db):
    """Test nutrition summary with recipes missing nutrition info."""
    # Register and login
    client.post("/api/auth/register", json={"username": "nutritionuser10", "password": "password123"})
    login_response = client.post("/api/auth/login", json={"username": "nutritionuser10", "password": "password123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create recipe WITHOUT nutrition
    recipe_response = client.post(
        "/api/recipes",
        json={"title": "Lunch", "ingredients": ["sandwich"], "steps": ["make"]},
        headers=headers
    )
    recipe_id = recipe_response.json()["id"]
    
    # Create meal plan
    client.post(
        "/api/meal-plans",
        json={"recipe_id": recipe_id, "meal_date": "2024-01-16", "meal_time": "lunch"},
        headers=headers
    )
    
    # Get nutrition summary
    response = client.get(
        "/api/meal-plans/nutrition-summary?start_date=2024-01-16&end_date=2024-01-16",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["missing_nutrition_count"] == 1
    assert data["weekly_total"]["calories"] == 0.0


def test_meal_plan_nutrition_summary_invalid_date_format(client, db):
    """Test nutrition summary with invalid date format."""
    # Register and login
    client.post("/api/auth/register", json={"username": "nutritionuser11", "password": "password123"})
    login_response = client.post("/api/auth/login", json={"username": "nutritionuser11", "password": "password123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to get summary with invalid date
    response = client.get(
        "/api/meal-plans/nutrition-summary?start_date=invalid&end_date=2024-01-15",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_meal_plan_nutrition_summary_invalid_date_range(client, db):
    """Test nutrition summary with start_date after end_date."""
    # Register and login
    client.post("/api/auth/register", json={"username": "nutritionuser12", "password": "password123"})
    login_response = client.post("/api/auth/login", json={"username": "nutritionuser12", "password": "password123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to get summary with invalid range
    response = client.get(
        "/api/meal-plans/nutrition-summary?start_date=2024-01-20&end_date=2024-01-15",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
