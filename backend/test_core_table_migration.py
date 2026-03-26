#!/usr/bin/env python3
"""
Test script for core table migration logic.

Tests the migration of users, recipes, nutrition_facts, dietary_labels, and allergen_warnings tables.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from migrate_to_mysql import DatabaseMigrator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_test_source_db():
    """Create a test source database with sample data."""
    # Use SQLite for source
    source_url = "sqlite:///test_source.db"
    engine = create_engine(source_url)
    
    # Create tables
    with engine.connect() as conn:
        # Users table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Recipes table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title VARCHAR(500) NOT NULL,
                image_url VARCHAR(1000),
                ingredients TEXT NOT NULL,
                steps TEXT NOT NULL,
                tags TEXT,
                reference_link VARCHAR(1000),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_favorite BOOLEAN DEFAULT 0,
                visibility VARCHAR(20) DEFAULT 'private',
                servings INTEGER DEFAULT 1,
                source_recipe_id INTEGER,
                source_author_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """))
        
        # Nutrition facts table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS nutrition_facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER UNIQUE NOT NULL,
                calories DECIMAL(10, 2),
                protein_g DECIMAL(10, 2),
                carbs_g DECIMAL(10, 2),
                fat_g DECIMAL(10, 2),
                fiber_g DECIMAL(10, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
            )
        """))
        
        # Dietary labels table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS dietary_labels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                label VARCHAR(50) NOT NULL,
                FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
            )
        """))
        
        # Allergen warnings table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS allergen_warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                allergen VARCHAR(50) NOT NULL,
                FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
            )
        """))
        
        conn.commit()
        
        # Insert sample data
        conn.execute(text("""
            INSERT INTO users (username, password_hash) VALUES
            ('user1', 'hash1'),
            ('user2', 'hash2'),
            ('user3', 'hash3')
        """))
        
        conn.execute(text("""
            INSERT INTO recipes (user_id, title, ingredients, steps, visibility, servings) VALUES
            (1, 'Recipe 1', '["ingredient1", "ingredient2"]', '["step1", "step2"]', 'public', 4),
            (1, 'Recipe 2', '["ingredient3"]', '["step3"]', 'private', 2),
            (2, 'Recipe 3', '["ingredient4", "ingredient5"]', '["step4"]', 'public', 6),
            (3, 'Recipe 4', '["ingredient6"]', '["step5", "step6"]', 'unlisted', 1)
        """))
        
        conn.execute(text("""
            INSERT INTO nutrition_facts (recipe_id, calories, protein_g, carbs_g, fat_g, fiber_g) VALUES
            (1, 350.5, 25.0, 40.0, 10.5, 5.0),
            (2, 200.0, 15.0, 20.0, 8.0, 3.0),
            (3, 450.0, 30.0, 50.0, 15.0, 7.0)
        """))
        
        conn.execute(text("""
            INSERT INTO dietary_labels (recipe_id, label) VALUES
            (1, 'vegan'),
            (1, 'gluten-free'),
            (2, 'vegetarian'),
            (3, 'keto'),
            (4, 'paleo')
        """))
        
        conn.execute(text("""
            INSERT INTO allergen_warnings (recipe_id, allergen) VALUES
            (1, 'nuts'),
            (2, 'dairy'),
            (3, 'soy'),
            (3, 'wheat'),
            (4, 'fish')
        """))
        
        conn.commit()
    
    logger.info("✓ Created test source database with sample data")
    return source_url


def setup_test_target_db():
    """Create a test target MySQL-compatible database."""
    # For testing, we'll use SQLite with MySQL-like schema
    target_url = "sqlite:///test_target.db"
    engine = create_engine(target_url)
    
    # Create tables (same schema as source)
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title VARCHAR(500) NOT NULL,
                image_url VARCHAR(1000),
                ingredients TEXT NOT NULL,
                steps TEXT NOT NULL,
                tags TEXT,
                reference_link VARCHAR(1000),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_favorite BOOLEAN DEFAULT 0,
                visibility VARCHAR(20) DEFAULT 'private',
                servings INTEGER DEFAULT 1,
                source_recipe_id INTEGER,
                source_author_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """))
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS nutrition_facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER UNIQUE NOT NULL,
                calories DECIMAL(10, 2),
                protein_g DECIMAL(10, 2),
                carbs_g DECIMAL(10, 2),
                fat_g DECIMAL(10, 2),
                fiber_g DECIMAL(10, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
            )
        """))
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS dietary_labels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                label VARCHAR(50) NOT NULL,
                FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
            )
        """))
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS allergen_warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                allergen VARCHAR(50) NOT NULL,
                FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
            )
        """))
        
        conn.commit()
    
    logger.info("✓ Created test target database")
    return target_url


def verify_migration(source_url, target_url):
    """Verify that migration was successful."""
    source_engine = create_engine(source_url)
    target_engine = create_engine(target_url)
    
    errors = []
    
    # Check record counts
    tables = ['users', 'recipes', 'nutrition_facts', 'dietary_labels', 'allergen_warnings']
    
    for table in tables:
        with source_engine.connect() as source_conn:
            source_count = source_conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
        
        with target_engine.connect() as target_conn:
            target_count = target_conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
        
        if source_count == target_count:
            logger.info(f"✓ {table}: {target_count}/{source_count} records migrated")
        else:
            error_msg = f"✗ {table}: {target_count}/{source_count} records (mismatch!)"
            logger.error(error_msg)
            errors.append(error_msg)
    
    # Verify foreign key relationships are preserved
    with target_engine.connect() as conn:
        # Check that all recipes have valid user_ids
        result = conn.execute(text("""
            SELECT COUNT(*) FROM recipes r
            LEFT JOIN users u ON r.user_id = u.id
            WHERE u.id IS NULL
        """)).scalar()
        
        if result == 0:
            logger.info("✓ All recipe foreign keys (user_id) are valid")
        else:
            error_msg = f"✗ Found {result} recipes with invalid user_id"
            logger.error(error_msg)
            errors.append(error_msg)
        
        # Check that all nutrition_facts have valid recipe_ids
        result = conn.execute(text("""
            SELECT COUNT(*) FROM nutrition_facts nf
            LEFT JOIN recipes r ON nf.recipe_id = r.id
            WHERE r.id IS NULL
        """)).scalar()
        
        if result == 0:
            logger.info("✓ All nutrition_facts foreign keys (recipe_id) are valid")
        else:
            error_msg = f"✗ Found {result} nutrition_facts with invalid recipe_id"
            logger.error(error_msg)
            errors.append(error_msg)
        
        # Check that all dietary_labels have valid recipe_ids
        result = conn.execute(text("""
            SELECT COUNT(*) FROM dietary_labels dl
            LEFT JOIN recipes r ON dl.recipe_id = r.id
            WHERE r.id IS NULL
        """)).scalar()
        
        if result == 0:
            logger.info("✓ All dietary_labels foreign keys (recipe_id) are valid")
        else:
            error_msg = f"✗ Found {result} dietary_labels with invalid recipe_id"
            logger.error(error_msg)
            errors.append(error_msg)
        
        # Check that all allergen_warnings have valid recipe_ids
        result = conn.execute(text("""
            SELECT COUNT(*) FROM allergen_warnings aw
            LEFT JOIN recipes r ON aw.recipe_id = r.id
            WHERE r.id IS NULL
        """)).scalar()
        
        if result == 0:
            logger.info("✓ All allergen_warnings foreign keys (recipe_id) are valid")
        else:
            error_msg = f"✗ Found {result} allergen_warnings with invalid recipe_id"
            logger.error(error_msg)
            errors.append(error_msg)
    
    return len(errors) == 0, errors


def cleanup():
    """Remove test databases."""
    for db_file in ['test_source.db', 'test_target.db']:
        if os.path.exists(db_file):
            os.remove(db_file)
            logger.info(f"✓ Cleaned up {db_file}")


def main():
    """Run the migration test."""
    logger.info("=" * 80)
    logger.info("Core Table Migration Test")
    logger.info("=" * 80)
    
    try:
        # Setup
        source_url = setup_test_source_db()
        target_url = setup_test_target_db()
        
        # Run migration
        logger.info("\n" + "=" * 80)
        logger.info("Running Migration")
        logger.info("=" * 80)
        
        migrator = DatabaseMigrator(
            source_url=source_url,
            target_url=target_url,
            dry_run=False,
            incremental=False
        )
        
        migrator.connect()
        
        if not migrator.validate_connections():
            logger.error("Connection validation failed")
            return 1
        
        migrator.migrate_all()
        migrator.disconnect()
        
        # Verify
        logger.info("\n" + "=" * 80)
        logger.info("Verifying Migration")
        logger.info("=" * 80)
        
        success, errors = verify_migration(source_url, target_url)
        
        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("Test Summary")
        logger.info("=" * 80)
        
        if success:
            logger.info("✓ ALL TESTS PASSED")
            logger.info("Core table migration is working correctly!")
            return 0
        else:
            logger.error("✗ TESTS FAILED")
            for error in errors:
                logger.error(f"  - {error}")
            return 1
    
    except Exception as e:
        logger.error(f"Test failed with exception: {e}", exc_info=True)
        return 1
    
    finally:
        cleanup()


if __name__ == "__main__":
    sys.exit(main())
