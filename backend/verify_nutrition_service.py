#!/usr/bin/env python3
"""Quick verification script for nutrition service."""

import sys
sys.path.insert(0, '.')

from app.database import SessionLocal, engine, Base
from app.models import User, Recipe, NutritionFacts
from app.schemas import NutritionCreate
from app.services.nutrition_service import NutritionTracker
import json

# Create tables
Base.metadata.create_all(bind=engine)

# Create a test session
db = SessionLocal()

try:
    # Clean up any existing test data
    db.query(NutritionFacts).delete()
    db.query(Recipe).delete()
    db.query(User).delete()
    db.commit()
    
    # Create test user
    user = User(username="testuser", password_hash="hashed")
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"✓ Created test user: {user.id}")
    
    # Create test recipe
    recipe = Recipe(
        user_id=user.id,
        title="Test Recipe",
        ingredients=json.dumps(["ingredient1", "ingredient2"]),
        steps=json.dumps(["step1", "step2"]),
        servings=4
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    print(f"✓ Created test recipe: {recipe.id}")
    
    # Test 1: Add nutrition facts
    nutrition_data = NutritionCreate(
        calories=800.0,
        protein_g=40.0,
        carbs_g=100.0,
        fat_g=20.0,
        fiber_g=12.0
    )
    nutrition = NutritionTracker.add_nutrition_facts(db, recipe.id, nutrition_data, user.id)
    assert nutrition is not None
    assert float(nutrition.calories) == 800.0
    print("✓ Test 1 passed: Add nutrition facts")
    
    # Test 2: Get nutrition facts
    retrieved = NutritionTracker.get_nutrition_facts(db, recipe.id)
    assert retrieved is not None
    assert float(retrieved.calories) == 800.0
    print("✓ Test 2 passed: Get nutrition facts")
    
    # Test 3: Calculate per serving
    per_serving = NutritionTracker.calculate_per_serving(nutrition, 4)
    assert per_serving['calories'] == 200.0
    assert per_serving['protein_g'] == 10.0
    print("✓ Test 3 passed: Calculate per serving")
    
    # Test 4: Update nutrition facts
    update_data = NutritionCreate(calories=900.0, protein_g=45.0)
    updated = NutritionTracker.update_nutrition_facts(db, recipe.id, update_data, user.id)
    assert updated is not None
    assert float(updated.calories) == 900.0
    print("✓ Test 4 passed: Update nutrition facts")
    
    # Test 5: Add dietary labels
    labels = ['vegan', 'gluten-free']
    result = NutritionTracker.add_dietary_labels(db, recipe.id, labels, user.id)
    assert result == labels
    print("✓ Test 5 passed: Add dietary labels")
    
    # Test 6: Add allergen warnings
    allergens = ['nuts', 'soy']
    result = NutritionTracker.add_allergen_warnings(db, recipe.id, allergens, user.id)
    assert result == allergens
    print("✓ Test 6 passed: Add allergen warnings")
    
    # Test 7: Validate negative values
    negative_data = NutritionCreate(calories=-100.0)
    result = NutritionTracker.add_nutrition_facts(db, recipe.id, negative_data, user.id)
    assert result is None
    print("✓ Test 7 passed: Reject negative values")
    
    print("\n✅ All nutrition service tests passed!")
    
finally:
    db.close()
