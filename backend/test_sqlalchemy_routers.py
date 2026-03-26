"""Quick test to verify SQLAlchemy routers work correctly."""
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models import User, Recipe, Collection
from passlib.context import CryptContext
from jose import jwt
from app.config import settings

# Create test client
client = TestClient(app)

# Setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def setup_test_db():
    """Create tables and test user."""
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Create test user
        test_user = db.query(User).filter(User.username == "testuser").first()
        if not test_user:
            # Use a pre-hashed password to avoid bcrypt issues
            test_user = User(username="testuser", password_hash="$2b$12$dummy_hash_for_testing")
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
        
        return test_user.id
    finally:
        db.close()

def get_auth_token(user_id: int) -> str:
    """Generate auth token for testing."""
    from datetime import datetime, timedelta
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode = {"sub": str(user_id), "exp": expire}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def test_recipes_endpoint():
    """Test recipes endpoints."""
    print("\n=== Testing Recipes Endpoints ===")
    
    user_id = setup_test_db()
    token = get_auth_token(user_id)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test GET /api/recipes
    response = client.get("/api/recipes", headers=headers)
    print(f"GET /api/recipes: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    # Test POST /api/recipes
    recipe_data = {
        "title": "Test Recipe",
        "ingredients": ["ingredient 1", "ingredient 2"],
        "steps": ["step 1", "step 2"],
        "tags": ["test"],
        "image_url": None,
        "reference_link": None
    }
    response = client.post("/api/recipes", json=recipe_data, headers=headers)
    print(f"POST /api/recipes: {response.status_code}")
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    recipe_id = response.json()["id"]
    
    # Test GET /api/recipes/{recipe_id}
    response = client.get(f"/api/recipes/{recipe_id}", headers=headers)
    print(f"GET /api/recipes/{recipe_id}: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    # Test GET /api/recipes/filter
    response = client.get("/api/recipes/filter?sort_by=date&sort_order=desc", headers=headers)
    print(f"GET /api/recipes/filter: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    print("✓ All recipe tests passed!")
    return recipe_id

def test_collections_endpoint():
    """Test collections endpoints."""
    print("\n=== Testing Collections Endpoints ===")
    
    user_id = setup_test_db()
    token = get_auth_token(user_id)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test GET /api/collections
    response = client.get("/api/collections", headers=headers)
    print(f"GET /api/collections: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    # Test POST /api/collections
    collection_data = {
        "name": "Test Collection",
        "description": "A test collection",
        "cover_image_url": None,
        "parent_collection_id": None
    }
    response = client.post("/api/collections", json=collection_data, headers=headers)
    print(f"POST /api/collections: {response.status_code}")
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    collection_id = response.json()["id"]
    
    # Test GET /api/collections/{collection_id}
    response = client.get(f"/api/collections/{collection_id}", headers=headers)
    print(f"GET /api/collections/{collection_id}: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    print("✓ All collection tests passed!")
    return collection_id

if __name__ == "__main__":
    try:
        recipe_id = test_recipes_endpoint()
        collection_id = test_collections_endpoint()
        print("\n✓✓✓ All tests passed! ✓✓✓")
        print(f"\nCreated test recipe ID: {recipe_id}")
        print(f"Created test collection ID: {collection_id}")
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
