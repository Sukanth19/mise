"""
Unit tests for basic CRUD operations with MySQL.

Feature: mongodb-migration
Task 4.1: Test basic CRUD operations
"""

import pytest
from datetime import date, datetime
from app.models import (
    User, Recipe, RecipeRating, RecipeNote, Collection, CollectionRecipe,
    MealPlan, MealPlanTemplate, MealPlanTemplateItem, ShoppingList,
    ShoppingListItem, NutritionFacts, DietaryLabel, AllergenWarning,
    UserFollow, RecipeLike, RecipeComment
)


# ============================================================================
# User CRUD Tests
# ============================================================================

def test_user_insert(db):
    """Test INSERT operation for User model. Validates: Requirements 3.2"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    assert user.id is not None
    assert user.username == "testuser"
    assert user.password_hash == "hashed_password"
    assert user.created_at is not None


def test_user_select_by_id(db):
    """Test SELECT by ID for User model. Validates: Requirements 3.1"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    user_id = user.id
    
    retrieved = db.query(User).filter(User.id == user_id).first()
    
    assert retrieved is not None
    assert retrieved.id == user_id
    assert retrieved.username == "testuser"


def test_user_update(db):
    """Test UPDATE operation for User model. Validates: Requirements 3.3"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    user.username = "updated_user"
    user.password_hash = "new_hashed_password"
    db.commit()
    db.refresh(user)
    
    assert user.username == "updated_user"
    assert user.password_hash == "new_hashed_password"


def test_user_delete(db):
    """Test DELETE operation for User model. Validates: Requirements 3.4"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    user_id = user.id
    
    db.delete(user)
    db.commit()
    
    deleted = db.query(User).filter(User.id == user_id).first()
    assert deleted is None


# ============================================================================
# Recipe CRUD Tests
# ============================================================================

def test_recipe_insert(db):
    """Test INSERT operation for Recipe model. Validates: Requirements 3.2"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1, ingredient2",
        steps="step1, step2",
        visibility="public",
        servings=4
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    
    assert recipe.id is not None
    assert recipe.title == "Test Recipe"
    assert recipe.user_id == user.id


def test_recipe_select_by_id(db):
    """Test SELECT by ID for Recipe model. Validates: Requirements 3.1"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    recipe_id = recipe.id
    
    retrieved = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    
    assert retrieved is not None
    assert retrieved.id == recipe_id
    assert retrieved.title == "Test Recipe"


def test_recipe_update(db):
    """Test UPDATE operation for Recipe model. Validates: Requirements 3.3"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    recipe.title = "Updated Recipe"
    recipe.servings = 6
    db.commit()
    db.refresh(recipe)
    
    assert recipe.title == "Updated Recipe"
    assert recipe.servings == 6


def test_recipe_delete(db):
    """Test DELETE operation for Recipe model. Validates: Requirements 3.4"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    recipe_id = recipe.id
    
    db.delete(recipe)
    db.commit()
    
    deleted = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    assert deleted is None


# ============================================================================
# RecipeRating CRUD Tests
# ============================================================================

def test_recipe_rating_insert(db):
    """Test INSERT operation for RecipeRating model. Validates: Requirements 3.2"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    rating = RecipeRating(recipe_id=recipe.id, user_id=user.id, rating=5)
    db.add(rating)
    db.commit()
    db.refresh(rating)
    
    assert rating.id is not None
    assert rating.rating == 5


def test_recipe_rating_select_by_id(db):
    """Test SELECT by ID for RecipeRating model. Validates: Requirements 3.1"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    rating = RecipeRating(recipe_id=recipe.id, user_id=user.id, rating=4)
    db.add(rating)
    db.commit()
    rating_id = rating.id
    
    retrieved = db.query(RecipeRating).filter(RecipeRating.id == rating_id).first()
    
    assert retrieved is not None
    assert retrieved.rating == 4


def test_recipe_rating_update(db):
    """Test UPDATE operation for RecipeRating model. Validates: Requirements 3.3"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    rating = RecipeRating(recipe_id=recipe.id, user_id=user.id, rating=3)
    db.add(rating)
    db.commit()
    
    rating.rating = 5
    db.commit()
    db.refresh(rating)
    
    assert rating.rating == 5


def test_recipe_rating_delete(db):
    """Test DELETE operation for RecipeRating model. Validates: Requirements 3.4"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    rating = RecipeRating(recipe_id=recipe.id, user_id=user.id, rating=4)
    db.add(rating)
    db.commit()
    rating_id = rating.id
    
    db.delete(rating)
    db.commit()
    
    deleted = db.query(RecipeRating).filter(RecipeRating.id == rating_id).first()
    assert deleted is None


