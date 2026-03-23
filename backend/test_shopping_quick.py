"""Quick test of shopping list endpoints."""
import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"

from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base, engine
from app.services.auth_service import AuthService
from app.services.recipe_service import RecipeManager
from app.schemas import RecipeCreate

# Create tables
Base.metadata.create_all(bind=engine)

client = TestClient(app)

# Create test user
db = next(get_db())
user = AuthService.create_user(db, "testuser123", "password123")
token = AuthService.create_token(user.id)
headers = {"Authorization": f"Bearer {token}"}

# Create test recipe
recipe_data = RecipeCreate(
    title="Test Recipe",
    ingredients=["2 cups flour", "1 cup sugar", "3 eggs"],
    steps=["Mix ingredients", "Bake"]
)
recipe = RecipeManager.create_recipe(db, user.id, recipe_data)

print(f"Created recipe with ID: {recipe.id}")

# Test 1: Create shopping list
print("\n=== Test 1: Create Shopping List ===")
response = client.post(
    "/api/shopping-lists",
    json={
        "name": "My Shopping List",
        "recipe_ids": [recipe.id]
    },
    headers=headers
)
print(f"Status: {response.status_code}")
if response.status_code == 201:
    data = response.json()
    print(f"Created list: {data['name']}")
    print(f"Items count: {len(data['items'])}")
    list_id = data['id']
    item_id = data['items'][0]['id'] if data['items'] else None
    print("✓ Test 1 PASSED")
else:
    print(f"✗ Test 1 FAILED: {response.text}")
    exit(1)

# Test 2: Get shopping lists
print("\n=== Test 2: Get Shopping Lists ===")
response = client.get("/api/shopping-lists", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Found {len(data)} lists")
    print("✓ Test 2 PASSED")
else:
    print(f"✗ Test 2 FAILED: {response.text}")
    exit(1)

# Test 3: Update item status
print("\n=== Test 3: Update Item Status ===")
if item_id:
    response = client.patch(
        f"/api/shopping-lists/{list_id}/items/{item_id}",
        json={"is_checked": True},
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Item checked: {data['is_checked']}")
        print("✓ Test 3 PASSED")
    else:
        print(f"✗ Test 3 FAILED: {response.text}")
        exit(1)

# Test 4: Add custom item
print("\n=== Test 4: Add Custom Item ===")
response = client.post(
    f"/api/shopping-lists/{list_id}/items",
    json={
        "ingredient_name": "Paper towels",
        "quantity": "1 roll",
        "category": "other"
    },
    headers=headers
)
print(f"Status: {response.status_code}")
if response.status_code == 201:
    data = response.json()
    print(f"Added custom item: {data['ingredient_name']}")
    print(f"Is custom: {data['is_custom']}")
    print("✓ Test 4 PASSED")
else:
    print(f"✗ Test 4 FAILED: {response.text}")
    exit(1)

# Test 5: Share shopping list
print("\n=== Test 5: Share Shopping List ===")
response = client.post(
    f"/api/shopping-lists/{list_id}/share",
    headers=headers
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Share token: {data['share_token'][:20]}...")
    share_token = data['share_token']
    print("✓ Test 5 PASSED")
else:
    print(f"✗ Test 5 FAILED: {response.text}")
    exit(1)

# Test 6: Access shared list
print("\n=== Test 6: Access Shared List ===")
response = client.get(f"/api/shopping-lists/shared/{share_token}")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Accessed shared list: {data['name']}")
    print("✓ Test 6 PASSED")
else:
    print(f"✗ Test 6 FAILED: {response.text}")
    exit(1)

print("\n=== ALL TESTS PASSED ===")
