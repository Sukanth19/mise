# Migration Guide for Recipe Saver Enhancements

## Quick Start

### Option 1: Using the Python Migration Runner (Recommended)

```bash
cd backend
python run_migrations.py
```

This script will:
- Auto-detect your database type (SQLite or PostgreSQL)
- Track which migrations have been applied
- Apply only pending migrations
- Skip already-applied migrations

### Option 2: Using the Shell Script

```bash
cd backend
./migrate.sh
```

### Option 3: Manual Migration (SQLite)

```bash
cd backend
for file in migrations/*.sql; do
  sqlite3 recipe_saver.db < "$file"
done
```

### Option 4: Manual Migration (PostgreSQL)

```bash
cd backend
for file in migrations/postgresql/*.sql; do
  psql -U postgres -d recipe_saver -f "$file"
done
```

## Migration Overview

The migrations add the following database tables and columns:

### 1. Recipe Extensions (001)
- Adds `is_favorite`, `visibility`, `servings`, `source_recipe_id`, `source_author_id` to recipes table

### 2. Recipe Ratings (002)
- New table: `recipe_ratings` (5-star rating system)

### 3. Recipe Notes (003)
- New table: `recipe_notes` (user notes on recipes)

### 4. Collections (004)
- New tables: `collections`, `collection_recipes` (recipe organization with nesting)

### 5. Meal Plans (005)
- New tables: `meal_plans`, `meal_plan_templates`, `meal_plan_template_items`

### 6. Shopping Lists (006)
- New tables: `shopping_lists`, `shopping_list_items`

### 7. Nutrition (007)
- New tables: `nutrition_facts`, `dietary_labels`, `allergen_warnings`

### 8. Social Features (008)
- New tables: `user_follows`, `recipe_likes`, `recipe_comments`

## Verifying Migrations

### SQLite

```bash
sqlite3 recipe_saver.db ".tables"
```

You should see all the new tables listed.

### PostgreSQL

```bash
psql -U postgres -d recipe_saver -c "\dt"
```

## Troubleshooting

### Migration Already Applied Error

If you see "table already exists" errors, the migration may have been partially applied. You can:

1. Check which migrations were applied:
   ```sql
   SELECT * FROM applied_migrations;
   ```

2. Manually mark a migration as applied:
   ```sql
   INSERT INTO applied_migrations (migration_name) VALUES ('001_recipe_extensions.sql');
   ```

### Foreign Key Constraint Errors

Make sure you apply migrations in order (001, 002, 003, etc.) as later migrations depend on earlier ones.

### SQLite vs PostgreSQL Differences

The main differences between SQLite and PostgreSQL migrations:
- **Primary Keys**: SQLite uses `INTEGER PRIMARY KEY AUTOINCREMENT`, PostgreSQL uses `SERIAL PRIMARY KEY`
- **Syntax**: Both are otherwise very similar for these migrations

## Rolling Back

To rollback migrations:

### Development (SQLite)
```bash
# Delete the database and recreate from scratch
rm recipe_saver.db
python init_db.py
python run_migrations.py
```

### Production (PostgreSQL)
Create manual rollback scripts or restore from backup. Example rollback:

```sql
-- Rollback 008_social.sql
DROP TABLE IF EXISTS recipe_comments;
DROP TABLE IF EXISTS recipe_likes;
DROP TABLE IF EXISTS user_follows;
```

## Creating New Migrations

When adding new features:

1. Create a new migration file with the next number: `009_feature_name.sql`
2. Create both SQLite and PostgreSQL versions
3. Update this guide with the new migration
4. Test the migration on a copy of your database first

## Best Practices

- Always backup your database before running migrations
- Test migrations on development database first
- Run migrations during low-traffic periods in production
- Keep migrations small and focused on one feature
- Document any manual steps required
