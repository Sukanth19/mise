"""
Property-based tests for API compatibility with MySQL backend.

This test file implements Property 14: API Request-Response Compatibility
to verify that the MySQL-backed API maintains the same behavior as the
original SQLAlchemy-backed API.

**Validates: Requirements 6.2, 6.3, 6.4, 6.5**

Task 9.2: Write property tests for API compatibility
"""
import os
import pytest
from hypothesis import given, strategies as st, settings as hyp_settings, HealthCheck
from datetime import timedelta
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
# HELPER STRATEGIES FOR GENERATING VALID TEST DATA
# ============================================================================

def valid_username():
    """Generate valid usernames."""
    return st.text(
        min_size=3,
        max_size=50,
        alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            blacklist_characters=' '
        )
    )


def valid_password():
    """Generate valid passwords."""
    return st.text(min_size=8, max_size=100)


def valid_recipe_title():
    """Generate valid recipe titles."""
    return st.text(
        min_size=1,
        max_size=200,
        alphabet=st.characters(min_codepoint=32, max_codepoint=126)
    )


def valid_ingredient_list():
    """Generate valid ingredient lists."""
    return st.lists(
        st.text(
            min_size=1,
            max_size=100,
            alphabet=st.characters(min_codepoint=32, max_codepoint=126)
        ),
        min_size=1,
        max_size=10
    )


def valid_step_list():
    """Generate valid step lists."""
    return st.lists(
        st.text(
            min_size=1,
            max_size=200,
            alphabet=st.characters(min_codepoint=32, max_codepoint=126)
        ),
        min_size=1,
        max_size=10
    )


def valid_tag_list():
    """Generate valid tag lists."""
    return st.one_of(
        st.none(),
        st.lists(
            st.text(
                min_size=1,
                max_size=30,
                alphabet=st.characters(min_codepoint=97, max_codepoint=122)
            ),
            min_size=0,
            max_size=5
        )
    )


def valid_reference_link():
    """Generate valid reference links."""
    return st.one_of(
        st.none(),
        st.text(
            min_size=10,
            max_size=200,
            alphabet=st.characters(min_codepoint=33, max_codepoint=126)
        )
    )


# ============================================================================
# PROPERTY 14: API REQUEST-RESPONSE COMPATIBILITY
# ============================================================================

