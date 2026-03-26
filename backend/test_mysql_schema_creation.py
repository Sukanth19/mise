"""
Test MySQL Schema Creation Script

This test verifies that the create_mysql_schema.py script is properly structured
and can create the MySQL schema.
"""

import pytest
import subprocess
import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_dry_run_validation():
    """
    Test that the schema creation script passes dry-run validation.
    
    This test verifies:
    - All 17 models can be imported
    - All tables are registered with SQLAlchemy
    - Script structure is valid
    """
    # Set required environment variables
    env = os.environ.copy()
    env['DATABASE_URL'] = 'sqlite:///./test.db'
    env['SECRET_KEY'] = 'test-secret-key'
    env['PYTHONPATH'] = f"{os.path.join(os.path.dirname(__file__), 'venv', 'lib', 'python3.14', 'site-packages')}:{os.path.dirname(__file__)}"
    
    # Run the script in dry-run mode
    result = subprocess.run(
        ['/bin/python3', 'create_mysql_schema.py', '--dry-run'],
        cwd=os.path.dirname(__file__),
        env=env,
        capture_output=True,
        text=True
    )
    
    # Check that the script succeeded
    assert result.returncode == 0, f"Script failed with output:\n{result.stdout}\n{result.stderr}"
    
    # Combine stdout and stderr for checking (logging goes to stderr)
    output = result.stdout + result.stderr
    
    # Verify expected output
    assert "✓ All 17 models imported successfully" in output
    assert "✓ Base.metadata contains 17 tables" in output
    assert "✓ All 17 expected tables registered" in output
    assert "✓ Script structure validation passed" in output
    assert "✓ Dry-run validation completed successfully" in output


def test_script_imports():
    """
    Test that all required modules can be imported.
    """
    from app.database import Base
    from app.models import (
        User, Recipe, RecipeRating, RecipeNote, Collection, CollectionRecipe,
        MealPlan, MealPlanTemplate, MealPlanTemplateItem, ShoppingList,
        ShoppingListItem, NutritionFacts, DietaryLabel, AllergenWarning,
        UserFollow, RecipeLike, RecipeComment
    )
    
    # Verify all models are registered
    assert len(Base.metadata.tables) == 17
    
    # Verify expected tables exist
    expected_tables = {
        'users', 'recipes', 'recipe_ratings', 'recipe_notes',
        'collections', 'collection_recipes', 'meal_plans',
        'meal_plan_templates', 'meal_plan_template_items',
        'shopping_lists', 'shopping_list_items', 'nutrition_facts',
        'dietary_labels', 'allergen_warnings', 'user_follows',
        'recipe_likes', 'recipe_comments'
    }
    
    actual_tables = set(Base.metadata.tables.keys())
    assert actual_tables == expected_tables


def test_script_has_fulltext_index_logic():
    """
    Test that the script contains logic for creating FULLTEXT indexes.
    """
    script_path = os.path.join(os.path.dirname(__file__), 'create_mysql_schema.py')
    
    with open(script_path, 'r') as f:
        content = f.read()
    
    # Verify FULLTEXT index creation logic exists
    assert 'CREATE FULLTEXT INDEX' in content
    assert 'idx_recipe_fulltext_search' in content
    assert 'recipes(title, ingredients)' in content


def test_script_has_verification_logic():
    """
    Test that the script contains schema verification logic.
    """
    script_path = os.path.join(os.path.dirname(__file__), 'create_mysql_schema.py')
    
    with open(script_path, 'r') as f:
        content = f.read()
    
    # Verify schema verification logic exists
    assert 'def verify_schema' in content
    assert 'verify_table_indexes' in content
    assert 'verify_table_foreign_keys' in content
    assert 'inspector.get_table_names()' in content
    assert 'inspector.get_indexes' in content
    assert 'inspector.get_foreign_keys' in content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
