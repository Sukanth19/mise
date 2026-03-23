"""Quick smoke test for meal plan endpoints."""
import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"

from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base, engine
from app.services.auth_service import AuthService
from app.services.recipe_service import RecipeManager
from app.schemas import RecipeCreate
from datetime import date, timedelta

# Create test database
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_meal_plan_endpoints():
    """Test basic meal plan endpoint functionality."""
    # Create a test user
    db = next(get_db())
    user = AuthService.create_user(db, "testuser_meal", "password123")
    token = AuthService.create_token(user.id)
    
    # Create a test recipe
    recipe_data = RecipeCreate(
        title="Test Recipe",
        ingredients=["ingredient1"],
        steps=["step1"]
    )
    recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Create meal plan
    meal_date = date.today().strftime('%Y-%m-%d')
    response = client.post(
        "/api/meal-plans",
        json={
            "recipe_id": recipe.id,
            "meal_date": meal_date,
            "meal_time": "breakfast"
        },
        headers=headers
    )
    assert response.status_code == 201, f"Create failed: {response.json()}"
    meal_plan = response.json()
    print(f"✓ Created meal plan: {meal_plan['id']}")
    
    # Test 2: Get meal plans
    start_date = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    end_date = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    response = client.get(
        f"/api/meal-plans?start_date={start_date}&end_date={end_date}",
        headers=headers
    )
    assert response.status_code == 200, f"Get failed: {response.json()}"
    meal_plans = response.json()
    assert len(meal_plans) > 0, "Should have at least one meal plan"
    print(f"✓ Retrieved {len(meal_plans)} meal plans")
    
    # Test 3: Update meal plan
    response = client.put(
        f"/api/meal-plans/{meal_plan['id']}",
        json={"meal_time": "lunch"},
        headers=headers
    )
    assert response.status_code == 200, f"Update failed: {response.json()}"
    updated = response.json()
    assert updated['meal_time'] == "lunch", "Meal time should be updated"
    print(f"✓ Updated meal plan to lunch")
    
    # Test 4: Create template
    response = client.post(
        "/api/meal-plan-templates",
        json={
            "name": "Test Template",
            "description": "Test description",
            "items": [
                {
                    "recipe_id": recipe.id,
                    "day_offset": 0,
                    "meal_time": "breakfast"
                },
                {
                    "recipe_id": recipe.id,
                    "day_offset": 1,
                    "meal_time": "dinner"
                }
            ]
        },
        headers=headers
    )
    assert response.status_code == 201, f"Template create failed: {response.json()}"
    template = response.json()
    print(f"✓ Created template: {template['id']}")
    
    # Test 5: Get templates
    response = client.get("/api/meal-plan-templates", headers=headers)
    assert response.status_code == 200, f"Get templates failed: {response.json()}"
    templates = response.json()
    assert len(templates) > 0, "Should have at least one template"
    print(f"✓ Retrieved {len(templates)} templates")
    
    # Test 6: Apply template
    apply_date = (date.today() + timedelta(days=7)).strftime('%Y-%m-%d')
    response = client.post(
        f"/api/meal-plan-templates/{template['id']}/apply?start_date={apply_date}",
        headers=headers
    )
    assert response.status_code == 200, f"Apply template failed: {response.json()}"
    result = response.json()
    assert result['created_count'] == 2, "Should create 2 meal plans from template"
    print(f"✓ Applied template, created {result['created_count']} meal plans")
    
    # Test 7: Export to iCal
    response = client.get(
        f"/api/meal-plans/export?start_date={start_date}&end_date={end_date}",
        headers=headers
    )
    assert response.status_code == 200, f"Export failed: {response.status_code}"
    assert response.headers['content-type'] == 'text/calendar', "Should return iCal format"
    print(f"✓ Exported meal plans to iCal")
    
    # Test 8: Delete meal plan
    response = client.delete(f"/api/meal-plans/{meal_plan['id']}", headers=headers)
    assert response.status_code == 200, f"Delete failed: {response.json()}"
    print(f"✓ Deleted meal plan")
    
    # Test 9: Delete template
    response = client.delete(f"/api/meal-plan-templates/{template['id']}", headers=headers)
    assert response.status_code == 200, f"Delete template failed: {response.json()}"
    print(f"✓ Deleted template")
    
    print("\n✅ All meal plan endpoint tests passed!")

if __name__ == "__main__":
    test_meal_plan_endpoints()
