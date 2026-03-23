"""Unit tests for meal plan API endpoints."""
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
from datetime import date, timedelta

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
        ingredients=["ingredient1"],
        steps=["step1"]
    )
    recipe = RecipeManager.create_recipe(db, user_id, recipe_data)
    return recipe


def test_create_meal_plan(db, auth_headers, test_recipe):
    """Test creating a meal plan."""
    headers, _ = auth_headers
    meal_date = date.today().strftime('%Y-%m-%d')
    
    response = client.post(
        "/api/meal-plans",
        json={
            "recipe_id": test_recipe.id,
            "meal_date": meal_date,
            "meal_time": "breakfast"
        },
        headers=headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["recipe_id"] == test_recipe.id
    assert data["meal_date"] == meal_date
    assert data["meal_time"] == "breakfast"


def test_get_meal_plans(db, auth_headers, test_recipe):
    """Test retrieving meal plans by date range."""
    headers, _ = auth_headers
    meal_date = date.today().strftime('%Y-%m-%d')
    
    # Create a meal plan first
    client.post(
        "/api/meal-plans",
        json={
            "recipe_id": test_recipe.id,
            "meal_date": meal_date,
            "meal_time": "lunch"
        },
        headers=headers
    )
    
    # Get meal plans
    start_date = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    end_date = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    response = client.get(
        f"/api/meal-plans?start_date={start_date}&end_date={end_date}",
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


def test_update_meal_plan(db, auth_headers, test_recipe):
    """Test updating a meal plan."""
    headers, _ = auth_headers
    meal_date = date.today().strftime('%Y-%m-%d')
    
    # Create a meal plan
    create_response = client.post(
        "/api/meal-plans",
        json={
            "recipe_id": test_recipe.id,
            "meal_date": meal_date,
            "meal_time": "breakfast"
        },
        headers=headers
    )
    meal_plan_id = create_response.json()["id"]
    
    # Update it
    response = client.put(
        f"/api/meal-plans/{meal_plan_id}",
        json={"meal_time": "dinner"},
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["meal_time"] == "dinner"


def test_delete_meal_plan(db, auth_headers, test_recipe):
    """Test deleting a meal plan."""
    headers, _ = auth_headers
    meal_date = date.today().strftime('%Y-%m-%d')
    
    # Create a meal plan
    create_response = client.post(
        "/api/meal-plans",
        json={
            "recipe_id": test_recipe.id,
            "meal_date": meal_date,
            "meal_time": "snack"
        },
        headers=headers
    )
    meal_plan_id = create_response.json()["id"]
    
    # Delete it
    response = client.delete(f"/api/meal-plans/{meal_plan_id}", headers=headers)
    
    assert response.status_code == 200
    assert response.json()["message"] == "Meal plan deleted successfully"


def test_create_template(db, auth_headers, test_recipe):
    """Test creating a meal plan template."""
    headers, _ = auth_headers
    
    response = client.post(
        "/api/meal-plan-templates",
        json={
            "name": "Test Template",
            "description": "Test description",
            "items": [
                {
                    "recipe_id": test_recipe.id,
                    "day_offset": 0,
                    "meal_time": "breakfast"
                },
                {
                    "recipe_id": test_recipe.id,
                    "day_offset": 1,
                    "meal_time": "dinner"
                }
            ]
        },
        headers=headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Template"
    assert len(data["items"]) == 2


def test_get_templates(db, auth_headers, test_recipe):
    """Test retrieving meal plan templates."""
    headers, _ = auth_headers
    
    # Create a template first
    client.post(
        "/api/meal-plan-templates",
        json={
            "name": "Test Template",
            "items": [
                {
                    "recipe_id": test_recipe.id,
                    "day_offset": 0,
                    "meal_time": "breakfast"
                }
            ]
        },
        headers=headers
    )
    
    # Get templates
    response = client.get("/api/meal-plan-templates", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


def test_apply_template(db, auth_headers, test_recipe):
    """Test applying a meal plan template."""
    headers, _ = auth_headers
    
    # Create a template
    create_response = client.post(
        "/api/meal-plan-templates",
        json={
            "name": "Test Template",
            "items": [
                {
                    "recipe_id": test_recipe.id,
                    "day_offset": 0,
                    "meal_time": "breakfast"
                },
                {
                    "recipe_id": test_recipe.id,
                    "day_offset": 1,
                    "meal_time": "lunch"
                }
            ]
        },
        headers=headers
    )
    template_id = create_response.json()["id"]
    
    # Apply template
    apply_date = (date.today() + timedelta(days=7)).strftime('%Y-%m-%d')
    response = client.post(
        f"/api/meal-plan-templates/{template_id}/apply?start_date={apply_date}",
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["created_count"] == 2


def test_delete_template(db, auth_headers, test_recipe):
    """Test deleting a meal plan template."""
    headers, _ = auth_headers
    
    # Create a template
    create_response = client.post(
        "/api/meal-plan-templates",
        json={
            "name": "Test Template",
            "items": [
                {
                    "recipe_id": test_recipe.id,
                    "day_offset": 0,
                    "meal_time": "breakfast"
                }
            ]
        },
        headers=headers
    )
    template_id = create_response.json()["id"]
    
    # Delete it
    response = client.delete(f"/api/meal-plan-templates/{template_id}", headers=headers)
    
    assert response.status_code == 200
    assert response.json()["message"] == "Template deleted successfully"


def test_export_ical(db, auth_headers, test_recipe):
    """Test exporting meal plans to iCal format."""
    headers, _ = auth_headers
    meal_date = date.today().strftime('%Y-%m-%d')
    
    # Create a meal plan
    client.post(
        "/api/meal-plans",
        json={
            "recipe_id": test_recipe.id,
            "meal_date": meal_date,
            "meal_time": "breakfast"
        },
        headers=headers
    )
    
    # Export to iCal
    start_date = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    end_date = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    response = client.get(
        f"/api/meal-plans/export?start_date={start_date}&end_date={end_date}",
        headers=headers
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/calendar"
    assert len(response.content) > 0
