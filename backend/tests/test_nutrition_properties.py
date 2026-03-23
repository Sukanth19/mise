"""Property-based tests for nutrition tracking."""
import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from app.services.nutrition_service import NutritionTracker
from app.models import Recipe, User, MealPlan, NutritionFacts
from app.schemas import NutritionCreate, NutritionUpdate
from datetime import date, timedelta


# ============================================================================
# Property 40: Nutrition facts validation
# Feature: recipe-saver-enhancements, Property 40: Nutrition facts validation
# ============================================================================

@given(
    calories=st.floats(min_value=0, max_value=10000, allow_nan=False, allow_infinity=False),
    protein_g=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
    carbs_g=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
    fat_g=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
    fiber_g=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_nutrition_facts_validation_property(db, calories, protein_g, carbs_g, fat_g, fiber_g):
    """
    Property 40: Nutrition facts validation
    For any nutrition values, they must be non-negative numbers.
    Validates: Requirements 24.2
    """
    # Create test user and recipe
    import uuid
    user = User(username=f"user_{uuid.uuid4().hex[:8]}", password_hash="hash")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients='["test"]',
        steps='["test"]'
    )
    db.add(recipe)
    db.commit()
    
    # Create nutrition data with non-negative values
    nutrition_data = NutritionCreate(
        calories=calories,
        protein_g=protein_g,
        carbs_g=carbs_g,
        fat_g=fat_g,
        fiber_g=fiber_g
    )
    
    # Add nutrition facts - should succeed with non-negative values
    nutrition = NutritionTracker.add_nutrition_facts(db, recipe.id, nutrition_data, user.id)
    
    # Verify nutrition was added successfully
    assert nutrition is not None
    # Compare with tolerance for Decimal/float conversion
    assert abs(float(nutrition.calories) - calories) < 0.01
    assert abs(float(nutrition.protein_g) - protein_g) < 0.01
    assert abs(float(nutrition.carbs_g) - carbs_g) < 0.01
    assert abs(float(nutrition.fat_g) - fat_g) < 0.01
    assert abs(float(nutrition.fiber_g) - fiber_g) < 0.01


# ============================================================================
# Property 41: Per-serving calculation
# Feature: recipe-saver-enhancements, Property 41: Per-serving calculation
# ============================================================================

@given(
    calories=st.floats(min_value=1, max_value=10000, allow_nan=False, allow_infinity=False),
    protein_g=st.floats(min_value=1, max_value=1000, allow_nan=False, allow_infinity=False),
    servings=st.integers(min_value=1, max_value=20)
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_per_serving_calculation_property(db, calories, protein_g, servings):
    """
    Property 41: Per-serving calculation
    For any recipe with nutrition facts and serving size, the per-serving values
    should equal total values divided by serving count.
    Validates: Requirements 25.2
    """
    # Create test user and recipe with servings
    import uuid
    user = User(username=f"user_{uuid.uuid4().hex[:8]}", password_hash="hash")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients='["test"]',
        steps='["test"]',
        servings=servings
    )
    db.add(recipe)
    db.commit()
    
    # Add nutrition facts
    nutrition_data = NutritionCreate(calories=calories, protein_g=protein_g)
    nutrition = NutritionTracker.add_nutrition_facts(db, recipe.id, nutrition_data, user.id)
    
    # Calculate per-serving values
    per_serving = NutritionTracker.calculate_per_serving(nutrition, servings)
    
    # Verify per-serving calculation
    expected_calories = calories / servings
    expected_protein = protein_g / servings
    
    # Allow small floating point tolerance
    assert abs(per_serving['calories'] - expected_calories) < 0.01
    assert abs(per_serving['protein_g'] - expected_protein) < 0.01


# ============================================================================
# Property 42: Default serving size
# Feature: recipe-saver-enhancements, Property 42: Default serving size
# ============================================================================

