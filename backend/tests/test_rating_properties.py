"""Property-based tests for rating system."""
import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"

from hypothesis import given, strategies as st, settings as hyp_settings, HealthCheck
from datetime import timedelta
import pytest
import uuid


# Feature: recipe-saver-enhancements, Property 5: Rating validation
@given(
    rating=st.integers()
)
@hyp_settings(max_examples=100, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_rating_validation_property(db, rating):
    """
    Property 5: Rating validation
    
    For any integer rating value, the validate_rating function should 
    return True if and only if the rating is between 1 and 5 (inclusive).
    
    **Validates: Requirements 3.1, 3.2**
    """
    from app.services.rating_service import RatingSystem
    
    result = RatingSystem.validate_rating(rating)
    
    if 1 <= rating <= 5:
        assert result is True, f"Rating {rating} should be valid"
    else:
        assert result is False, f"Rating {rating} should be invalid"


# Feature: recipe-saver-enhancements, Property 6: Rating persistence and updates
@given(
    initial_rating=st.integers(min_value=1, max_value=5),
    updated_rating=st.integers(min_value=1, max_value=5)
)
@hyp_settings(max_examples=100, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_rating_persistence_and_updates_property(db, initial_rating, updated_rating):
    """
    Property 6: Rating persistence and updates
    
    For any valid rating value, creating a rating and then retrieving it 
    should return the same value. Updating the rating and retrieving it 
    should return the updated value.
    
    **Validates: Requirements 3.1, 3.3**
    """
    from app.services.rating_service import RatingSystem
    from app.services.recipe_service import RecipeManager
    from app.services.auth_service import AuthService
    from app.schemas import RecipeCreate
    
    # Create a test user with unique username
    unique_username = f"ratinguser_{uuid.uuid4().hex[:8]}"
    user = AuthService.create_user(db, unique_username, "password123")
    
    # Create a recipe
    recipe_data = RecipeCreate(
        title="Test Recipe",
        ingredients=["ingredient1"],
        steps=["step1"]
    )
    recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
    
    # Add initial rating
    created_rating = RatingSystem.add_rating(db, recipe.id, user.id, initial_rating)
    
    assert created_rating is not None, "Rating should be created successfully"
    assert created_rating.rating == initial_rating, "Created rating should match initial value"
    assert created_rating.recipe_id == recipe.id, "Rating should be associated with correct recipe"
    assert created_rating.user_id == user.id, "Rating should be associated with correct user"
    
    # Retrieve the rating
    retrieved_rating = RatingSystem.get_user_rating(db, recipe.id, user.id)
    
    assert retrieved_rating is not None, "Rating should be retrievable"
    assert retrieved_rating.rating == initial_rating, "Retrieved rating should match initial value"
    assert retrieved_rating.id == created_rating.id, "Retrieved rating should have same ID"
    
    # Update the rating
    updated = RatingSystem.update_rating(db, recipe.id, user.id, updated_rating)
    
    assert updated is not None, "Rating should be updated successfully"
    assert updated.rating == updated_rating, "Updated rating should match new value"
    assert updated.id == created_rating.id, "Updated rating should have same ID (not create new)"
    
    # Retrieve the updated rating
    retrieved_updated = RatingSystem.get_user_rating(db, recipe.id, user.id)
    
    assert retrieved_updated is not None, "Updated rating should be retrievable"
    assert retrieved_updated.rating == updated_rating, "Retrieved rating should match updated value"
    assert retrieved_updated.id == created_rating.id, "Should still be the same rating record"


# Feature: recipe-saver-enhancements, Property 7: Rating user isolation
@given(
    user1_rating=st.integers(min_value=1, max_value=5),
    user2_rating=st.integers(min_value=1, max_value=5)
)
@hyp_settings(max_examples=100, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_rating_user_isolation_property(db, user1_rating, user2_rating):
    """
    Property 7: Rating user isolation
    
    For any recipe, each user should be able to have their own independent 
    rating. Retrieving a user's rating should return only their rating, 
    not other users' ratings.
    
    **Validates: Requirements 3.4**
    """
    from app.services.rating_service import RatingSystem
    from app.services.recipe_service import RecipeManager
    from app.services.auth_service import AuthService
    from app.schemas import RecipeCreate
    
    # Create two test users with unique usernames
    unique_id = uuid.uuid4().hex[:8]
    user1 = AuthService.create_user(db, f"ratinguser1_{unique_id}", "password123")
    user2 = AuthService.create_user(db, f"ratinguser2_{unique_id}", "password456")
    
    # Create a recipe owned by user1
    recipe_data = RecipeCreate(
        title="Shared Recipe",
        ingredients=["ingredient1"],
        steps=["step1"]
    )
    recipe = RecipeManager.create_recipe(db, user1.id, recipe_data)
    
    # User1 adds a rating
    user1_created = RatingSystem.add_rating(db, recipe.id, user1.id, user1_rating)
    
    assert user1_created is not None, "User1 should be able to create rating"
    assert user1_created.rating == user1_rating, "User1's rating should match"
    
    # User2 adds a different rating for the same recipe
    user2_created = RatingSystem.add_rating(db, recipe.id, user2.id, user2_rating)
    
    assert user2_created is not None, "User2 should be able to create rating"
    assert user2_created.rating == user2_rating, "User2's rating should match"
    assert user2_created.id != user1_created.id, "User2's rating should be a separate record"
    
    # Retrieve user1's rating
    user1_retrieved = RatingSystem.get_user_rating(db, recipe.id, user1.id)
    
    assert user1_retrieved is not None, "User1's rating should be retrievable"
    assert user1_retrieved.rating == user1_rating, "User1 should see their own rating"
    assert user1_retrieved.user_id == user1.id, "Rating should belong to user1"
    assert user1_retrieved.id == user1_created.id, "Should retrieve user1's rating record"
    
    # Retrieve user2's rating
    user2_retrieved = RatingSystem.get_user_rating(db, recipe.id, user2.id)
    
    assert user2_retrieved is not None, "User2's rating should be retrievable"
    assert user2_retrieved.rating == user2_rating, "User2 should see their own rating"
    assert user2_retrieved.user_id == user2.id, "Rating should belong to user2"
    assert user2_retrieved.id == user2_created.id, "Should retrieve user2's rating record"
    
    # Verify ratings are independent
    assert user1_retrieved.rating != user2_retrieved.rating or user1_rating == user2_rating, \
        "Users should have independent ratings (unless they happen to be the same value)"
    
    # Calculate average rating
    avg_rating = RatingSystem.get_average_rating(db, recipe.id)
    
    assert avg_rating is not None, "Average rating should be calculable"
    expected_avg = (user1_rating + user2_rating) / 2.0
    assert abs(avg_rating - expected_avg) < 0.01, f"Average rating should be {expected_avg}, got {avg_rating}"
