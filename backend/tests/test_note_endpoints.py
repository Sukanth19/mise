"""Unit tests for recipe notes endpoints."""
import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base, engine
from sqlalchemy.orm import Session

client = TestClient(app)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


def create_test_user_and_login(username="testuser", password="password123"):
    """Helper function to create a user and get auth token."""
    # Register user
    register_response = client.post(
        "/api/auth/register",
        json={"username": username, "password": password}
    )
    assert register_response.status_code == 201
    
    # Login to get token
    login_response = client.post(
        "/api/auth/login",
        json={"username": username, "password": password}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return token


def create_test_recipe(token):
    """Helper function to create a test recipe."""
    recipe_data = {
        "title": "Test Recipe",
        "ingredients": ["ingredient1", "ingredient2"],
        "steps": ["step1", "step2"],
        "tags": ["tag1"]
    }
    response = client.post(
        "/api/recipes",
        json=recipe_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_create_note_success(db):
    """Test creating a note for a recipe."""
    token = create_test_user_and_login()
    recipe_id = create_test_recipe(token)
    
    note_data = {"note_text": "This is a test note"}
    response = client.post(
        f"/api/recipes/{recipe_id}/notes",
        json=note_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["note_text"] == "This is a test note"
    assert data["recipe_id"] == recipe_id
    assert "id" in data
    assert "created_at" in data


def test_create_note_empty_text(db):
    """Test creating a note with empty text should fail validation."""
    token = create_test_user_and_login()
    recipe_id = create_test_recipe(token)
    
    note_data = {"note_text": ""}
    response = client.post(
        f"/api/recipes/{recipe_id}/notes",
        json=note_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 422  # Validation error


def test_create_note_nonexistent_recipe(db):
    """Test creating a note for a non-existent recipe."""
    token = create_test_user_and_login()
    
    note_data = {"note_text": "This is a test note"}
    response = client.post(
        "/api/recipes/99999/notes",
        json=note_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Recipe not found"


def test_create_note_unauthorized(db):
    """Test creating a note without authentication."""
    note_data = {"note_text": "This is a test note"}
    response = client.post(
        "/api/recipes/1/notes",
        json=note_data
    )
    
    assert response.status_code == 422  # Missing authorization header


def test_get_notes_success(db):
    """Test retrieving notes for a recipe."""
    token = create_test_user_and_login()
    recipe_id = create_test_recipe(token)
    
    # Create multiple notes
    note1_data = {"note_text": "First note"}
    note2_data = {"note_text": "Second note"}
    note3_data = {"note_text": "Third note"}
    
    client.post(
        f"/api/recipes/{recipe_id}/notes",
        json=note1_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    client.post(
        f"/api/recipes/{recipe_id}/notes",
        json=note2_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    client.post(
        f"/api/recipes/{recipe_id}/notes",
        json=note3_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Get all notes
    response = client.get(
        f"/api/recipes/{recipe_id}/notes",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) == 3
    assert notes[0]["note_text"] == "First note"
    assert notes[1]["note_text"] == "Second note"
    assert notes[2]["note_text"] == "Third note"


def test_get_notes_chronological_order(db):
    """Test that notes are returned in chronological order."""
    token = create_test_user_and_login()
    recipe_id = create_test_recipe(token)
    
    # Create notes
    note1_data = {"note_text": "First note"}
    note2_data = {"note_text": "Second note"}
    
    response1 = client.post(
        f"/api/recipes/{recipe_id}/notes",
        json=note1_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    response2 = client.post(
        f"/api/recipes/{recipe_id}/notes",
        json=note2_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Get all notes
    response = client.get(
        f"/api/recipes/{recipe_id}/notes",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) == 2
    
    # Verify chronological order (first created should be first)
    assert notes[0]["id"] == response1.json()["id"]
    assert notes[1]["id"] == response2.json()["id"]


def test_get_notes_empty_list(db):
    """Test retrieving notes for a recipe with no notes."""
    token = create_test_user_and_login()
    recipe_id = create_test_recipe(token)
    
    response = client.get(
        f"/api/recipes/{recipe_id}/notes",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) == 0


def test_get_notes_nonexistent_recipe(db):
    """Test retrieving notes for a non-existent recipe."""
    token = create_test_user_and_login()
    
    response = client.get(
        "/api/recipes/99999/notes",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Recipe not found"


def test_delete_note_success(db):
    """Test deleting a note."""
    token = create_test_user_and_login()
    recipe_id = create_test_recipe(token)
    
    # Create a note
    note_data = {"note_text": "Test note to delete"}
    create_response = client.post(
        f"/api/recipes/{recipe_id}/notes",
        json=note_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    note_id = create_response.json()["id"]
    
    # Delete the note
    response = client.delete(
        f"/api/recipes/{recipe_id}/notes/{note_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Note deleted successfully"
    
    # Verify note is deleted
    get_response = client.get(
        f"/api/recipes/{recipe_id}/notes",
        headers={"Authorization": f"Bearer {token}"}
    )
    notes = get_response.json()
    assert len(notes) == 0


def test_delete_note_nonexistent(db):
    """Test deleting a non-existent note."""
    token = create_test_user_and_login()
    recipe_id = create_test_recipe(token)
    
    response = client.delete(
        f"/api/recipes/{recipe_id}/notes/99999",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"


def test_delete_note_wrong_user(db):
    """Test that a user cannot delete another user's note."""
    # Create first user and recipe with note
    token1 = create_test_user_and_login("user1", "password123")
    recipe_id = create_test_recipe(token1)
    
    note_data = {"note_text": "User1's note"}
    create_response = client.post(
        f"/api/recipes/{recipe_id}/notes",
        json=note_data,
        headers={"Authorization": f"Bearer {token1}"}
    )
    note_id = create_response.json()["id"]
    
    # Create second user
    token2 = create_test_user_and_login("user2", "password456")
    
    # Try to delete user1's note as user2
    response = client.delete(
        f"/api/recipes/{recipe_id}/notes/{note_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    
    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have permission to delete this note"


def test_notes_user_isolation(db):
    """Test that notes are associated with the correct user."""
    # Create two users
    token1 = create_test_user_and_login("user1", "password123")
    token2 = create_test_user_and_login("user2", "password456")
    
    # User1 creates a recipe
    recipe_id = create_test_recipe(token1)
    
    # Both users add notes to the same recipe
    note1_data = {"note_text": "User1's note"}
    note2_data = {"note_text": "User2's note"}
    
    response1 = client.post(
        f"/api/recipes/{recipe_id}/notes",
        json=note1_data,
        headers={"Authorization": f"Bearer {token1}"}
    )
    response2 = client.post(
        f"/api/recipes/{recipe_id}/notes",
        json=note2_data,
        headers={"Authorization": f"Bearer {token2}"}
    )
    
    # Get all notes
    response = client.get(
        f"/api/recipes/{recipe_id}/notes",
        headers={"Authorization": f"Bearer {token1}"}
    )
    
    notes = response.json()
    assert len(notes) == 2
    
    # Verify each note is associated with the correct user
    note1 = next(n for n in notes if n["id"] == response1.json()["id"])
    note2 = next(n for n in notes if n["id"] == response2.json()["id"])
    
    assert note1["note_text"] == "User1's note"
    assert note2["note_text"] == "User2's note"