# ============================================================================
# RecipeNote CRUD Tests
# ============================================================================

def test_recipe_note_insert(db):
    """Test INSERT operation for RecipeNote model. Validates: Requirements 3.2"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    note = RecipeNote(
        recipe_id=recipe.id,
        user_id=user.id,
        note_text="This is a test note"
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    
    assert note.id is not None
    assert note.note_text == "This is a test note"


def test_recipe_note_select_by_id(db):
    """Test SELECT by ID for RecipeNote model. Validates: Requirements 3.1"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    note = RecipeNote(
        recipe_id=recipe.id,
        user_id=user.id,
        note_text="Test note"
    )
    db.add(note)
    db.commit()
    note_id = note.id
    
    retrieved = db.query(RecipeNote).filter(RecipeNote.id == note_id).first()
    
    assert retrieved is not None
    assert retrieved.note_text == "Test note"


def test_recipe_note_update(db):
    """Test UPDATE operation for RecipeNote model. Validates: Requirements 3.3"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    note = RecipeNote(
        recipe_id=recipe.id,
        user_id=user.id,
        note_text="Original note"
    )
    db.add(note)
    db.commit()
    
    note.note_text = "Updated note"
    db.commit()
    db.refresh(note)
    
    assert note.note_text == "Updated note"


def test_recipe_note_delete(db):
    """Test DELETE operation for RecipeNote model. Validates: Requirements 3.4"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    note = RecipeNote(
        recipe_id=recipe.id,
        user_id=user.id,
        note_text="Test note"
    )
    db.add(note)
    db.commit()
    note_id = note.id
    
    db.delete(note)
    db.commit()
    
    deleted = db.query(RecipeNote).filter(RecipeNote.id == note_id).first()
    assert deleted is None


# ============================================================================
# Collection CRUD Tests
# ============================================================================

def test_collection_insert(db):
    """Test INSERT operation for Collection model. Validates: Requirements 3.2"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    collection = Collection(
        user_id=user.id,
        name="My Collection",
        description="Test collection"
    )
    db.add(collection)
    db.commit()
    db.refresh(collection)
    
    assert collection.id is not None
    assert collection.name == "My Collection"


def test_collection_select_by_id(db):
    """Test SELECT by ID for Collection model. Validates: Requirements 3.1"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    collection = Collection(user_id=user.id, name="My Collection")
    db.add(collection)
    db.commit()
    collection_id = collection.id
    
    retrieved = db.query(Collection).filter(Collection.id == collection_id).first()
    
    assert retrieved is not None
    assert retrieved.name == "My Collection"


def test_collection_update(db):
    """Test UPDATE operation for Collection model. Validates: Requirements 3.3"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    collection = Collection(user_id=user.id, name="My Collection")
    db.add(collection)
    db.commit()
    
    collection.name = "Updated Collection"
    collection.description = "New description"
    db.commit()
    db.refresh(collection)
    
    assert collection.name == "Updated Collection"
    assert collection.description == "New description"


def test_collection_delete(db):
    """Test DELETE operation for Collection model. Validates: Requirements 3.4"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    collection = Collection(user_id=user.id, name="My Collection")
    db.add(collection)
    db.commit()
    collection_id = collection.id
    
    db.delete(collection)
    db.commit()
    
    deleted = db.query(Collection).filter(Collection.id == collection_id).first()
    assert deleted is None


# ============================================================================
# CollectionRecipe CRUD Tests
# ============================================================================

def test_collection_recipe_insert(db):
    """Test INSERT operation for CollectionRecipe model. Validates: Requirements 3.2"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    collection = Collection(user_id=user.id, name="My Collection")
    db.add(collection)
    db.commit()
    
    collection_recipe = CollectionRecipe(
        collection_id=collection.id,
        recipe_id=recipe.id
    )
    db.add(collection_recipe)
    db.commit()
    db.refresh(collection_recipe)
    
    assert collection_recipe.id is not None
    assert collection_recipe.collection_id == collection.id
    assert collection_recipe.recipe_id == recipe.id


def test_collection_recipe_select_by_id(db):
    """Test SELECT by ID for CollectionRecipe model. Validates: Requirements 3.1"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    collection = Collection(user_id=user.id, name="My Collection")
    db.add(collection)
    db.commit()
    
    collection_recipe = CollectionRecipe(
        collection_id=collection.id,
        recipe_id=recipe.id
    )
    db.add(collection_recipe)
    db.commit()
    cr_id = collection_recipe.id
    
    retrieved = db.query(CollectionRecipe).filter(CollectionRecipe.id == cr_id).first()
    
    assert retrieved is not None
    assert retrieved.collection_id == collection.id


