"""
Property-based tests for CRUD round trips with MySQL.

Feature: mongodb-migration
Task 4.2: Write property tests for CRUD round trips
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from datetime import date, datetime
from decimal import Decimal
from app.models import (
    User, Recipe, RecipeRating, RecipeNote, Collection, CollectionRecipe,
    MealPlan, MealPlanTemplate, MealPlanTemplateItem, ShoppingList,
    ShoppingListItem, NutritionFacts, DietaryLabel, AllergenWarning,
    UserFollow, RecipeLike, RecipeComment
)


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

# Strategy for generating valid long text fields
long_text_strategy = st.text(
    min_size=1,
    max_size=1000,
    alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))
)

# Strategy for meal times
meal_time_strategy = st.sampled_from(['breakfast', 'lunch', 'dinner', 'snack'])

# Strategy for dietary labels
dietary_label_strategy = st.sampled_from([
    'vegan', 'vegetarian', 'gluten-free', 'dairy-free', 'keto', 'paleo', 'low-carb'
])

# Strategy for allergens
allergen_strategy = st.sampled_from([
    'nuts', 'dairy', 'eggs', 'soy', 'wheat', 'fish', 'shellfish'
])

# Strategy for categories
category_strategy = st.sampled_from(['produce', 'dairy', 'meat', 'pantry', 'other'])


# ============================================================================
# Property 2: Insert-Retrieve Round Trip
# **Validates: Requirements 3.2**
# ============================================================================

@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(username=username_strategy, password=password_strategy)
def test_user_insert_retrieve_round_trip(db, username, password):
    """
    Property 2: Insert-Retrieve Round Trip
    
    For any valid model instance, inserting it into MySQL and then retrieving 
    it by ID should return equivalent data.
    
    Property 2: Insert-Retrieve Round Trip
    **Validates: Requirements 3.2**
    """
    # Insert
    user = User(username=username, password_hash=password)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        user_id = user.id
        
        # Retrieve
        retrieved = db.query(User).filter(User.id == user_id).first()
        
        # Assert equivalence
        assert retrieved is not None, "Retrieved user should not be None"
        assert retrieved.id == user_id, "IDs should match"
        assert retrieved.username == username, "Usernames should match"
        assert retrieved.password_hash == password, "Password hashes should match"
        assert retrieved.created_at is not None, "Created timestamp should exist"
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
    title=text_strategy,
    ingredients=long_text_strategy,
    steps=long_text_strategy,
    servings=st.integers(min_value=1, max_value=20)
)
def test_recipe_insert_retrieve_round_trip(db, username, password, title, ingredients, steps, servings):
    """
    Property 2: Insert-Retrieve Round Trip for Recipe
    
    Property 2: Insert-Retrieve Round Trip
    **Validates: Requirements 3.2**
    """
    # Create user first
    user = User(username=username, password_hash=password)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        
        # Insert recipe
        recipe = Recipe(
            user_id=user.id,
            title=title,
            ingredients=ingredients,
            steps=steps,
            servings=servings
        )
        db.add(recipe)
        db.commit()
        db.refresh(recipe)
        recipe_id = recipe.id
        
        # Retrieve
        retrieved = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        
        # Assert equivalence
        assert retrieved is not None
        assert retrieved.id == recipe_id
        assert retrieved.title == title
        assert retrieved.ingredients == ingredients
        assert retrieved.steps == steps
        assert retrieved.servings == servings
        assert retrieved.user_id == user.id
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
    collection_name=text_strategy,
    description=st.one_of(st.none(), long_text_strategy)
)
def test_collection_insert_retrieve_round_trip(db, username, password, collection_name, description):
    """
    Property 2: Insert-Retrieve Round Trip for Collection
    
    Property 2: Insert-Retrieve Round Trip
    **Validates: Requirements 3.2**
    """
    # Create user first
    user = User(username=username, password_hash=password)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        
        # Insert collection
        collection = Collection(
            user_id=user.id,
            name=collection_name,
            description=description
        )
        db.add(collection)
        db.commit()
        db.refresh(collection)
        collection_id = collection.id
        
        # Retrieve
        retrieved = db.query(Collection).filter(Collection.id == collection_id).first()
        
        # Assert equivalence
        assert retrieved is not None
        assert retrieved.id == collection_id
        assert retrieved.name == collection_name
        assert retrieved.description == description
        assert retrieved.user_id == user.id
    finally:
        db.rollback()


# ============================================================================
# Property 3: Update-Retrieve Round Trip
# **Validates: Requirements 3.3**
# ============================================================================

@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    username1=username_strategy,
    username2=username_strategy,
    password1=password_strategy,
    password2=password_strategy
)
def test_user_update_retrieve_round_trip(db, username1, username2, password1, password2):
    """
    Property 3: Update-Retrieve Round Trip
    
    For any existing record and valid update data, updating the record and 
    then retrieving it should reflect all changes.
    
    Property 3: Update-Retrieve Round Trip
    **Validates: Requirements 3.3**
    """
    # Ensure usernames are different
    if username1 == username2:
        username2 = username2 + "_updated"
    
    # Insert initial user
    user = User(username=username1, password_hash=password1)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        user_id = user.id
        
        # Update
        user.username = username2
        user.password_hash = password2
        db.commit()
        
        # Retrieve
        retrieved = db.query(User).filter(User.id == user_id).first()
        
        # Assert updates are reflected
        assert retrieved is not None
        assert retrieved.id == user_id
        assert retrieved.username == username2, "Username should be updated"
        assert retrieved.password_hash == password2, "Password should be updated"
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
    title1=text_strategy,
    title2=text_strategy,
    servings1=st.integers(min_value=1, max_value=10),
    servings2=st.integers(min_value=1, max_value=10)
)
def test_recipe_update_retrieve_round_trip(db, username, password, title1, title2, servings1, servings2):
    """
    Property 3: Update-Retrieve Round Trip for Recipe
    
    Property 3: Update-Retrieve Round Trip
    **Validates: Requirements 3.3**
    """
    # Create user first
    user = User(username=username, password_hash=password)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        
        # Insert initial recipe
        recipe = Recipe(
            user_id=user.id,
            title=title1,
            ingredients="ingredient1",
            steps="step1",
            servings=servings1
        )
        db.add(recipe)
        db.commit()
        db.refresh(recipe)
        recipe_id = recipe.id
        
        # Update
        recipe.title = title2
        recipe.servings = servings2
        db.commit()
        
        # Retrieve
        retrieved = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        
        # Assert updates are reflected
        assert retrieved is not None
        assert retrieved.id == recipe_id
        assert retrieved.title == title2, "Title should be updated"
        assert retrieved.servings == servings2, "Servings should be updated"
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
    rating1=st.integers(min_value=1, max_value=5),
    rating2=st.integers(min_value=1, max_value=5)
)
def test_rating_update_retrieve_round_trip(db, username, password, rating1, rating2):
    """
    Property 3: Update-Retrieve Round Trip for RecipeRating
    
    Property 3: Update-Retrieve Round Trip
    **Validates: Requirements 3.3**
    """
    # Create user and recipe first
    user = User(username=username, password_hash=password)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        
        recipe = Recipe(
            user_id=user.id,
            title="Test Recipe",
            ingredients="ingredient1",
            steps="step1"
        )
        db.add(recipe)
        db.commit()
        db.refresh(recipe)
        
        # Insert initial rating
        rating = RecipeRating(
            recipe_id=recipe.id,
            user_id=user.id,
            rating=rating1
        )
        db.add(rating)
        db.commit()
        db.refresh(rating)
        rating_id = rating.id
        
        # Update
        rating.rating = rating2
        db.commit()
        
        # Retrieve
        retrieved = db.query(RecipeRating).filter(RecipeRating.id == rating_id).first()
        
        # Assert updates are reflected
        assert retrieved is not None
        assert retrieved.id == rating_id
        assert retrieved.rating == rating2, "Rating should be updated"
    finally:
        db.rollback()


# ============================================================================
# Property 4: Delete Removes Record
# **Validates: Requirements 3.4**
# ============================================================================

@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(username=username_strategy, password=password_strategy)
def test_user_delete_removes_record(db, username, password):
    """
    Property 4: Delete Removes Record
    
    For any existing record, deleting it should result in the record no longer 
    being retrievable.
    
    Property 4: Delete Removes Record
    **Validates: Requirements 3.4**
    """
    # Insert user
    user = User(username=username, password_hash=password)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        user_id = user.id
        
        # Verify it exists
        exists = db.query(User).filter(User.id == user_id).first()
        assert exists is not None, "User should exist before deletion"
        
        # Delete
        db.delete(user)
        db.commit()
        
        # Verify it's gone
        deleted = db.query(User).filter(User.id == user_id).first()
        assert deleted is None, "User should not exist after deletion"
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
    title=text_strategy
)
def test_recipe_delete_removes_record(db, username, password, title):
    """
    Property 4: Delete Removes Record for Recipe
    
    Property 4: Delete Removes Record
    **Validates: Requirements 3.4**
    """
    # Create user first
    user = User(username=username, password_hash=password)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        
        # Insert recipe
        recipe = Recipe(
            user_id=user.id,
            title=title,
            ingredients="ingredient1",
            steps="step1"
        )
        db.add(recipe)
        db.commit()
        db.refresh(recipe)
        recipe_id = recipe.id
        
        # Verify it exists
        exists = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        assert exists is not None, "Recipe should exist before deletion"
        
        # Delete
        db.delete(recipe)
        db.commit()
        
        # Verify it's gone
        deleted = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        assert deleted is None, "Recipe should not exist after deletion"
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
    collection_name=text_strategy
)
def test_collection_delete_removes_record(db, username, password, collection_name):
    """
    Property 4: Delete Removes Record for Collection
    
    Property 4: Delete Removes Record
    **Validates: Requirements 3.4**
    """
    # Create user first
    user = User(username=username, password_hash=password)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        
        # Insert collection
        collection = Collection(
            user_id=user.id,
            name=collection_name
        )
        db.add(collection)
        db.commit()
        db.refresh(collection)
        collection_id = collection.id
        
        # Verify it exists
        exists = db.query(Collection).filter(Collection.id == collection_id).first()
        assert exists is not None, "Collection should exist before deletion"
        
        # Delete
        db.delete(collection)
        db.commit()
        
        # Verify it's gone
        deleted = db.query(Collection).filter(Collection.id == collection_id).first()
        assert deleted is None, "Collection should not exist after deletion"
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
    note_text=long_text_strategy
)
def test_note_delete_removes_record(db, username, password, note_text):
    """
    Property 4: Delete Removes Record for RecipeNote
    
    Property 4: Delete Removes Record
    **Validates: Requirements 3.4**
    """
    # Create user and recipe first
    user = User(username=username, password_hash=password)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        
        recipe = Recipe(
            user_id=user.id,
            title="Test Recipe",
            ingredients="ingredient1",
            steps="step1"
        )
        db.add(recipe)
        db.commit()
        db.refresh(recipe)
        
        # Insert note
        note = RecipeNote(
            recipe_id=recipe.id,
            user_id=user.id,
            note_text=note_text
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        note_id = note.id
        
        # Verify it exists
        exists = db.query(RecipeNote).filter(RecipeNote.id == note_id).first()
        assert exists is not None, "Note should exist before deletion"
        
        # Delete
        db.delete(note)
        db.commit()
        
        # Verify it's gone
        deleted = db.query(RecipeNote).filter(RecipeNote.id == note_id).first()
        assert deleted is None, "Note should not exist after deletion"
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
    label=dietary_label_strategy
)
def test_dietary_label_delete_removes_record(db, username, password, label):
    """
    Property 4: Delete Removes Record for DietaryLabel
    
    Property 4: Delete Removes Record
    **Validates: Requirements 3.4**
    """
    # Create user and recipe first
    user = User(username=username, password_hash=password)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        
        recipe = Recipe(
            user_id=user.id,
            title="Test Recipe",
            ingredients="ingredient1",
            steps="step1"
        )
        db.add(recipe)
        db.commit()
        db.refresh(recipe)
        
        # Insert dietary label
        dietary_label = DietaryLabel(
            recipe_id=recipe.id,
            label=label
        )
        db.add(dietary_label)
        db.commit()
        db.refresh(dietary_label)
        label_id = dietary_label.id
        
        # Verify it exists
        exists = db.query(DietaryLabel).filter(DietaryLabel.id == label_id).first()
        assert exists is not None, "Dietary label should exist before deletion"
        
        # Delete
        db.delete(dietary_label)
        db.commit()
        
        # Verify it's gone
        deleted = db.query(DietaryLabel).filter(DietaryLabel.id == label_id).first()
        assert deleted is None, "Dietary label should not exist after deletion"
    finally:
        db.rollback()
