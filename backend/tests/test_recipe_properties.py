"""Property-based tests for recipe management service."""
import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"

from hypothesis import given, strategies as st, settings as hyp_settings, HealthCheck
from datetime import timedelta
import pytest
import uuid


# Feature: recipe-saver, Property 9: Recipe data round trip preserves all fields
@given(
    title=st.text(min_size=1, max_size=100, alphabet=st.characters(min_codepoint=32, max_codepoint=126)),
    ingredients=st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=10),
    steps=st.lists(st.text(min_size=1, max_size=100), min_size=1, max_size=10),
    tags=st.one_of(st.none(), st.lists(st.text(min_size=1, max_size=20), min_size=0, max_size=5)),
    reference_link=st.one_of(st.none(), st.text(min_size=10, max_size=100))
)
@hyp_settings(max_examples=5, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_recipe_data_round_trip_property(db, title, ingredients, steps, tags, reference_link):
    """
    Property 9: Recipe data round trip preserves all fields
    
    For any recipe with ingredients, steps, tags, and reference link, 
    creating the recipe and then retrieving it should return data 
    matching the original input.
    
    **Validates: Requirements 3.3, 3.4, 3.5, 3.6**
    """
    from app.services.recipe_service import RecipeManager
    from app.services.auth_service import AuthService
    from app.schemas import RecipeCreate
    
    # Create a test user with unique username
    unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
    user = AuthService.create_user(db, unique_username, "password123")
    
    # Create recipe data
    recipe_data = RecipeCreate(
        title=title,
        ingredients=ingredients,
        steps=steps,
        tags=tags,
        reference_link=reference_link
    )
    
    # Create recipe
    created_recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
    
    # Retrieve recipe
    retrieved_recipe = RecipeManager.get_recipe_by_id(db, created_recipe.id)
    
    assert retrieved_recipe is not None, "Recipe should be retrievable after creation"
    
    # Verify all fields are preserved
    import json
    assert retrieved_recipe.title == title, "Title should be preserved"
    assert json.loads(retrieved_recipe.ingredients) == ingredients, "Ingredients should be preserved"
    assert json.loads(retrieved_recipe.steps) == steps, "Steps should be preserved in order"
    
    if tags is not None:
        assert retrieved_recipe.tags is not None, "Tags should not be None when provided"
        assert json.loads(retrieved_recipe.tags) == tags, "Tags should be preserved"
    else:
        assert retrieved_recipe.tags is None, "Tags should be None if not provided"
    
    assert retrieved_recipe.reference_link == reference_link, "Reference link should be preserved"


# Feature: recipe-saver, Property 12: User recipes are isolated
@given(
    user1_recipe_count=st.integers(min_value=1, max_value=5),
    user2_recipe_count=st.integers(min_value=1, max_value=5)
)
@hyp_settings(max_examples=5, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_user_recipe_isolation_property(db, user1_recipe_count, user2_recipe_count):
    """
    Property 12: User recipes are isolated
    
    For any user, retrieving their recipes should return only recipes 
    where the user_id matches that user, and no recipes from other users.
    
    **Validates: Requirements 5.1**
    """
    from app.services.recipe_service import RecipeManager
    from app.services.auth_service import AuthService
    from app.schemas import RecipeCreate
    
    # Create two test users with unique usernames
    user1 = AuthService.create_user(db, f"user1_{uuid.uuid4().hex[:8]}", "password123")
    user2 = AuthService.create_user(db, f"user2_{uuid.uuid4().hex[:8]}", "password456")
    
    # Create recipes for user1
    user1_recipe_ids = []
    for i in range(user1_recipe_count):
        recipe_data = RecipeCreate(
            title=f"User1 Recipe {i}",
            ingredients=["ingredient1"],
            steps=["step1"]
        )
        recipe = RecipeManager.create_recipe(db, user1.id, recipe_data)
        user1_recipe_ids.append(recipe.id)
    
    # Create recipes for user2
    user2_recipe_ids = []
    for i in range(user2_recipe_count):
        recipe_data = RecipeCreate(
            title=f"User2 Recipe {i}",
            ingredients=["ingredient2"],
            steps=["step2"]
        )
        recipe = RecipeManager.create_recipe(db, user2.id, recipe_data)
        user2_recipe_ids.append(recipe.id)
    
    # Retrieve recipes for user1
    user1_recipes = RecipeManager.get_user_recipes(db, user1.id)
    
    # Verify user1 only sees their own recipes
    assert len(user1_recipes) == user1_recipe_count, f"User1 should have {user1_recipe_count} recipes"
    
    for recipe in user1_recipes:
        assert recipe.user_id == user1.id, "All recipes should belong to user1"
        assert recipe.id in user1_recipe_ids, "Recipe ID should be in user1's recipe list"
        assert recipe.id not in user2_recipe_ids, "Recipe ID should not be in user2's recipe list"
    
    # Retrieve recipes for user2
    user2_recipes = RecipeManager.get_user_recipes(db, user2.id)
    
    # Verify user2 only sees their own recipes
    assert len(user2_recipes) == user2_recipe_count, f"User2 should have {user2_recipe_count} recipes"
    
    for recipe in user2_recipes:
        assert recipe.user_id == user2.id, "All recipes should belong to user2"
        assert recipe.id in user2_recipe_ids, "Recipe ID should be in user2's recipe list"
        assert recipe.id not in user1_recipe_ids, "Recipe ID should not be in user1's recipe list"


# Feature: recipe-saver, Property 18: Recipe updates require ownership
# Feature: recipe-saver, Property 22: Recipe deletion requires ownership
@given(
    title=st.text(min_size=1, max_size=50, alphabet=st.characters(min_codepoint=32, max_codepoint=126)),
    new_title=st.text(min_size=1, max_size=50, alphabet=st.characters(min_codepoint=32, max_codepoint=126))
)
@hyp_settings(max_examples=5, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_ownership_validation_property(db, title, new_title):
    """
    Property 18: Recipe updates require ownership
    Property 22: Recipe deletion requires ownership
    
    For any recipe owned by user A, attempting to update or delete it 
    as user B should fail with an authorization error.
    
    **Validates: Requirements 8.2, 9.2**
    """
    from app.services.recipe_service import RecipeManager
    from app.services.auth_service import AuthService
    from app.schemas import RecipeCreate, RecipeUpdate
    
    # Create two test users with unique usernames
    unique_id = uuid.uuid4().hex[:8]
    owner = AuthService.create_user(db, f"owner_{unique_id}", "password123")
    other_user = AuthService.create_user(db, f"other_{unique_id}", "password456")
    
    # Owner creates a recipe
    recipe_data = RecipeCreate(
        title=title,
        ingredients=["ingredient1"],
        steps=["step1"]
    )
    recipe = RecipeManager.create_recipe(db, owner.id, recipe_data)
    
    # Test Property 18: Other user cannot update the recipe
    update_data = RecipeUpdate(title=new_title)
    updated_recipe = RecipeManager.update_recipe(db, recipe.id, other_user.id, update_data)
    
    assert updated_recipe is None, "Other user should not be able to update owner's recipe"
    
    # Verify recipe was not modified
    unchanged_recipe = RecipeManager.get_recipe_by_id(db, recipe.id)
    import json
    assert unchanged_recipe.title == title, "Recipe title should remain unchanged"
    
    # Test Property 22: Other user cannot delete the recipe
    delete_success = RecipeManager.delete_recipe(db, recipe.id, other_user.id)
    
    assert delete_success is False, "Other user should not be able to delete owner's recipe"
    
    # Verify recipe still exists
    still_exists = RecipeManager.get_recipe_by_id(db, recipe.id)
    assert still_exists is not None, "Recipe should still exist after failed deletion attempt"
    
    # Verify owner can update their own recipe
    owner_update = RecipeManager.update_recipe(db, recipe.id, owner.id, update_data)
    assert owner_update is not None, "Owner should be able to update their own recipe"
    assert owner_update.title == new_title, "Recipe should be updated with new title"
    
    # Verify owner can delete their own recipe
    owner_delete = RecipeManager.delete_recipe(db, recipe.id, owner.id)
    assert owner_delete is True, "Owner should be able to delete their own recipe"
    
    # Verify recipe is deleted
    deleted_recipe = RecipeManager.get_recipe_by_id(db, recipe.id)
    assert deleted_recipe is None, "Recipe should be deleted after owner deletion"



# Feature: recipe-saver, Property 15: Search matches titles case-insensitively
@given(
    base_word=st.sampled_from(['Chocolate', 'Vanilla', 'Strawberry', 'Banana', 'Apple', 'Orange']),
    case_variant=st.sampled_from(['lower', 'upper', 'mixed'])
)
@hyp_settings(max_examples=100, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_search_case_insensitivity_property(db, base_word, case_variant):
    """
    Property 15: Search matches titles case-insensitively
    
    For any search query and recipe collection, the search results should 
    include all recipes whose titles contain the query string, regardless 
    of case differences.
    
    **Validates: Requirements 7.1, 7.2**
    """
    from app.services.recipe_service import RecipeManager
    from app.services.search_service import SearchEngine
    from app.services.auth_service import AuthService
    from app.schemas import RecipeCreate
    
    # Create a test user with unique username
    unique_username = f"searchuser_{uuid.uuid4().hex[:8]}"
    user = AuthService.create_user(db, unique_username, "password123")
    
    # Create a recipe with the base word in title
    title = f"{base_word} Recipe"
    recipe_data = RecipeCreate(
        title=title,
        ingredients=["ingredient1"],
        steps=["step1"]
    )
    recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
    
    # Apply case transformation to search query
    if case_variant == 'lower':
        search_query = base_word.lower()
    elif case_variant == 'upper':
        search_query = base_word.upper()
    else:  # mixed
        # Alternate case for each character
        search_query = ''.join(
            c.upper() if i % 2 == 0 else c.lower() 
            for i, c in enumerate(base_word)
        )
    
    # Search for recipes
    results = SearchEngine.search_recipes(db, user.id, search_query)
    
    # Verify the recipe is found regardless of case
    recipe_ids = [r.id for r in results]
    assert recipe.id in recipe_ids, f"Recipe with title '{title}' should be found with search query '{search_query}' (case-insensitive)"
    
    # Verify all results belong to the user
    for result in results:
        assert result.user_id == user.id, "All search results should belong to the searching user"



# Feature: recipe-saver, Property 16: Search respects user boundaries
@given(
    common_word=st.sampled_from(['pasta', 'chicken', 'salad', 'soup', 'cake']),
    user1_recipe_count=st.integers(min_value=1, max_value=3),
    user2_recipe_count=st.integers(min_value=1, max_value=3)
)
@hyp_settings(max_examples=100, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_search_user_boundaries_property(db, common_word, user1_recipe_count, user2_recipe_count):
    """
    Property 16: Search respects user boundaries
    
    For any user performing a search, the results should only include 
    recipes belonging to that user.
    
    **Validates: Requirements 7.3**
    """
    from app.services.recipe_service import RecipeManager
    from app.services.search_service import SearchEngine
    from app.services.auth_service import AuthService
    from app.schemas import RecipeCreate
    
    # Create two test users with unique usernames
    unique_id = uuid.uuid4().hex[:8]
    user1 = AuthService.create_user(db, f"searchuser1_{unique_id}", "password123")
    user2 = AuthService.create_user(db, f"searchuser2_{unique_id}", "password456")
    
    # Create recipes for user1 with the common word in title
    user1_recipe_ids = []
    for i in range(user1_recipe_count):
        recipe_data = RecipeCreate(
            title=f"User1 {common_word} Recipe {i}",
            ingredients=["ingredient1"],
            steps=["step1"]
        )
        recipe = RecipeManager.create_recipe(db, user1.id, recipe_data)
        user1_recipe_ids.append(recipe.id)
    
    # Create recipes for user2 with the same common word in title
    user2_recipe_ids = []
    for i in range(user2_recipe_count):
        recipe_data = RecipeCreate(
            title=f"User2 {common_word} Recipe {i}",
            ingredients=["ingredient2"],
            steps=["step2"]
        )
        recipe = RecipeManager.create_recipe(db, user2.id, recipe_data)
        user2_recipe_ids.append(recipe.id)
    
    # User1 searches for the common word
    user1_results = SearchEngine.search_recipes(db, user1.id, common_word)
    
    # Verify user1 only sees their own recipes
    assert len(user1_results) == user1_recipe_count, f"User1 should find {user1_recipe_count} recipes"
    
    for recipe in user1_results:
        assert recipe.user_id == user1.id, "All search results should belong to user1"
        assert recipe.id in user1_recipe_ids, "Recipe ID should be in user1's recipe list"
        assert recipe.id not in user2_recipe_ids, "Recipe ID should not be in user2's recipe list"
    
    # User2 searches for the same common word
    user2_results = SearchEngine.search_recipes(db, user2.id, common_word)
    
    # Verify user2 only sees their own recipes
    assert len(user2_results) == user2_recipe_count, f"User2 should find {user2_recipe_count} recipes"
    
    for recipe in user2_results:
        assert recipe.user_id == user2.id, "All search results should belong to user2"
        assert recipe.id in user2_recipe_ids, "Recipe ID should be in user2's recipe list"
        assert recipe.id not in user1_recipe_ids, "Recipe ID should not be in user1's recipe list"


# Feature: recipe-saver-enhancements, Property 13: Recipe duplication preserves content
# Feature: recipe-saver-enhancements, Property 14: Duplicated recipe title modification
@given(
    title=st.text(min_size=1, max_size=50, alphabet=st.characters(min_codepoint=32, max_codepoint=126)),
    ingredients=st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=10),
    steps=st.lists(st.text(min_size=1, max_size=100), min_size=1, max_size=10),
    tags=st.one_of(st.none(), st.lists(st.text(min_size=1, max_size=20), min_size=0, max_size=5)),
    reference_link=st.one_of(st.none(), st.text(min_size=10, max_size=100))
)
@hyp_settings(max_examples=100, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_recipe_duplication_property(db, title, ingredients, steps, tags, reference_link):
    """
    Property 13: Recipe duplication preserves content
    Property 14: Duplicated recipe title modification
    
    For any recipe, duplicating it should create a new recipe with identical 
    ingredients, steps, tags, and reference link, but with a different ID and 
    a modified title containing the original title plus a suffix.
    
    **Validates: Requirements 5.1, 5.2, 5.4**
    """
    from app.services.recipe_service import RecipeManager
    from app.services.auth_service import AuthService
    from app.schemas import RecipeCreate
    
    # Create a test user with unique username
    unique_username = f"dupuser_{uuid.uuid4().hex[:8]}"
    user = AuthService.create_user(db, unique_username, "password123")
    
    # Create original recipe
    recipe_data = RecipeCreate(
        title=title,
        ingredients=ingredients,
        steps=steps,
        tags=tags,
        reference_link=reference_link
    )
    original_recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
    
    # Duplicate the recipe
    duplicated_recipe = RecipeManager.duplicate_recipe(db, original_recipe.id, user.id)
    
    assert duplicated_recipe is not None, "Duplication should succeed"
    
    # Property 13: Content preservation
    import json
    assert duplicated_recipe.id != original_recipe.id, "Duplicated recipe should have a different ID"
    assert json.loads(duplicated_recipe.ingredients) == ingredients, "Ingredients should be preserved"
    assert json.loads(duplicated_recipe.steps) == steps, "Steps should be preserved"
    
    if tags is not None:
        assert duplicated_recipe.tags is not None, "Tags should not be None when provided"
        assert json.loads(duplicated_recipe.tags) == tags, "Tags should be preserved"
    else:
        assert duplicated_recipe.tags is None, "Tags should be None if not provided"
    
    assert duplicated_recipe.reference_link == reference_link, "Reference link should be preserved"
    
    # Property 14: Title modification
    assert duplicated_recipe.title != title, "Duplicated recipe title should be modified"
    assert title in duplicated_recipe.title, "Duplicated recipe title should contain original title"
    assert duplicated_recipe.title == f"{title} (Copy)", "Duplicated recipe should have ' (Copy)' suffix"
    
    # Verify source tracking
    assert duplicated_recipe.source_recipe_id == original_recipe.id, "Source recipe ID should be set"
    assert duplicated_recipe.source_author_id == original_recipe.user_id, "Source author ID should be set"


# Feature: recipe-saver-enhancements, Property 15: Bulk deletion completeness
# Feature: recipe-saver-enhancements, Property 16: Bulk operation atomicity
@given(
    recipe_count=st.integers(min_value=2, max_value=5)
)
@hyp_settings(max_examples=100, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_bulk_deletion_property(db, recipe_count):
    """
    Property 15: Bulk deletion completeness
    Property 16: Bulk operation atomicity
    
    For any set of user-owned recipes, bulk deletion should remove all 
    selected recipes from the database. If any recipe fails validation 
    (e.g., not owned by user), no recipes should be modified.
    
    **Validates: Requirements 6.1, 6.4**
    """
    from app.services.recipe_service import RecipeManager
    from app.services.auth_service import AuthService
    from app.schemas import RecipeCreate
    
    # Create two test users with unique usernames
    unique_id = uuid.uuid4().hex[:8]
    user1 = AuthService.create_user(db, f"bulkuser1_{unique_id}", "password123")
    user2 = AuthService.create_user(db, f"bulkuser2_{unique_id}", "password456")
    
    # Create recipes for user1
    user1_recipe_ids = []
    for i in range(recipe_count):
        recipe_data = RecipeCreate(
            title=f"User1 Recipe {i}",
            ingredients=["ingredient1"],
            steps=["step1"]
        )
        recipe = RecipeManager.create_recipe(db, user1.id, recipe_data)
        user1_recipe_ids.append(recipe.id)
    
    # Create one recipe for user2
    user2_recipe_data = RecipeCreate(
        title="User2 Recipe",
        ingredients=["ingredient2"],
        steps=["step2"]
    )
    user2_recipe = RecipeManager.create_recipe(db, user2.id, user2_recipe_data)
    
    # Property 15: Test successful bulk deletion
    deleted_count = RecipeManager.bulk_delete_recipes(db, user1_recipe_ids, user1.id)
    
    assert deleted_count == recipe_count, f"Should delete all {recipe_count} recipes"
    
    # Verify all recipes are deleted
    for recipe_id in user1_recipe_ids:
        recipe = RecipeManager.get_recipe_by_id(db, recipe_id)
        assert recipe is None, f"Recipe {recipe_id} should be deleted"
    
    # Property 16: Test atomicity - attempting to delete mix of owned and unowned recipes
    # Create new recipes for user1
    new_user1_recipe_ids = []
    for i in range(recipe_count):
        recipe_data = RecipeCreate(
            title=f"User1 New Recipe {i}",
            ingredients=["ingredient1"],
            steps=["step1"]
        )
        recipe = RecipeManager.create_recipe(db, user1.id, recipe_data)
        new_user1_recipe_ids.append(recipe.id)
    
    # Try to delete user1's recipes plus user2's recipe (should fail atomically)
    mixed_recipe_ids = new_user1_recipe_ids + [user2_recipe.id]
    
    try:
        RecipeManager.bulk_delete_recipes(db, mixed_recipe_ids, user1.id)
        assert False, "Bulk delete should fail when user doesn't own all recipes"
    except PermissionError:
        # Expected - operation should fail
        pass
    
    # Verify NO recipes were deleted (atomicity)
    for recipe_id in new_user1_recipe_ids:
        recipe = RecipeManager.get_recipe_by_id(db, recipe_id)
        assert recipe is not None, f"Recipe {recipe_id} should still exist (atomicity)"
    
    # Verify user2's recipe still exists
    user2_recipe_check = RecipeManager.get_recipe_by_id(db, user2_recipe.id)
    assert user2_recipe_check is not None, "User2's recipe should still exist"