def test_collection_recipe_delete(db):
    """Test DELETE operation for CollectionRecipe model. Validates: Requirements 3.4"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    collection = Collection(user_id=user.id, name="My Collection")
    db.add(collection)
    db.commit()
    
    collection_recipe = CollectionRecipe(
        collection_id=collection.id,
        recipe_id=recipe.id
    )
    db.add(collection_recipe)
    db.commit()
    cr_id = collection_recipe.id
    
    db.delete(collection_recipe)
    db.commit()
    
    deleted = db.query(CollectionRecipe).filter(CollectionRecipe.id == cr_id).first()
    assert deleted is None


# ============================================================================
# MealPlan CRUD Tests
# ============================================================================

def test_meal_plan_insert(db):
    """Test INSERT operation for MealPlan model. Validates: Requirements 3.2"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    meal_plan = MealPlan(
        user_id=user.id,
        recipe_id=recipe.id,
        meal_date=date(2024, 1, 15),
        meal_time="dinner"
    )
    db.add(meal_plan)
    db.commit()
    db.refresh(meal_plan)
    
    assert meal_plan.id is not None
    assert meal_plan.meal_time == "dinner"


def test_meal_plan_select_by_id(db):
    """Test SELECT by ID for MealPlan model. Validates: Requirements 3.1"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    meal_plan = MealPlan(
        user_id=user.id,
        recipe_id=recipe.id,
        meal_date=date(2024, 1, 15),
        meal_time="lunch"
    )
    db.add(meal_plan)
    db.commit()
    mp_id = meal_plan.id
    
    retrieved = db.query(MealPlan).filter(MealPlan.id == mp_id).first()
    
    assert retrieved is not None
    assert retrieved.meal_time == "lunch"


def test_meal_plan_update(db):
    """Test UPDATE operation for MealPlan model. Validates: Requirements 3.3"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    meal_plan = MealPlan(
        user_id=user.id,
        recipe_id=recipe.id,
        meal_date=date(2024, 1, 15),
        meal_time="breakfast"
    )
    db.add(meal_plan)
    db.commit()
    
    meal_plan.meal_time = "dinner"
    db.commit()
    db.refresh(meal_plan)
    
    assert meal_plan.meal_time == "dinner"


def test_meal_plan_delete(db):
    """Test DELETE operation for MealPlan model. Validates: Requirements 3.4"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    meal_plan = MealPlan(
        user_id=user.id,
        recipe_id=recipe.id,
        meal_date=date(2024, 1, 15),
        meal_time="snack"
    )
    db.add(meal_plan)
    db.commit()
    mp_id = meal_plan.id
    
    db.delete(meal_plan)
    db.commit()
    
    deleted = db.query(MealPlan).filter(MealPlan.id == mp_id).first()
    assert deleted is None



# ============================================================================
# MealPlanTemplate CRUD Tests
# ============================================================================

def test_meal_plan_template_insert(db):
    """Test INSERT operation for MealPlanTemplate model. Validates: Requirements 3.2"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    template = MealPlanTemplate(
        user_id=user.id,
        name="Weekly Template",
        description="My weekly meal plan"
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    
    assert template.id is not None
    assert template.name == "Weekly Template"


def test_meal_plan_template_select_by_id(db):
    """Test SELECT by ID for MealPlanTemplate model. Validates: Requirements 3.1"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    template = MealPlanTemplate(user_id=user.id, name="Weekly Template")
    db.add(template)
    db.commit()
    template_id = template.id
    
    retrieved = db.query(MealPlanTemplate).filter(MealPlanTemplate.id == template_id).first()
    
    assert retrieved is not None
    assert retrieved.name == "Weekly Template"


def test_meal_plan_template_update(db):
    """Test UPDATE operation for MealPlanTemplate model. Validates: Requirements 3.3"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    template = MealPlanTemplate(user_id=user.id, name="Weekly Template")
    db.add(template)
    db.commit()
    
    template.name = "Monthly Template"
    template.description = "Updated description"
    db.commit()
    db.refresh(template)
    
    assert template.name == "Monthly Template"


