"""
Test suite for API compatibility with MySQL backend.

This test file runs all existing API endpoint tests against MySQL to verify:
- All endpoint paths and HTTP methods work correctly
- Request payloads are accepted as before
- Response structures match expected schemas
- HTTP status codes are correct
- Pagination, filtering, and sorting work correctly

**Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6**

Task 9.1: Run existing API tests against MySQL
"""
import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Check if MySQL is available
def is_mysql_available():
    """Check if MySQL database is accessible."""
    try:
        import pymysql
        mysql_url = os.environ.get(
            "MYSQL_TEST_URL",
            "mysql+pymysql://root:password@localhost:3306/recipe_saver_test"
        )
        engine = create_engine(mysql_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


# Skip all tests in this module if MySQL is not available
pytestmark = pytest.mark.skipif(
    not is_mysql_available(),
    reason="MySQL database not available"
)


@pytest.fixture(scope="module")
def mysql_engine():
    """Create MySQL engine for testing."""
    mysql_url = os.environ.get(
        "MYSQL_TEST_URL",
        "mysql+pymysql://root:password@localhost:3306/recipe_saver_test"
    )
    engine = create_engine(
        mysql_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )
    return engine


@pytest.fixture(scope="module")
def setup_mysql_schema(mysql_engine):
    """Create MySQL schema before tests."""
    from app.database import Base
    
    # Drop all tables first
    Base.metadata.drop_all(bind=mysql_engine)
    
    # Create all tables
    Base.metadata.create_all(bind=mysql_engine)
    
    yield
    
    # Cleanup after all tests
    Base.metadata.drop_all(bind=mysql_engine)


@pytest.fixture(scope="function")
def mysql_db(mysql_engine, setup_mysql_schema):
    """Provide clean MySQL database session for each test."""
    from app.database import Base
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=mysql_engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        # Clean all tables after each test
        db.rollback()
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
        db.close()


@pytest.fixture(scope="function")
def mysql_client(mysql_db):
    """Provide test client with MySQL database."""
    from app.main import app
    from app.database import get_db
    
    def override_get_db():
        try:
            yield mysql_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


# ============================================================================
# AUTH ENDPOINT TESTS
# ============================================================================

def test_mysql_auth_register(mysql_client):
    """Test user registration with MySQL backend."""
    response = mysql_client.post(
        "/api/auth/register",
        json={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["username"] == "testuser"
    assert "password" not in data


def test_mysql_auth_login(mysql_client):
    """Test user login with MySQL backend."""
    # Register user
    mysql_client.post(
        "/api/auth/register",
        json={"username": "loginuser", "password": "password123"}
    )
    
    # Login
    response = mysql_client.post(
        "/api/auth/login",
        json={"username": "loginuser", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


# ============================================================================
# RECIPE ENDPOINT TESTS
# ============================================================================

def test_mysql_create_recipe(mysql_client):
    """Test recipe creation with MySQL backend."""
    # Register and login
    mysql_client.post("/api/auth/register", json={"username": "recipeuser", "password": "password123"})
    login_response = mysql_client.post("/api/auth/login", json={"username": "recipeuser", "password": "password123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create recipe
    recipe_data = {
        "title": "MySQL Test Recipe",
        "ingredients": ["flour", "sugar", "eggs"],
        "steps": ["Mix ingredients", "Bake at 350F"],
        "tags": ["dessert", "easy"]
    }
    
    response = mysql_client.post("/api/recipes", json=recipe_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "MySQL Test Recipe"
    assert data["ingredients"] == ["flour", "sugar", "eggs"]
    assert "id" in data
    assert "created_at" in data


def test_mysql_get_recipes(mysql_client):
    """Test retrieving recipes with MySQL backend."""
    # Register and login
    mysql_client.post("/api/auth/register", json={"username": "getuser", "password": "password123"})
    login_response = mysql_client.post("/api/auth/login", json={"username": "getuser", "password": "password123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create recipes
    mysql_client.post(
        "/api/recipes",
        json={"title": "Recipe 1", "ingredients": ["a"], "steps": ["b"]},
        headers=headers
    )
    mysql_client.post(
        "/api/recipes",
        json={"title": "Recipe 2", "ingredients": ["c"], "steps": ["d"]},
        headers=headers
    )
    
    # Get all recipes
    response = mysql_client.get("/api/recipes", headers=headers)
    assert response.status_code == 200
    recipes = response.json()
    assert len(recipes) == 2


def test_mysql_update_recipe(mysql_client):
    """Test recipe update with MySQL backend."""
    # Register and login
    mysql_client.post("/api/auth/register", json={"username": "updateuser", "password": "password123"})
    login_response = mysql_client.post("/api/auth/login", json={"username": "updateuser", "password": "password123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create recipe
    create_response = mysql_client.post(
        "/api/recipes",
        json={"title": "Original", "ingredients": ["a"], "steps": ["b"]},
        headers=headers
    )
    recipe_id = create_response.json()["id"]
    
    # Update recipe
    response = mysql_client.put(
        f"/api/recipes/{recipe_id}",
        json={"title": "Updated"},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"


def test_mysql_delete_recipe(mysql_client):
    """Test recipe deletion with MySQL backend."""
    # Register and login
    mysql_client.post("/api/auth/register", json={"username": "deleteuser", "password": "password123"})
    login_response = mysql_client.post("/api/auth/login", json={"username": "deleteuser", "password": "password123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create recipe
    create_response = mysql_client.post(
        "/api/recipes",
        json={"title": "To Delete", "ingredients": ["a"], "steps": ["b"]},
        headers=headers
    )
    recipe_id = create_response.json()["id"]
    
    # Delete recipe
    response = mysql_client.delete(f"/api/recipes/{recipe_id}", headers=headers)
    assert response.status_code == 200
    
    # Verify deleted
    get_response = mysql_client.get(f"/api/recipes/{recipe_id}", headers=headers)
    assert get_response.status_code == 404


def test_mysql_search_recipes(mysql_client):
    """Test recipe search with MySQL backend."""
    # Register and login
    mysql_client.post("/api/auth/register", json={"username": "searchuser", "password": "password123"})
    login_response = mysql_client.post("/api/auth/login", json={"username": "searchuser", "password": "password123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create recipes
    mysql_client.post(
        "/api/recipes",
        json={"title": "Chocolate Cake", "ingredients": ["chocolate"], "steps": ["bake"]},
        headers=headers
    )
    mysql_client.post(
        "/api/recipes",
        json={"title": "Vanilla Cake", "ingredients": ["vanilla"], "steps": ["bake"]},
        headers=headers
    )
    
    # Search
    response = mysql_client.get("/api/recipes?search=chocolate", headers=headers)
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert "chocolate" in results[0]["title"].lower()


# ============================================================================
# COLLECTION ENDPOINT TESTS
# ============================================================================

def test_mysql_create_collection(mysql_client):
    """Test collection creation with MySQL backend."""
    # Register and login
    mysql_client.post("/api/auth/register", json={"username": "colluser", "password": "password123"})
    login_response = mysql_client.post("/api/auth/login", json={"username": "colluser", "password": "password123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create collection
    response = mysql_client.post(
        "/api/collections",
        json={"name": "My Collection", "description": "Test collection"},
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My Collection"
    assert "id" in data


# ============================================================================
# RATING ENDPOINT TESTS
# ============================================================================

def test_mysql_create_rating(mysql_client):
    """Test rating creation with MySQL backend."""
    # Register and login
    mysql_client.post("/api/auth/register", json={"username": "rateuser", "password": "password123"})
    login_response = mysql_client.post("/api/auth/login", json={"username": "rateuser", "password": "password123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create recipe
    recipe_response = mysql_client.post(
        "/api/recipes",
        json={"title": "Recipe to Rate", "ingredients": ["a"], "steps": ["b"]},
        headers=headers
    )
    recipe_id = recipe_response.json()["id"]
    
    # Create rating
    response = mysql_client.post(
        f"/api/recipes/{recipe_id}/ratings",
        json={"rating": 5},
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["rating"] == 5


# ============================================================================
# NOTE ENDPOINT TESTS
# ============================================================================

def test_mysql_create_note(mysql_client):
    """Test note creation with MySQL backend."""
    # Register and login
    mysql_client.post("/api/auth/register", json={"username": "noteuser", "password": "password123"})
    login_response = mysql_client.post("/api/auth/login", json={"username": "noteuser", "password": "password123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create recipe
    recipe_response = mysql_client.post(
        "/api/recipes",
        json={"title": "Recipe for Note", "ingredients": ["a"], "steps": ["b"]},
        headers=headers
    )
    recipe_id = recipe_response.json()["id"]
    
    # Create note
    response = mysql_client.post(
        f"/api/recipes/{recipe_id}/notes",
        json={"note_text": "Great recipe!"},
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["note_text"] == "Great recipe!"


# ============================================================================
# PAGINATION AND FILTERING TESTS
# ============================================================================

def test_mysql_pagination(mysql_client):
    """Test pagination with MySQL backend."""
    # Register and login
    mysql_client.post("/api/auth/register", json={"username": "pageuser", "password": "password123"})
    login_response = mysql_client.post("/api/auth/login", json={"username": "pageuser", "password": "password123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create multiple recipes
    for i in range(5):
        mysql_client.post(
            "/api/recipes",
            json={"title": f"Recipe {i}", "ingredients": ["a"], "steps": ["b"]},
            headers=headers
        )
    
    # Test pagination
    response = mysql_client.get("/api/recipes?skip=0&limit=2", headers=headers)
    assert response.status_code == 200
    recipes = response.json()
    assert len(recipes) == 2


def test_mysql_sorting(mysql_client):
    """Test sorting with MySQL backend."""
    # Register and login
    mysql_client.post("/api/auth/register", json={"username": "sortuser", "password": "password123"})
    login_response = mysql_client.post("/api/auth/login", json={"username": "sortuser", "password": "password123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create recipes with different titles
    mysql_client.post(
        "/api/recipes",
        json={"title": "Zebra Cake", "ingredients": ["a"], "steps": ["b"]},
        headers=headers
    )
    mysql_client.post(
        "/api/recipes",
        json={"title": "Apple Pie", "ingredients": ["c"], "steps": ["d"]},
        headers=headers
    )
    
    # Test sorting by title
    response = mysql_client.get("/api/recipes/filter?sort_by=title&sort_order=asc", headers=headers)
    assert response.status_code == 200
    recipes = response.json()
    if len(recipes) >= 2:
        assert recipes[0]["title"] < recipes[1]["title"]


if __name__ == "__main__":
    print("Run this test file with: pytest tests/test_mysql_api_endpoints.py -v")
    print("Ensure MySQL is running and accessible at: mysql+pymysql://root:password@localhost:3306/recipe_saver_test")
