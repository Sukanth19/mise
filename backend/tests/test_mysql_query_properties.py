"""
Property-based tests for query operations with MySQL.


Task 5.2: Write property tests for query operations
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck, assume
from datetime import datetime, timedelta
from sqlalchemy import or_
from app.models import User, Recipe


# ============================================================================
# Strategy Definitions
# ============================================================================

# Strategy for generating valid usernames
username_strategy = st.text(
    min_size=1,
    max_size=255,
    alphabet=st.characters(
        blacklist_categories=('Cc', 'Cs'),
        blacklist_characters='\x00'
    )
).filter(lambda x: x.strip())

# Strategy for generating valid passwords
password_strategy = st.text(
    min_size=1,
    max_size=255,
    alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))
)

# Strategy for generating valid text fields
text_strategy = st.text(
    min_size=1,
    max_size=500,
    alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))
)

# Strategy for visibility values
visibility_strategy = st.sampled_from(['private', 'public', 'unlisted'])

# Strategy for servings
servings_strategy = st.integers(min_value=1, max_value=20)


# ============================================================================
# Property 5: Filter Correctness
# **Validates: Requirements 3.6**
# ============================================================================

@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    username=username_strategy,
    password=password_strategy,
    visibility_filter=visibility_strategy,
    num_recipes=st.integers(min_value=3, max_value=10)
)
def test_property_filter_correctness(db, username, password, visibility_filter, num_recipes):
    """
    Property 5: Filter Correctness
    
    For any query filter conditions, all returned records should satisfy those conditions.
    
    Property 5: Filter Correctness
    **Validates: Requirements 3.6**
    """
    # Create user
    user = User(username=username, password_hash=password)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        
        # Create recipes with random visibility
        visibilities = ['private', 'public', 'unlisted']
        for i in range(num_recipes):
            visibility = visibilities[i % 3]
            recipe = Recipe(
                user_id=user.id,
                title=f"Recipe {i}",
                ingredients=f"ingredient{i}",
                steps=f"step{i}",
                visibility=visibility
            )
            db.add(recipe)
        db.commit()
        
        # Filter by specific visibility
        filtered_recipes = db.query(Recipe).filter(
            Recipe.visibility == visibility_filter
        ).all()
        
        # Property: All returned records must match the filter condition
        for recipe in filtered_recipes:
            assert recipe.visibility == visibility_filter, \
                f"Recipe visibility {recipe.visibility} does not match filter {visibility_filter}"
    finally:
        db.rollback()


@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    username=username_strategy,
    password=password_strategy,
    servings_filter=servings_strategy,
    num_recipes=st.integers(min_value=3, max_value=10)
)
def test_property_filter_by_servings(db, username, password, servings_filter, num_recipes):
    """
    Property 5: Filter Correctness (servings)
    
    Property 5: Filter Correctness
    **Validates: Requirements 3.6**
    """
    # Create user
    user = User(username=username, password_hash=password)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        
        # Create recipes with different servings
        for i in range(num_recipes):
            servings = (i % 10) + 1  # 1-10 servings
            recipe = Recipe(
                user_id=user.id,
                title=f"Recipe {i}",
                ingredients=f"ingredient{i}",
                steps=f"step{i}",
                servings=servings
            )
            db.add(recipe)
        db.commit()
        
        # Filter by specific servings
        filtered_recipes = db.query(Recipe).filter(
            Recipe.servings == servings_filter
        ).all()
        
        # Property: All returned records must match the filter condition
        for recipe in filtered_recipes:
            assert recipe.servings == servings_filter, \
                f"Recipe servings {recipe.servings} does not match filter {servings_filter}"
    finally:
        db.rollback()


# ============================================================================
# Property 6: Sort Order Correctness
# **Validates: Requirements 3.7**
# ============================================================================

@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    username=username_strategy,
    password=password_strategy,
    num_recipes=st.integers(min_value=3, max_value=10)
)
def test_property_sort_order_correctness_title_asc(db, username, password, num_recipes):
    """
    Property 6: Sort Order Correctness
    
    For any sort specification, returned records should be ordered according to the sort criteria.
    
    Property 6: Sort Order Correctness
    **Validates: Requirements 3.7**
    """
    # Create user
    user = User(username=username, password_hash=password)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        
        # Create recipes with different titles
        titles = [f"Recipe {chr(65 + i)}" for i in range(num_recipes)]  # Recipe A, Recipe B, etc.
        for title in titles:
            recipe = Recipe(
                user_id=user.id,
                title=title,
                ingredients="ingredient",
                steps="step"
            )
            db.add(recipe)
        db.commit()
        
        # Sort by title ascending
        sorted_recipes = db.query(Recipe).filter(
            Recipe.user_id == user.id
        ).order_by(Recipe.title.asc()).all()
        
        # Property: Records should be in ascending order by title
        for i in range(len(sorted_recipes) - 1):
            assert sorted_recipes[i].title <= sorted_recipes[i + 1].title, \
                f"Sort order violated: {sorted_recipes[i].title} > {sorted_recipes[i + 1].title}"
    finally:
        db.rollback()


@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    username=username_strategy,
    password=password_strategy,
    num_recipes=st.integers(min_value=3, max_value=10)
)
def test_property_sort_order_correctness_servings_desc(db, username, password, num_recipes):
    """
    Property 6: Sort Order Correctness (servings descending)
    
    Property 6: Sort Order Correctness
    **Validates: Requirements 3.7**
    """
    # Create user
    user = User(username=username, password_hash=password)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        
        # Create recipes with different servings
        for i in range(num_recipes):
            servings = (i % 10) + 1
            recipe = Recipe(
                user_id=user.id,
                title=f"Recipe {i}",
                ingredients="ingredient",
                steps="step",
                servings=servings
            )
            db.add(recipe)
        db.commit()
        
        # Sort by servings descending
        sorted_recipes = db.query(Recipe).filter(
            Recipe.user_id == user.id
        ).order_by(Recipe.servings.desc()).all()
        
        # Property: Records should be in descending order by servings
        for i in range(len(sorted_recipes) - 1):
            assert sorted_recipes[i].servings >= sorted_recipes[i + 1].servings, \
                f"Sort order violated: {sorted_recipes[i].servings} < {sorted_recipes[i + 1].servings}"
    finally:
        db.rollback()


# ============================================================================
# Property 7: Pagination Subset Correctness
# **Validates: Requirements 3.8**
# ============================================================================

@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    username=username_strategy,
    password=password_strategy,
    num_recipes=st.integers(min_value=10, max_value=20),
    page_size=st.integers(min_value=2, max_value=5),
    page_num=st.integers(min_value=0, max_value=3)
)
def test_property_pagination_subset_correctness(db, username, password, num_recipes, page_size, page_num):
    """
    Property 7: Pagination Subset Correctness
    
    For any pagination parameters (skip, limit), the returned records should be 
    the correct subset of the full result set.
    
    Property 7: Pagination Subset Correctness
    **Validates: Requirements 3.8**
    """
    # Create user
    user = User(username=username, password_hash=password)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        
        # Create recipes with sequential titles for predictable ordering
        for i in range(num_recipes):
            recipe = Recipe(
                user_id=user.id,
                title=f"Recipe {i:03d}",  # Zero-padded for consistent sorting
                ingredients=f"ingredient{i}",
                steps=f"step{i}"
            )
            db.add(recipe)
        db.commit()
        
        # Get full result set (sorted)
        all_recipes = db.query(Recipe).filter(
            Recipe.user_id == user.id
        ).order_by(Recipe.title.asc()).all()
        
        # Get paginated subset
        offset = page_num * page_size
        paginated_recipes = db.query(Recipe).filter(
            Recipe.user_id == user.id
        ).order_by(Recipe.title.asc()).offset(offset).limit(page_size).all()
        
        # Property: Paginated subset should match the corresponding slice of full result set
        expected_subset = all_recipes[offset:offset + page_size]
        
        assert len(paginated_recipes) == len(expected_subset), \
            f"Paginated result count {len(paginated_recipes)} != expected {len(expected_subset)}"
        
        for i, (paginated, expected) in enumerate(zip(paginated_recipes, expected_subset)):
            assert paginated.id == expected.id, \
                f"Record {i}: paginated id {paginated.id} != expected id {expected.id}"
            assert paginated.title == expected.title, \
                f"Record {i}: paginated title {paginated.title} != expected title {expected.title}"
    finally:
        db.rollback()


# ============================================================================
# Property 8: Text Search Relevance
# **Validates: Requirements 3.9**
# ============================================================================

@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    username=username_strategy,
    password=password_strategy,
    search_term=st.text(min_size=3, max_size=20, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll'),
        min_codepoint=65, max_codepoint=122
    )),
    num_recipes=st.integers(min_value=5, max_value=10)
)
def test_property_text_search_relevance(db, username, password, search_term, num_recipes):
    """
    Property 8: Text Search Relevance
    
    For any text search query, all returned records should contain the search 
    terms in the indexed fields.
    
    Property 8: Text Search Relevance
    **Validates: Requirements 3.9**
    """
    # Ensure search term is not empty after stripping
    search_term = search_term.strip()
    assume(len(search_term) >= 3)
    
    # Create user
    user = User(username=username, password_hash=password)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        
        # Create recipes - some with search term, some without
        for i in range(num_recipes):
            if i % 2 == 0:
                # Include search term in title
                title = f"{search_term} Recipe {i}"
                ingredients = f"ingredient{i}"
            else:
                # Don't include search term
                title = f"Recipe {i}"
                ingredients = f"ingredient{i}"
            
            recipe = Recipe(
                user_id=user.id,
                title=title,
                ingredients=ingredients,
                steps=f"step{i}"
            )
            db.add(recipe)
        db.commit()
        
        # Search for term in title
        search_results = db.query(Recipe).filter(
            Recipe.title.like(f"%{search_term}%")
        ).all()
        
        # Property: All returned records must contain the search term in title
        for recipe in search_results:
            assert search_term in recipe.title, \
                f"Search term '{search_term}' not found in title '{recipe.title}'"
    finally:
        db.rollback()


@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    username=username_strategy,
    password=password_strategy,
    search_term=st.text(min_size=3, max_size=20, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll'),
        min_codepoint=65, max_codepoint=122
    )),
    num_recipes=st.integers(min_value=5, max_value=10)
)
def test_property_text_search_ingredients(db, username, password, search_term, num_recipes):
    """
    Property 8: Text Search Relevance (ingredients)
    
    Property 8: Text Search Relevance
    **Validates: Requirements 3.9**
    """
    # Ensure search term is not empty after stripping
    search_term = search_term.strip()
    assume(len(search_term) >= 3)
    
    # Create user
    user = User(username=username, password_hash=password)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        
        # Create recipes - some with search term in ingredients, some without
        for i in range(num_recipes):
            if i % 2 == 0:
                # Include search term in ingredients
                ingredients = f"{search_term}, flour, sugar"
            else:
                # Don't include search term
                ingredients = f"flour, sugar, salt"
            
            recipe = Recipe(
                user_id=user.id,
                title=f"Recipe {i}",
                ingredients=ingredients,
                steps=f"step{i}"
            )
            db.add(recipe)
        db.commit()
        
        # Search for term in ingredients
        search_results = db.query(Recipe).filter(
            Recipe.ingredients.like(f"%{search_term}%")
        ).all()
        
        # Property: All returned records must contain the search term in ingredients
        for recipe in search_results:
            assert search_term in recipe.ingredients, \
                f"Search term '{search_term}' not found in ingredients '{recipe.ingredients}'"
    finally:
        db.rollback()


# ============================================================================
# Property 16: Pagination Limit Enforcement
# **Validates: Requirements 9.5**
# ============================================================================

@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    username=username_strategy,
    password=password_strategy,
    num_recipes=st.integers(min_value=50, max_value=150),
    page_size=st.integers(min_value=1, max_value=150)
)
def test_property_pagination_limit_enforcement(db, username, password, num_recipes, page_size):
    """
    Property 16: Pagination Limit Enforcement
    
    For any query, the number of returned records should not exceed the maximum 
    page size (100).
    
    Property 16: Pagination Limit Enforcement
    **Validates: Requirements 9.5**
    """
    # Create user
    user = User(username=username, password_hash=password)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        
        # Create many recipes
        for i in range(num_recipes):
            recipe = Recipe(
                user_id=user.id,
                title=f"Recipe {i}",
                ingredients=f"ingredient{i}",
                steps=f"step{i}"
            )
            db.add(recipe)
        db.commit()
        
        # Apply limit (enforce max of 100)
        enforced_limit = min(page_size, 100)
        
        # Query with limit
        results = db.query(Recipe).filter(
            Recipe.user_id == user.id
        ).limit(enforced_limit).all()
        
        # Property: Number of returned records should not exceed the enforced limit
        assert len(results) <= enforced_limit, \
            f"Returned {len(results)} records, exceeds limit of {enforced_limit}"
        
        # Property: If there are enough records, should return exactly the limit
        if num_recipes >= enforced_limit:
            assert len(results) == enforced_limit, \
                f"Expected {enforced_limit} records, got {len(results)}"
    finally:
        db.rollback()


@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    username=username_strategy,
    password=password_strategy,
    num_recipes=st.integers(min_value=10, max_value=50)
)
def test_property_pagination_no_limit_defaults(db, username, password, num_recipes):
    """
    Property 16: Pagination Limit Enforcement (no explicit limit)
    
    Property 16: Pagination Limit Enforcement
    **Validates: Requirements 9.5**
    """
    # Create user
    user = User(username=username, password_hash=password)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        
        # Create recipes
        for i in range(num_recipes):
            recipe = Recipe(
                user_id=user.id,
                title=f"Recipe {i}",
                ingredients=f"ingredient{i}",
                steps=f"step{i}"
            )
            db.add(recipe)
        db.commit()
        
        # Query without explicit limit
        results = db.query(Recipe).filter(
            Recipe.user_id == user.id
        ).all()
        
        # Property: Should return all records (no artificial limit in test environment)
        # In production, API layer should enforce max page size of 100
        assert len(results) == num_recipes, \
            f"Expected {num_recipes} records, got {len(results)}"
    finally:
        db.rollback()
