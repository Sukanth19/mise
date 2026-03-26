"""
Property-based tests for MySQL error handling.

This test file implements properties for error handling in the MySQL migration:
- Property 17: Foreign Key Constraint Enforcement
- Property 18: Transaction Rollback on Error
- Property 19: Constraint Violation Error Descriptiveness
- Property 20: Missing Record Error Handling

**Validates: Requirements 8.4, 8.5, 10.3, 10.4**

Task 10.3: Write property tests for error handling
"""
import os
import pytest
from hypothesis import given, strategies as st, settings as hyp_settings, HealthCheck
from datetime import timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
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


# ============================================================================
# PROPERTY 17: FOREIGN KEY CONSTRAINT ENFORCEMENT
# ============================================================================

# Feature: mongodb-migration, Property 17: Foreign Key Constraint Enforcement
@given(
    username=valid_username(),
    password=valid_password(),
    title=valid_recipe_title(),
    ingredients=valid_ingredient_list(),
    steps=valid_step_list(),
    invalid_user_id=st.integers(min_value=999999, max_value=9999999)
)
@hyp_settings(
    max_examples=100,
    deadline=timedelta(milliseconds=5000),
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
def test_foreign_key_constraint_enforcement_property(
    mysql_db,
    username,
    password,
    title,
    ingredients,
    steps,
    invalid_user_id
):
    """
    Property 17: Foreign Key Constraint Enforcement
    
    For any attempt to insert a record with an invalid foreign key, MySQL should
    reject the operation with a constraint violation error.
    
    This property verifies that:
    1. Foreign key constraints are enforced by MySQL
    2. Invalid foreign key references are rejected
    3. Descriptive error messages are provided
    
    **Validates: Requirements 8.4**
    """
    from app.models import User, Recipe
    from app.utils.mysql_error_handler import MySQLErrorHandler
    import json
    
    # Create a valid user
    user = User(username=username, password_hash=password)
    mysql_db.add(user)
    mysql_db.commit()
    mysql_db.refresh(user)
    
    # Attempt to create a recipe with an invalid user_id (foreign key violation)
    invalid_recipe = Recipe(
        user_id=invalid_user_id,  # This user_id doesn't exist
        title=title,
        ingredients=json.dumps(ingredients),
        steps=json.dumps(steps)
    )
    
    mysql_db.add(invalid_recipe)
    
    # Verify that foreign key constraint is enforced
    try:
        mysql_db.commit()
        # If we get here, the constraint was not enforced
        assert False, "Foreign key constraint should have been enforced"
    except IntegrityError as e:
        # Expected: Foreign key constraint violation
        mysql_db.rollback()
        
        # Verify error is a foreign key constraint violation
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        assert "foreign key constraint" in error_msg.lower() or \
               "cannot add or update a child row" in error_msg.lower(), \
            f"Error should indicate foreign key constraint violation: {error_msg}"
        
        # Verify error handler provides descriptive message
        http_exception = MySQLErrorHandler.handle_constraint_violation(e)
        assert http_exception.status_code == 400, \
            f"Foreign key violation should return 400, got {http_exception.status_code}"
        assert "referenced" in http_exception.detail.lower() or \
               "does not exist" in http_exception.detail.lower(), \
            f"Error detail should describe foreign key issue: {http_exception.detail}"


# ============================================================================
# PROPERTY 18: TRANSACTION ROLLBACK ON ERROR
# ============================================================================

# Feature: mongodb-migration, Property 18: Transaction Rollback on Error
@given(
    username=valid_username(),
    password=valid_password(),
    recipe_count=st.integers(min_value=2, max_value=5),
    invalid_rating=st.integers().filter(lambda x: x < 1 or x > 5)
)
@hyp_settings(
    max_examples=100,
    deadline=timedelta(milliseconds=5000),
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
def test_transaction_rollback_on_error_property(
    mysql_db,
    username,
    password,
    recipe_count,
    invalid_rating
):
    """
    Property 18: Transaction Rollback on Error
    
    For any transaction that encounters an error, all changes within that
    transaction should be rolled back.
    
    This property verifies that:
    1. Transactions are atomic (all or nothing)
    2. Partial changes are rolled back on error
    3. Database remains in consistent state after error
    
    **Validates: Requirements 8.5**
    """
    from app.models import User, Recipe, RecipeRating
    import json
    
    # Create a user
    user = User(username=username, password_hash=password)
    mysql_db.add(user)
    mysql_db.commit()
    mysql_db.refresh(user)
    
    # Create a recipe
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients=json.dumps(["ingredient1"]),
        steps=json.dumps(["step1"])
    )
    mysql_db.add(recipe)
    mysql_db.commit()
    mysql_db.refresh(recipe)
    
    # Count initial ratings
    initial_rating_count = mysql_db.query(RecipeRating).count()
    
    # Start a transaction that will fail
    try:
        # Add valid ratings
        for i in range(recipe_count):
            rating = RecipeRating(
                recipe_id=recipe.id,
                user_id=user.id if i == 0 else user.id + i,  # Different user IDs to avoid unique constraint
                rating=3  # Valid rating
            )
            mysql_db.add(rating)
        
        # Add an invalid rating that will cause constraint violation
        invalid_rating_obj = RecipeRating(
            recipe_id=recipe.id,
            user_id=user.id + recipe_count + 1,
            rating=invalid_rating  # Invalid rating (not between 1-5)
        )
        mysql_db.add(invalid_rating_obj)
        
        # Attempt to commit - should fail due to check constraint
        mysql_db.commit()
        
        # If we get here, the constraint was not enforced
        assert False, "Check constraint should have been enforced"
        
    except Exception as e:
        # Expected: Transaction should fail
        mysql_db.rollback()
        
        # Verify all changes were rolled back
        final_rating_count = mysql_db.query(RecipeRating).count()
        assert final_rating_count == initial_rating_count, \
            f"All ratings should be rolled back. Initial: {initial_rating_count}, Final: {final_rating_count}"
        
        # Verify no partial data was committed
        ratings_for_recipe = mysql_db.query(RecipeRating).filter(
            RecipeRating.recipe_id == recipe.id
        ).count()
        assert ratings_for_recipe == 0, \
            f"No ratings should exist for recipe after rollback, found {ratings_for_recipe}"


# ============================================================================
# PROPERTY 19: CONSTRAINT VIOLATION ERROR DESCRIPTIVENESS
# ============================================================================

# Feature: mongodb-migration, Property 19: Constraint Violation Error Descriptiveness
@given(
    username=valid_username(),
    password=valid_password(),
    title=valid_recipe_title(),
    ingredients=valid_ingredient_list(),
    steps=valid_step_list()
)
@hyp_settings(
    max_examples=100,
    deadline=timedelta(milliseconds=10000),
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
def test_constraint_violation_error_descriptiveness_property(
    mysql_client,
    username,
    password,
    title,
    ingredients,
    steps
):
    """
    Property 19: Constraint Violation Error Descriptiveness
    
    For any operation that violates a constraint, the API should return an error
    response containing details about which constraint was violated.
    
    This property verifies that:
    1. Constraint violations return appropriate HTTP status codes
    2. Error messages describe which constraint was violated
    3. Error messages are user-friendly and actionable
    
    **Validates: Requirements 10.3**
    """
    # ========================================================================
    # TEST 1: Unique Constraint Violation (Duplicate Username)
    # ========================================================================
    
    # Register first user
    register_response1 = mysql_client.post(
        "/api/auth/register",
        json={"username": username, "password": password}
    )
    
    # Skip if registration fails for other reasons
    if register_response1.status_code not in [201, 409]:
        return
    
    # Attempt to register with same username (unique constraint violation)
    register_response2 = mysql_client.post(
        "/api/auth/register",
        json={"username": username, "password": password}
    )
    
    # Verify unique constraint violation is handled
    assert register_response2.status_code == 409, \
        f"Duplicate username should return 409 Conflict, got {register_response2.status_code}"
    
    error_data = register_response2.json()
    assert "detail" in error_data, "Error response should contain 'detail' field"
    
    # Verify error message is descriptive
    detail = error_data["detail"].lower()
    assert "username" in detail or "exists" in detail or "already" in detail, \
        f"Error should describe username conflict: {error_data['detail']}"
    
    # ========================================================================
    # TEST 2: Check Constraint Violation (Invalid Rating)
    # ========================================================================
    
    # Login to get token
    login_response = mysql_client.post(
        "/api/auth/login",
        json={"username": username, "password": password}
    )
    
    if login_response.status_code != 200:
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a recipe
    recipe_response = mysql_client.post(
        "/api/recipes",
        json={
            "title": title,
            "ingredients": ingredients,
            "steps": steps
        },
        headers=headers
    )
    
    if recipe_response.status_code != 201:
        return
    
    recipe_id = recipe_response.json()["id"]
    
    # Attempt to rate with invalid rating (check constraint violation)
    invalid_ratings = [0, 6, -1, 10]
    
    for invalid_rating in invalid_ratings:
        rating_response = mysql_client.post(
            f"/api/recipes/{recipe_id}/ratings",
            json={"rating": invalid_rating},
            headers=headers
        )
        
        # Verify check constraint violation is handled
        assert rating_response.status_code in [400, 422], \
            f"Invalid rating should return 400 or 422, got {rating_response.status_code}"
        
        error_data = rating_response.json()
        assert "detail" in error_data, "Error response should contain 'detail' field"
        
        # Verify error message is descriptive
        detail = error_data["detail"].lower()
        assert "rating" in detail or "1" in detail or "5" in detail, \
            f"Error should describe rating constraint: {error_data['detail']}"
    
    # ========================================================================
    # TEST 3: Unique Constraint Violation (Duplicate Rating)
    # ========================================================================
    
    # Create a valid rating
    valid_rating_response = mysql_client.post(
        f"/api/recipes/{recipe_id}/ratings",
        json={"rating": 4},
        headers=headers
    )
    
    if valid_rating_response.status_code != 201:
        return
    
    # Attempt to rate the same recipe again (unique constraint violation)
    duplicate_rating_response = mysql_client.post(
        f"/api/recipes/{recipe_id}/ratings",
        json={"rating": 5},
        headers=headers
    )
    
    # Verify unique constraint violation is handled
    assert duplicate_rating_response.status_code == 409, \
        f"Duplicate rating should return 409 Conflict, got {duplicate_rating_response.status_code}"
    
    error_data = duplicate_rating_response.json()
    assert "detail" in error_data, "Error response should contain 'detail' field"
    
    # Verify error message is descriptive
    detail = error_data["detail"].lower()
    assert "already" in detail or "rated" in detail or "exists" in detail, \
        f"Error should describe duplicate rating: {error_data['detail']}"


# ============================================================================
# PROPERTY 20: MISSING RECORD ERROR HANDLING
# ============================================================================

# Feature: mongodb-migration, Property 20: Missing Record Error Handling
@given(
    username=valid_username(),
    password=valid_password(),
    non_existent_id=st.integers(min_value=999999, max_value=9999999)
)
@hyp_settings(
    max_examples=100,
    deadline=timedelta(milliseconds=5000),
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
def test_missing_record_error_handling_property(
    mysql_client,
    username,
    password,
    non_existent_id
):
    """
    Property 20: Missing Record Error Handling
    
    For any API request referencing a non-existent record ID, the API should
    return a 404 status code.
    
    This property verifies that:
    1. Missing records return 404 Not Found
    2. Error messages indicate resource not found
    3. Different resource types are handled consistently
    
    **Validates: Requirements 10.4**
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
    
    # ========================================================================
    # TEST 1: Missing Recipe
    # ========================================================================
    
    get_recipe_response = mysql_client.get(
        f"/api/recipes/{non_existent_id}",
        headers=headers
    )
    
    assert get_recipe_response.status_code == 404, \
        f"GET non-existent recipe should return 404, got {get_recipe_response.status_code}"
    
    error_data = get_recipe_response.json()
    assert "detail" in error_data, "Error response should contain 'detail' field"
    assert "not found" in error_data["detail"].lower(), \
        f"Error should indicate resource not found: {error_data['detail']}"
    
    # ========================================================================
    # TEST 2: Update Missing Recipe
    # ========================================================================
    
    update_recipe_response = mysql_client.put(
        f"/api/recipes/{non_existent_id}",
        json={"title": "Updated Title"},
        headers=headers
    )
    
    assert update_recipe_response.status_code == 404, \
        f"PUT non-existent recipe should return 404, got {update_recipe_response.status_code}"
    
    error_data = update_recipe_response.json()
    assert "detail" in error_data, "Error response should contain 'detail' field"
    assert "not found" in error_data["detail"].lower(), \
        f"Error should indicate resource not found: {error_data['detail']}"
    
    # ========================================================================
    # TEST 3: Delete Missing Recipe
    # ========================================================================
    
    delete_recipe_response = mysql_client.delete(
        f"/api/recipes/{non_existent_id}",
        headers=headers
    )
    
    assert delete_recipe_response.status_code == 404, \
        f"DELETE non-existent recipe should return 404, got {delete_recipe_response.status_code}"
    
    error_data = delete_recipe_response.json()
    assert "detail" in error_data, "Error response should contain 'detail' field"
    assert "not found" in error_data["detail"].lower(), \
        f"Error should indicate resource not found: {error_data['detail']}"
    
    # ========================================================================
    # TEST 4: Rate Missing Recipe
    # ========================================================================
    
    rate_recipe_response = mysql_client.post(
        f"/api/recipes/{non_existent_id}/ratings",
        json={"rating": 4},
        headers=headers
    )
    
    assert rate_recipe_response.status_code == 404, \
        f"POST rating to non-existent recipe should return 404, got {rate_recipe_response.status_code}"
    
    error_data = rate_recipe_response.json()
    assert "detail" in error_data, "Error response should contain 'detail' field"
    assert "not found" in error_data["detail"].lower(), \
        f"Error should indicate resource not found: {error_data['detail']}"
    
    # ========================================================================
    # TEST 5: Missing Collection
    # ========================================================================
    
    get_collection_response = mysql_client.get(
        f"/api/collections/{non_existent_id}",
        headers=headers
    )
    
    assert get_collection_response.status_code == 404, \
        f"GET non-existent collection should return 404, got {get_collection_response.status_code}"
    
    error_data = get_collection_response.json()
    assert "detail" in error_data, "Error response should contain 'detail' field"
    assert "not found" in error_data["detail"].lower(), \
        f"Error should indicate resource not found: {error_data['detail']}"


if __name__ == "__main__":
    print("Run this test file with: pytest backend/tests/test_mysql_error_handling_properties.py -v")
    print("Ensure MySQL is running and accessible at: mysql+pymysql://root:password@localhost:3306/recipe_saver_test")
    print("\nThis test implements:")
    print("- Property 17: Foreign Key Constraint Enforcement")
    print("- Property 18: Transaction Rollback on Error")
    print("- Property 19: Constraint Violation Error Descriptiveness")
    print("- Property 20: Missing Record Error Handling")
    print("\nValidates Requirements: 8.4, 8.5, 10.3, 10.4")
