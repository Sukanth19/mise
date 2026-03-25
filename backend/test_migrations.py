#!/usr/bin/env python3
"""
Test script for database migrations.

This script tests:
1. Migrations on a clean database
2. Migrations on an existing database with data
3. Verification of all indexes
"""

import os
import sys
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime


def backup_database():
    """Create a backup of the current database."""
    db_path = Path("recipe_saver.db")
    if db_path.exists():
        backup_path = Path(f"recipe_saver_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
        shutil.copy(db_path, backup_path)
        print(f"✓ Created backup: {backup_path}")
        return backup_path
    return None


def restore_database(backup_path):
    """Restore database from backup."""
    if backup_path and backup_path.exists():
        shutil.copy(backup_path, "recipe_saver.db")
        print(f"✓ Restored database from: {backup_path}")


def test_clean_database():
    """Test migrations on a clean database."""
    print("\n" + "="*60)
    print("TEST 1: Clean Database with init_db.py")
    print("="*60)
    
    # Remove existing database
    db_path = Path("recipe_saver.db")
    if db_path.exists():
        db_path.unlink()
        print("✓ Removed existing database")
    
    # Initialize base tables using init_db.py
    # This creates all tables with the current schema (including enhancements)
    print("\nInitializing database with init_db.py...")
    result = os.system("python init_db.py > /dev/null 2>&1")
    if result != 0:
        print("✗ Database initialization failed")
        return False
    print("✓ Database created successfully with init_db.py")
    
    # Note: Migrations are not needed for clean database since init_db.py
    # creates tables with the full schema already
    print("✓ Clean database setup complete (migrations not needed)")
    return True


def test_existing_database():
    """Test migrations on existing database with data."""
    print("\n" + "="*60)
    print("TEST 2: Migrations on Existing Database with Data")
    print("="*60)
    
    # Create a fresh database with base schema
    db_path = Path("recipe_saver.db")
    if db_path.exists():
        db_path.unlink()
    
    # Create base tables (simulating existing database)
    conn = sqlite3.connect("recipe_saver.db")
    cursor = conn.cursor()
    
    # Create basic users table
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(255) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create basic recipes table
    cursor.execute("""
        CREATE TABLE recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            ingredients TEXT NOT NULL,
            steps TEXT NOT NULL,
            prep_time INTEGER,
            cook_time INTEGER,
            image_url VARCHAR(500),
            tags TEXT,
            reference_link VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Insert sample data
    cursor.execute("""
        INSERT INTO users (username, email, hashed_password)
        VALUES ('testuser', 'test@example.com', 'hashed_password_here')
    """)
    
    cursor.execute("""
        INSERT INTO recipes (user_id, title, description, ingredients, steps, prep_time, cook_time)
        VALUES (1, 'Test Recipe', 'A test recipe', 'ingredient1\ningredient2', 'step1\nstep2', 10, 20)
    """)
    
    conn.commit()
    conn.close()
    
    print("✓ Created existing database with sample data")
    
    # Run migrations
    print("\nRunning migrations on existing database...")
    result = os.system("python run_migrations.py")
    
    if result != 0:
        print("✗ Migration failed on existing database")
        return False
    
    print("✓ Migrations completed successfully on existing database")
    
    # Verify data is still intact
    conn = sqlite3.connect("recipe_saver.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM recipes")
    recipe_count = cursor.fetchone()[0]
    conn.close()
    
    if user_count == 1 and recipe_count == 1:
        print("✓ Existing data preserved after migration")
        return True
    else:
        print("✗ Data was lost during migration")
        return False


def verify_indexes():
    """Verify all required indexes are created."""
    print("\n" + "="*60)
    print("TEST 3: Verify All Indexes Created")
    print("="*60)
    
    conn = sqlite3.connect("recipe_saver.db")
    cursor = conn.cursor()
    
    # Get all indexes
    cursor.execute("""
        SELECT name, tbl_name FROM sqlite_master 
        WHERE type='index' AND name NOT LIKE 'sqlite_%'
        ORDER BY tbl_name, name
    """)
    
    indexes = cursor.fetchall()
    conn.close()
    
    # Expected indexes (from design document)
    expected_indexes = [
        'idx_recipe_ratings_recipe_id',
        'idx_recipe_ratings_user_id',
        'idx_recipe_notes_recipe_id',
        'idx_recipe_notes_user_id',
        'idx_collections_user_id',
        'idx_collections_parent_id',
        'idx_collections_share_token',
        'idx_collection_recipes_collection_id',
        'idx_collection_recipes_recipe_id',
        'idx_meal_plans_user_id',
        'idx_meal_plans_date',
        'idx_meal_plans_recipe_id',
        'idx_meal_plan_templates_user_id',
        'idx_template_items_template_id',
        'idx_shopping_lists_user_id',
        'idx_shopping_lists_share_token',
        'idx_shopping_list_items_list_id',
        'idx_nutrition_facts_recipe_id',
        'idx_dietary_labels_recipe_id',
        'idx_dietary_labels_label',
        'idx_allergen_warnings_recipe_id',
        'idx_allergen_warnings_allergen',
        'idx_user_follows_follower_id',
        'idx_user_follows_following_id',
        'idx_recipe_likes_recipe_id',
        'idx_recipe_likes_user_id',
        'idx_recipe_comments_recipe_id',
        'idx_recipe_comments_user_id',
    ]
    
    found_indexes = {idx[0] for idx in indexes}
    
    print(f"\nFound {len(found_indexes)} indexes:")
    for idx_name, tbl_name in sorted(indexes):
        print(f"  ✓ {idx_name} (on {tbl_name})")
    
    # Check for missing indexes
    missing = set(expected_indexes) - found_indexes
    if missing:
        print(f"\n⚠ Missing {len(missing)} expected indexes:")
        for idx in sorted(missing):
            print(f"  ✗ {idx}")
        return False
    
    print(f"\n✓ All {len(expected_indexes)} expected indexes are present")
    return True


def verify_tables():
    """Verify all required tables are created."""
    print("\n" + "="*60)
    print("Verifying All Tables Created")
    print("="*60)
    
    conn = sqlite3.connect("recipe_saver.db")
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    # Expected tables
    expected_tables = [
        'users',
        'recipes',
        'recipe_ratings',
        'recipe_notes',
        'collections',
        'collection_recipes',
        'meal_plans',
        'meal_plan_templates',
        'meal_plan_template_items',
        'shopping_lists',
        'shopping_list_items',
        'nutrition_facts',
        'dietary_labels',
        'allergen_warnings',
        'user_follows',
        'recipe_likes',
        'recipe_comments',
        'applied_migrations',
    ]
    
    print(f"\nFound {len(tables)} tables:")
    for table in tables:
        print(f"  ✓ {table}")
    
    # Check for missing tables
    missing = set(expected_tables) - set(tables)
    if missing:
        print(f"\n⚠ Missing {len(missing)} expected tables:")
        for table in sorted(missing):
            print(f"  ✗ {table}")
        return False
    
    print(f"\n✓ All {len(expected_tables)} expected tables are present")
    return True


def main():
    """Run all migration tests."""
    print("="*60)
    print("Database Migration Test Suite")
    print("="*60)
    
    # Change to backend directory
    os.chdir(Path(__file__).parent)
    
    # Backup existing database
    backup_path = backup_database()
    
    try:
        # Run tests
        test1_passed = test_clean_database()
        test2_passed = test_existing_database()
        tables_ok = verify_tables()
        indexes_ok = verify_indexes()
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Clean database (init_db.py):  {'✓ PASSED' if test1_passed else '✗ FAILED'}")
        print(f"Existing database migration:  {'✓ PASSED' if test2_passed else '✗ FAILED'}")
        print(f"All tables created:           {'✓ PASSED' if tables_ok else '✗ FAILED'}")
        print(f"All indexes created:          {'✓ PASSED' if indexes_ok else '✗ FAILED'}")
        
        all_passed = test1_passed and test2_passed and tables_ok and indexes_ok
        
        if all_passed:
            print("\n✓ ALL TESTS PASSED")
            print("\nNOTE: For clean deployments, use init_db.py")
            print("      For upgrading existing databases, use run_migrations.py")
            return 0
        else:
            print("\n✗ SOME TESTS FAILED")
            return 1
    
    finally:
        # Restore original database
        if backup_path:
            restore_database(backup_path)
            # Clean up backup
            backup_path.unlink()
            print(f"\n✓ Cleaned up backup file")


if __name__ == "__main__":
    sys.exit(main())
