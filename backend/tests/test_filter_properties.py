"""Property-based tests for filter engine service."""
import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"

from hypothesis import given, strategies as st, settings as hyp_settings, HealthCheck
from datetime import timedelta
import pytest
import uuid
import json


# Feature: recipe-saver-enhancements, Property 4: Favorite filtering correctness
@given(
    favorite_count=st.integers(min_value=1, max_value=5),
    non_favorite_count=st.integers(min_value=1, max_value=5)
)
@hyp_settings(max_examples=5, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_favorite_filtering_correctness_property(db, favorite_count, non_favorite_count):
    """
    Property 4: Favorite filtering correctness
    
    For any user's recipe collection, filtering by favorites should return 
    only recipes where is_favorite=true.
    
    **Validates: Requirements 2.4, 4.2**
    """
    from app.services.recipe_service import RecipeManager
    from app.services.auth_service import AuthService
    from app.services.filter_service import FilterEngine
    from app.schemas import RecipeCreate
    
    # Create a test user
    user = AuthService.create_user(db, f"testuser_{uuid.uuid4().hex[:8]}", "password123")
    
    # Create favorite recipes
    favorite_recipe_ids = []
    for i in range(favorite_count):
        recipe_data = RecipeCreate(
            title=f"Favorite Recipe {i}",
            ingredients=["ingredient1"],
            steps=["step1"]
        )
        recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
        recipe.is_favorite = True
        db.commit()
        favorite_recipe_ids.append(recipe.id)
    
    # Create non-favorite recipes
    non_favorite_recipe_ids = []
    for i in range(non_favorite_count):
        recipe_data = RecipeCreate(
            title=f"Non-Favorite Recipe {i}",
            ingredients=["ingredient1"],
            steps=["step1"]
        )
        recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
        recipe.is_favorite = False
        db.commit()
        non_favorite_recipe_ids.append(recipe.id)
    
    # Filter by favorites
    filtered_recipes = FilterEngine.filter_recipes(
        db=db,
        user_id=user.id,
        favorites=True
    )
    
    # Verify all returned recipes are favorites
    assert len(filtered_recipes) == favorite_count, "Should return exactly the favorite recipes"
    for recipe in filtered_recipes:
        assert recipe.is_favorite is True, "All filtered recipes should be favorites"
        assert recipe.id in favorite_recipe_ids, "Recipe should be one of the favorites"


# Feature: recipe-saver-enhancements, Property 8: Tag filtering correctness
@given(
    matching_tag_count=st.integers(min_value=1, max_value=5),
    non_matching_count=st.integers(min_value=1, max_value=5)
)
@hyp_settings(max_examples=5, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_tag_filtering_correctness_property(db, matching_tag_count, non_matching_count):
    """
    Property 8: Tag filtering correctness
    
    For any set of selected tags, filtering should return only recipes 
    that contain at least one of the selected tags.
    
    **Validates: Requirements 4.1**
    """
    from app.services.recipe_service import RecipeManager
    from app.services.auth_service import AuthService
    from app.services.filter_service import FilterEngine
    from app.schemas import RecipeCreate
    
    # Create a test user
    user = AuthService.create_user(db, f"testuser_{uuid.uuid4().hex[:8]}", "password123")
    
    # Create recipes with matching tags
    filter_tags = ["italian", "pasta"]
    for i in range(matching_tag_count):
        recipe_data = RecipeCreate(
            title=f"Italian Recipe {i}",
            ingredients=["ingredient1"],
            steps=["step1"],
            tags=["italian", "dinner"]
        )
        RecipeManager.create_recipe(db, user.id, recipe_data)
    
    # Create recipes without matching tags
    for i in range(non_matching_count):
        recipe_data = RecipeCreate(
            title=f"Mexican Recipe {i}",
            ingredients=["ingredient1"],
            steps=["step1"],
            tags=["mexican", "spicy"]
        )
        RecipeManager.create_recipe(db, user.id, recipe_data)
    
    # Filter by tags
    filtered_recipes = FilterEngine.filter_recipes(
        db=db,
        user_id=user.id,
        tags=filter_tags
    )
    
    # Verify all returned recipes have at least one matching tag
    assert len(filtered_recipes) == matching_tag_count, "Should return only recipes with matching tags"
    for recipe in filtered_recipes:
        recipe_tags = json.loads(recipe.tags)
        recipe_tags_lower = [t.lower() for t in recipe_tags]
        assert any(tag in recipe_tags_lower for tag in filter_tags), "Recipe should have at least one matching tag"


# Feature: recipe-saver-enhancements, Property 9: Rating threshold filtering
@given(
    high_rating_count=st.integers(min_value=1, max_value=5),
    low_rating_count=st.integers(min_value=1, max_value=5)
)
@hyp_settings(max_examples=5, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_rating_threshold_filtering_property(db, high_rating_count, low_rating_count):
    """
    Property 9: Rating threshold filtering
    
    For any minimum rating threshold, filtering should return only recipes 
    with average rating >= threshold.
    
    **Validates: Requirements 4.3**
    """
    from app.services.recipe_service import RecipeManager
    from app.services.auth_service import AuthService
    from app.services.filter_service import FilterEngine
    from app.services.rating_service import RatingSystem
    from app.schemas import RecipeCreate
    
    # Create a test user
    user = AuthService.create_user(db, f"testuser_{uuid.uuid4().hex[:8]}", "password123")
    
    # Create recipes with high ratings (4-5 stars)
    for i in range(high_rating_count):
        recipe_data = RecipeCreate(
            title=f"High Rated Recipe {i}",
            ingredients=["ingredient1"],
            steps=["step1"]
        )
        recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
        RatingSystem.add_rating(db, recipe.id, user.id, 5)
    
    # Create recipes with low ratings (1-2 stars)
    for i in range(low_rating_count):
        recipe_data = RecipeCreate(
            title=f"Low Rated Recipe {i}",
            ingredients=["ingredient1"],
            steps=["step1"]
        )
        recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
        RatingSystem.add_rating(db, recipe.id, user.id, 2)
    
    # Filter by minimum rating of 4
    filtered_recipes = FilterEngine.filter_recipes(
        db=db,
        user_id=user.id,
        min_rating=4.0
    )
    
    # Verify all returned recipes meet the threshold
    assert len(filtered_recipes) == high_rating_count, "Should return only high-rated recipes"
    for recipe in filtered_recipes:
        avg_rating = RatingSystem.get_average_rating(db, recipe.id)
        assert avg_rating >= 4.0, f"Recipe rating {avg_rating} should be >= 4.0"


# Feature: recipe-saver-enhancements, Property 10: Sort by date correctness
@given(
    recipe_count=st.integers(min_value=2, max_value=5)
)
@hyp_settings(max_examples=5, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_sort_by_date_correctness_property(db, recipe_count):
    """
    Property 10: Sort by date correctness
    
    For any recipe collection, sorting by creation date should return 
    recipes ordered by created_at timestamp.
    
    **Validates: Requirements 4.4**
    """
    from app.services.recipe_service import RecipeManager
    from app.services.auth_service import AuthService
    from app.services.filter_service import FilterEngine
    from app.schemas import RecipeCreate
    import time
    
    # Create a test user
    user = AuthService.create_user(db, f"testuser_{uuid.uuid4().hex[:8]}", "password123")
    
    # Create recipes with slight delays to ensure different timestamps
    for i in range(recipe_count):
        recipe_data = RecipeCreate(
            title=f"Recipe {i}",
            ingredients=["ingredient1"],
            steps=["step1"]
        )
        RecipeManager.create_recipe(db, user.id, recipe_data)
        time.sleep(0.01)  # Small delay to ensure different timestamps
    
    # Sort by date ascending
    sorted_asc = FilterEngine.filter_recipes(
        db=db,
        user_id=user.id,
        sort_by="date",
        sort_order="asc"
    )
    
    # Verify ascending order
    for i in range(len(sorted_asc) - 1):
        assert sorted_asc[i].created_at <= sorted_asc[i + 1].created_at, "Recipes should be in ascending date order"
    
    # Sort by date descending
    sorted_desc = FilterEngine.filter_recipes(
        db=db,
        user_id=user.id,
        sort_by="date",
        sort_order="desc"
    )
    
    # Verify descending order
    for i in range(len(sorted_desc) - 1):
        assert sorted_desc[i].created_at >= sorted_desc[i + 1].created_at, "Recipes should be in descending date order"


# Feature: recipe-saver-enhancements, Property 11: Sort by rating correctness
@given(
    recipe_count=st.integers(min_value=2, max_value=5)
)
@hyp_settings(max_examples=5, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_sort_by_rating_correctness_property(db, recipe_count):
    """
    Property 11: Sort by rating correctness
    
    For any recipe collection, sorting by rating should return recipes 
    ordered by rating value in descending order.
    
    **Validates: Requirements 4.5**
    """
    from app.services.recipe_service import RecipeManager
    from app.services.auth_service import AuthService
    from app.services.filter_service import FilterEngine
    from app.services.rating_service import RatingSystem
    from app.schemas import RecipeCreate
    
    # Create a test user
    user = AuthService.create_user(db, f"testuser_{uuid.uuid4().hex[:8]}", "password123")
    
    # Create recipes with different ratings
    for i in range(recipe_count):
        recipe_data = RecipeCreate(
            title=f"Recipe {i}",
            ingredients=["ingredient1"],
            steps=["step1"]
        )
        recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
        # Assign rating from 1 to 5
        rating = (i % 5) + 1
        RatingSystem.add_rating(db, recipe.id, user.id, rating)
    
    # Sort by rating descending
    sorted_desc = FilterEngine.filter_recipes(
        db=db,
        user_id=user.id,
        sort_by="rating",
        sort_order="desc"
    )
    
    # Verify descending order
    for i in range(len(sorted_desc) - 1):
        rating1 = RatingSystem.get_average_rating(db, sorted_desc[i].id) or 0
        rating2 = RatingSystem.get_average_rating(db, sorted_desc[i + 1].id) or 0
        assert rating1 >= rating2, "Recipes should be in descending rating order"


# Feature: recipe-saver-enhancements, Property 12: Combined filters correctness
@given(
    matching_count=st.integers(min_value=1, max_value=3),
    non_matching_count=st.integers(min_value=1, max_value=3)
)
@hyp_settings(max_examples=5, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_combined_filters_correctness_property(db, matching_count, non_matching_count):
    """
    Property 12: Combined filters correctness
    
    For any combination of filters (favorites, tags, rating), the results 
    should satisfy all filter criteria simultaneously.
    
    **Validates: Requirements 4.6**
    """
    from app.services.recipe_service import RecipeManager
    from app.services.auth_service import AuthService
    from app.services.filter_service import FilterEngine
    from app.services.rating_service import RatingSystem
    from app.schemas import RecipeCreate
    
    # Create a test user
    user = AuthService.create_user(db, f"testuser_{uuid.uuid4().hex[:8]}", "password123")
    
    # Create recipes that match all criteria (favorite + italian tag + high rating)
    for i in range(matching_count):
        recipe_data = RecipeCreate(
            title=f"Matching Recipe {i}",
            ingredients=["ingredient1"],
            steps=["step1"],
            tags=["italian", "dinner"]
        )
        recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
        recipe.is_favorite = True
        db.commit()
        RatingSystem.add_rating(db, recipe.id, user.id, 5)
    
    # Create recipes that don't match all criteria
    for i in range(non_matching_count):
        recipe_data = RecipeCreate(
            title=f"Non-Matching Recipe {i}",
            ingredients=["ingredient1"],
            steps=["step1"],
            tags=["mexican"]
        )
        recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
        recipe.is_favorite = False
        db.commit()
        RatingSystem.add_rating(db, recipe.id, user.id, 2)
    
    # Apply combined filters
    filtered_recipes = FilterEngine.filter_recipes(
        db=db,
        user_id=user.id,
        favorites=True,
        min_rating=4.0,
        tags=["italian"]
    )
    
    # Verify all criteria are met
    assert len(filtered_recipes) == matching_count, "Should return only recipes matching all criteria"
    for recipe in filtered_recipes:
        assert recipe.is_favorite is True, "Recipe should be favorite"
        avg_rating = RatingSystem.get_average_rating(db, recipe.id)
        assert avg_rating >= 4.0, "Recipe should have high rating"
        recipe_tags = json.loads(recipe.tags)
        recipe_tags_lower = [t.lower() for t in recipe_tags]
        assert "italian" in recipe_tags_lower, "Recipe should have italian tag"


# Feature: recipe-saver-enhancements, Property 43: Dietary label filtering
@given(
    matching_count=st.integers(min_value=1, max_value=5),
    non_matching_count=st.integers(min_value=1, max_value=5)
)
@hyp_settings(max_examples=5, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_dietary_label_filtering_property(db, matching_count, non_matching_count):
    """
    Property 43: Dietary label filtering
    
    For any set of dietary labels, filtering should return only recipes 
    that have all specified labels.
    
    **Validates: Requirements 26.3**
    """
    from app.services.recipe_service import RecipeManager
    from app.services.auth_service import AuthService
    from app.services.filter_service import FilterEngine
    from app.services.nutrition_service import NutritionTracker
    from app.schemas import RecipeCreate
    
    # Create a test user
    user = AuthService.create_user(db, f"testuser_{uuid.uuid4().hex[:8]}", "password123")
    
    # Create recipes with matching dietary labels
    for i in range(matching_count):
        recipe_data = RecipeCreate(
            title=f"Vegan Recipe {i}",
            ingredients=["ingredient1"],
            steps=["step1"]
        )
        recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
        NutritionTracker.add_dietary_labels(db, recipe.id, ["vegan", "gluten-free"], user.id)
    
    # Create recipes without matching dietary labels
    for i in range(non_matching_count):
        recipe_data = RecipeCreate(
            title=f"Non-Vegan Recipe {i}",
            ingredients=["ingredient1"],
            steps=["step1"]
        )
        recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
        NutritionTracker.add_dietary_labels(db, recipe.id, ["vegetarian"], user.id)
    
    # Filter by dietary labels
    filtered_recipes = FilterEngine.filter_recipes(
        db=db,
        user_id=user.id,
        dietary_labels=["vegan"]
    )
    
    # Verify all returned recipes have the dietary label
    assert len(filtered_recipes) == matching_count, "Should return only recipes with matching dietary labels"
    for recipe in filtered_recipes:
        from app.models import DietaryLabel
        labels = db.query(DietaryLabel).filter(DietaryLabel.recipe_id == recipe.id).all()
        label_names = [label.label for label in labels]
        assert "vegan" in label_names, "Recipe should have vegan label"


# Feature: recipe-saver-enhancements, Property 44: Allergen exclusion filtering
@given(
    safe_count=st.integers(min_value=1, max_value=5),
    unsafe_count=st.integers(min_value=1, max_value=5)
)
@hyp_settings(max_examples=5, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_allergen_exclusion_filtering_property(db, safe_count, unsafe_count):
    """
    Property 44: Allergen exclusion filtering
    
    For any set of allergens, filtering should return only recipes that 
    do not contain any of the specified allergens.
    
    **Validates: Requirements 27.3**
    """
    from app.services.recipe_service import RecipeManager
    from app.services.auth_service import AuthService
    from app.services.filter_service import FilterEngine
    from app.services.nutrition_service import NutritionTracker
    from app.schemas import RecipeCreate
    
    # Create a test user
    user = AuthService.create_user(db, f"testuser_{uuid.uuid4().hex[:8]}", "password123")
    
    # Create recipes without nuts
    for i in range(safe_count):
        recipe_data = RecipeCreate(
            title=f"Nut-Free Recipe {i}",
            ingredients=["ingredient1"],
            steps=["step1"]
        )
        recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
        NutritionTracker.add_allergen_warnings(db, recipe.id, ["dairy"], user.id)
    
    # Create recipes with nuts
    for i in range(unsafe_count):
        recipe_data = RecipeCreate(
            title=f"Recipe with Nuts {i}",
            ingredients=["ingredient1"],
            steps=["step1"]
        )
        recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
        NutritionTracker.add_allergen_warnings(db, recipe.id, ["nuts", "dairy"], user.id)
    
    # Filter excluding nuts
    filtered_recipes = FilterEngine.filter_recipes(
        db=db,
        user_id=user.id,
        exclude_allergens=["nuts"]
    )
    
    # Verify no returned recipes contain nuts
    assert len(filtered_recipes) == safe_count, "Should return only recipes without nuts"
    for recipe in filtered_recipes:
        from app.models import AllergenWarning
        allergens = db.query(AllergenWarning).filter(AllergenWarning.recipe_id == recipe.id).all()
        allergen_names = [allergen.allergen for allergen in allergens]
        assert "nuts" not in allergen_names, "Recipe should not contain nuts"
