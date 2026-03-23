"""Property-based tests for recipe notes system."""
import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"

from hypothesis import given, strategies as st, settings as hyp_settings, HealthCheck
from datetime import timedelta
import pytest
import uuid


# Feature: recipe-saver-enhancements, Property 17: Recipe notes persistence
@given(
    note_text=st.text(min_size=1, max_size=500)
)
@hyp_settings(max_examples=100, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_recipe_notes_persistence_property(db, note_text):
    """
    Property 17: Recipe notes persistence
    
    For any recipe and note text, adding a note should store it with a 
    timestamp and associate it with the user and recipe. Retrieving the 
    note should return the same text, timestamp, and associations.
    
    **Validates: Requirements 9.1, 9.2**
    """
    from app.models import RecipeNote, Recipe, User
    from app.services.auth_service import AuthService
    from app.services.recipe_service import RecipeManager
    from app.schemas import RecipeCreate
    
    # Create a test user with unique username
    unique_username = f"noteuser_{uuid.uuid4().hex[:8]}"
    user = AuthService.create_user(db, unique_username, "password123")
    
    # Create a recipe
    recipe_data = RecipeCreate(
        title="Test Recipe",
        ingredients=["ingredient1"],
        steps=["step1"]
    )
    recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
    
    # Add a note
    note = RecipeNote(
        recipe_id=recipe.id,
        user_id=user.id,
        note_text=note_text
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    
    # Verify note was created
    assert note.id is not None, "Note should have an ID"
    assert note.note_text == note_text, "Note text should match input"
    assert note.recipe_id == recipe.id, "Note should be associated with correct recipe"
    assert note.user_id == user.id, "Note should be associated with correct user"
    assert note.created_at is not None, "Note should have a timestamp"
    
    # Retrieve the note
    retrieved_note = db.query(RecipeNote).filter(RecipeNote.id == note.id).first()
    
    assert retrieved_note is not None, "Note should be retrievable"
    assert retrieved_note.note_text == note_text, "Retrieved note text should match"
    assert retrieved_note.recipe_id == recipe.id, "Retrieved note should have correct recipe_id"
    assert retrieved_note.user_id == user.id, "Retrieved note should have correct user_id"
    assert retrieved_note.created_at == note.created_at, "Timestamp should be preserved"


# Feature: recipe-saver-enhancements, Property 18: Notes chronological ordering
@given(
    note_count=st.integers(min_value=2, max_value=10),
    note_texts=st.lists(
        st.text(min_size=1, max_size=100),
        min_size=2,
        max_size=10
    )
)
@hyp_settings(max_examples=100, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_notes_chronological_ordering_property(db, note_count, note_texts):
    """
    Property 18: Notes chronological ordering
    
    For any recipe with multiple notes, retrieving notes should return 
    them ordered by created_at timestamp in ascending order (oldest first).
    
    **Validates: Requirements 9.3**
    """
    from app.models import RecipeNote, Recipe, User
    from app.services.auth_service import AuthService
    from app.services.recipe_service import RecipeManager
    from app.schemas import RecipeCreate
    import time
    
    # Ensure we have the right number of note texts
    if len(note_texts) < note_count:
        note_texts = note_texts + [f"note_{i}" for i in range(len(note_texts), note_count)]
    note_texts = note_texts[:note_count]
    
    # Create a test user with unique username
    unique_username = f"noteuser_{uuid.uuid4().hex[:8]}"
    user = AuthService.create_user(db, unique_username, "password123")
    
    # Create a recipe
    recipe_data = RecipeCreate(
        title="Test Recipe",
        ingredients=["ingredient1"],
        steps=["step1"]
    )
    recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
    
    # Add multiple notes with slight delays to ensure different timestamps
    created_notes = []
    for i, note_text in enumerate(note_texts):
        note = RecipeNote(
            recipe_id=recipe.id,
            user_id=user.id,
            note_text=note_text
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        created_notes.append(note)
        
        # Small delay to ensure different timestamps (SQLite has second precision)
        if i < len(note_texts) - 1:
            time.sleep(0.01)
    
    # Retrieve all notes for the recipe, ordered by created_at
    retrieved_notes = db.query(RecipeNote).filter(
        RecipeNote.recipe_id == recipe.id
    ).order_by(RecipeNote.created_at.asc()).all()
    
    assert len(retrieved_notes) == note_count, f"Should retrieve {note_count} notes"
    
    # Verify chronological ordering
    for i in range(len(retrieved_notes) - 1):
        current_note = retrieved_notes[i]
        next_note = retrieved_notes[i + 1]
        
        assert current_note.created_at <= next_note.created_at, \
            f"Note {i} should have timestamp <= Note {i+1}"
    
    # Verify the notes are in the order they were created
    # (by checking IDs which are auto-incrementing)
    for i in range(len(retrieved_notes) - 1):
        current_note = retrieved_notes[i]
        next_note = retrieved_notes[i + 1]
        
        assert current_note.id <= next_note.id, \
            f"Note {i} (ID {current_note.id}) should have ID <= Note {i+1} (ID {next_note.id})"


# Additional property test: Note deletion
@given(
    note_text=st.text(min_size=1, max_size=200)
)
@hyp_settings(max_examples=100, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_note_deletion_property(db, note_text):
    """
    Property: Note deletion
    
    For any note, deleting it should remove it from the database and 
    subsequent queries should not return it.
    
    **Validates: Requirements 9.4**
    """
    from app.models import RecipeNote, Recipe, User
    from app.services.auth_service import AuthService
    from app.services.recipe_service import RecipeManager
    from app.schemas import RecipeCreate
    
    # Create a test user with unique username
    unique_username = f"noteuser_{uuid.uuid4().hex[:8]}"
    user = AuthService.create_user(db, unique_username, "password123")
    
    # Create a recipe
    recipe_data = RecipeCreate(
        title="Test Recipe",
        ingredients=["ingredient1"],
        steps=["step1"]
    )
    recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
    
    # Add a note
    note = RecipeNote(
        recipe_id=recipe.id,
        user_id=user.id,
        note_text=note_text
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    
    note_id = note.id
    
    # Verify note exists
    existing_note = db.query(RecipeNote).filter(RecipeNote.id == note_id).first()
    assert existing_note is not None, "Note should exist before deletion"
    
    # Delete the note
    db.delete(note)
    db.commit()
    
    # Verify note is deleted
    deleted_note = db.query(RecipeNote).filter(RecipeNote.id == note_id).first()
    assert deleted_note is None, "Note should not exist after deletion"
    
    # Verify recipe still exists (note deletion should not cascade to recipe)
    recipe_still_exists = db.query(Recipe).filter(Recipe.id == recipe.id).first()
    assert recipe_still_exists is not None, "Recipe should still exist after note deletion"


# Additional property test: Multiple users can add notes to the same recipe
@given(
    user1_note=st.text(min_size=1, max_size=100),
    user2_note=st.text(min_size=1, max_size=100)
)
@hyp_settings(max_examples=100, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_multiple_users_notes_property(db, user1_note, user2_note):
    """
    Property: Multiple users can add notes to the same recipe
    
    For any recipe, multiple users should be able to add their own notes 
    independently. Each note should be associated with the correct user.
    
    **Validates: Requirements 9.2**
    """
    from app.models import RecipeNote, Recipe, User
    from app.services.auth_service import AuthService
    from app.services.recipe_service import RecipeManager
    from app.schemas import RecipeCreate
    
    # Create two test users with unique usernames
    unique_id = uuid.uuid4().hex[:8]
    user1 = AuthService.create_user(db, f"noteuser1_{unique_id}", "password123")
    user2 = AuthService.create_user(db, f"noteuser2_{unique_id}", "password456")
    
    # User1 creates a recipe
    recipe_data = RecipeCreate(
        title="Shared Recipe",
        ingredients=["ingredient1"],
        steps=["step1"]
    )
    recipe = RecipeManager.create_recipe(db, user1.id, recipe_data)
    
    # User1 adds a note
    note1 = RecipeNote(
        recipe_id=recipe.id,
        user_id=user1.id,
        note_text=user1_note
    )
    db.add(note1)
    db.commit()
    db.refresh(note1)
    
    # User2 adds a note to the same recipe
    note2 = RecipeNote(
        recipe_id=recipe.id,
        user_id=user2.id,
        note_text=user2_note
    )
    db.add(note2)
    db.commit()
    db.refresh(note2)
    
    # Verify both notes exist
    assert note1.id is not None, "User1's note should be created"
    assert note2.id is not None, "User2's note should be created"
    assert note1.id != note2.id, "Notes should have different IDs"
    
    # Verify notes are associated with correct users
    assert note1.user_id == user1.id, "Note1 should belong to user1"
    assert note2.user_id == user2.id, "Note2 should belong to user2"
    
    # Verify both notes are for the same recipe
    assert note1.recipe_id == recipe.id, "Note1 should be for the recipe"
    assert note2.recipe_id == recipe.id, "Note2 should be for the recipe"
    
    # Retrieve all notes for the recipe
    all_notes = db.query(RecipeNote).filter(
        RecipeNote.recipe_id == recipe.id
    ).order_by(RecipeNote.created_at.asc()).all()
    
    assert len(all_notes) == 2, "Should have 2 notes for the recipe"
    
    # Verify we can retrieve each user's notes separately
    user1_notes = db.query(RecipeNote).filter(
        RecipeNote.recipe_id == recipe.id,
        RecipeNote.user_id == user1.id
    ).all()
    
    user2_notes = db.query(RecipeNote).filter(
        RecipeNote.recipe_id == recipe.id,
        RecipeNote.user_id == user2.id
    ).all()
    
    assert len(user1_notes) == 1, "User1 should have 1 note"
    assert len(user2_notes) == 1, "User2 should have 1 note"
    assert user1_notes[0].note_text == user1_note, "User1's note text should match"
    assert user2_notes[0].note_text == user2_note, "User2's note text should match"