# Feature: mongodb-migration, Property 14: API Request-Response Compatibility
@given(
    username=valid_username(),
    password=valid_password(),
    title=valid_recipe_title(),
    ingredients=valid_ingredient_list(),
    steps=valid_step_list(),
    tags=valid_tag_list(),
    reference_link=valid_reference_link()
)
@hyp_settings(
    max_examples=100,
    deadline=timedelta(milliseconds=10000),
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
def test_mysql_api_request_response_compatibility_property(
    mysql_client,
    username,
    password,
    title,
    ingredients,
    steps,
    tags,
    reference_link
):
    """
    Property 14: API Request-Response Compatibility
    
    For any valid API request that worked before migration, the MySQL-backed API
    should return the same response structure and status code.
    
    This property verifies:
    1. Request payloads are accepted (Requirement 6.2)
    2. Response structures match expected schemas (Requirement 6.3)
    3. HTTP status codes are correct (Requirement 6.4)
    4. Query parameters work correctly (Requirement 6.5)
    
    **Validates: Requirements 6.2, 6.3, 6.4, 6.5**
    """
    # ========================================================================
    # PART 1: Test Authentication Endpoints
    # ========================================================================
    
    # Register user
    register_response = mysql_client.post(
        "/api/auth/register",
        json={"username": username, "password": password}
    )
    
    # Skip if username already exists (collision in random generation)
    if register_response.status_code == 409:
        return
    
    # Verify registration response
    assert register_response.status_code == 201, \
        f"Registration should return 201, got {register_response.status_code}: {register_response.text}"
    
    register_data = register_response.json()
    assert "id" in register_data, "Registration response should contain 'id'"
    assert "username" in register_data, "Registration response should contain 'username'"
    assert register_data["username"] == username, "Username should match"
    assert "password" not in register_data, "Password should not be in response"
    
    # Login user
    login_response = mysql_client.post(
        "/api/auth/login",
        json={"username": username, "password": password}
    )
    
    assert login_response.status_code == 200, \
        f"Login should return 200, got {login_response.status_code}: {login_response.text}"
    
    login_data = login_response.json()
    assert "access_token" in login_data, "Login response should contain 'access_token'"
    assert "token_type" in login_data, "Login response should contain 'token_type'"
    assert login_data["token_type"] == "bearer", "Token type should be 'bearer'"
    
    token = login_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # ========================================================================
    # PART 2: Test Recipe Creation Endpoint
    # ========================================================================
    
    recipe_payload = {
        "title": title,
        "ingredients": ingredients,
        "steps": steps,
        "tags": tags,
        "reference_link": reference_link
    }
    
    create_response = mysql_client.post(
        "/api/recipes",
        json=recipe_payload,
        headers=headers
    )
    
    assert create_response.status_code == 201, \
        f"Recipe creation should return 201, got {create_response.status_code}: {create_response.text}"
    
    recipe_data = create_response.json()
    
    # Verify required fields in response
    required_fields = ["id", "user_id", "title", "ingredients", "steps", "created_at", "updated_at"]
    for field in required_fields:
        assert field in recipe_data, f"Recipe response should contain '{field}' field"
    
    # Verify field types
    assert isinstance(recipe_data["id"], (int, str)), "id should be int or string"
    assert isinstance(recipe_data["user_id"], (int, str)), "user_id should be int or string"
    assert isinstance(recipe_data["title"], str), "title should be string"
    assert isinstance(recipe_data["ingredients"], list), "ingredients should be list"
    assert isinstance(recipe_data["steps"], list), "steps should be list"
    assert isinstance(recipe_data["created_at"], str), "created_at should be ISO string"
    assert isinstance(recipe_data["updated_at"], str), "updated_at should be ISO string"
    
    # Verify field values match input
    assert recipe_data["title"] == title, "Title should match input"
    assert recipe_data["ingredients"] == ingredients, "Ingredients should match input"
    assert recipe_data["steps"] == steps, "Steps should match input"
    
    # Verify optional fields
    if tags is not None:
        assert "tags" in recipe_data, "Response should contain 'tags' when provided"
        assert recipe_data["tags"] == tags, "Tags should match input"
    
    if reference_link is not None:
        assert "reference_link" in recipe_data, "Response should contain 'reference_link' when provided"
        assert recipe_data["reference_link"] == reference_link, "Reference link should match input"
    
    recipe_id = recipe_data["id"]
    
    # ========================================================================
    # PART 3: Test Recipe Retrieval Endpoint (GET by ID)
    # ========================================================================
    
    get_response = mysql_client.get(
        f"/api/recipes/{recipe_id}",
        headers=headers
    )
    
    assert get_response.status_code == 200, \
        f"GET recipe should return 200, got {get_response.status_code}: {get_response.text}"
    
    get_data = get_response.json()
    
    # Verify same structure as create response
    for field in required_fields:
        assert field in get_data, f"GET response should contain '{field}' field"
    
    # Verify data matches created recipe
    assert get_data["id"] == recipe_id, "Recipe ID should match"
    assert get_data["title"] == title, "Title should match"
    assert get_data["ingredients"] == ingredients, "Ingredients should match"
    assert get_data["steps"] == steps, "Steps should match"
    
    # ========================================================================
    # PART 4: Test Recipe List Endpoint (GET all)
    # ========================================================================
    
    list_response = mysql_client.get(
        "/api/recipes",
        headers=headers
    )
    
    assert list_response.status_code == 200, \
        f"GET recipes list should return 200, got {list_response.status_code}: {list_response.text}"
    
    list_data = list_response.json()
    
    assert isinstance(list_data, list), "List response should be an array"
    assert len(list_data) >= 1, "List should contain at least the created recipe"
    
    # Find our recipe in the list
    our_recipe = next((r for r in list_data if r["id"] == recipe_id), None)
    assert our_recipe is not None, "Created recipe should be in the list"
    
    # Verify structure of list items
    for field in required_fields:
        assert field in our_recipe, f"List item should contain '{field}' field"
    
    # ========================================================================
    # PART 5: Test Recipe Update Endpoint
    # ========================================================================
    
    update_payload = {
        "title": f"Updated {title[:100]}"
    }
    
    update_response = mysql_client.put(
        f"/api/recipes/{recipe_id}",
        json=update_payload,
        headers=headers
    )
    
    assert update_response.status_code == 200, \
        f"Recipe update should return 200, got {update_response.status_code}: {update_response.text}"
    
    update_data = update_response.json()
    
    # Verify response structure
    for field in required_fields:
        assert field in update_data, f"Update response should contain '{field}' field"
    
    # Verify title was updated
    assert update_data["title"] == f"Updated {title[:100]}", "Title should be updated"
    
    # Verify other fields remain unchanged
    assert update_data["ingredients"] == ingredients, "Ingredients should remain unchanged"
    assert update_data["steps"] == steps, "Steps should remain unchanged"
    
    # ========================================================================
    # PART 6: Test Recipe Search with Query Parameters
    # ========================================================================
    
    # Search by title (if title has searchable content)
    if len(title) > 3:
        search_term = title[:5]
        search_response = mysql_client.get(
            f"/api/recipes?search={search_term}",
            headers=headers
        )
        
        assert search_response.status_code == 200, \
            f"Search should return 200, got {search_response.status_code}: {search_response.text}"
        
        search_results = search_response.json()
        assert isinstance(search_results, list), "Search results should be a list"
        
        # Our recipe should be in results if search term matches
        if search_term.lower() in title.lower():
            matching_recipe = next((r for r in search_results if r["id"] == recipe_id), None)
            assert matching_recipe is not None, "Recipe should be in search results"
    
    # ========================================================================
    # PART 7: Test Recipe Deletion Endpoint
    # ========================================================================
    
    delete_response = mysql_client.delete(
        f"/api/recipes/{recipe_id}",
        headers=headers
    )
    
    assert delete_response.status_code == 200, \
        f"Recipe deletion should return 200, got {delete_response.status_code}: {delete_response.text}"
    
    delete_data = delete_response.json()
    assert "message" in delete_data, "Delete response should contain 'message'"
    
    # Verify recipe is deleted
    get_deleted_response = mysql_client.get(
        f"/api/recipes/{recipe_id}",
        headers=headers
    )
    
    assert get_deleted_response.status_code == 404, \
        f"GET deleted recipe should return 404, got {get_deleted_response.status_code}"


# ============================================================================
# PROPERTY 14 (VARIANT): API PAGINATION AND FILTERING
# ============================================================================

# Feature: mongodb-migration, Property 14: API Request-Response Compatibility (Pagination)
@given(
    username=valid_username(),
    password=valid_password(),
    recipe_count=st.integers(min_value=3, max_value=10),
    page_size=st.integers(min_value=1, max_value=5),
    skip_count=st.integers(min_value=0, max_value=3)
)
@hyp_settings(
    max_examples=50,
    deadline=timedelta(milliseconds=15000),
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
def test_mysql_api_pagination_compatibility_property(
    mysql_client,
    username,
    password,
    recipe_count,
    page_size,
    skip_count
):
    """
    Property 14 (Variant): API Pagination Compatibility
    
    For any pagination parameters (skip, limit), the MySQL-backed API should
    return the correct subset of results.
    
    **Validates: Requirements 6.5**
    """
    # Register and login
    register_response = mysql_client.post(
        "/api/auth/register",
        json={"username": username, "password": password}
    )
    
    # Skip if username already exists
    if register_response.status_code == 409:
        return
    
    assert register_response.status_code == 201, "Registration should succeed"
    
    login_response = mysql_client.post(
        "/api/auth/login",
        json={"username": username, "password": password}
    )
    assert login_response.status_code == 200, "Login should succeed"
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create multiple recipes
    created_ids = []
    for i in range(recipe_count):
        recipe_payload = {
            "title": f"Recipe {i:03d}",
            "ingredients": [f"ingredient{i}"],
            "steps": [f"step{i}"]
        }
        
        create_response = mysql_client.post(
            "/api/recipes",
            json=recipe_payload,
            headers=headers
        )
        assert create_response.status_code == 201, "Recipe creation should succeed"
        created_ids.append(create_response.json()["id"])
    
    # Test pagination
    paginated_response = mysql_client.get(
        f"/api/recipes?skip={skip_count}&limit={page_size}",
        headers=headers
    )
    
    assert paginated_response.status_code == 200, \
        f"Paginated request should return 200, got {paginated_response.status_code}"
    
    paginated_results = paginated_response.json()
    
    # Verify pagination constraints
    assert isinstance(paginated_results, list), "Results should be a list"
    
    # Number of results should not exceed page_size
    assert len(paginated_results) <= page_size, \
        f"Results should not exceed page size {page_size}, got {len(paginated_results)}"
    
    # If skip_count < recipe_count, we should get results
    if skip_count < recipe_count:
        expected_count = min(page_size, recipe_count - skip_count)
        assert len(paginated_results) == expected_count, \
            f"Should return {expected_count} results, got {len(paginated_results)}"
    else:
        # If skip_count >= recipe_count, should return empty list
        assert len(paginated_results) == 0, "Should return empty list when skip exceeds total"


# ============================================================================
# PROPERTY 14 (VARIANT): API FILTERING AND SORTING
# ============================================================================

# Feature: mongodb-migration, Property 14: API Request-Response Compatibility (Filtering)
@given(
    username=valid_username(),
    password=valid_password(),
    tag=st.text(min_size=3, max_size=20, alphabet=st.characters(min_codepoint=97, max_codepoint=122)),
    sort_by=st.sampled_from(["title", "date"]),
    sort_order=st.sampled_from(["asc", "desc"])
)
@hyp_settings(
    max_examples=50,
    deadline=timedelta(milliseconds=15000),
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
def test_mysql_api_filtering_sorting_compatibility_property(
    mysql_client,
    username,
    password,
    tag,
    sort_by,
    sort_order
):
    """
    Property 14 (Variant): API Filtering and Sorting Compatibility
    
    For any filter and sort parameters, the MySQL-backed API should return
    correctly filtered and sorted results.
    
    **Validates: Requirements 6.5**
    """
    # Register and login
    register_response = mysql_client.post(
        "/api/auth/register",
        json={"username": username, "password": password}
    )
    
    # Skip if username already exists
    if register_response.status_code == 409:
        return
    
    assert register_response.status_code == 201, "Registration should succeed"
    
    login_response = mysql_client.post(
        "/api/auth/login",
        json={"username": username, "password": password}
    )
    assert login_response.status_code == 200, "Login should succeed"
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create recipes with and without the tag
    recipes_with_tag = []
    recipes_without_tag = []
    
    for i in range(3):
        # Recipe with tag
        recipe_with = {
            "title": f"Recipe With Tag {i:03d}",
            "ingredients": ["ingredient"],
            "steps": ["step"],
            "tags": [tag, "other"]
        }
        response = mysql_client.post("/api/recipes", json=recipe_with, headers=headers)
        assert response.status_code == 201
        recipes_with_tag.append(response.json()["id"])
        
        # Recipe without tag
        recipe_without = {
            "title": f"Recipe Without Tag {i:03d}",
            "ingredients": ["ingredient"],
            "steps": ["step"],
            "tags": ["different"]
        }
        response = mysql_client.post("/api/recipes", json=recipe_without, headers=headers)
        assert response.status_code == 201
        recipes_without_tag.append(response.json()["id"])
    
    # Test filtering by tag
    filter_response = mysql_client.get(
        f"/api/recipes/filter?tags={tag}&sort_by={sort_by}&sort_order={sort_order}",
        headers=headers
    )
    
    assert filter_response.status_code == 200, \
        f"Filter request should return 200, got {filter_response.status_code}"
    
    filter_results = filter_response.json()
    
    # Verify all results have the requested tag
    assert isinstance(filter_results, list), "Results should be a list"
    
    for recipe in filter_results:
        assert "tags" in recipe, "Recipe should have tags field"
        assert tag in recipe["tags"], f"Recipe should have tag '{tag}'"
    
    # Verify sorting
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


if __name__ == "__main__":
    print("Run this test file with: pytest tests/test_mysql_api_compatibility_property.py -v")
    print("Ensure MySQL is running and accessible at: mysql+pymysql://root:password@localhost:3306/recipe_saver_test")
    print("\nThis test implements Property 14: API Request-Response Compatibility")
    print("Validates Requirements: 6.2, 6.3, 6.4, 6.5")
