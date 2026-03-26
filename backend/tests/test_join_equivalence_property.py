"""Property-based test for join equivalence.

Feature: mongodb-migration
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from datetime import datetime
from bson import ObjectId

from app.repositories.recipe_repository import RecipeRepository
from app.repositories.recipe_rating_repository import RecipeRatingRepository
from app.database import mongodb
from tests.conftest import clean_all_collections


@st.composite
def recipe_with_ratings_strategy(draw):
    """Generate a recipe with associated ratings."""
    recipe_id = ObjectId()
    user_id = ObjectId()
    
    recipe = {
        "user_id": user_id,
        "title": draw(st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',), blacklist_characters=['\x00']))),
        "ingredients": ["ingredient1", "ingredient2"],
        "steps": ["step1", "step2"],
        "tags": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "visibility": "public",
        "servings": 4,
        "dietary_labels": [],
        "allergen_warnings": []
    }
    
    # Generate 1-5 ratings for this recipe
    num_ratings = draw(st.integers(min_value=1, max_value=5))
    ratings = []
    for _ in range(num_ratings):
        rating = {
            "recipe_id": recipe_id,
            "user_id": ObjectId(),
            "rating": draw(st.integers(min_value=1, max_value=5)),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        ratings.append(rating)
    
    return recipe_id, recipe, ratings


# Property 9: Join Equivalence
# **Validates: Requirements 3.5**
@given(recipe_data=recipe_with_ratings_strategy())
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@pytest.mark.asyncio
async def test_join_equivalence(recipe_data, setup_mongodb):
    """
    Property 9: Join Equivalence
    
    For any query involving related collections, the results should match 
    the equivalent relational JOIN operation.
    
    This test verifies that fetching a recipe and its ratings using MongoDB
    references produces the same result as a relational JOIN would.
    """
    await clean_all_collections()
    
    db = await mongodb.get_database()
    
    recipe_repo = RecipeRepository(db)
    rating_repo = RecipeRatingRepository(db)
    
    await recipe_repo.ensure_indexes()
    await rating_repo.ensure_indexes()
    
    recipe_id, recipe, ratings = recipe_data
    
    # Insert recipe with known _id
    recipe["_id"] = recipe_id
    await recipe_repo.collection.insert_one(recipe)
    
    # Insert ratings
    for rating in ratings:
        await rating_repo.create(rating)
    
    # MongoDB approach: Fetch recipe, then fetch ratings by recipe_id
    fetched_recipe = await recipe_repo.find_by_id(str(recipe_id))
    fetched_ratings = await rating_repo.find_by_recipe(str(recipe_id), limit=100)
    
    # Verify join equivalence
    assert fetched_recipe is not None, "Recipe should be found"
    assert len(fetched_ratings) == len(ratings), \
        f"Expected {len(ratings)} ratings, got {len(fetched_ratings)}"
    
    # Verify all ratings belong to the correct recipe
    for fetched_rating in fetched_ratings:
        assert fetched_rating["recipe_id"] == recipe_id, \
            "Rating recipe_id doesn't match"
    
    # Verify rating values match (order may differ)
    fetched_rating_values = sorted([r["rating"] for r in fetched_ratings])
    expected_rating_values = sorted([r["rating"] for r in ratings])
    assert fetched_rating_values == expected_rating_values, \
        "Rating values don't match"
    
    # Test aggregation (equivalent to SQL GROUP BY with AVG)
    avg_rating = await rating_repo.get_average_rating(str(recipe_id))
    expected_avg = sum(r["rating"] for r in ratings) / len(ratings)
    
    assert avg_rating is not None, "Average rating should be calculated"
    assert abs(avg_rating - expected_avg) < 0.01, \
        f"Average rating {avg_rating} doesn't match expected {expected_avg}"
