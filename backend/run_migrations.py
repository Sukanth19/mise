#!/usr/bin/env python3
"""
Database migration runner for Recipe Saver Enhancements.

This script automatically detects the database type (SQLite or MySQL)
and applies all pending migrations in order.
"""

import os
import sys
from pathlib import Path
from app.config import settings
from app.database import engine
from sqlalchemy import text


def get_migration_files(db_type: str) -> list[Path]:
    """Get list of migration files for the specified database type."""
    migrations_dir = Path(__file__).parent / "migrations"
    
    # Get all .sql files and sort them
    migration_files = sorted(migrations_dir.glob("*.sql"))
    return migration_files


def create_migrations_table():
    """Create a table to track applied migrations."""
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS applied_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                migration_name VARCHAR(255) NOT NULL UNIQUE,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()


def get_applied_migrations() -> set[str]:
    """Get set of already applied migration names."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT migration_name FROM applied_migrations"))
        return {row[0] for row in result}


def mark_migration_applied(migration_name: str):
    """Mark a migration as applied."""
    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO applied_migrations (migration_name) VALUES (:name)"),
            {"name": migration_name}
        )
        conn.commit()


def apply_migration(migration_file: Path, db_type: str):
    """Apply a single migration file."""
    migration_name = migration_file.name
    
    print(f"Applying migration: {migration_name}")
    
    # Read the migration SQL
    with open(migration_file, 'r') as f:
        sql = f.read()
    
    # Split by semicolons and execute each statement
    statements = [s.strip() for s in sql.split(';') if s.strip()]
    
    # Execute each statement in its own transaction for SQLite compatibility
    for statement in statements:
        # Skip comments
        if statement.startswith('--'):
            continue
        try:
            with engine.connect() as conn:
                conn.execute(text(statement))
                conn.commit()
        except Exception as e:
            print(f"Error executing statement: {statement[:100]}...")
            raise e
    
    # Mark as applied
    mark_migration_applied(migration_name)
    print(f"✓ Applied: {migration_name}")


def main():
    """Main migration runner."""
    # Detect database type
    db_url = settings.database_url
    if db_url.startswith("sqlite"):
        db_type = "sqlite"
        print("Detected database: SQLite")
    elif db_url.startswith("mysql"):
        db_type = "mysql"
        print("Detected database: MySQL")
    else:
        print(f"Unsupported database type: {db_url}")
        sys.exit(1)
    
    # Create migrations tracking table
    print("\nInitializing migrations tracking...")
    create_migrations_table()
    
    # Get applied migrations
    applied = get_applied_migrations()
    print(f"Already applied: {len(applied)} migrations")
    
    # Get migration files
    migration_files = get_migration_files(db_type)
    print(f"Found: {len(migration_files)} migration files")
    
    # Apply pending migrations
    pending = [f for f in migration_files if f.name not in applied]
    
    if not pending:
        print("\n✓ All migrations are up to date!")
        return
    
    print(f"\nApplying {len(pending)} pending migrations...\n")
    
    for migration_file in pending:
        try:
            apply_migration(migration_file, db_type)
        except Exception as e:
            print(f"\n✗ Migration failed: {migration_file.name}")
            print(f"Error: {e}")
            sys.exit(1)
    
    print(f"\n✓ Successfully applied {len(pending)} migrations!")


if __name__ == "__main__":
    main()
