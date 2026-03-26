"""
Quick test to verify nutrition service works with MongoDB.
"""
import asyncio
from datetime import datetime
from bson import ObjectId
from app.database import mongodb
from app.repositories.recipe_repository import RecipeRepository
from app.repositories.meal_plan_repository import MealPlanRepository
from app.services.nutrition_service import NutritionTracker
from app.schemas import NutritionCreate, NutritionUpdate


async def test_nutrition_service():
    """Test nutrition service with MongoDB."""
    print("Connecting to MongoDB...")
    await mongodb.connect("mongodb://localhost:27017", "recipe_saver_test")
    
    try:
        db = await mongodb.get_database()
        
        # Clean up test data
        await db.recipes.delete_many({})
        await db.users.delete_many({})
        
        # Create test user
        user_result = await db.users.insert_one({
            "username": "testuser",
            "password_hash": "hashed",
            "created_at": datetime.utcnow()
        })
        user_id = str(user_result.inserted_id)
        print(f"✓ Created test user: {user_id}")
        
        # Create test recipe
        recipe_result = await db.recipes.insert_one({
            "user_id": ObjectId(user_id),
            "title": "Test Recipe",
            "ingredients": ["ingredient1", "ingredient2"],
            "steps": ["step1", "step2"],
            "servings": 4,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        recipe_id = str(recipe_result.inserted_id)
        print(f"✓ Created test recipe: {recipe_id}")
        
        # Initialize repositories and service
        recipe_repository = RecipeRepository(db)
        meal_plan_repository = MealPlanRepository(db)
        nutrition_tracker = NutritionTracker(recipe_repository, meal_plan_repository)
        
        # Test 1: Add nutrition facts
        print("\nTest 1: Add nutrition facts")
        nutrition_data = NutritionCreate(
            calories=500.0,
            protein_g=25.0,
            carbs_g=60.0,
            fat_g=15.0,
            fiber_g=8.0
        )
        recipe = await nutrition_tracker.add_nutrition_facts(recipe_id, nutrition_data, user_id)
        assert recipe is not None, "Failed to add nutrition facts"
        assert recipe.get("nutrition_facts") is not None, "Nutrition facts not embedded"
        assert recipe["nutrition_facts"]["calories"] == 500.0
        print("✓ Nutrition facts added successfully")
        
        # Test 2: Get nutrition facts
        print("\nTest 2: Get nutrition facts")
        nutrition = await nutrition_tracker.get_nutrition_facts(recipe_id)
        assert nutrition is not None, "Failed to get nutrition facts"
        assert nutrition["calories"] == 500.0
        assert nutrition["protein_g"] == 25.0
        print("✓ Nutrition facts retrieved successfully")
        
        # Test 3: Update nutrition facts
        print("\nTest 3: Update nutrition facts")
        update_data = NutritionUpdate(calories=600.0, carbs_g=70.0)
        recipe = await nutrition_tracker.update_nutrition_facts(recipe_id, update_data, user_id)
        assert recipe is not None, "Failed to update nutrition facts"
        assert recipe["nutrition_facts"]["calories"] == 600.0
        assert recipe["nutrition_facts"]["carbs_g"] == 70.0
        assert recipe["nutrition_facts"]["protein_g"] == 25.0  # Unchanged
        print("✓ Nutrition facts updated successfully")
        
        # Test 4: Add dietary labels
        print("\nTest 4: Add dietary labels")
        labels = await nutrition_tracker.add_dietary_labels(recipe_id, ["vegan", "gluten-free"], user_id)
        assert labels is not None, "Failed to add dietary labels"
        assert len(labels) == 2
        assert "vegan" in labels
        print("✓ Dietary labels added successfully")
        
        # Test 5: Add allergen warnings
        print("\nTest 5: Add allergen warnings")
        allergens = await nutrition_tracker.add_allergen_warnings(recipe_id, ["nuts", "soy"], user_id)
        assert allergens is not None, "Failed to add allergen warnings"
        assert len(allergens) == 2
        assert "nuts" in allergens
        print("✓ Allergen warnings added successfully")
        
        # Test 6: Verify embedded data
        print("\nTest 6: Verify embedded data in recipe")
        recipe = await recipe_repository.find_by_id(recipe_id)
        assert recipe["nutrition_facts"]["calories"] == 600.0
        assert "vegan" in recipe["dietary_labels"]
        assert "nuts" in recipe["allergen_warnings"]
        print("✓ All data properly embedded in recipe document")
        
        # Test 7: Calculate per serving
        print("\nTest 7: Calculate per serving")
        per_serving = nutrition_tracker.calculate_per_serving(recipe["nutrition_facts"], 4)
        assert per_serving["calories"] == 150.0  # 600 / 4
        assert per_serving["protein_g"] == 6.25  # 25 / 4
        print("✓ Per-serving calculation correct")
        
        print("\n" + "="*50)
        print("All tests passed! ✓")
        print("="*50)
        
    finally:
        # Clean up
        await db.recipes.delete_many({})
        await db.users.delete_many({})
        await mongodb.disconnect()
        print("\nCleaned up test data and disconnected")


if __name__ == "__main__":
    asyncio.run(test_nutrition_service())
