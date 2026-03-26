"""
Unit tests for relationship loading with MySQL.

Task 4.3: Test relationship loading
"""

import pytest
from datetime import date
from app.models import (
    User, Recipe, RecipeRating, RecipeNote, Collection, CollectionRecipe,
    MealPlan, NutritionFacts, DietaryLabel
)
from sqlalchemy.orm import joinedload


# ============================================================================
# Test User with Recipes (one-to-many)
# **Validates: Requirements 3.5, 4.5**
# ============================================================================

def test_load_user_with_recipes(db):
    """
    Test loading User with recipes (one-to-many relationship).
    
    **Validates: Requirements 3.5, 4.5**
    """
    # Create user
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create multiple recipes for the user
    recipe1 = Recipe(
        user_id=user.id,
        title="Recipe 1",
        ingredients="ingredient1",
        steps="step1"
    )
    recipe2 = Recipe(
        user_id=user.id,
        title="Recipe 2",
        ingredients="ingredient2",
        steps="step2"
    )
    recipe3 = Recipe(
        user_id=user.id,
        title="Recipe 3",
        ingredients="ingredient3",
        steps="step3"
    )
    db.add_all([recipe1, recipe2, recipe3])
    db.commit()
    
    # Load user with recipes using JOIN
    loaded_user = db.query(User).options(
        joinedload(User.recipes)
    ).filter(User.id == user.id).first()
    
    # Verify relationship loading
    assert loaded_user is not None
    assert len(loaded_user.recipes) == 3
    assert all(r.user_id == user.id for r in loaded_user.recipes)
    
    # Verify recipe titles
    titles = {r.title for r in loaded_user.recipes}
    assert titles == {"Recipe 1", "Recipe 2", "Recipe 3"}


# ============================================================================
# Test Recipe with NutritionFacts (one-to-one)
# **Validates: Requirements 3.5, 4.1**
# ============================================================================

