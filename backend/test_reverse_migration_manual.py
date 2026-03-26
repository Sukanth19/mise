#!/usr/bin/env python3
"""
Manual test script to verify reverse migration functionality.
This script creates test data, performs a round-trip migration, and verifies data integrity.
"""

import os
import sys
import tempfile
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set up environment
os.environ["DATABASE_URL"] = "sqlite:///./test_migration.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"

# Import required modules
from migrate_to_mysql import DatabaseMigrator
from migrate_from_mysql import ReverseDatabaseMigrator
from app.database import Base
from app.models import User, Recipe, NutritionFacts

def test_reverse_migration_round_trip():
    """Test that data survives a round-trip migration (MySQL → SQLite → MySQL)."""
    
    print("=" * 80)
    print("Testing Reverse Migration Round Trip")
    print("=" * 80)
    
    # Create temporary database files
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as mysql_file:
        mysql_path = mysql_file.name
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as intermediate_file:
        intermediate_path = intermediate_file.name
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as final_file:
        final_path = final_file.name
    
    mysql_url = f"sqlite:///{mysql_path}"
    intermediate_url = f"sqlite:///{intermediate_path}"
    final_mysql_url = f"sqlite:///{final_path}"
    
    try:
        # Step 1: Create initial MySQL database with test data
        print("\n[Step 1] Creating initial database with test data...")
        mysql_engine = create_engine(mysql_url)
        Base.metadata.create_all(bind=mysql_engine)
        MySQLSession = sessionmaker(bind=mysql_engine)
        mysql_session = MySQLSession()
        
        # Create user
        user = User(
            username="testuser",
            password_hash="test_hash_123"
        )
        mysql_session.add(user)
        mysql_session.flush()
        
        # Create recipe
        recipe = Recipe(
            user_id=user.id,
            title="Test Recipe",
            ingredients=json.dumps(["ingredient1", "ingredient2", "ingredient3"]),
            steps=json.dumps(["step1", "step2"]),
            tags=json.dumps(["tag1", "tag2"]),
            reference_link="https://example.com/recipe",
            is_favorite=True,
            visibility="public",
            servings=4
        )
        mysql_session.add(recipe)
        mysql_session.flush()
        
        # Add nutrition facts
        nutrition = NutritionFacts(
            recipe_id=recipe.id,
            calories=500.0,
            protein_g=20.0,
            carbs_g=50.0,
            fat_g=15.0,
            fiber_g=5.0
        )
        mysql_session.add(nutrition)
        mysql_session.commit()
        
        # Store original data
        original_username = user.username
        original_title = recipe.title
        original_ingredients = json.loads(recipe.ingredients)
        original_servings = recipe.servings
        original_calories = nutrition.calories
        
        print(f"✓ Created user: {original_username}")
        print(f"✓ Created recipe: {original_title}")
        print(f"✓ Added nutrition facts: {original_calories} calories")
        
        mysql_session.close()
        mysql_engine.dispose()
        
        # Step 2: Reverse migrate from MySQL to SQLite
        print("\n[Step 2] Reverse migrating from MySQL to SQLite...")
        intermediate_engine = create_engine(intermediate_url)
        Base.metadata.create_all(bind=intermediate_engine)
        intermediate_engine.dispose()
        
        reverse_migrator = ReverseDatabaseMigrator(
            source_url=mysql_url,
            target_url=intermediate_url,
            dry_run=False,
            incremental=False
        )
        reverse_migrator.connect()
        reverse_migrator.migrate_all()
        reverse_migrator.disconnect()
        
        print("✓ Reverse migration completed")
        
        # Step 3: Forward migrate from SQLite back to MySQL
        print("\n[Step 3] Forward migrating from SQLite back to MySQL...")
        final_mysql_engine = create_engine(final_mysql_url)
        Base.metadata.create_all(bind=final_mysql_engine)
        final_mysql_engine.dispose()
        
        forward_migrator = DatabaseMigrator(
            source_url=intermediate_url,
            target_url=final_mysql_url,
            dry_run=False,
            incremental=False
        )
        forward_migrator.connect()
        forward_migrator.migrate_all()
        forward_migrator.disconnect()
        
        print("✓ Forward migration completed")
        
        # Step 4: Verify data equivalence
        print("\n[Step 4] Verifying data integrity after round trip...")
        FinalSession = sessionmaker(bind=create_engine(final_mysql_url))
        final_session = FinalSession()
        
        # Find migrated user
        final_user = final_session.query(User).filter(User.username == original_username).first()
        assert final_user is not None, "User should exist after round trip"
        assert final_user.username == original_username, "Username should be preserved"
        print(f"✓ User preserved: {final_user.username}")
        
        # Find migrated recipe
        final_recipe = final_session.query(Recipe).filter(Recipe.title == original_title).first()
        assert final_recipe is not None, "Recipe should exist after round trip"
        assert final_recipe.title == original_title, "Title should be preserved"
        assert json.loads(final_recipe.ingredients) == original_ingredients, "Ingredients should be preserved"
        assert final_recipe.servings == original_servings, "Servings should be preserved"
        print(f"✓ Recipe preserved: {final_recipe.title}")
        
        # Verify nutrition facts
        final_nutrition = final_session.query(NutritionFacts).filter(
            NutritionFacts.recipe_id == final_recipe.id
        ).first()
        assert final_nutrition is not None, "Nutrition facts should exist after round trip"
        assert final_nutrition.calories == original_calories, "Calories should be preserved"
        print(f"✓ Nutrition facts preserved: {final_nutrition.calories} calories")
        
        final_session.close()
        
        print("\n" + "=" * 80)
        print("✓ ALL TESTS PASSED - Round trip migration successful!")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up test databases
        try:
            os.unlink(mysql_path)
            os.unlink(intermediate_path)
            os.unlink(final_path)
        except:
            pass

if __name__ == '__main__':
    success = test_reverse_migration_round_trip()
    sys.exit(0 if success else 1)
