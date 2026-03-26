# MySQL Schema Setup Guide

This guide explains how to create the MySQL database schema for the Recipe Saver application.

## Prerequisites

1. MySQL server installed and running (local or cloud-hosted)
2. Python dependencies installed (`pip install -r requirements.txt`)
3. MySQL database created (e.g., `recipe_saver`)
4. MySQL user with appropriate permissions

## Quick Start

### Option 1: Using Environment Variables

1. Set the DATABASE_URL environment variable:
```bash
export DATABASE_URL="mysql+pymysql://user:password@host:port/database"
export SECRET_KEY="your-secret-key"
```

2. Run the schema creation script:
```bash
python create_mysql_schema.py
```

### Option 2: Using Command Line Arguments

```bash
python create_mysql_schema.py --database-url "mysql+pymysql://user:password@host:port/database"
```

### Option 3: Using .env File

1. Update the `.env` file in the backend directory:
```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/recipe_saver
SECRET_KEY=your-secret-key-here
```

2. Run the schema creation script:
```bash
python create_mysql_schema.py
```

## Dry-Run Mode

To validate the script structure without connecting to MySQL:

```bash
python create_mysql_schema.py --dry-run
```

This will:
- Verify all 17 models are importable
- Verify all tables are registered with SQLAlchemy
- Validate the script structure

## What the Script Does

The `create_mysql_schema.py` script performs the following operations:

### 1. Creates All Tables (Subtask 3.1)

Creates 17 tables using SQLAlchemy's `Base.metadata.create_all()`:

- users
- recipes
- recipe_ratings
- recipe_notes
- collections
- collection_recipes
- meal_plans
- meal_plan_templates
- meal_plan_template_items
- shopping_lists
- shopping_list_items
- nutrition_facts
- dietary_labels
- allergen_warnings
- user_follows
- recipe_likes
- recipe_comments

All tables include:
- Primary keys with AUTO_INCREMENT
- Foreign key constraints with appropriate ON DELETE actions
- Indexes on frequently queried columns
- Unique constraints where needed
- Check constraints for data validation

### 2. Creates FULLTEXT Indexes (Subtask 3.2)

Creates a FULLTEXT index on the recipes table for search functionality:

```sql
CREATE FULLTEXT INDEX idx_recipe_fulltext_search ON recipes(title, ingredients)
```

This enables efficient full-text search queries using MySQL's MATCH AGAINST syntax.

### 3. Verifies Schema (Subtask 3.3)

After creating the schema, the script verifies:

- All 17 tables exist
- Indexes are created on key tables:
  - recipes: user_id, title, created_at, visibility, idx_recipe_user_created, idx_recipe_fulltext_search
  - users: username
  - collections: user_id, share_token
  - meal_plans: user_id, meal_date
- Foreign keys are created on key tables:
  - recipes: user_id
  - recipe_ratings: recipe_id, user_id
  - collections: user_id
  - collection_recipes: collection_id, recipe_id
  - meal_plans: user_id, recipe_id
  - shopping_list_items: shopping_list_id
  - nutrition_facts: recipe_id

## Example Output

