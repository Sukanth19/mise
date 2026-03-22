"""Unit tests for authentication endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import User

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_register_success():
    """Test successful user registration."""
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data
    assert "password" not in data


def test_register_duplicate_username():
    """Test registration with duplicate username returns 409."""
    # Register first user
    client.post(
        "/api/auth/register",
        json={"username": "testuser", "password": "password123"}
    )
    
    # Try to register with same username
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser", "password": "different456"}
    )
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"].lower()


def test_register_short_password():
    """Test registration with short password returns 422 validation error."""
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser", "password": "short"}
    )
    assert response.status_code == 422
    errors = response.json()["detail"]
    # Check that password field has validation error
    password_errors = [e for e in errors if 'password' in str(e.get('loc', []))]
    assert len(password_errors) > 0


def test_login_success():
    """Test successful login returns JWT token."""
    # Register user first
    client.post(
        "/api/auth/register",
        json={"username": "testuser", "password": "password123"}
    )
    
    # Login
    response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


def test_login_invalid_username():
    """Test login with non-existent username returns 401."""
    response = client.post(
        "/api/auth/login",
        json={"username": "nonexistent", "password": "password123"}
    )
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_login_invalid_password():
    """Test login with wrong password returns 401."""
    # Register user first
    client.post(
        "/api/auth/register",
        json={"username": "testuser", "password": "password123"}
    )
    
    # Try to login with wrong password
    response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_password_is_hashed():
    """Test that passwords are hashed in database, not stored as plain text."""
    # Register user
    client.post(
        "/api/auth/register",
        json={"username": "testuser", "password": "password123"}
    )
    
    # Check database directly
    db = TestingSessionLocal()
    user = db.query(User).filter(User.username == "testuser").first()
    assert user is not None
    assert user.password_hash != "password123"
    assert len(user.password_hash) > 0
    db.close()