def test_meal_plan_template_delete(db):
    """Test DELETE operation for MealPlanTemplate model. Validates: Requirements 3.4"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    template = MealPlanTemplate(user_id=user.id, name="Weekly Template")
    db.add(template)
    db.commit()
    template_id = template.id
    
    db.delete(template)
    db.commit()
    
    deleted = db.query(MealPlanTemplate).filter(MealPlanTemplate.id == template_id).first()
    assert deleted is None


# ============================================================================
# MealPlanTemplateItem CRUD Tests
# ============================================================================

def test_meal_plan_template_item_insert(db):
    """Test INSERT operation for MealPlanTemplateItem model. Validates: Requirements 3.2"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    template = MealPlanTemplate(user_id=user.id, name="Weekly Template")
    db.add(template)
    db.commit()
    
    item = MealPlanTemplateItem(
        template_id=template.id,
        recipe_id=recipe.id,
        day_offset=0,
        meal_time="breakfast"
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    
    assert item.id is not None
    assert item.day_offset == 0


def test_meal_plan_template_item_select_by_id(db):
    """Test SELECT by ID for MealPlanTemplateItem model. Validates: Requirements 3.1"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    template = MealPlanTemplate(user_id=user.id, name="Weekly Template")
    db.add(template)
    db.commit()
    
    item = MealPlanTemplateItem(
        template_id=template.id,
        recipe_id=recipe.id,
        day_offset=1,
        meal_time="lunch"
    )
    db.add(item)
    db.commit()
    item_id = item.id
    
    retrieved = db.query(MealPlanTemplateItem).filter(MealPlanTemplateItem.id == item_id).first()
    
    assert retrieved is not None
    assert retrieved.day_offset == 1


def test_meal_plan_template_item_update(db):
    """Test UPDATE operation for MealPlanTemplateItem model. Validates: Requirements 3.3"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    template = MealPlanTemplate(user_id=user.id, name="Weekly Template")
    db.add(template)
    db.commit()
    
    item = MealPlanTemplateItem(
        template_id=template.id,
        recipe_id=recipe.id,
        day_offset=0,
        meal_time="breakfast"
    )
    db.add(item)
    db.commit()
    
    item.day_offset = 2
    item.meal_time = "dinner"
    db.commit()
    db.refresh(item)
    
    assert item.day_offset == 2
    assert item.meal_time == "dinner"


def test_meal_plan_template_item_delete(db):
    """Test DELETE operation for MealPlanTemplateItem model. Validates: Requirements 3.4"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    template = MealPlanTemplate(user_id=user.id, name="Weekly Template")
    db.add(template)
    db.commit()
    
    item = MealPlanTemplateItem(
        template_id=template.id,
        recipe_id=recipe.id,
        day_offset=0,
        meal_time="snack"
    )
    db.add(item)
    db.commit()
    item_id = item.id
    
    db.delete(item)
    db.commit()
    
    deleted = db.query(MealPlanTemplateItem).filter(MealPlanTemplateItem.id == item_id).first()
    assert deleted is None


# ============================================================================
# ShoppingList CRUD Tests
# ============================================================================

def test_shopping_list_insert(db):
    """Test INSERT operation for ShoppingList model. Validates: Requirements 3.2"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    shopping_list = ShoppingList(
        user_id=user.id,
        name="Weekly Shopping"
    )
    db.add(shopping_list)
    db.commit()
    db.refresh(shopping_list)
    
    assert shopping_list.id is not None
    assert shopping_list.name == "Weekly Shopping"


def test_shopping_list_select_by_id(db):
    """Test SELECT by ID for ShoppingList model. Validates: Requirements 3.1"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    shopping_list = ShoppingList(user_id=user.id, name="Weekly Shopping")
    db.add(shopping_list)
    db.commit()
    list_id = shopping_list.id
    
    retrieved = db.query(ShoppingList).filter(ShoppingList.id == list_id).first()
    
    assert retrieved is not None
    assert retrieved.name == "Weekly Shopping"


def test_shopping_list_update(db):
    """Test UPDATE operation for ShoppingList model. Validates: Requirements 3.3"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    shopping_list = ShoppingList(user_id=user.id, name="Weekly Shopping")
    db.add(shopping_list)
    db.commit()
    
    shopping_list.name = "Monthly Shopping"
    db.commit()
    db.refresh(shopping_list)
    
    assert shopping_list.name == "Monthly Shopping"