```
2024-03-26 14:40:24,130 - INFO - MySQL Schema Creation Script
2024-03-26 14:40:24,131 - INFO - ============================================================
2024-03-26 14:40:24,131 - INFO - Database URL: localhost:3306/recipe_saver
2024-03-26 14:40:24,131 - INFO - ============================================================

2024-03-26 14:40:24,200 - INFO - Successfully connected to MySQL
2024-03-26 14:40:24,250 - INFO - Creating tables from SQLAlchemy models...
2024-03-26 14:40:25,100 - INFO - All tables created successfully
2024-03-26 14:40:25,150 - INFO - Creating FULLTEXT indexes for search...
2024-03-26 14:40:25,200 - INFO - FULLTEXT index created on recipes(title, ingredients)
2024-03-26 14:40:25,250 - INFO - 
============================================================
2024-03-26 14:40:25,250 - INFO - SCHEMA VERIFICATION
2024-03-26 14:40:25,250 - INFO - ============================================================
2024-03-26 14:40:25,300 - INFO - 
Tables created: 17
2024-03-26 14:40:25,300 - INFO - ✓ All 17 expected tables exist
2024-03-26 14:40:25,300 - INFO -   - allergen_warnings
2024-03-26 14:40:25,300 - INFO -   - collection_recipes
2024-03-26 14:40:25,300 - INFO -   - collections
2024-03-26 14:40:25,300 - INFO -   - dietary_labels
2024-03-26 14:40:25,300 - INFO -   - meal_plan_template_items
2024-03-26 14:40:25,300 - INFO -   - meal_plan_templates
2024-03-26 14:40:25,300 - INFO -   - meal_plans
2024-03-26 14:40:25,300 - INFO -   - nutrition_facts
2024-03-26 14:40:25,300 - INFO -   - recipe_comments
2024-03-26 14:40:25,300 - INFO -   - recipe_likes
2024-03-26 14:40:25,300 - INFO -   - recipe_notes
2024-03-26 14:40:25,300 - INFO -   - recipe_ratings
2024-03-26 14:40:25,300 - INFO -   - recipes
2024-03-26 14:40:25,300 - INFO -   - shopping_list_items
2024-03-26 14:40:25,300 - INFO -   - shopping_lists
2024-03-26 14:40:25,300 - INFO -   - user_follows
2024-03-26 14:40:25,300 - INFO -   - users
2024-03-26 14:40:25,350 - INFO - 
Verifying indexes...
2024-03-26 14:40:25,400 - INFO -   recipes: 6/6 indexes verified
2024-03-26 14:40:25,420 - INFO -   users: 1/1 indexes verified
2024-03-26 14:40:25,440 - INFO -   collections: 2/2 indexes verified
2024-03-26 14:40:25,460 - INFO -   meal_plans: 2/2 indexes verified
2024-03-26 14:40:25,480 - INFO - 
Verifying foreign keys...
2024-03-26 14:40:25,500 - INFO -   recipes: 1/1 foreign keys verified
2024-03-26 14:40:25,520 - INFO -   recipe_ratings: 2/2 foreign keys verified
2024-03-26 14:40:25,540 - INFO -   collections: 1/1 foreign keys verified
2024-03-26 14:40:25,560 - INFO -   collection_recipes: 2/2 foreign keys verified
2024-03-26 14:40:25,580 - INFO -   meal_plans: 2/2 foreign keys verified
2024-03-26 14:40:25,600 - INFO -   shopping_list_items: 1/1 foreign keys verified
2024-03-26 14:40:25,620 - INFO -   nutrition_facts: 1/1 foreign keys verified
2024-03-26 14:40:25,650 - INFO - 
============================================================
2024-03-26 14:40:25,650 - INFO - Schema creation completed successfully!
2024-03-26 14:40:25,650 - INFO - ============================================================
2024-03-26 14:40:25,700 - INFO - 
✓ Schema creation completed successfully
```

## Troubleshooting

### Connection Errors

If you see connection errors:

1. Verify MySQL is running:
```bash
mysql -u root -p -e "SELECT 1"
```

2. Check the connection string format:
```
mysql+pymysql://username:password@host:port/database
```

3. Verify the database exists:
```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS recipe_saver"
```

4. Check user permissions:
```bash
mysql -u root -p -e "GRANT ALL PRIVILEGES ON recipe_saver.* TO 'user'@'localhost'"
```

### Import Errors

If you see import errors, ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

Specifically, ensure PyMySQL is installed:

```bash
pip install pymysql
```

### Schema Already Exists

The script is idempotent - it can be run multiple times safely. If tables already exist, SQLAlchemy will skip creating them. The FULLTEXT index creation checks if the index exists before creating it.

To recreate the schema from scratch:

```bash
# Drop all tables (WARNING: This will delete all data!)
mysql -u root -p recipe_saver -e "DROP DATABASE recipe_saver; CREATE DATABASE recipe_saver"

# Run the schema creation script
python create_mysql_schema.py
```

## Manual Verification

To manually verify the schema in MySQL:

```bash
# Connect to MySQL
mysql -u root -p recipe_saver

# Show all tables
SHOW TABLES;

# Show table structure
DESCRIBE recipes;

# Show indexes for a table
SHOW INDEX FROM recipes;

# Show foreign keys for a table
SHOW CREATE TABLE recipes;
```

## Requirements Satisfied

This script satisfies the following requirements from the MySQL migration spec:

- **Requirement 2.1**: Maintains all existing SQLAlchemy models
- **Requirement 2.2**: Uses MySQL-compatible data types
- **Requirement 2.3**: Maintains all foreign key relationships
- **Requirement 2.4**: Maintains all unique constraints and indexes
- **Requirement 3.9**: Supports text search using MySQL FULLTEXT indexes
- **Requirement 9.2**: Creates FULLTEXT indexes on Recipe.title and Recipe.ingredients

## Next Steps

After creating the schema:

1. Update the `.env` file to use the MySQL connection string
2. Run the data migration script (if migrating from SQLite)
3. Start the FastAPI application
4. Run tests to verify functionality

## Related Files

- `backend/app/models.py` - SQLAlchemy model definitions
- `backend/app/database.py` - Database connection management
- `backend/app/config.py` - Configuration settings
- `backend/.env` - Environment variables
