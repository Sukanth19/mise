"""
Unit tests for query operations with MySQL.

Task 5.1: Test filtering and sorting
"""

import pytest
from datetime import datetime, timedelta
from app.models import User, Recipe


# ============================================================================
# Test WHERE clauses with various conditions
# **Validates: Requirements 3.6**
# ============================================================================

def test_filter_by_user_id(db):
    """Test WHERE clause filtering by user_id. Validates: Requirements 3.6"""
    # Create two users
    user1 = User(username="user1", password_hash="hash1")
    user2 = User(username="user2", password_hash="hash2")
    db.add_all([user1, user2])
    db.commit()
    db.refresh(user1)
    db.refresh(user2)
    
    # Create recipes for each user
    recipe1 = Recipe(
        user_id=user1.id,
        title="User1 Recipe 1",
        ingredients="ingredient1",
        steps="step1"
    )
    recipe2 = Recipe(
        user_id=user1.id,
        title="User1 Recipe 2",
        ingredients="ingredient2",
        steps="step2"
    )
    recipe3 = Recipe(
        user_id=user2.id,
        title="User2 Recipe 1",
        ingredients="ingredient3",
        steps="step3"
    )
    db.add_all([recipe1, recipe2, recipe3])
    db.commit()
    
    # Filter by user1
    user1_recipes = db.query(Recipe).filter(Recipe.user_id == user1.id).all()
    
    assert len(user1_recipes) == 2
    assert all(r.user_id == user1.id for r in user1_recipes)
    assert {r.title for r in user1_recipes} == {"User1 Recipe 1", "User1 Recipe 2"}


def test_filter_by_visibility(db):
    """Test WHERE clause filtering by visibility. Validates: Requirements 3.6"""
    # Create user
    user = User(username="testuser", password_hash="hash")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create recipes with different visibility
    recipe1 = Recipe(
        user_id=user.id,
        title="Public Recipe",
        ingredients="ingredient1",
        steps="step1",
        visibility="public"
    )
    recipe2 = Recipe(
        user_id=user.id,
        title="Private Recipe",
        ingredients="ingredient2",
        steps="step2",
        visibility="private"
    )
    recipe3 = Recipe(
        user_id=user.id,
        title="Unlisted Recipe",
        ingredients="ingredient3",
        steps="step3",
        visibility="unlisted"
    )
    db.add_all([recipe1, recipe2, recipe3])
    db.commit()
    
    # Filter by public visibility
    public_recipes = db.query(Recipe).filter(Recipe.visibility == "public").all()
    
    assert len(public_recipes) == 1
    assert public_recipes[0].title == "Public Recipe"
    assert public_recipes[0].visibility == "public"


