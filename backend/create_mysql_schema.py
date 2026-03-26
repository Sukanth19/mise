#!/usr/bin/env python3
"""
MySQL Schema Creation Script

This script creates all tables, indexes, and constraints for the Recipe Saver application
in MySQL using SQLAlchemy ORM models.

Requirements: 2.1, 2.2, 2.3, 2.4, 3.9, 9.2
"""

import sys
import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import Base and all models to register them with Base.metadata
from app.database import Base
from app.models import (
    User, Recipe, RecipeRating, RecipeNote, Collection, CollectionRecipe,
    MealPlan, MealPlanTemplate, MealPlanTemplateItem, ShoppingList,
    ShoppingListItem, NutritionFacts, DietaryLabel, AllergenWarning,
    UserFollow, RecipeLike, RecipeComment
)


def create_mysql_schema(database_url: str) -> bool:
    """
    Create MySQL database schema with all tables, indexes, and constraints.
    
    Args:
        database_url: MySQL connection string (mysql+pymysql://user:pass@host:port/db)
        
    Returns:
        True if schema creation successful, False otherwise
    """
    try:
        logger.info(f"Connecting to MySQL database...")
        
        # Create engine with MySQL-specific configuration
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            echo=False
        )
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Successfully connected to MySQL")
        
        # Create all tables using Base.metadata
        logger.info("Creating tables from SQLAlchemy models...")
        Base.metadata.create_all(bind=engine)
        logger.info("All tables created successfully")
        
        # Add FULLTEXT indexes for search functionality
        logger.info("Creating FULLTEXT indexes for search...")
        with engine.connect() as conn:
            # Check if FULLTEXT index already exists
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM information_schema.statistics
                WHERE table_schema = DATABASE()
                AND table_name = 'recipes'
                AND index_name = 'idx_recipe_fulltext_search'
            """))
            index_exists = result.fetchone()[0] > 0
            
            if not index_exists:
                # Create FULLTEXT index on recipes(title, ingredients)
                conn.execute(text("""
                    CREATE FULLTEXT INDEX idx_recipe_fulltext_search
                    ON recipes(title, ingredients)
                """))
                conn.commit()
                logger.info("FULLTEXT index created on recipes(title, ingredients)")
            else:
                logger.info("FULLTEXT index already exists on recipes table")
        
        # Verify schema creation
        logger.info("\n" + "="*60)
        logger.info("SCHEMA VERIFICATION")
        logger.info("="*60)
        
        verify_schema(engine)
        
        logger.info("\n" + "="*60)
        logger.info("Schema creation completed successfully!")
        logger.info("="*60)
        
        engine.dispose()
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"Database error during schema creation: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during schema creation: {e}")
        return False


def verify_schema(engine) -> None:
    """
    Verify all tables, indexes, and foreign keys are created correctly.
    
    Args:
        engine: SQLAlchemy engine instance
    """
    inspector = inspect(engine)
    
    # Expected tables
    expected_tables = [
        'users', 'recipes', 'recipe_ratings', 'recipe_notes',
        'collections', 'collection_recipes', 'meal_plans',
        'meal_plan_templates', 'meal_plan_template_items',
        'shopping_lists', 'shopping_list_items', 'nutrition_facts',
        'dietary_labels', 'allergen_warnings', 'user_follows',
        'recipe_likes', 'recipe_comments'
    ]
    
    # Verify tables exist
    actual_tables = inspector.get_table_names()
    logger.info(f"\nTables created: {len(actual_tables)}")
    
    missing_tables = set(expected_tables) - set(actual_tables)
    if missing_tables:
        logger.error(f"Missing tables: {missing_tables}")
    else:
        logger.info("✓ All 17 expected tables exist")
        for table in sorted(actual_tables):
            logger.info(f"  - {table}")
    
    # Verify indexes for key tables
    logger.info("\nVerifying indexes...")
    verify_table_indexes(inspector, 'recipes', [
        'user_id', 'title', 'created_at', 'visibility',
        'idx_recipe_user_created', 'idx_recipe_fulltext_search'
    ])
    verify_table_indexes(inspector, 'users', ['username'])
    verify_table_indexes(inspector, 'collections', ['user_id', 'share_token'])
    verify_table_indexes(inspector, 'meal_plans', ['user_id', 'meal_date'])
    
    # Verify foreign keys for key tables
    logger.info("\nVerifying foreign keys...")
    verify_table_foreign_keys(inspector, 'recipes', ['user_id'])
    verify_table_foreign_keys(inspector, 'recipe_ratings', ['recipe_id', 'user_id'])
    verify_table_foreign_keys(inspector, 'collections', ['user_id'])
    verify_table_foreign_keys(inspector, 'collection_recipes', ['collection_id', 'recipe_id'])
    verify_table_foreign_keys(inspector, 'meal_plans', ['user_id', 'recipe_id'])
    verify_table_foreign_keys(inspector, 'shopping_list_items', ['shopping_list_id'])
    verify_table_foreign_keys(inspector, 'nutrition_facts', ['recipe_id'])


def verify_table_indexes(inspector, table_name: str, expected_indexes: list) -> None:
    """
    Verify indexes exist for a table.
    
    Args:
        inspector: SQLAlchemy inspector instance
        table_name: Name of the table to check
        expected_indexes: List of expected index names or column names
    """
    try:
        indexes = inspector.get_indexes(table_name)
        index_names = {idx['name'] for idx in indexes}
        index_columns = {col for idx in indexes for col in idx['column_names']}
        
        found_count = 0
        for expected in expected_indexes:
            if expected in index_names or expected in index_columns:
                found_count += 1
        
        logger.info(f"  {table_name}: {found_count}/{len(expected_indexes)} indexes verified")
        
    except Exception as e:
        logger.warning(f"  Could not verify indexes for {table_name}: {e}")


def verify_table_foreign_keys(inspector, table_name: str, expected_fk_columns: list) -> None:
    """
    Verify foreign keys exist for a table.
    
    Args:
        inspector: SQLAlchemy inspector instance
        table_name: Name of the table to check
        expected_fk_columns: List of expected foreign key column names
    """
    try:
        foreign_keys = inspector.get_foreign_keys(table_name)
        fk_columns = {fk['constrained_columns'][0] for fk in foreign_keys if fk['constrained_columns']}
        
        found_count = sum(1 for col in expected_fk_columns if col in fk_columns)
        logger.info(f"  {table_name}: {found_count}/{len(expected_fk_columns)} foreign keys verified")
        
    except Exception as e:
        logger.warning(f"  Could not verify foreign keys for {table_name}: {e}")


def validate_script_structure() -> bool:
    """
    Validate that the script is properly structured and all models are importable.
    This is a dry-run mode that doesn't require MySQL connection.
    
    Returns:
        True if validation successful, False otherwise
    """
    try:
        logger.info("Validating script structure (dry-run mode)...")
        
        # Verify all models are imported
        models = [
            User, Recipe, RecipeRating, RecipeNote, Collection, CollectionRecipe,
            MealPlan, MealPlanTemplate, MealPlanTemplateItem, ShoppingList,
            ShoppingListItem, NutritionFacts, DietaryLabel, AllergenWarning,
            UserFollow, RecipeLike, RecipeComment
        ]
        
        logger.info(f"✓ All {len(models)} models imported successfully")
        
        # Verify Base.metadata has all tables
        table_count = len(Base.metadata.tables)
        logger.info(f"✓ Base.metadata contains {table_count} tables")
        
        expected_tables = [
            'users', 'recipes', 'recipe_ratings', 'recipe_notes',
            'collections', 'collection_recipes', 'meal_plans',
            'meal_plan_templates', 'meal_plan_template_items',
            'shopping_lists', 'shopping_list_items', 'nutrition_facts',
            'dietary_labels', 'allergen_warnings', 'user_follows',
            'recipe_likes', 'recipe_comments'
        ]
        
        actual_table_names = set(Base.metadata.tables.keys())
        expected_table_names = set(expected_tables)
        
        if actual_table_names == expected_table_names:
            logger.info(f"✓ All {len(expected_tables)} expected tables registered")
        else:
            missing = expected_table_names - actual_table_names
            extra = actual_table_names - expected_table_names
            if missing:
                logger.error(f"✗ Missing tables: {missing}")
            if extra:
                logger.warning(f"⚠ Extra tables: {extra}")
            return False
        
        logger.info("\n✓ Script structure validation passed")
        return True
        
    except Exception as e:
        logger.error(f"✗ Validation failed: {e}")
        return False


def main():
    """Main entry point for schema creation script."""
    import os
    from dotenv import load_dotenv
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='MySQL Schema Creation Script')
    parser.add_argument('--dry-run', action='store_true',
                       help='Validate script structure without connecting to MySQL')
    parser.add_argument('--database-url', type=str,
                       help='MySQL connection string (overrides DATABASE_URL env var)')
    args = parser.parse_args()
    
    # Change to script directory to find .env file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Load environment variables
    load_dotenv()
    
    logger.info("MySQL Schema Creation Script")
    logger.info("="*60)
    
    # Dry-run mode
    if args.dry_run:
        logger.info("Running in DRY-RUN mode (no MySQL connection required)")
        logger.info("="*60 + "\n")
        success = validate_script_structure()
        if success:
            logger.info("\n✓ Dry-run validation completed successfully")
            sys.exit(0)
        else:
            logger.error("\n✗ Dry-run validation failed")
            sys.exit(1)
    
    # Normal mode - create schema
    database_url = args.database_url or os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://root:password@localhost:3306/recipe_saver'
    )
    
    logger.info(f"Database URL: {database_url.split('@')[1] if '@' in database_url else database_url}")
    logger.info("="*60 + "\n")
    
    # Create schema
    success = create_mysql_schema(database_url)
    
    if success:
        logger.info("\n✓ Schema creation completed successfully")
        sys.exit(0)
    else:
        logger.error("\n✗ Schema creation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
