# Database Migrations

This directory contains SQL migration scripts for the Recipe Saver Enhancements feature.

## Migration Files

The migrations are numbered sequentially and should be applied in order:

1. **001_recipe_extensions.sql** - Adds new columns to recipes table (is_favorite, visibility, servings, source tracking)
2. **002_recipe_ratings.sql** - Creates recipe_ratings table for 5-star rating system
3. **003_recipe_notes.sql** - Creates recipe_notes table for user notes on recipes
4. **004_collections.sql** - Creates collections and collection_recipes tables for recipe organization
5. **005_meal_plans.sql** - Creates meal_plans and meal_plan_templates tables for meal planning
6. **006_shopping_lists.sql** - Creates shopping_lists and shopping_list_items tables
7. **007_nutrition.sql** - Creates nutrition_facts, dietary_labels, and allergen_warnings tables
8. **008_social.sql** - Creates user_follows, recipe_likes, and recipe_comments tables

## Database Compatibility

The migration scripts are written for **SQLite** (the current development database). For **PostgreSQL** production deployment, use the scripts in the `postgresql/` subdirectory which include:

- `SERIAL` instead of `INTEGER PRIMARY KEY AUTOINCREMENT`
- Proper `TIMESTAMP` handling
- PostgreSQL-specific syntax

## Running Migrations

### SQLite (Development)

```bash
# From the backend directory
sqlite3 recipe_saver.db < migrations/001_recipe_extensions.sql
sqlite3 recipe_saver.db < migrations/002_recipe_ratings.sql
sqlite3 recipe_saver.db < migrations/003_recipe_notes.sql
sqlite3 recipe_saver.db < migrations/004_collections.sql
sqlite3 recipe_saver.db < migrations/005_meal_plans.sql
sqlite3 recipe_saver.db < migrations/006_shopping_lists.sql
sqlite3 recipe_saver.db < migrations/007_nutrition.sql
sqlite3 recipe_saver.db < migrations/008_social.sql
```

Or run all at once:

```bash
for file in migrations/*.sql; do
  sqlite3 recipe_saver.db < "$file"
done
```

### PostgreSQL (Production)

```bash
# From the backend directory
psql -U postgres -d recipe_saver -f migrations/postgresql/001_recipe_extensions.sql
psql -U postgres -d recipe_saver -f migrations/postgresql/002_recipe_ratings.sql
# ... and so on
```

Or run all at once:

```bash
for file in migrations/postgresql/*.sql; do
  psql -U postgres -d recipe_saver -f "$file"
done
```

## Migration Script

A Python migration runner script is provided for convenience:

```bash
python run_migrations.py
```

This script will:
- Detect the database type (SQLite or PostgreSQL) from the DATABASE_URL
- Apply all pending migrations in order
- Track which migrations have been applied
- Skip already-applied migrations

## Rollback

Currently, rollback scripts are not provided. If you need to rollback:

1. For development: Delete the SQLite database and recreate it from scratch
2. For production: Create manual rollback scripts or restore from backup

## Notes

- All migrations include proper indexes as specified in the design document
- Foreign key constraints are enforced with appropriate ON DELETE actions
- CHECK constraints ensure data integrity (e.g., rating 1-5, valid meal times)
- UNIQUE constraints prevent duplicate entries where appropriate
- Timestamps use CURRENT_TIMESTAMP for automatic timestamping