def test_filter_by_created_at_range(db):
    """Test WHERE clause filtering by created_at date range. Validates: Requirements 3.6"""
    # Create user
    user = User(username="testuser", password_hash="hash")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create recipes with different timestamps
    now = datetime.now()
    recipe1 = Recipe(
        user_id=user.id,
        title="Old Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe1)
    db.commit()
    db.refresh(recipe1)
    
    # Manually set created_at to simulate older recipe
    old_time = now - timedelta(days=10)
    db.execute(
        Recipe.__table__.update().where(Recipe.id == recipe1.id).values(created_at=old_time)
    )
    db.commit()
    
    recipe2 = Recipe(
        user_id=user.id,
        title="Recent Recipe",
        ingredients="ingredient2",
        steps="step2"
    )
    db.add(recipe2)
    db.commit()
    
    # Filter by recent recipes (last 7 days)
    cutoff_date = now - timedelta(days=7)
    recent_recipes = db.query(Recipe).filter(Recipe.created_at >= cutoff_date).all()
    
    assert len(recent_recipes) == 1
    assert recent_recipes[0].title == "Recent Recipe"


def test_filter_by_multiple_conditions(db):
    """Test WHERE clause with multiple AND conditions. Validates: Requirements 3.6"""
    # Create user
    user = User(username="testuser", password_hash="hash")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create recipes
    recipe1 = Recipe(
        user_id=user.id,
        title="Public Recipe 1",
        ingredients="ingredient1",
        steps="step1",
        visibility="public",
        servings=4
    )
    recipe2 = Recipe(
        user_id=user.id,
        title="Public Recipe 2",
        ingredients="ingredient2",
        steps="step2",
        visibility="public",
        servings=2
    )
    recipe3 = Recipe(
        user_id=user.id,
        title="Private Recipe",
        ingredients="ingredient3",
        steps="step3",
        visibility="private",
        servings=4
    )
    db.add_all([recipe1, recipe2, recipe3])
    db.commit()
    
    # Filter by visibility=public AND servings=4
    filtered_recipes = db.query(Recipe).filter(
        Recipe.visibility == "public",
        Recipe.servings == 4
    ).all()
    
    assert len(filtered_recipes) == 1
    assert filtered_recipes[0].title == "Public Recipe 1"


def test_filter_by_is_favorite(db):
    """Test WHERE clause filtering by is_favorite boolean. Validates: Requirements 3.6"""
    # Create user
    user = User(username="testuser", password_hash="hash")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create recipes
    recipe1 = Recipe(
        user_id=user.id,
        title="Favorite Recipe",
        ingredients="ingredient1",
        steps="step1",
        is_favorite=True
    )
    recipe2 = Recipe(
        user_id=user.id,
        title="Normal Recipe",
        ingredients="ingredient2",
        steps="step2",
        is_favorite=False
    )
    db.add_all([recipe1, recipe2])
    db.commit()
    
    # Filter by favorites
    favorite_recipes = db.query(Recipe).filter(Recipe.is_favorite == True).all()
    
    assert len(favorite_recipes) == 1
    assert favorite_recipes[0].title == "Favorite Recipe"


# ============================================================================
# Test ORDER BY with different columns
# **Validates: Requirements 3.7**
# ============================================================================

def test_order_by_title_ascending(db):
    """Test ORDER BY title ascending. Validates: Requirements 3.7"""
    # Create user
    user = User(username="testuser", password_hash="hash")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create recipes with different titles
    recipe1 = Recipe(
        user_id=user.id,
        title="Zebra Cake",
        ingredients="ingredient1",
        steps="step1"
    )
    recipe2 = Recipe(
        user_id=user.id,
        title="Apple Pie",
        ingredients="ingredient2",
        steps="step2"
    )
    recipe3 = Recipe(
        user_id=user.id,
        title="Mango Smoothie",
        ingredients="ingredient3",
        steps="step3"
    )
    db.add_all([recipe1, recipe2, recipe3])
    db.commit()
    
    # Order by title ascending
    sorted_recipes = db.query(Recipe).order_by(Recipe.title.asc()).all()
    
    assert len(sorted_recipes) == 3
    assert sorted_recipes[0].title == "Apple Pie"
    assert sorted_recipes[1].title == "Mango Smoothie"
    assert sorted_recipes[2].title == "Zebra Cake"


def test_order_by_title_descending(db):
    """Test ORDER BY title descending. Validates: Requirements 3.7"""
    # Create user
    user = User(username="testuser", password_hash="hash")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create recipes
    recipe1 = Recipe(
        user_id=user.id,
        title="Apple Pie",
        ingredients="ingredient1",
        steps="step1"
    )
    recipe2 = Recipe(
        user_id=user.id,
        title="Zebra Cake",
        ingredients="ingredient2",
        steps="step2"
    )
    db.add_all([recipe1, recipe2])
    db.commit()
    
    # Order by title descending
    sorted_recipes = db.query(Recipe).order_by(Recipe.title.desc()).all()
    
    assert len(sorted_recipes) == 2
    assert sorted_recipes[0].title == "Zebra Cake"
    assert sorted_recipes[1].title == "Apple Pie"


def test_order_by_created_at_descending(db):
    """Test ORDER BY created_at descending (most recent first). Validates: Requirements 3.7"""
    # Create user
    user = User(username="testuser", password_hash="hash")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create recipes with explicit timestamps to ensure ordering
    now = datetime.now()
    
    recipe1 = Recipe(
        user_id=user.id,
        title="First Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe1)
    db.commit()
    db.refresh(recipe1)
    
    # Set explicit timestamp for first recipe (oldest)
    old_time = now - timedelta(seconds=10)
    db.execute(
        Recipe.__table__.update().where(Recipe.id == recipe1.id).values(created_at=old_time)
    )
    db.commit()
    
    recipe2 = Recipe(
        user_id=user.id,
        title="Second Recipe",
        ingredients="ingredient2",
        steps="step2"
    )
    db.add(recipe2)
    db.commit()
    db.refresh(recipe2)
    
    # Set explicit timestamp for second recipe (middle)
    mid_time = now - timedelta(seconds=5)
    db.execute(
        Recipe.__table__.update().where(Recipe.id == recipe2.id).values(created_at=mid_time)
    )
    db.commit()
    
    recipe3 = Recipe(
        user_id=user.id,
        title="Third Recipe",
        ingredients="ingredient3",
        steps="step3"
    )
    db.add(recipe3)
    db.commit()
    db.refresh(recipe3)
    
    # Set explicit timestamp for third recipe (newest)
    db.execute(
        Recipe.__table__.update().where(Recipe.id == recipe3.id).values(created_at=now)
    )
    db.commit()
    
    # Order by created_at descending (most recent first)
    sorted_recipes = db.query(Recipe).order_by(Recipe.created_at.desc()).all()
    
    assert len(sorted_recipes) == 3
    # Most recent should be first
    assert sorted_recipes[0].title == "Third Recipe"
    assert sorted_recipes[1].title == "Second Recipe"
    assert sorted_recipes[2].title == "First Recipe"


def test_order_by_servings(db):
    """Test ORDER BY servings. Validates: Requirements 3.7"""
    # Create user
    user = User(username="testuser", password_hash="hash")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create recipes with different servings
    recipe1 = Recipe(
        user_id=user.id,
        title="Recipe 1",
        ingredients="ingredient1",
        steps="step1",
        servings=8
    )
    recipe2 = Recipe(
        user_id=user.id,
        title="Recipe 2",
        ingredients="ingredient2",
        steps="step2",
        servings=2
    )
    recipe3 = Recipe(
        user_id=user.id,
        title="Recipe 3",
        ingredients="ingredient3",
        steps="step3",
        servings=4
    )
    db.add_all([recipe1, recipe2, recipe3])
    db.commit()
    
    # Order by servings ascending
    sorted_recipes = db.query(Recipe).order_by(Recipe.servings.asc()).all()
    
    assert len(sorted_recipes) == 3
    assert sorted_recipes[0].servings == 2
    assert sorted_recipes[1].servings == 4
    assert sorted_recipes[2].servings == 8


# ============================================================================
# Test pagination with LIMIT and OFFSET
# **Validates: Requirements 3.8**
# ============================================================================

def test_pagination_limit(db):
    """Test pagination with LIMIT. Validates: Requirements 3.8"""
    # Create user
    user = User(username="testuser", password_hash="hash")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create 10 recipes
    recipes = []
    for i in range(10):
        recipe = Recipe(
            user_id=user.id,
            title=f"Recipe {i+1}",
            ingredients=f"ingredient{i+1}",
            steps=f"step{i+1}"
        )
        recipes.append(recipe)
    db.add_all(recipes)
    db.commit()
    
    # Get first 5 recipes
    page1 = db.query(Recipe).limit(5).all()
    
    assert len(page1) == 5


def test_pagination_offset(db):
    """Test pagination with OFFSET. Validates: Requirements 3.8"""
    # Create user
    user = User(username="testuser", password_hash="hash")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create 10 recipes
    recipes = []
    for i in range(10):
        recipe = Recipe(
            user_id=user.id,
            title=f"Recipe {i+1}",
            ingredients=f"ingredient{i+1}",
            steps=f"step{i+1}"
        )
        recipes.append(recipe)
    db.add_all(recipes)
    db.commit()
    
    # Get recipes with offset
    page2 = db.query(Recipe).offset(5).limit(5).all()
    
    assert len(page2) == 5


def test_pagination_with_order(db):
    """Test pagination with ORDER BY. Validates: Requirements 3.8"""
    # Create user
    user = User(username="testuser", password_hash="hash")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create recipes with specific titles
    for i in range(10):
        recipe = Recipe(
            user_id=user.id,
            title=f"Recipe {i:02d}",  # Zero-padded for consistent sorting
            ingredients=f"ingredient{i}",
            steps=f"step{i}"
        )
        db.add(recipe)
    db.commit()
    
    # Get first page (sorted by title)
    page1 = db.query(Recipe).order_by(Recipe.title.asc()).limit(3).all()
    
    assert len(page1) == 3
    assert page1[0].title == "Recipe 00"
    assert page1[1].title == "Recipe 01"
    assert page1[2].title == "Recipe 02"
    
    # Get second page
    page2 = db.query(Recipe).order_by(Recipe.title.asc()).offset(3).limit(3).all()
    
    assert len(page2) == 3
    assert page2[0].title == "Recipe 03"
    assert page2[1].title == "Recipe 04"
    assert page2[2].title == "Recipe 05"


def test_pagination_empty_page(db):
    """Test pagination beyond available records. Validates: Requirements 3.8"""
    # Create user
    user = User(username="testuser", password_hash="hash")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create only 5 recipes
    for i in range(5):
        recipe = Recipe(
            user_id=user.id,
            title=f"Recipe {i+1}",
            ingredients=f"ingredient{i+1}",
            steps=f"step{i+1}"
        )
        db.add(recipe)
    db.commit()
    
    # Try to get page beyond available records
    empty_page = db.query(Recipe).offset(10).limit(5).all()
    
    assert len(empty_page) == 0


# ============================================================================
# Test text search with LIKE
# **Validates: Requirements 3.9**
# ============================================================================

def test_text_search_title_like(db):
    """Test text search on title using LIKE. Validates: Requirements 3.9"""
    # Create user
    user = User(username="testuser", password_hash="hash")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create recipes with different titles
    recipe1 = Recipe(
        user_id=user.id,
        title="Chocolate Cake",
        ingredients="chocolate, flour, sugar",
        steps="mix and bake"
    )
    recipe2 = Recipe(
        user_id=user.id,
        title="Vanilla Cake",
        ingredients="vanilla, flour, sugar",
        steps="mix and bake"
    )
    recipe3 = Recipe(
        user_id=user.id,
        title="Chocolate Cookies",
        ingredients="chocolate chips, flour",
        steps="mix and bake"
    )
    db.add_all([recipe1, recipe2, recipe3])
    db.commit()
    
    # Search for "Chocolate" in title
    search_results = db.query(Recipe).filter(Recipe.title.like("%Chocolate%")).all()
    
    assert len(search_results) == 2
    titles = {r.title for r in search_results}
    assert titles == {"Chocolate Cake", "Chocolate Cookies"}


def test_text_search_ingredients_like(db):
    """Test text search on ingredients using LIKE. Validates: Requirements 3.9"""
    # Create user
    user = User(username="testuser", password_hash="hash")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create recipes
    recipe1 = Recipe(
        user_id=user.id,
        title="Pasta",
        ingredients="tomato sauce, pasta, cheese",
        steps="cook pasta"
    )
    recipe2 = Recipe(
        user_id=user.id,
        title="Pizza",
        ingredients="tomato sauce, dough, cheese",
        steps="bake pizza"
    )
    recipe3 = Recipe(
        user_id=user.id,
        title="Salad",
        ingredients="lettuce, cucumber, dressing",
        steps="mix ingredients"
    )
    db.add_all([recipe1, recipe2, recipe3])
    db.commit()
    
    # Search for "tomato" in ingredients
    search_results = db.query(Recipe).filter(Recipe.ingredients.like("%tomato%")).all()
    
    assert len(search_results) == 2
    titles = {r.title for r in search_results}
    assert titles == {"Pasta", "Pizza"}


def test_text_search_case_insensitive(db):
    """Test case-insensitive text search. Validates: Requirements 3.9"""
    # Create user
    user = User(username="testuser", password_hash="hash")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create recipe
    recipe = Recipe(
        user_id=user.id,
        title="Banana Bread",
        ingredients="bananas, flour, sugar",
        steps="mix and bake"
    )
    db.add(recipe)
    db.commit()
    
    # Search with different cases
    search_lower = db.query(Recipe).filter(Recipe.title.ilike("%banana%")).all()
    search_upper = db.query(Recipe).filter(Recipe.title.ilike("%BANANA%")).all()
    search_mixed = db.query(Recipe).filter(Recipe.title.ilike("%BaNaNa%")).all()
    
    assert len(search_lower) == 1
    assert len(search_upper) == 1
    assert len(search_mixed) == 1
    assert search_lower[0].title == "Banana Bread"


def test_text_search_multiple_fields(db):
    """Test text search across multiple fields (title OR ingredients). Validates: Requirements 3.9"""
    # Create user
    user = User(username="testuser", password_hash="hash")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create recipes
    recipe1 = Recipe(
        user_id=user.id,
        title="Chicken Soup",
        ingredients="chicken, vegetables, broth",
        steps="simmer"
    )
    recipe2 = Recipe(
        user_id=user.id,
        title="Beef Stew",
        ingredients="beef, potatoes, chicken broth",
        steps="stew"
    )
    recipe3 = Recipe(
        user_id=user.id,
        title="Vegetable Curry",
        ingredients="vegetables, curry paste, coconut milk",
        steps="cook"
    )
    db.add_all([recipe1, recipe2, recipe3])
    db.commit()
    
    # Search for "chicken" in title OR ingredients
    from sqlalchemy import or_
    search_results = db.query(Recipe).filter(
        or_(
            Recipe.title.like("%chicken%"),
            Recipe.ingredients.like("%chicken%")
        )
    ).all()
    
    assert len(search_results) == 2
    titles = {r.title for r in search_results}
    assert titles == {"Chicken Soup", "Beef Stew"}


def test_text_search_empty_results(db):
    """Test text search with no matching results. Validates: Requirements 3.9"""
    # Create user
    user = User(username="testuser", password_hash="hash")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create recipe
    recipe = Recipe(
        user_id=user.id,
        title="Simple Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    # Search for non-existent term
    search_results = db.query(Recipe).filter(Recipe.title.like("%nonexistent%")).all()
    
    assert len(search_results) == 0


# ============================================================================
# Test combined filtering, sorting, and pagination
# **Validates: Requirements 3.6, 3.7, 3.8**
# ============================================================================

def test_combined_filter_sort_paginate(db):
    """Test combined filtering, sorting, and pagination. Validates: Requirements 3.6, 3.7, 3.8"""
    # Create user
    user = User(username="testuser", password_hash="hash")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create recipes with different visibility
    for i in range(10):
        visibility = "public" if i % 2 == 0 else "private"
        recipe = Recipe(
            user_id=user.id,
            title=f"Recipe {i:02d}",
            ingredients=f"ingredient{i}",
            steps=f"step{i}",
            visibility=visibility
        )
        db.add(recipe)
    db.commit()
    
    # Filter by public, sort by title, paginate
    results = db.query(Recipe).filter(
        Recipe.visibility == "public"
    ).order_by(
        Recipe.title.asc()
    ).offset(1).limit(2).all()
    
    assert len(results) == 2
    # Should get Recipe 02 and Recipe 04 (skipping Recipe 00)
    assert results[0].title == "Recipe 02"
    assert results[1].title == "Recipe 04"
    assert all(r.visibility == "public" for r in results)
