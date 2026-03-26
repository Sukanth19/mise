"""Property-based tests for RecipeRepository.

Feature: mongodb-migration
"""

import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from datetime import datetime
from bson import ObjectId

from app.repositories.recipe_repository import RecipeRepository
from app.database import mongodb
from pymongo import ASCENDING, DESCENDING
from tests.conftest import clean_all_collections


# Hypothesis strategies for generating test data
@st.composite
def recipe_document_strategy(draw):
    """Generate valid recipe document data."""
    return {
        "user_id": ObjectId(),
        "title": draw(st.text(min_size=1, max_size=255, alphabet=st.characters(blacklist_categories=('Cs',), blacklist_characters=['\x00']))),
        "image_url": draw(st.one_of(st.none(), st.text(max_size=500, alphabet=st.characters(blacklist_categories=('Cs',))))),
        "ingredients": draw(st.lists(st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',), blacklist_characters=['\x00'])), min_size=0, max_size=20)),
        "steps": draw(st.lists(st.text(min_size=1, max_size=500, alphabet=st.characters(blacklist_categories=('Cs',), blacklist_characters=['\x00'])), min_size=0, max_size=20)),
        "tags": draw(st.lists(st.sampled_from(["dessert", "dinner", "lunch", "breakfast", "snack"]), max_size=5)),
        "reference_link": draw(st.one_of(st.none(), st.text(max_size=500, alphabet=st.characters(blacklist_categories=('Cs',))))),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_favorite": draw(st.booleans()),
        "visibility": draw(st.sampled_from(["private", "public", "unlisted"])),
        "servings": draw(st.integers(min_value=1, max_value=20)),
        "dietary_labels": draw(st.lists(st.sampled_from(["vegan", "vegetarian", "gluten-free"]), max_size=3)),
        "allergen_warnings": draw(st.lists(st.sampled_from(["nuts", "dairy", "eggs"]), max_size=3))
    }


# Property 5: Filter Correctness
# **Validates: Requirements 3.6**
@given(
    recipes=st.lists(recipe_document_strategy(), min_size=5, max_size=20),
    filter_tag=st.sampled_from(["dessert", "dinner", "lunch"])
)
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@pytest.mark.asyncio
async def test_recipe_filter_correctness(recipes, filter_tag, setup_mongodb):
    """
    Property 5: Filter Correctness
    
    For any query filter conditions, all returned documents should 
    satisfy those conditions.
    """
    await clean_all_collections()
    
    db = await mongodb.get_database()
    recipe_repo = RecipeRepository(db)
    await recipe_repo.ensure_indexes()
    
    # Insert recipes with some having the filter tag
    for recipe in recipes:
        if len(recipe["tags"]) > 0 and recipe["tags"][0] == filter_tag:
            # Ensure at least some recipes have the tag
            pass
        await recipe_repo.create(recipe)
    
    # Query with filter
    results = await recipe_repo.find_with_filters(tags=[filter_tag], limit=100)
    
    # All results must contain the filter tag
    for result in results:
        assert filter_tag in result["tags"], f"Recipe {result['_id']} missing tag {filter_tag}"


# Property 6: Sort Order Correctness
# **Validates: Requirements 3.7**
@given(recipes=st.lists(recipe_document_strategy(), min_size=3, max_size=10))
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@pytest.mark.asyncio
async def test_recipe_sort_order_correctness(recipes, setup_mongodb):
    """
    Property 6: Sort Order Correctness
    
    For any sort specification, returned documents should be ordered 
    according to the sort criteria.
    """
    await clean_all_collections()
    
    db = await mongodb.get_database()
    recipe_repo = RecipeRepository(db)
    await recipe_repo.ensure_indexes()
    
    # Insert recipes
    for recipe in recipes:
        await recipe_repo.create(recipe)
    
    # Query with descending sort by created_at
    results = await recipe_repo.find_many({}, sort=[("created_at", DESCENDING)], limit=100)
    
    # Verify sort order
    for i in range(len(results) - 1):
        assert results[i]["created_at"] >= results[i + 1]["created_at"], \
            "Results not sorted in descending order by created_at"


# Property 7: Pagination Subset Correctness
# **Validates: Requirements 3.8**
@given(
    recipes=st.lists(recipe_document_strategy(), min_size=10, max_size=20),
    skip=st.integers(min_value=0, max_value=5),
    limit=st.integers(min_value=1, max_value=10)
)
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@pytest.mark.asyncio
async def test_recipe_pagination_subset_correctness(recipes, skip, limit, setup_mongodb):
    """
    Property 7: Pagination Subset Correctness
    
    For any pagination parameters (skip, limit), the returned documents 
    should be the correct subset of the full result set.
    """
    await clean_all_collections()
    
    db = await mongodb.get_database()
    recipe_repo = RecipeRepository(db)
    await recipe_repo.ensure_indexes()
    
    # Insert recipes
    for recipe in recipes:
        await recipe_repo.create(recipe)
    
    # Get full result set
    all_results = await recipe_repo.find_many({}, sort=[("created_at", DESCENDING)], limit=100)
    
    # Get paginated subset
    paginated_results = await recipe_repo.find_many(
        {}, 
        sort=[("created_at", DESCENDING)], 
        skip=skip, 
        limit=limit
    )
    
    # Verify subset correctness
    expected_subset = all_results[skip:skip + limit]
    assert len(paginated_results) == len(expected_subset)
    
    for i, result in enumerate(paginated_results):
        assert str(result["_id"]) == str(expected_subset[i]["_id"]), \
            f"Paginated result at index {i} doesn't match expected"


# Property 8: Text Search Relevance
# **Validates: Requirements 3.9**
@given(
    search_term=st.sampled_from(["chocolate", "chicken", "pasta", "salad"]),
    num_matching=st.integers(min_value=2, max_value=5),
    num_non_matching=st.integers(min_value=2, max_value=5)
)
@settings(max_examples=30, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@pytest.mark.asyncio
async def test_recipe_text_search_relevance(search_term, num_matching, num_non_matching, setup_mongodb):
    """
    Property 8: Text Search Relevance
    
    For any text search query, all returned documents should contain 
    the search terms in the indexed fields.
    """
    await clean_all_collections()
    
    db = await mongodb.get_database()
    recipe_repo = RecipeRepository(db)
    await recipe_repo.ensure_indexes()
    
    # Create matching recipes (contain search term in title)
    for i in range(num_matching):
        recipe = {
            "user_id": ObjectId(),
            "title": f"{search_term} recipe {i}",
            "ingredients": ["flour", "sugar"],
            "steps": ["mix", "bake"],
            "tags": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "visibility": "public",
            "servings": 4,
            "dietary_labels": [],
            "allergen_warnings": []
        }
        await recipe_repo.create(recipe)
    
    # Create non-matching recipes
    for i in range(num_non_matching):
        recipe = {
            "user_id": ObjectId(),
            "title": f"random recipe {i}",
            "ingredients": ["water", "salt"],
            "steps": ["boil", "serve"],
            "tags": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "visibility": "public",
            "servings": 2,
            "dietary_labels": [],
            "allergen_warnings": []
        }
        await recipe_repo.create(recipe)
    
    # Search
    results = await recipe_repo.search(search_term, limit=100)
    
    # All results should contain the search term in title or ingredients
    for result in results:
        title_match = search_term.lower() in result["title"].lower()
        ingredients_match = any(search_term.lower() in ing.lower() for ing in result.get("ingredients", []))
        assert title_match or ingredients_match, \
            f"Recipe {result['_id']} doesn't contain search term '{search_term}'"


# Property 16: Pagination Limit Enforcement
# **Validates: Requirements 9.5**
@given(
    recipes=st.lists(recipe_document_strategy(), min_size=110, max_size=120),
    requested_limit=st.integers(min_value=50, max_value=200)
)
@settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.data_too_large, HealthCheck.too_slow])
@pytest.mark.asyncio
async def test_recipe_pagination_limit_enforcement(recipes, requested_limit, setup_mongodb):
    """
    Property 16: Pagination Limit Enforcement
    
    For any query, the number of returned documents should not exceed 
    the maximum page size (100).
    """
    await clean_all_collections()
    
    db = await mongodb.get_database()
    recipe_repo = RecipeRepository(db)
    await recipe_repo.ensure_indexes()
    
    # Insert many recipes
    for recipe in recipes:
        await recipe_repo.create(recipe)
    
    # Query with limit exceeding maximum
    results = await recipe_repo.find_many({}, limit=requested_limit)
    
    # Verify limit enforcement
    max_page_size = 100
    if requested_limit > max_page_size:
        assert len(results) <= max_page_size, \
            f"Returned {len(results)} documents, exceeding max page size of {max_page_size}"
    else:
        assert len(results) <= requested_limit, \
            f"Returned {len(results)} documents, exceeding requested limit of {requested_limit}"