def test_shopping_list_delete(db):
    """Test DELETE operation for ShoppingList model. Validates: Requirements 3.4"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    shopping_list = ShoppingList(user_id=user.id, name="Weekly Shopping")
    db.add(shopping_list)
    db.commit()
    list_id = shopping_list.id
    
    db.delete(shopping_list)
    db.commit()
    
    deleted = db.query(ShoppingList).filter(ShoppingList.id == list_id).first()
    assert deleted is None


# ============================================================================
# ShoppingListItem CRUD Tests
# ============================================================================

def test_shopping_list_item_insert(db):
    """Test INSERT operation for ShoppingListItem model. Validates: Requirements 3.2"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    shopping_list = ShoppingList(user_id=user.id, name="Weekly Shopping")
    db.add(shopping_list)
    db.commit()
    
    item = ShoppingListItem(
        shopping_list_id=shopping_list.id,
        ingredient_name="Tomatoes",
        quantity="2 lbs",
        category="produce"
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    
    assert item.id is not None
    assert item.ingredient_name == "Tomatoes"


def test_shopping_list_item_select_by_id(db):
    """Test SELECT by ID for ShoppingListItem model. Validates: Requirements 3.1"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    shopping_list = ShoppingList(user_id=user.id, name="Weekly Shopping")
    db.add(shopping_list)
    db.commit()
    
    item = ShoppingListItem(
        shopping_list_id=shopping_list.id,
        ingredient_name="Milk",
        category="dairy"
    )
    db.add(item)
    db.commit()
    item_id = item.id
    
    retrieved = db.query(ShoppingListItem).filter(ShoppingListItem.id == item_id).first()
    
    assert retrieved is not None
    assert retrieved.ingredient_name == "Milk"


def test_shopping_list_item_update(db):
    """Test UPDATE operation for ShoppingListItem model. Validates: Requirements 3.3"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    shopping_list = ShoppingList(user_id=user.id, name="Weekly Shopping")
    db.add(shopping_list)
    db.commit()
    
    item = ShoppingListItem(
        shopping_list_id=shopping_list.id,
        ingredient_name="Bread",
        is_checked=False
    )
    db.add(item)
    db.commit()
    
    item.is_checked = True
    item.quantity = "2 loaves"
    db.commit()
    db.refresh(item)
    
    assert item.is_checked is True
    assert item.quantity == "2 loaves"


def test_shopping_list_item_delete(db):
    """Test DELETE operation for ShoppingListItem model. Validates: Requirements 3.4"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    shopping_list = ShoppingList(user_id=user.id, name="Weekly Shopping")
    db.add(shopping_list)
    db.commit()
    
    item = ShoppingListItem(
        shopping_list_id=shopping_list.id,
        ingredient_name="Eggs"
    )
    db.add(item)
    db.commit()
    item_id = item.id
    
    db.delete(item)
    db.commit()
    
    deleted = db.query(ShoppingListItem).filter(ShoppingListItem.id == item_id).first()
    assert deleted is None


# ============================================================================
# NutritionFacts CRUD Tests
# ============================================================================

def test_nutrition_facts_insert(db):
    """Test INSERT operation for NutritionFacts model. Validates: Requirements 3.2"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    nutrition = NutritionFacts(
        recipe_id=recipe.id,
        calories=250.5,
        protein_g=15.0,
        carbs_g=30.0,
        fat_g=10.0
    )
    db.add(nutrition)
    db.commit()
    db.refresh(nutrition)
    
    assert nutrition.id is not None
    assert float(nutrition.calories) == 250.5


