"""Property-based tests for API compatibility after MongoDB migration."""
import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"
os.environ["MONGODB_URL"] = "mongodb://localhost:27017"
os.environ["MONGODB_DATABASE"] = "recipe_saver_test"

from hypothesis import given, strategies as st, settings as hyp_settings, HealthCheck
from datetime import timedelta
import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.database import mongodb


# Helper strategies for generating valid test data
def valid_recipe_title():
    """Generate valid recipe titles."""
    return st.text(min_size=1, max_size=100, alphabet=st.characters(min_codepoint=32, max_codepoint=126))


def valid_ingredient_list():
    """Generate valid ingredient lists."""
    return st.lists(
        st.text(min_size=1, max_size=50, alphabet=st.characters(min_codepoint=32, max_codepoint=126)),
        min_size=1,
        max_size=10
    )


def valid_step_list():
    """Generate valid step lists."""
    return st.lists(
        st.text(min_size=1, max_size=100, alphabet=st.characters(min_codepoint=32, max_codepoint=126)),
        min_size=1,
        max_size=10
    )


def valid_tag_list():
    """Generate valid tag lists."""
    return st.one_of(
        st.none(),
        st.lists(
            st.text(min_size=1, max_size=20, alphabet=st.characters(min_codepoint=97, max_codepoint=122)),
            min_size=0,
            max_size=5
        )
    )


def valid_reference_link():
    """Generate valid reference links."""
    return st.one_of(
        st.none(),
        st.text(min_size=10, max_size=100, alphabet=st.characters(min_codepoint=33, max_codepoint=126))
    )