@given(
    calories=st.floats(min_value=1, max_value=10000, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_default_serving_size_property(db, calories):
    """
    Property 42: Default serving size
    For any recipe without a specified serving size, the default should be 1 serving.
    Validates: Requirements 25.4
    """
    # Create test user and recipe WITHOUT explicit servings
    import uuid
    user = User(username=f"user_{uuid.uuid4().hex[:8]}", password_hash="hash")
    db.add(user)
    db.commit()
    
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients='["test"]',
        steps='["test"]'
        # servings not specified, should default to 1
    )
    db.add(recipe)
    db.commit()
    
    # Add nutrition facts
    nutrition_data = NutritionCreate(calories=calories)
    nutrition = NutritionTracker.add_nutrition_facts(db, recipe.id, nutrition_data, user.id)
    
    # Get recipe servings (should default to 1)
    db.refresh(recipe)
    servings = recipe.servings if recipe.servings else 1
    
    # Calculate per-serving values
    per_serving = NutritionTracker.calculate_per_serving(nutrition, servings)
    
    # With default serving of 1, per-serving should equal total
    assert abs(per_serving['calories'] - calories) < 0.01


# ============================================================================
# Property 45: Meal plan nutrition summation
# Feature: recipe-saver-enhancements, Property 45: Meal plan nutrition summation
# ============================================================================

@given(
    recipe_count=st.integers(min_value=1, max_value=5),
    calories_list=st.lists(
        st.floats(min_value=100, max_value=1000, allow_nan=False, allow_infinity=False),
        min_size=1,
        max_size=5
    )
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_meal_plan_nutrition_summation_property(db, recipe_count, calories_list):
    """
    Property 45: Meal plan nutrition summation
    For any meal plan date range, the total nutrition should equal the sum of
    nutrition facts from all planned recipes.
    Validates: Requirements 28.1, 28.2, 28.3
    """
    # Ensure lists match
    recipe_count = min(recipe_count, len(calories_list))
    calories_list = calories_list[:recipe_count]
    
    # Create test user
    import uuid
    user = User(username=f"user_{uuid.uuid4().hex[:8]}", password_hash="hash")
    db.add(user)
    db.commit()
    
    # Create recipes with nutrition
    meal_date = date(2024, 1, 15)
    expected_total_calories = 0
    
    for i, calories in enumerate(calories_list):
        recipe = Recipe(
            user_id=user.id,
            title=f"Recipe {i}",
            ingredients='["test"]',
            steps='["test"]'
        )
        db.add(recipe)
        db.commit()
        
        # Add nutrition
        nutrition_data = NutritionCreate(calories=calories)
        NutritionTracker.add_nutrition_facts(db, recipe.id, nutrition_data, user.id)
        
        # Add to meal plan
        meal_plan = MealPlan(
            user_id=user.id,
            recipe_id=recipe.id,
            meal_date=meal_date,
            meal_time='lunch'
        )
        db.add(meal_plan)
        
        expected_total_calories += calories
    
    db.commit()
    
    # Get nutrition summary
    summary = NutritionTracker.get_meal_plan_nutrition_summary(
        db, user.id, meal_date, meal_date
    )
    
    # Verify summation
    assert len(summary['daily_totals']) == 1
    actual_calories = summary['weekly_total']['calories']
    
    # Allow small floating point tolerance
    assert abs(actual_calories - expected_total_calories) < 0.1


# ============================================================================
# Property 46: Missing nutrition exclusion
# Feature: recipe-saver-enhancements, Property 46: Missing nutrition exclusion
# ============================================================================

@given(
    recipes_with_nutrition=st.integers(min_value=0, max_value=3),
    recipes_without_nutrition=st.integers(min_value=1, max_value=3)
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_missing_nutrition_exclusion_property(db, recipes_with_nutrition, recipes_without_nutrition):
    """
    Property 46: Missing nutrition exclusion
    For any meal plan nutrition summary, recipes without nutrition facts should be
    excluded from calculations and counted separately.
    Validates: Requirements 28.4
    """
    # Create test user
    import uuid
    user = User(username=f"user_{uuid.uuid4().hex[:8]}", password_hash="hash")
    db.add(user)
    db.commit()
    
    meal_date = date(2024, 1, 16)
    
    # Create recipes WITH nutrition
    for i in range(recipes_with_nutrition):
        recipe = Recipe(
            user_id=user.id,
            title=f"Recipe with nutrition {i}",
            ingredients='["test"]',
            steps='["test"]'
        )
        db.add(recipe)
        db.commit()
        
        # Add nutrition
        nutrition_data = NutritionCreate(calories=300.0)
        NutritionTracker.add_nutrition_facts(db, recipe.id, nutrition_data, user.id)
        
        # Add to meal plan
        meal_plan = MealPlan(
            user_id=user.id,
            recipe_id=recipe.id,
            meal_date=meal_date,
            meal_time='breakfast'
        )
        db.add(meal_plan)
    
    # Create recipes WITHOUT nutrition
    for i in range(recipes_without_nutrition):
        recipe = Recipe(
            user_id=user.id,
            title=f"Recipe without nutrition {i}",
            ingredients='["test"]',
            steps='["test"]'
        )
        db.add(recipe)
        db.commit()
        
        # Add to meal plan WITHOUT adding nutrition
        meal_plan = MealPlan(
            user_id=user.id,
            recipe_id=recipe.id,
            meal_date=meal_date,
            meal_time='lunch'
        )
        db.add(meal_plan)
    
    db.commit()
    
    # Get nutrition summary
    summary = NutritionTracker.get_meal_plan_nutrition_summary(
        db, user.id, meal_date, meal_date
    )
    
    # Verify missing nutrition count
    assert summary['missing_nutrition_count'] == recipes_without_nutrition
    
    # Verify only recipes with nutrition are included in totals
    expected_calories = recipes_with_nutrition * 300.0
    actual_calories = summary['weekly_total']['calories']
    assert abs(actual_calories - expected_calories) < 0.1