def test_nutrition_facts_select_by_id(db):
    """Test SELECT by ID for NutritionFacts model. Validates: Requirements 3.1"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    nutrition = NutritionFacts(
        recipe_id=recipe.id,
        calories=300.0,
        protein_g=20.0
    )
    db.add(nutrition)
    db.commit()
    nutrition_id = nutrition.id
    
    retrieved = db.query(NutritionFacts).filter(NutritionFacts.id == nutrition_id).first()
    
    assert retrieved is not None
    assert float(retrieved.calories) == 300.0


def test_nutrition_facts_update(db):
    """Test UPDATE operation for NutritionFacts model. Validates: Requirements 3.3"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    nutrition = NutritionFacts(
        recipe_id=recipe.id,
        calories=200.0
    )
    db.add(nutrition)
    db.commit()
    
    nutrition.calories = 250.0
    nutrition.protein_g = 18.0
    db.commit()
    db.refresh(nutrition)
    
    assert float(nutrition.calories) == 250.0
    assert float(nutrition.protein_g) == 18.0


def test_nutrition_facts_delete(db):
    """Test DELETE operation for NutritionFacts model. Validates: Requirements 3.4"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    nutrition = NutritionFacts(recipe_id=recipe.id, calories=200.0)
    db.add(nutrition)
    db.commit()
    nutrition_id = nutrition.id
    
    db.delete(nutrition)
    db.commit()
    
    deleted = db.query(NutritionFacts).filter(NutritionFacts.id == nutrition_id).first()
    assert deleted is None


# ============================================================================
# DietaryLabel CRUD Tests
# ============================================================================

def test_dietary_label_insert(db):
    """Test INSERT operation for DietaryLabel model. Validates: Requirements 3.2"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    label = DietaryLabel(recipe_id=recipe.id, label="vegan")
    db.add(label)
    db.commit()
    db.refresh(label)
    
    assert label.id is not None
    assert label.label == "vegan"


def test_dietary_label_select_by_id(db):
    """Test SELECT by ID for DietaryLabel model. Validates: Requirements 3.1"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    label = DietaryLabel(recipe_id=recipe.id, label="gluten-free")
    db.add(label)
    db.commit()
    label_id = label.id
    
    retrieved = db.query(DietaryLabel).filter(DietaryLabel.id == label_id).first()
    
    assert retrieved is not None
    assert retrieved.label == "gluten-free"


def test_dietary_label_delete(db):
    """Test DELETE operation for DietaryLabel model. Validates: Requirements 3.4"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    label = DietaryLabel(recipe_id=recipe.id, label="keto")
    db.add(label)
    db.commit()
    label_id = label.id
    
    db.delete(label)
    db.commit()
    
    deleted = db.query(DietaryLabel).filter(DietaryLabel.id == label_id).first()
    assert deleted is None


# ============================================================================
# AllergenWarning CRUD Tests
# ============================================================================

def test_allergen_warning_insert(db):
    """Test INSERT operation for AllergenWarning model. Validates: Requirements 3.2"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    allergen = AllergenWarning(recipe_id=recipe.id, allergen="nuts")
    db.add(allergen)
    db.commit()
    db.refresh(allergen)
    
    assert allergen.id is not None
    assert allergen.allergen == "nuts"


def test_allergen_warning_select_by_id(db):
    """Test SELECT by ID for AllergenWarning model. Validates: Requirements 3.1"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    allergen = AllergenWarning(recipe_id=recipe.id, allergen="dairy")
    db.add(allergen)
    db.commit()
    allergen_id = allergen.id
    
    retrieved = db.query(AllergenWarning).filter(AllergenWarning.id == allergen_id).first()
    
    assert retrieved is not None
    assert retrieved.allergen == "dairy"


