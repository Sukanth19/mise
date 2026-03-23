"""Quick test for nutrition endpoints"""
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base, engine
from sqlalchemy.orm import Session
import json

# Create test database
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_nutrition_endpoints():
    """Test nutrition endpoints work correctly"""
    
    # Register and login
    register_response = client.post("/api/auth/register", json={
        "username": "nutritiontest",
        "password": "testpass123"
    })
    assert register_response.status_code == 201
    
    login_response = client.post("/api/auth/login", json={
        "username": "nutritiontest",
        "password": "testpass123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a recipe
    recipe_response = client.post("/api/recipes", headers=headers, json={
        "title": "Healthy Salad",
        "ingredients": ["lettuce", "tomato", "cucumber"],
        "steps": ["Mix ingredients", "Add dressing"]
    })
    assert recipe_response.status_code == 201
    recipe_id = recipe_response.json()["id"]
    print(f"✓ Created recipe {recipe_id}")
    
    # Test 16.1: Add nutrition facts
    nutrition_response = client.post(
        f"/api/recipes/{recipe_id}/nutrition",
        headers=headers,
        json={
            "calories": 150.0,
            "protein_g": 5.0,
            "carbs_g": 20.0,
            "fat_g": 3.0,
            "fiber_g": 4.0
        }
    )
    assert nutrition_response.status_code == 201
    print(f"✓ Added nutrition facts: {nutrition_response.json()}")
    
    # Test 16.1: Get nutrition facts (total and per-serving)
    get_nutrition_response = client.get(
        f"/api/recipes/{recipe_id}/nutrition",
        headers=headers
    )
    assert get_nutrition_response.status_code == 200
    nutrition_data = get_nutrition_response.json()
    assert nutrition_data["nutrition_facts"] is not None
    assert nutrition_data["per_serving"] is not None
    print(f"✓ Retrieved nutrition facts with per-serving calculation")
    
    # Test 16.1: Update nutrition facts
    update_response = client.put(
        f"/api/recipes/{recipe_id}/nutrition",
        headers=headers,
        json={
            "calories": 200.0,
            "protein_g": 7.0
        }
    )
    assert update_response.status_code == 200
    print(f"✓ Updated nutrition facts")
    
    # Test 16.2: Set dietary labels
    labels_response = client.post(
        f"/api/recipes/{recipe_id}/dietary-labels",
        headers=headers,
        json={
            "labels": ["vegan", "gluten-free"]
        }
    )
    assert labels_response.status_code == 200
    assert labels_response.json()["labels"] == ["vegan", "gluten-free"]
    print(f"✓ Set dietary labels: {labels_response.json()['labels']}")
    
    # Test 16.2: Set allergen warnings
    allergens_response = client.post(
        f"/api/recipes/{recipe_id}/allergens",
        headers=headers,
        json={
            "allergens": ["nuts", "soy"]
        }
    )
    assert allergens_response.status_code == 200
    assert allergens_response.json()["allergens"] == ["nuts", "soy"]
    print(f"✓ Set allergen warnings: {allergens_response.json()['allergens']}")
    
    # Test 16.3: Create meal plan for nutrition summary
    meal_plan_response = client.post(
        "/api/meal-plans",
        headers=headers,
        json={
            "recipe_id": recipe_id,
            "meal_date": "2024-01-15",
            "meal_time": "lunch"
        }
    )
    assert meal_plan_response.status_code == 201
    print(f"✓ Created meal plan")
    
    # Test 16.3: Get meal plan nutrition summary
    summary_response = client.get(
        "/api/meal-plans/nutrition-summary?start_date=2024-01-15&end_date=2024-01-15",
        headers=headers
    )
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert "daily_totals" in summary
    assert "weekly_total" in summary
    assert "missing_nutrition_count" in summary
    print(f"✓ Retrieved nutrition summary: {len(summary['daily_totals'])} days")
    print(f"  Weekly total calories: {summary['weekly_total']['calories']}")
    print(f"  Missing nutrition count: {summary['missing_nutrition_count']}")
    
    print("\n✅ All nutrition endpoint tests passed!")

if __name__ == "__main__":
    test_nutrition_endpoints()