# Feature: mongodb-migration, Property 12: API Request Compatibility
@given(
    title=valid_recipe_title(),
    ingredients=valid_ingredient_list(),
    steps=valid_step_list(),
    tags=valid_tag_list(),
    reference_link=valid_reference_link()
)
@hyp_settings(
    max_examples=100,
    deadline=timedelta(milliseconds=5000),
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.asyncio
async def test_api_request_compatibility_property(
    setup_mongodb,
    title,
    ingredients,
    steps,
    tags,
    reference_link
):
    """
    Property 12: API Request Compatibility
    
    For any valid API request payload that worked before migration,
    the MongoDB-backed API should accept it without errors.
    
    **Validates: Requirements 6.2**
    """
    # Clean database before test
    db = await mongodb.get_database()
    for collection_name in await db.list_collection_names():
        await db[collection_name].delete_many({})
    
    client = TestClient(app)
    
    # Register a user
    register_response = client.post(
        "/api/auth/register",
        json={"username": f"testuser_{title[:10]}", "password": "password123"}
    )
    
    # Skip if username already exists (collision in random generation)
    if register_response.status_code == 409:
        return
    
    assert register_response.status_code == 201, \
        f"Registration should succeed, got {register_response.status_code}: {register_response.text}"
    
    # Login to get token
    login_response = client.post(
        "/api/auth/login",
        json={"username": f"testuser_{title[:10]}", "password": "password123"}
    )
    assert login_response.status_code == 200, "Login should succeed"
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test: Create recipe with valid payload
    recipe_payload = {
        "title": title,
        "ingredients": ingredients,
        "steps": steps,
        "tags": tags,
        "reference_link": reference_link
    }
    
    create_response = client.post(
        "/api/recipes",
        json=recipe_payload,
        headers=headers
    )
    
    # The API should accept the request without errors
    assert create_response.status_code == 201, \
        f"API should accept valid recipe payload, got {create_response.status_code}: {create_response.text}"
    
    recipe_data = create_response.json()
    recipe_id = recipe_data["id"]
    
    # Test: Update recipe with valid payload
    update_payload = {
        "title": f"Updated {title[:50]}"
    }
    
    update_response = client.put(
        f"/api/recipes/{recipe_id}",
        json=update_payload,
        headers=headers
    )
    
    assert update_response.status_code == 200, \
        f"API should accept valid update payload, got {update_response.status_code}: {update_response.text}"


# Feature: mongodb-migration, Property 13: API Response Compatibility
@given(
    title=valid_recipe_title(),
    ingredients=valid_ingredient_list(),
    steps=valid_step_list(),
    tags=valid_tag_list(),
    reference_link=valid_reference_link()
)
@hyp_settings(
    max_examples=100,
    deadline=timedelta(milliseconds=5000),
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.asyncio
async def test_api_response_compatibility_property(
    setup_mongodb,
    title,
    ingredients,
    steps,
    tags,
    reference_link
):
    """
    Property 13: API Response Compatibility
    
    For any API request, the response structure from the MongoDB-backed API
    should match the original SQLAlchemy-backed API structure.
    
    **Validates: Requirements 6.3, 6.4**
    """
    # Clean database before test
    db = await mongodb.get_database()
    for collection_name in await db.list_collection_names():
        await db[collection_name].delete_many({})
    
    client = TestClient(app)
    
    # Register and login
    username = f"testuser_{title[:10]}"
    register_response = client.post(
        "/api/auth/register",
        json={"username": username, "password": "password123"}
    )
    
    # Skip if username already exists
    if register_response.status_code == 409:
        return
    
    assert register_response.status_code == 201, "Registration should succeed"
    
    login_response = client.post(
        "/api/auth/login",
        json={"username": username, "password": "password123"}
    )
    assert login_response.status_code == 200, "Login should succeed"
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create recipe
    recipe_payload = {
        "title": title,
        "ingredients": ingredients,
        "steps": steps,
        "tags": tags,
        "reference_link": reference_link
    }
    
    create_response = client.post(
        "/api/recipes",
        json=recipe_payload,
        headers=headers
    )
    assert create_response.status_code == 201, "Recipe creation should succeed"
    
    # Verify response structure matches expected schema
    recipe_data = create_response.json()
    
    # Required fields that must be present
    required_fields = ["id", "user_id", "title", "ingredients", "steps", "created_at", "updated_at"]
    for field in required_fields:
        assert field in recipe_data, f"Response should contain '{field}' field"
    
    # Verify field types
    assert isinstance(recipe_data["id"], (int, str)), "id should be int or string"
    assert isinstance(recipe_data["user_id"], (int, str)), "user_id should be int or string"
    assert isinstance(recipe_data["title"], str), "title should be string"
    assert isinstance(recipe_data["ingredients"], list), "ingredients should be list"
    assert isinstance(recipe_data["steps"], list), "steps should be list"
    assert isinstance(recipe_data["created_at"], str), "created_at should be ISO string"
    assert isinstance(recipe_data["updated_at"], str), "updated_at should be ISO string"
    
    # Verify optional fields
    if tags is not None:
        assert "tags" in recipe_data, "Response should contain 'tags' field when provided"
        assert isinstance(recipe_data["tags"], list), "tags should be list"
    
    if reference_link is not None:
        assert "reference_link" in recipe_data, "Response should contain 'reference_link' field when provided"
    
    # Test GET endpoint response structure
    recipe_id = recipe_data["id"]
    get_response = client.get(
        f"/api/recipes/{recipe_id}",
        headers=headers
    )
    
    assert get_response.status_code == 200, "GET request should succeed"
    get_data = get_response.json()
    
    # Verify GET response has same structure
    for field in required_fields:
        assert field in get_data, f"GET response should contain '{field}' field"
    
    # Test LIST endpoint response structure
    list_response = client.get(
        "/api/recipes",
        headers=headers
    )
    
    assert list_response.status_code == 200, "LIST request should succeed"
    list_data = list_response.json()
    
    assert isinstance(list_data, list), "LIST response should be an array"
    if len(list_data) > 0:
        for field in required_fields:
            assert field in list_data[0], f"LIST response items should contain '{field}' field"


# Feature: mongodb-migration, Property 14: API Query Parameter Compatibility
@given(
    recipe_count=st.integers(min_value=2, max_value=5),
    search_term=st.sampled_from(["pasta", "chicken", "salad", "soup", "cake"]),
    sort_by=st.sampled_from(["date", "title"]),
    sort_order=st.sampled_from(["asc", "desc"])
)
@hyp_settings(
    max_examples=100,
    deadline=timedelta(milliseconds=5000),
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.asyncio
async def test_api_query_parameter_compatibility_property(
    setup_mongodb,
    recipe_count,
    search_term,
    sort_by,
    sort_order
):
    """
    Property 14: API Query Parameter Compatibility
    
    For any API request with query parameters (filters, sorting, pagination),
    the MongoDB-backed API should return results equivalent to the original API.
    
    **Validates: Requirements 6.5**
    """
    # Clean database before test
    db = await mongodb.get_database()
    for collection_name in await db.list_collection_names():
        await db[collection_name].delete_many({})
    
    client = TestClient(app)
    
    # Register and login
    username = f"testuser_{search_term}"
    register_response = client.post(
        "/api/auth/register",
        json={"username": username, "password": "password123"}
    )
    
    # Skip if username already exists
    if register_response.status_code == 409:
        return
    
    assert register_response.status_code == 201, "Registration should succeed"
    
    login_response = client.post(
        "/api/auth/login",
        json={"username": username, "password": "password123"}
    )
    assert login_response.status_code == 200, "Login should succeed"
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create multiple recipes with search term in title
    created_recipe_ids = []
    for i in range(recipe_count):
        recipe_payload = {
            "title": f"{search_term} Recipe {i}",
            "ingredients": ["ingredient1", "ingredient2"],
            "steps": ["step1", "step2"],
            "tags": ["tag1", "tag2"]
        }
        
        create_response = client.post(
            "/api/recipes",
            json=recipe_payload,
            headers=headers
        )
        assert create_response.status_code == 201, "Recipe creation should succeed"
        created_recipe_ids.append(create_response.json()["id"])
    
    # Test: Search query parameter
    search_response = client.get(
        f"/api/recipes?search={search_term}",
        headers=headers
    )
    
    assert search_response.status_code == 200, \
        f"Search with query parameter should succeed, got {search_response.status_code}"
    
    search_results = search_response.json()
    assert isinstance(search_results, list), "Search results should be a list"
    assert len(search_results) == recipe_count, \
        f"Search should return all {recipe_count} recipes with '{search_term}' in title"
    
    # Verify all results contain the search term
    for recipe in search_results:
        assert search_term.lower() in recipe["title"].lower(), \
            f"Search result should contain search term '{search_term}'"
    
    # Test: Filter query parameters
    filter_response = client.get(
        f"/api/recipes/filter?tags=tag1&sort_by={sort_by}&sort_order={sort_order}",
        headers=headers
    )
    
    assert filter_response.status_code == 200, \
        f"Filter with query parameters should succeed, got {filter_response.status_code}"
    
    filter_results = filter_response.json()
    assert isinstance(filter_results, list), "Filter results should be a list"
    
    # Verify all results have the requested tag
    for recipe in filter_results:
        assert "tags" in recipe, "Recipe should have tags field"
        assert "tag1" in recipe["tags"], "Recipe should have the filtered tag"
    
    # Verify sort order
    if len(filter_results) > 1:
        if sort_by == "title":
            titles = [r["title"] for r in filter_results]
            if sort_order == "asc":
                assert titles == sorted(titles), "Results should be sorted by title ascending"
            else:
                assert titles == sorted(titles, reverse=True), "Results should be sorted by title descending"
        elif sort_by == "date":
            dates = [r["created_at"] for r in filter_results]
            if sort_order == "asc":
                assert dates == sorted(dates), "Results should be sorted by date ascending"
            else:
                assert dates == sorted(dates, reverse=True), "Results should be sorted by date descending"
    
    # Test: Favorites filter
    # Mark first recipe as favorite
    if len(created_recipe_ids) > 0:
        favorite_response = client.patch(
            f"/api/recipes/{created_recipe_ids[0]}/favorite",
            json={"is_favorite": True},
            headers=headers
        )
        assert favorite_response.status_code == 200, "Favorite toggle should succeed"
        
        # Filter by favorites
        favorites_response = client.get(
            "/api/recipes/filter?favorites=true",
            headers=headers
        )
        
        assert favorites_response.status_code == 200, "Favorites filter should succeed"
        favorites_results = favorites_response.json()
        
        # Should return at least the one favorite recipe
        assert len(favorites_results) >= 1, "Should return at least one favorite recipe"
        
        # Verify all results are favorites
        for recipe in favorites_results:
            assert recipe.get("is_favorite") is True, "All results should be favorites"
