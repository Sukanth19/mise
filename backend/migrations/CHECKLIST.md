# Migration Deployment Checklist

Use this checklist when deploying the Recipe Saver Enhancements database migrations.

## Pre-Migration

- [ ] **Backup Database**: Create a full backup of the current database
- [ ] **Review Migrations**: Read through all migration files to understand changes
- [ ] **Test Environment**: Set up a test database with production data copy
- [ ] **Dependencies**: Ensure Python 3.x and required packages are installed
- [ ] **Database Access**: Verify you have appropriate database permissions

## Testing Phase

- [ ] **Run on Test DB**: Execute migrations on test database
  ```bash
  cd backend
  python run_migrations.py
  ```
- [ ] **Verify Tables**: Check that all 15 new tables were created
  ```bash
  # SQLite
  sqlite3 recipe_saver.db ".tables"
  
  # PostgreSQL
  psql -U postgres -d recipe_saver -c "\dt"
  ```
- [ ] **Verify Indexes**: Confirm all 35 indexes were created
  ```bash
  # SQLite
  sqlite3 recipe_saver.db ".indexes"
  
  # PostgreSQL
  psql -U postgres -d recipe_saver -c "\di"
  ```
- [ ] **Test Constraints**: Verify CHECK constraints work
  ```sql
  -- Should fail (rating out of range)
  INSERT INTO recipe_ratings (recipe_id, user_id, rating) VALUES (1, 1, 6);
  
  -- Should succeed
  INSERT INTO recipe_ratings (recipe_id, user_id, rating) VALUES (1, 1, 5);
  ```
- [ ] **Test Foreign Keys**: Verify cascading deletes work correctly
- [ ] **Check Performance**: Run sample queries to verify index performance

## Migration Execution

- [ ] **Schedule Downtime**: Plan migration during low-traffic period (if needed)
- [ ] **Notify Users**: Inform users of potential downtime
- [ ] **Stop Application**: Stop the backend application
- [ ] **Final Backup**: Create one more backup right before migration
- [ ] **Run Migrations**: Execute migration script
  ```bash
  cd backend
  python run_migrations.py
  ```
- [ ] **Verify Success**: Check that all migrations completed without errors
- [ ] **Check Migration Log**: Review applied_migrations table
  ```sql
  SELECT * FROM applied_migrations ORDER BY applied_at;
  ```

## Post-Migration Verification

- [ ] **Table Count**: Verify 15 new tables exist
- [ ] **Column Count**: Verify recipes table has 5 new columns
- [ ] **Index Count**: Verify all indexes were created
- [ ] **Constraint Check**: Test a few constraints manually
- [ ] **Sample Queries**: Run test queries on new tables
- [ ] **Application Start**: Start the backend application
- [ ] **Health Check**: Verify application starts without errors
- [ ] **API Tests**: Test existing API endpoints still work
- [ ] **Monitor Logs**: Watch for any database-related errors

## Rollback Plan (If Needed)

If something goes wrong:

- [ ] **Stop Application**: Immediately stop the backend
- [ ] **Restore Backup**: Restore from the pre-migration backup
- [ ] **Verify Restore**: Confirm backup restoration was successful
- [ ] **Restart Application**: Start application with old schema
- [ ] **Document Issues**: Record what went wrong for troubleshooting
- [ ] **Fix and Retry**: Address issues and plan another migration attempt

## Post-Deployment

- [ ] **Monitor Performance**: Watch database performance for 24-48 hours
- [ ] **Check Logs**: Review application logs for any issues
- [ ] **User Feedback**: Monitor for user-reported issues
- [ ] **Document Completion**: Record migration completion date and any issues
- [ ] **Update Documentation**: Update any relevant documentation
- [ ] **Clean Up**: Remove old backups after confirming stability (keep at least one)

## Migration Details

### Expected Changes

**New Tables**: 15
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

**Extended Tables**: 1
- recipes (5 new columns)

**New Indexes**: 35

**Migration Files**: 8
- 001_recipe_extensions.sql
- 002_recipe_ratings.sql
- 003_recipe_notes.sql
- 004_collections.sql
- 005_meal_plans.sql
- 006_shopping_lists.sql
- 007_nutrition.sql
- 008_social.sql

### Estimated Time

- **SQLite (Development)**: < 1 second
- **PostgreSQL (Small DB)**: < 5 seconds
- **PostgreSQL (Large DB)**: Varies based on data volume

### Downtime Required

- **Development**: None
- **Production**: Minimal (< 1 minute recommended for safety)

## Contact Information

**Migration Owner**: [Your Name]
**Date**: [Date]
**Environment**: [Development/Staging/Production]

## Notes

Add any environment-specific notes or special considerations here:

---

**Signature**: _________________ **Date**: _________
