"""
Property-based tests for MySQL model compatibility.

Feature: mongodb-migration
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from app.models import (
    User, Recipe, RecipeRating, RecipeNote, Collection, CollectionRecipe,
    MealPlan, MealPlanTemplate, MealPlanTemplateItem, ShoppingList,
    ShoppingListItem, NutritionFacts, DietaryLabel, AllergenWarning,
    UserFollow, RecipeLike, RecipeComment
)


# Strategy for generating valid usernames
username_strategy = st.text(
    min_size=1,
    max_size=255,
    alphabet=st.characters(
        blacklist_categories=('Cc', 'Cs'),  # Exclude control characters
        blacklist_characters='\x00'  # Exclude null bytes
    )
).filter(lambda x: x.strip())  # Ensure non-empty after stripping


# Strategy for generating valid passwords
password_strategy = st.text(
    min_size=1,
    max_size=255,
    alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))
)


# Property 1: Primary Key Auto-Generation
# **Validates: Requirements 2.5**
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(username=username_strategy, password=password_strategy)
def test_primary_key_auto_generation_user(db, username, password):
    """
    For any model instance inserted into MySQL, the database should automatically
    assign a unique integer primary key.
    
    Feature: mongodb-migration, Property 1: Primary Key Auto-Generation
    """
    # Create user without specifying ID
    user = User(username=username, password_hash=password)
    assert user.id is None, "ID should be None before insertion"
    
    # Insert into database
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        
        # Verify ID was auto-generated
        assert user.id is not None, "ID should be auto-generated after insertion"
        assert isinstance(user.id, int), "ID should be an integer"
        assert user.id > 0, "ID should be positive"
    finally:
        # Clean up for next iteration
        db.rollback()


@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    username=username_strategy,
    password=password_strategy,
    title=st.text(min_size=1, max_size=500, alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))),
    ingredients=st.text(min_size=1, max_size=1000),
    steps=st.text(min_size=1, max_size=1000)
)
def test_primary_key_auto_generation_recipe(db, username, password, title, ingredients, steps):
    """
    For any Recipe instance inserted, the database should automatically assign a unique ID.
    
    Feature: mongodb-migration, Property 1: Primary Key Auto-Generation
    """
    # Create user first (required for foreign key)
    user = User(username=username, password_hash=password)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        
        # Create recipe without specifying ID
        recipe = Recipe(
            user_id=user.id,
            title=title,
            ingredients=ingredients,
            steps=steps
        )
        assert recipe.id is None, "Recipe ID should be None before insertion"
        
        # Insert into database
        db.add(recipe)
        db.commit()
        db.refresh(recipe)
        
        # Verify ID was auto-generated
        assert recipe.id is not None, "Recipe ID should be auto-generated"
        assert isinstance(recipe.id, int), "Recipe ID should be an integer"
        assert recipe.id > 0, "Recipe ID should be positive"
    finally:
        # Clean up for next iteration
        db.rollback()


@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    username=username_strategy,
    password=password_strategy,
    collection_name=st.text(min_size=1, max_size=255, alphabet=st.characters(blacklist_categories=('Cc', 'Cs')))
)
def test_primary_key_auto_generation_collection(db, username, password, collection_name):
    """
    For any Collection instance inserted, the database should automatically assign a unique ID.
    
    Feature: mongodb-migration, Property 1: Primary Key Auto-Generation
    """
    # Create user first
    user = User(username=username, password_hash=password)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        
        # Create collection without specifying ID
        collection = Collection(user_id=user.id, name=collection_name)
        assert collection.id is None, "Collection ID should be None before insertion"
        
        # Insert into database
        db.add(collection)
        db.commit()
        db.refresh(collection)
        
        # Verify ID was auto-generated
        assert collection.id is not None, "Collection ID should be auto-generated"
        assert isinstance(collection.id, int), "Collection ID should be an integer"
        assert collection.id > 0, "Collection ID should be positive"
    finally:
        # Clean up for next iteration
        db.rollback()


def test_primary_key_uniqueness(db):
    """
    Verify that auto-generated primary keys are unique across multiple insertions.
    
    Feature: mongodb-migration, Property 1: Primary Key Auto-Generation
    """
    import random
    ids = set()
    
    # Create multiple users
    for i in range(10):
        user = User(username=f"user_{i}_{random.randint(0, 1000000)}", password_hash="password")
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Verify ID is unique
        assert user.id not in ids, f"Duplicate ID generated: {user.id}"
        ids.add(user.id)
    
    # Verify we got 10 unique IDs
    assert len(ids) == 10, "Should have 10 unique IDs"


@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    username1=username_strategy,
    username2=username_strategy,
    password=password_strategy
)
def test_primary_key_sequential_generation(db, username1, username2, password):
    """
    Verify that auto-generated IDs are assigned in sequential order.
    
    Feature: mongodb-migration, Property 1: Primary Key Auto-Generation
    """
    # Ensure usernames are different
    if username1 == username2:
        username2 = username2 + "_2"
    
    try:
        # Create first user
        user1 = User(username=username1, password_hash=password)
        db.add(user1)
        db.commit()
        db.refresh(user1)
        
        # Create second user
        user2 = User(username=username2, password_hash=password)
        db.add(user2)
        db.commit()
        db.refresh(user2)
        
        # Verify IDs are sequential (second ID should be greater than first)
        assert user2.id > user1.id, f"IDs should be sequential: {user1.id} < {user2.id}"
    finally:
        # Clean up for next iteration
        db.rollback()