def test_allergen_warning_delete(db):
    """Test DELETE operation for AllergenWarning model. Validates: Requirements 3.4"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    allergen = AllergenWarning(recipe_id=recipe.id, allergen="shellfish")
    db.add(allergen)
    db.commit()
    allergen_id = allergen.id
    
    db.delete(allergen)
    db.commit()
    
    deleted = db.query(AllergenWarning).filter(AllergenWarning.id == allergen_id).first()
    assert deleted is None


# ============================================================================
# UserFollow CRUD Tests
# ============================================================================

def test_user_follow_insert(db):
    """Test INSERT operation for UserFollow model. Validates: Requirements 3.2"""
    user1 = User(username="user1", password_hash="hashed_password")
    user2 = User(username="user2", password_hash="hashed_password")
    db.add(user1)
    db.add(user2)
    db.commit()
    
    follow = UserFollow(follower_id=user1.id, following_id=user2.id)
    db.add(follow)
    db.commit()
    db.refresh(follow)
    
    assert follow.id is not None
    assert follow.follower_id == user1.id
    assert follow.following_id == user2.id


def test_user_follow_select_by_id(db):
    """Test SELECT by ID for UserFollow model. Validates: Requirements 3.1"""
    user1 = User(username="user1", password_hash="hashed_password")
    user2 = User(username="user2", password_hash="hashed_password")
    db.add(user1)
    db.add(user2)
    db.commit()
    
    follow = UserFollow(follower_id=user1.id, following_id=user2.id)
    db.add(follow)
    db.commit()
    follow_id = follow.id
    
    retrieved = db.query(UserFollow).filter(UserFollow.id == follow_id).first()
    
    assert retrieved is not None
    assert retrieved.follower_id == user1.id


def test_user_follow_delete(db):
    """Test DELETE operation for UserFollow model. Validates: Requirements 3.4"""
    user1 = User(username="user1", password_hash="hashed_password")
    user2 = User(username="user2", password_hash="hashed_password")
    db.add(user1)
    db.add(user2)
    db.commit()
    
    follow = UserFollow(follower_id=user1.id, following_id=user2.id)
    db.add(follow)
    db.commit()
    follow_id = follow.id
    
    db.delete(follow)
    db.commit()
    
    deleted = db.query(UserFollow).filter(UserFollow.id == follow_id).first()
    assert deleted is None


# ============================================================================
# RecipeLike CRUD Tests
# ============================================================================

def test_recipe_like_insert(db):
    """Test INSERT operation for RecipeLike model. Validates: Requirements 3.2"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    like = RecipeLike(recipe_id=recipe.id, user_id=user.id)
    db.add(like)
    db.commit()
    db.refresh(like)
    
    assert like.id is not None
    assert like.recipe_id == recipe.id


def test_recipe_like_select_by_id(db):
    """Test SELECT by ID for RecipeLike model. Validates: Requirements 3.1"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    like = RecipeLike(recipe_id=recipe.id, user_id=user.id)
    db.add(like)
    db.commit()
    like_id = like.id
    
    retrieved = db.query(RecipeLike).filter(RecipeLike.id == like_id).first()
    
    assert retrieved is not None
    assert retrieved.user_id == user.id


def test_recipe_like_delete(db):
    """Test DELETE operation for RecipeLike model. Validates: Requirements 3.4"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    like = RecipeLike(recipe_id=recipe.id, user_id=user.id)
    db.add(like)
    db.commit()
    like_id = like.id
    
    db.delete(like)
    db.commit()
    
    deleted = db.query(RecipeLike).filter(RecipeLike.id == like_id).first()
    assert deleted is None


# ============================================================================
# RecipeComment CRUD Tests
# ============================================================================

def test_recipe_comment_insert(db):
    """Test INSERT operation for RecipeComment model. Validates: Requirements 3.2"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    comment = RecipeComment(
        recipe_id=recipe.id,
        user_id=user.id,
        comment_text="Great recipe!"
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    assert comment.id is not None
    assert comment.comment_text == "Great recipe!"


def test_recipe_comment_select_by_id(db):
    """Test SELECT by ID for RecipeComment model. Validates: Requirements 3.1"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    comment = RecipeComment(
        recipe_id=recipe.id,
        user_id=user.id,
        comment_text="Nice!"
    )
    db.add(comment)
    db.commit()
    comment_id = comment.id
    
    retrieved = db.query(RecipeComment).filter(RecipeComment.id == comment_id).first()
    
    assert retrieved is not None
    assert retrieved.comment_text == "Nice!"


def test_recipe_comment_update(db):
    """Test UPDATE operation for RecipeComment model. Validates: Requirements 3.3"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    comment = RecipeComment(
        recipe_id=recipe.id,
        user_id=user.id,
        comment_text="Original comment"
    )
    db.add(comment)
    db.commit()
    
    comment.comment_text = "Updated comment"
    db.commit()
    db.refresh(comment)
    
    assert comment.comment_text == "Updated comment"


def test_recipe_comment_delete(db):
    """Test DELETE operation for RecipeComment model. Validates: Requirements 3.4"""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    
    comment = RecipeComment(
        recipe_id=recipe.id,
        user_id=user.id,
        comment_text="Test comment"
    )
    db.add(comment)
    db.commit()
    comment_id = comment.id
    
    db.delete(comment)
    db.commit()
    
    deleted = db.query(RecipeComment).filter(RecipeComment.id == comment_id).first()
    assert deleted is None