def test_load_recipe_with_nutrition_facts(db):
    """
    Test loading Recipe with nutrition_facts (one-to-one relationship).
    
    **Validates: Requirements 3.5, 4.1**
    """
    # Create user and recipe
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    recipe = Recipe(
        user_id=user.id,
        title="Healthy Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    
    # Create nutrition facts for the recipe
    nutrition = NutritionFacts(
        recipe_id=recipe.id,
        calories=250.5,
        protein_g=15.0,
        carbs_g=30.0,
        fat_g=10.0,
        fiber_g=5.0
    )
    db.add(nutrition)
    db.commit()
    
    # Load recipe with nutrition facts using JOIN
    loaded_recipe = db.query(Recipe).options(
        joinedload(Recipe.nutrition_facts)
    ).filter(Recipe.id == recipe.id).first()
    
    # Verify relationship loading
    assert loaded_recipe is not None
    assert loaded_recipe.nutrition_facts is not None
    assert loaded_recipe.nutrition_facts.recipe_id == recipe.id
    assert float(loaded_recipe.nutrition_facts.calories) == 250.5
    assert float(loaded_recipe.nutrition_facts.protein_g) == 15.0


def test_load_recipe_without_nutrition_facts(db):
    """
    Test loading Recipe that has no nutrition_facts (one-to-one relationship).
    
    **Validates: Requirements 3.5, 4.1**
    """
    # Create user and recipe without nutrition facts
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    recipe = Recipe(
        user_id=user.id,
        title="Simple Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    
    # Load recipe with nutrition facts using JOIN
    loaded_recipe = db.query(Recipe).options(
        joinedload(Recipe.nutrition_facts)
    ).filter(Recipe.id == recipe.id).first()
    
    # Verify relationship loading
    assert loaded_recipe is not None
    assert loaded_recipe.nutrition_facts is None


# ============================================================================
# Test Recipe with DietaryLabels (one-to-many)
# **Validates: Requirements 3.5, 4.2**
# ============================================================================

def test_load_recipe_with_dietary_labels(db):
    """
    Test loading Recipe with dietary_labels (one-to-many relationship).
    
    **Validates: Requirements 3.5, 4.2**
    """
    # Create user and recipe
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    recipe = Recipe(
        user_id=user.id,
        title="Vegan Gluten-Free Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    
    # Create multiple dietary labels for the recipe
    label1 = DietaryLabel(recipe_id=recipe.id, label="vegan")
    label2 = DietaryLabel(recipe_id=recipe.id, label="gluten-free")
    label3 = DietaryLabel(recipe_id=recipe.id, label="dairy-free")
    db.add_all([label1, label2, label3])
    db.commit()
    
    # Load recipe with dietary labels using JOIN
    loaded_recipe = db.query(Recipe).options(
        joinedload(Recipe.dietary_labels)
    ).filter(Recipe.id == recipe.id).first()
    
    # Verify relationship loading
    assert loaded_recipe is not None
    assert len(loaded_recipe.dietary_labels) == 3
    assert all(l.recipe_id == recipe.id for l in loaded_recipe.dietary_labels)
    
    # Verify labels
    labels = {l.label for l in loaded_recipe.dietary_labels}
    assert labels == {"vegan", "gluten-free", "dairy-free"}


# ============================================================================
# Test Collection with Recipes via CollectionRecipes (many-to-many)
# **Validates: Requirements 3.5, 4.6**
# ============================================================================

def test_load_collection_with_recipes(db):
    """
    Test loading Collection with recipes via collection_recipes (many-to-many relationship).
    
    **Validates: Requirements 3.5, 4.6**
    """
    # Create user
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create collection
    collection = Collection(
        user_id=user.id,
        name="My Favorite Recipes"
    )
    db.add(collection)
    db.commit()
    db.refresh(collection)
    
    # Create multiple recipes
    recipe1 = Recipe(
        user_id=user.id,
        title="Recipe 1",
        ingredients="ingredient1",
        steps="step1"
    )
    recipe2 = Recipe(
        user_id=user.id,
        title="Recipe 2",
        ingredients="ingredient2",
        steps="step2"
    )
    recipe3 = Recipe(
        user_id=user.id,
        title="Recipe 3",
        ingredients="ingredient3",
        steps="step3"
    )
    db.add_all([recipe1, recipe2, recipe3])
    db.commit()
    
    # Add recipes to collection via join table
    cr1 = CollectionRecipe(collection_id=collection.id, recipe_id=recipe1.id)
    cr2 = CollectionRecipe(collection_id=collection.id, recipe_id=recipe2.id)
    cr3 = CollectionRecipe(collection_id=collection.id, recipe_id=recipe3.id)
    db.add_all([cr1, cr2, cr3])
    db.commit()
    
    # Load collection with collection_recipes
    loaded_collection = db.query(Collection).options(
        joinedload(Collection.collection_recipes)
    ).filter(Collection.id == collection.id).first()
    
    # Verify relationship loading
    assert loaded_collection is not None
    assert len(loaded_collection.collection_recipes) == 3
    assert all(cr.collection_id == collection.id for cr in loaded_collection.collection_recipes)
    
    # Verify we can access recipes through the join table
    recipe_ids = {cr.recipe_id for cr in loaded_collection.collection_recipes}
    assert recipe_ids == {recipe1.id, recipe2.id, recipe3.id}


def test_load_collection_with_recipes_full_join(db):
    """
    Test loading Collection with full recipe data via nested joins.
    
    **Validates: Requirements 3.5, 4.6**
    """
    # Create user
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create collection
    collection = Collection(
        user_id=user.id,
        name="My Collection"
    )
    db.add(collection)
    db.commit()
    db.refresh(collection)
    
    # Create recipes
    recipe1 = Recipe(
        user_id=user.id,
        title="Recipe A",
        ingredients="ingredient1",
        steps="step1"
    )
    recipe2 = Recipe(
        user_id=user.id,
        title="Recipe B",
        ingredients="ingredient2",
        steps="step2"
    )
    db.add_all([recipe1, recipe2])
    db.commit()
    
    # Add recipes to collection
    cr1 = CollectionRecipe(collection_id=collection.id, recipe_id=recipe1.id)
    cr2 = CollectionRecipe(collection_id=collection.id, recipe_id=recipe2.id)
    db.add_all([cr1, cr2])
    db.commit()
    
    # Load collection with nested joins to get full recipe data
    loaded_collection = db.query(Collection).options(
        joinedload(Collection.collection_recipes).joinedload(CollectionRecipe.recipe)
    ).filter(Collection.id == collection.id).first()
    
    # Verify relationship loading with full recipe data
    assert loaded_collection is not None
    assert len(loaded_collection.collection_recipes) == 2
    
    # Access full recipe data through the relationship
    recipes = [cr.recipe for cr in loaded_collection.collection_recipes]
    assert len(recipes) == 2
    titles = {r.title for r in recipes}
    assert titles == {"Recipe A", "Recipe B"}


# ============================================================================
# Test MealPlan with Recipe Reference
# **Validates: Requirements 3.5, 4.7**
# ============================================================================

def test_load_meal_plan_with_recipe(db):
    """
    Test loading MealPlan with recipe reference.
    
    **Validates: Requirements 3.5, 4.7**
    """
    # Create user
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create recipe
    recipe = Recipe(
        user_id=user.id,
        title="Dinner Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    
    # Create meal plan
    meal_plan = MealPlan(
        user_id=user.id,
        recipe_id=recipe.id,
        meal_date=date(2024, 1, 15),
        meal_time="dinner"
    )
    db.add(meal_plan)
    db.commit()
    
    # Load meal plan with recipe using JOIN
    loaded_meal_plan = db.query(MealPlan).options(
        joinedload(MealPlan.recipe)
    ).filter(MealPlan.id == meal_plan.id).first()
    
    # Verify relationship loading
    assert loaded_meal_plan is not None
    assert loaded_meal_plan.recipe is not None
    assert loaded_meal_plan.recipe.id == recipe.id
    assert loaded_meal_plan.recipe.title == "Dinner Recipe"


def test_load_multiple_meal_plans_for_user(db):
    """
    Test loading multiple MealPlans for a user with recipe references.
    
    **Validates: Requirements 3.5, 4.7**
    """
    # Create user
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create recipes
    breakfast_recipe = Recipe(
        user_id=user.id,
        title="Breakfast Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    lunch_recipe = Recipe(
        user_id=user.id,
        title="Lunch Recipe",
        ingredients="ingredient2",
        steps="step2"
    )
    dinner_recipe = Recipe(
        user_id=user.id,
        title="Dinner Recipe",
        ingredients="ingredient3",
        steps="step3"
    )
    db.add_all([breakfast_recipe, lunch_recipe, dinner_recipe])
    db.commit()
    
    # Create meal plans
    mp1 = MealPlan(
        user_id=user.id,
        recipe_id=breakfast_recipe.id,
        meal_date=date(2024, 1, 15),
        meal_time="breakfast"
    )
    mp2 = MealPlan(
        user_id=user.id,
        recipe_id=lunch_recipe.id,
        meal_date=date(2024, 1, 15),
        meal_time="lunch"
    )
    mp3 = MealPlan(
        user_id=user.id,
        recipe_id=dinner_recipe.id,
        meal_date=date(2024, 1, 15),
        meal_time="dinner"
    )
    db.add_all([mp1, mp2, mp3])
    db.commit()
    
    # Load all meal plans for user with recipes
    loaded_meal_plans = db.query(MealPlan).options(
        joinedload(MealPlan.recipe)
    ).filter(MealPlan.user_id == user.id).all()
    
    # Verify relationship loading
    assert len(loaded_meal_plans) == 3
    assert all(mp.recipe is not None for mp in loaded_meal_plans)
    
    # Verify meal times and recipes
    meal_data = {mp.meal_time: mp.recipe.title for mp in loaded_meal_plans}
    assert meal_data == {
        "breakfast": "Breakfast Recipe",
        "lunch": "Lunch Recipe",
        "dinner": "Dinner Recipe"
    }


# ============================================================================
# Test Complex Multi-Level Relationships
# **Validates: Requirements 3.5, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9**
# ============================================================================

def test_load_recipe_with_all_relationships(db):
    """
    Test loading Recipe with all related data (nutrition, labels, ratings, notes).
    
    **Validates: Requirements 3.5, 4.1, 4.2, 4.3, 4.4**
    """
    # Create user
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create recipe
    recipe = Recipe(
        user_id=user.id,
        title="Complete Recipe",
        ingredients="ingredient1",
        steps="step1"
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    
    # Add nutrition facts
    nutrition = NutritionFacts(
        recipe_id=recipe.id,
        calories=300.0,
        protein_g=20.0
    )
    db.add(nutrition)
    
    # Add dietary labels
    label1 = DietaryLabel(recipe_id=recipe.id, label="vegan")
    label2 = DietaryLabel(recipe_id=recipe.id, label="gluten-free")
    db.add_all([label1, label2])
    
    # Add rating
    rating = RecipeRating(
        recipe_id=recipe.id,
        user_id=user.id,
        rating=5
    )
    db.add(rating)
    
    # Add note
    note = RecipeNote(
        recipe_id=recipe.id,
        user_id=user.id,
        note_text="Great recipe!"
    )
    db.add(note)
    
    db.commit()
    
    # Load recipe with all relationships
    loaded_recipe = db.query(Recipe).options(
        joinedload(Recipe.nutrition_facts),
        joinedload(Recipe.dietary_labels),
        joinedload(Recipe.ratings),
        joinedload(Recipe.notes)
    ).filter(Recipe.id == recipe.id).first()
    
    # Verify all relationships are loaded
    assert loaded_recipe is not None
    assert loaded_recipe.nutrition_facts is not None
    assert float(loaded_recipe.nutrition_facts.calories) == 300.0
    assert len(loaded_recipe.dietary_labels) == 2
    assert len(loaded_recipe.ratings) == 1
    assert loaded_recipe.ratings[0].rating == 5
    assert len(loaded_recipe.notes) == 1
    assert loaded_recipe.notes[0].note_text == "Great recipe!"
