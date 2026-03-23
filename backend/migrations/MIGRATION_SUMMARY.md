# Migration Summary - Recipe Saver Enhancements

## Overview

This migration package adds comprehensive database schema changes to support the Recipe Saver Enhancements feature set. All migrations include proper indexes, foreign key constraints, and data validation rules as specified in the design document.

## Files Created

### SQLite Migrations (Development)
- `001_recipe_extensions.sql` - Recipe table extensions
- `002_recipe_ratings.sql` - Recipe ratings table
- `003_recipe_notes.sql` - Recipe notes table
- `004_collections.sql` - Collections and collection_recipes tables
- `005_meal_plans.sql` - Meal planning tables
- `006_shopping_lists.sql` - Shopping list tables
- `007_nutrition.sql` - Nutrition tracking tables
- `008_social.sql` - Social features tables

### PostgreSQL Migrations (Production)
- `postgresql/001_recipe_extensions.sql` through `postgresql/008_social.sql`
- Identical structure to SQLite versions but using PostgreSQL-specific syntax

### Supporting Files
- `README.md` - Overview and basic usage instructions
- `MIGRATION_GUIDE.md` - Detailed guide for running migrations
- `MIGRATION_SUMMARY.md` - This file
- `run_migrations.py` - Python script for automated migration execution
- `migrate.sh` - Shell script wrapper for convenience

## Database Schema Changes

### New Tables (8 migrations, 15 new tables)

1. **recipe_ratings** - User ratings (1-5 stars) for recipes
2. **recipe_notes** - Personal notes users can add to recipes
3. **collections** - User-created folders for organizing recipes
4. **collection_recipes** - Many-to-many relationship between collections and recipes
5. **meal_plans** - Calendar-based meal planning entries
6. **meal_plan_templates** - Reusable meal plan templates
7. **meal_plan_template_items** - Items within meal plan templates
8. **shopping_lists** - Shopping lists generated from recipes
9. **shopping_list_items** - Individual items in shopping lists
10. **nutrition_facts** - Nutritional information for recipes
11. **dietary_labels** - Dietary labels (vegan, keto, etc.)
12. **allergen_warnings** - Allergen warnings for recipes
13. **user_follows** - User following relationships
14. **recipe_likes** - Recipe likes from users
15. **recipe_comments** - Comments on recipes

### Extended Tables

**recipes** table gets 5 new columns:
- `is_favorite` (BOOLEAN) - Mark recipes as favorites
- `visibility` (VARCHAR) - Control recipe visibility (private/public/unlisted)
- `servings` (INTEGER) - Number of servings
- `source_recipe_id` (INTEGER) - Track forked recipes
- `source_author_id` (INTEGER) - Track original author of forked recipes

### Indexes Created (35 total)

All tables include appropriate indexes for:
- Foreign key columns (for join performance)
- Frequently queried columns (user_id, recipe_id, dates)
- Share tokens (for quick lookup)
- Filtering columns (visibility, labels, allergens)

### Constraints Implemented

**CHECK Constraints:**
- Rating values: 1-5 only
- Meal times: breakfast, lunch, dinner, snack only
- Visibility: private, public, unlisted only
- Categories: produce, dairy, meat, pantry, other only
- Dietary labels: vegan, vegetarian, gluten-free, dairy-free, keto, paleo, low-carb
- Allergens: nuts, dairy, eggs, soy, wheat, fish, shellfish
- Nesting level: 0-3 only
- Self-follow prevention: follower_id != following_id

**UNIQUE Constraints:**
- One rating per user per recipe
- One note per user per recipe (can be multiple notes, but tracked separately)
- One collection-recipe pair (no duplicates in collections)
- One dietary label per recipe (no duplicate labels)
- One allergen per recipe (no duplicate allergens)
- One like per user per recipe
- One follow relationship per user pair
- Unique share tokens

**Foreign Key Constraints:**
- All user_id columns reference users(id) with CASCADE delete
- All recipe_id columns reference recipes(id) with CASCADE delete
- Collection nesting references collections(id) with CASCADE delete
- Template items reference templates with CASCADE delete
- Source tracking uses SET NULL on delete (preserve fork history)

## Data Integrity Features

1. **Cascading Deletes**: When a user or recipe is deleted, all related data is automatically cleaned up
2. **Referential Integrity**: All foreign keys are enforced
3. **Validation**: CHECK constraints ensure data quality
4. **Uniqueness**: UNIQUE constraints prevent duplicate entries
5. **Timestamps**: Automatic created_at and updated_at tracking
6. **Indexes**: Optimized query performance for common operations

## Migration Tracking

The `run_migrations.py` script creates an `applied_migrations` table to track which migrations have been run. This prevents duplicate application and allows for safe re-runs.

## Testing Recommendations

Before deploying to production:

1. **Backup**: Always backup your database
2. **Test Environment**: Run migrations on a copy of production data
3. **Verify Indexes**: Check that indexes were created successfully
4. **Test Queries**: Verify that common queries perform well
5. **Check Constraints**: Test that constraints work as expected
6. **Rollback Plan**: Have a rollback strategy ready

## Performance Considerations

- All foreign key columns are indexed for join performance
- Frequently filtered columns (visibility, labels, dates) are indexed
- Share tokens are indexed for quick lookup
- Composite indexes may be added later based on query patterns

## Compatibility

- **SQLite**: Fully compatible with SQLite 3.x (development)
- **PostgreSQL**: Fully compatible with PostgreSQL 12+ (production)
- **Migration Path**: Easy migration from SQLite to PostgreSQL using standard tools

## Next Steps

After running migrations:

1. Update SQLAlchemy models in `backend/app/models.py`
2. Create Pydantic schemas for new tables
3. Implement service layer for new features
4. Create API endpoints
5. Add tests for new functionality

## Support

For issues or questions:
- Check `MIGRATION_GUIDE.md` for detailed instructions
- Review `README.md` for quick reference
- Examine individual migration files for schema details
