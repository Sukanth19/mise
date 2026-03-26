# MySQL Migration Guide

## Overview

This guide provides step-by-step instructions for migrating the Recipe Saver application from PostgreSQL or SQLite to MySQL. The migration process preserves all data, relationships, and constraints while ensuring minimal downtime.

## Prerequisites

Before starting the migration, ensure you have:

1. **MySQL 8.0+** installed and running
2. **Python 3.10+** with all backend dependencies installed
3. **Backup** of your current database
4. **Access credentials** for both source and target databases
5. **Sufficient disk space** for both databases during migration

## Migration Overview

The migration process consists of the following phases:

1. **Preparation**: Set up MySQL database and verify connections
2. **Schema Creation**: Create MySQL tables with proper indexes and constraints
3. **Data Migration**: Transfer data from source to target database
4. **Validation**: Verify data integrity and record counts
5. **Application Update**: Update configuration to use MySQL
6. **Testing**: Run tests to ensure everything works correctly

---

## Phase 1: Preparation

### Step 1.1: Install MySQL

Choose your installation method:

**macOS (Homebrew):**
```bash
brew install mysql
brew services start mysql
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql
```

**Docker (Recommended for Development):**
```bash
# Create docker-compose.yml (already provided in project root)
docker-compose up -d
```

### Step 1.2: Create MySQL Database

```bash
# Connect to MySQL
mysql -u root -p

# Create database with UTF-8 support
CREATE DATABASE recipe_saver CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Create user and grant permissions
CREATE USER 'recipe_user'@'localhost' IDENTIFIED BY 'recipe_password';
GRANT ALL PRIVILEGES ON recipe_saver.* TO 'recipe_user'@'localhost';
FLUSH PRIVILEGES;

# Exit MySQL
EXIT;
```

### Step 1.3: Backup Current Database

**PostgreSQL:**
```bash
pg_dump -U postgres recipe_saver > backup_$(date +%Y%m%d_%H%M%S).sql
```

**SQLite:**
```bash
cp recipe_saver.db backup_$(date +%Y%m%d_%H%M%S).db
```

### Step 1.4: Verify Connections

Test both source and target database connections:

```bash
cd backend

# Test source database (PostgreSQL)
python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://user:password@localhost:5432/recipe_saver'); engine.connect(); print('✓ Source connection OK')"

# Test target database (MySQL)
python -c "from sqlalchemy import create_engine; engine = create_engine('mysql+pymysql://recipe_user:recipe_password@localhost:3306/recipe_saver'); engine.connect(); print('✓ Target connection OK')"
```

---

## Phase 2: Schema Creation

### Step 2.1: Create MySQL Schema

Run the schema creation script:

```bash
cd backend
python create_mysql_schema.py
```

This script will:
- Create all 17 tables with proper data types
- Create all indexes (including FULLTEXT indexes)
- Create all foreign key constraints
- Set up proper character encoding (utf8mb4)

### Step 2.2: Verify Schema

Verify that all tables were created:

```bash
mysql -u recipe_user -p recipe_saver -e "SHOW TABLES;"
```

Expected output:
```
+---------------------------+
| Tables_in_recipe_saver    |
+---------------------------+
| allergen_warnings         |
| collection_recipes        |
| collections               |
| dietary_labels            |
| meal_plan_template_items  |
| meal_plan_templates       |
| meal_plans                |
| nutrition_facts           |
| recipe_comments           |
| recipe_likes              |
| recipe_notes              |
| recipe_ratings            |
| recipes                   |
| shopping_list_items       |
| shopping_lists            |
| user_follows              |
| users                     |
+---------------------------+
```

Verify indexes on a table:

```bash
mysql -u recipe_user -p recipe_saver -e "SHOW INDEX FROM recipes;"
```

---

## Phase 3: Data Migration

### Step 3.1: Dry-Run Migration

Always perform a dry-run first to validate the migration without writing data:

```bash
cd backend
python migrate_to_mysql.py \
  --source-url "postgresql://user:password@localhost:5432/recipe_saver" \
  --target-url "mysql+pymysql://recipe_user:recipe_password@localhost:3306/recipe_saver" \
  --dry-run
```

**For SQLite source:**
```bash
python migrate_to_mysql.py \
  --source-url "sqlite:///./recipe_saver.db" \
  --target-url "mysql+pymysql://recipe_user:recipe_password@localhost:3306/recipe_saver" \
  --dry-run
```

Review the output for:
- ✓ Connection success messages
- ✓ Record counts for each table
- ✓ No critical errors
- ✓ Validation summary

### Step 3.2: Run Full Migration

If dry-run succeeds, run the actual migration:

```bash
python migrate_to_mysql.py \
  --source-url "postgresql://user:password@localhost:5432/recipe_saver" \
  --target-url "mysql+pymysql://recipe_user:recipe_password@localhost:3306/recipe_saver"
```

The migration script will:
1. Connect to both databases
2. Migrate tables in dependency order:
   - users (no dependencies)
   - recipes (depends on users)
   - nutrition_facts, dietary_labels, allergen_warnings (depend on recipes)
   - recipe_ratings, recipe_notes (depend on recipes and users)
   - collections (depends on users)
   - collection_recipes (depends on collections and recipes)
   - meal_plans, meal_plan_templates (depend on users and recipes)
   - shopping_lists, shopping_list_items (depend on users and recipes)
   - user_follows, recipe_likes, recipe_comments (social features)
3. Map foreign key relationships
4. Verify record counts
5. Generate migration report

### Step 3.3: Monitor Migration Progress

The migration script provides real-time progress:

```
2024-01-15 10:30:00 - INFO - Connecting to source database...
2024-01-15 10:30:01 - INFO - ✓ Successfully connected to source database
2024-01-15 10:30:01 - INFO - Connecting to target database (MySQL)...
2024-01-15 10:30:02 - INFO - ✓ Successfully connected to target database (MySQL)
2024-01-15 10:30:02 - INFO - Starting migration for table: users
2024-01-15 10:30:02 - INFO - Table users: 150 records to migrate
2024-01-15 10:30:03 - INFO - ✓ Table users: Successfully migrated 150/150 records
2024-01-15 10:30:03 - INFO - Starting migration for table: recipes
2024-01-15 10:30:03 - INFO - Table recipes: 1250 records to migrate
2024-01-15 10:30:08 - INFO - ✓ Table recipes: Successfully migrated 1250/1250 records
...
```

### Step 3.4: Incremental Migration (Optional)

For large databases, use incremental migration to resume from failures:

```bash
python migrate_to_mysql.py \
  --source-url "postgresql://user:password@localhost:5432/recipe_saver" \
  --target-url "mysql+pymysql://recipe_user:recipe_password@localhost:3306/recipe_saver" \
  --incremental
```

This mode:
- Skips tables that already have matching record counts
- Resumes from the last incomplete table
- Useful for very large datasets or unstable connections

---

## Phase 4: Validation

### Step 4.1: Verify Record Counts

Compare record counts between source and target:

```bash
# PostgreSQL source
psql -U postgres recipe_saver -c "SELECT 'users' as table_name, COUNT(*) FROM users UNION ALL SELECT 'recipes', COUNT(*) FROM recipes UNION ALL SELECT 'collections', COUNT(*) FROM collections;"

# MySQL target
mysql -u recipe_user -p recipe_saver -e "SELECT 'users' as table_name, COUNT(*) FROM users UNION ALL SELECT 'recipes', COUNT(*) FROM recipes UNION ALL SELECT 'collections', COUNT(*) FROM collections;"
```

All counts should match exactly.

### Step 4.2: Verify Relationships

Test foreign key relationships:

```bash
mysql -u recipe_user -p recipe_saver -e "
SELECT 
  r.id, r.title, u.username 
FROM recipes r 
JOIN users u ON r.user_id = u.id 
LIMIT 5;
"
```

### Step 4.3: Verify Data Integrity

Sample some records to ensure data was migrated correctly:

```bash
mysql -u recipe_user -p recipe_saver -e "
SELECT id, username, created_at FROM users LIMIT 5;
SELECT id, title, ingredients, created_at FROM recipes LIMIT 5;
"
```

Compare with source database to ensure values match.

### Step 4.4: Check Migration Log

Review the migration log file:

```bash
cat migration.log | grep -E "(ERROR|WARNING|✓)"
```

Look for:
- ✓ Success messages for all tables
- No ERROR messages
- Acceptable WARNING messages (e.g., skipped records with missing foreign keys)

---

## Phase 5: Application Update

### Step 5.1: Update Environment Configuration

Edit `backend/.env`:

```env
# Comment out old database
# DATABASE_URL=postgresql://user:password@localhost:5432/recipe_saver

# Add MySQL connection
DATABASE_URL=mysql+pymysql://recipe_user:recipe_password@localhost:3306/recipe_saver

# JWT settings (unchanged)
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Step 5.2: Update Dependencies

Ensure MySQL driver is installed:

```bash
cd backend
pip install pymysql
# Or for production:
# pip install mysqlclient
```

### Step 5.3: Restart Backend

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

Check startup logs for:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 5.4: Verify Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

## Phase 6: Testing

### Step 6.1: Run Backend Tests

```bash
cd backend
pytest tests/ -v
```

All tests should pass with MySQL backend.

### Step 6.2: Run Property-Based Tests

```bash
pytest tests/test_*_properties.py -v
```

### Step 6.3: Manual API Testing

Test key endpoints:

**Authentication:**
```bash
# Register user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
```

**Recipes:**
```bash
# Get recipes (use token from login)
curl http://localhost:8000/api/recipes \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Step 6.4: Frontend Testing

Start the frontend and test the full application:

```bash
cd frontend
npm run dev
```

Navigate to http://localhost:3000 and test:
- User login
- Recipe creation
- Recipe search
- Collections
- Meal planning
- Shopping lists

---

## Troubleshooting

### Issue: Connection Refused

**Symptom:**
```
Failed to connect to MySQL: Can't connect to MySQL server on 'localhost'
```

**Solutions:**
1. Verify MySQL is running:
   ```bash
   # macOS/Linux
   sudo systemctl status mysql
   # or
   brew services list
   
   # Docker
   docker ps | grep mysql
   ```

2. Check MySQL port:
   ```bash
   netstat -an | grep 3306
   ```

3. Verify credentials:
   ```bash
   mysql -u recipe_user -p recipe_saver
   ```

### Issue: Character Encoding Errors

**Symptom:**
```
Incorrect string value: '\xF0\x9F\x8D\x95' for column 'title'
```

**Solution:**
Ensure database uses utf8mb4:
```sql
ALTER DATABASE recipe_saver CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE recipes CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Issue: Foreign Key Constraint Failures

**Symptom:**
```
Cannot add or update a child row: a foreign key constraint fails
```

**Solution:**
1. Check migration order - parent tables must be migrated before child tables
2. Verify ID mappings in migration script
3. Check for orphaned records in source database:
   ```sql
   SELECT r.id, r.user_id 
   FROM recipes r 
   LEFT JOIN users u ON r.user_id = u.id 
   WHERE u.id IS NULL;
   ```

### Issue: Slow Migration Performance

**Symptom:**
Migration takes hours for large datasets

**Solutions:**
1. Use incremental migration mode:
   ```bash
   python migrate_to_mysql.py --incremental ...
   ```

2. Temporarily disable indexes during migration:
   ```sql
   ALTER TABLE recipes DISABLE KEYS;
   -- Run migration
   ALTER TABLE recipes ENABLE KEYS;
   ```

3. Increase MySQL buffer sizes:
   ```sql
   SET GLOBAL innodb_buffer_pool_size = 2147483648; -- 2GB
   ```

4. Use batch inserts (modify migration script if needed)

### Issue: FULLTEXT Index Not Working

**Symptom:**
Search queries don't return expected results

**Solution:**
Verify FULLTEXT index exists:
```sql
SHOW INDEX FROM recipes WHERE Key_name = 'idx_search';
```

If missing, create it:
```sql
CREATE FULLTEXT INDEX idx_search ON recipes(title, ingredients);
```

Test FULLTEXT search:
```sql
SELECT id, title 
FROM recipes 
WHERE MATCH(title, ingredients) AGAINST('pasta' IN NATURAL LANGUAGE MODE);
```

### Issue: Migration Rollback Needed

**Symptom:**
Migration failed and you need to start over

**Solution:**
1. Stop the migration (Ctrl+C)
2. Clear MySQL database:
   ```bash
   mysql -u recipe_user -p recipe_saver -e "
   SET FOREIGN_KEY_CHECKS = 0;
   DROP TABLE IF EXISTS allergen_warnings, collection_recipes, collections, 
     dietary_labels, meal_plan_template_items, meal_plan_templates, meal_plans, 
     nutrition_facts, recipe_comments, recipe_likes, recipe_notes, recipe_ratings, 
     recipes, shopping_list_items, shopping_lists, user_follows, users;
   SET FOREIGN_KEY_CHECKS = 1;
   "
   ```
3. Recreate schema:
   ```bash
   python backend/create_mysql_schema.py
   ```
4. Retry migration

### Issue: Application Errors After Migration

**Symptom:**
API returns 500 errors after switching to MySQL

**Solutions:**
1. Check backend logs:
   ```bash
   tail -f backend/app.log
   ```

2. Verify database connection in `.env`:
   ```bash
   cat backend/.env | grep DATABASE_URL
   ```

3. Test database connection:
   ```bash
   python -c "from app.database import database; database.connect('mysql+pymysql://...'); print(database.health_check())"
   ```

4. Check for MySQL-specific SQL syntax issues in queries

---

## Performance Optimization

### After Migration

Once migration is complete, optimize MySQL performance:

1. **Analyze Tables:**
   ```sql
   ANALYZE TABLE users, recipes, collections, meal_plans, shopping_lists;
   ```

2. **Optimize Tables:**
   ```sql
   OPTIMIZE TABLE users, recipes, collections;
   ```

3. **Update Statistics:**
   ```sql
   ANALYZE TABLE recipes;
   ```

4. **Monitor Slow Queries:**
   ```sql
   SET GLOBAL slow_query_log = 'ON';
   SET GLOBAL long_query_time = 2;
   ```

5. **Review Query Performance:**
   ```sql
   EXPLAIN SELECT * FROM recipes WHERE user_id = 1 ORDER BY created_at DESC LIMIT 20;
   ```

---

## Migration Checklist

Use this checklist to track your migration progress:

- [ ] Backup current database
- [ ] Install and configure MySQL
- [ ] Create MySQL database and user
- [ ] Verify source and target connections
- [ ] Run schema creation script
- [ ] Verify all tables and indexes created
- [ ] Run dry-run migration
- [ ] Review dry-run results
- [ ] Run full migration
- [ ] Verify record counts match
- [ ] Verify data integrity
- [ ] Update application configuration
- [ ] Restart backend application
- [ ] Run backend tests
- [ ] Test API endpoints manually
- [ ] Test frontend application
- [ ] Monitor application logs
- [ ] Optimize MySQL performance
- [ ] Document any issues encountered
- [ ] Update team documentation

---

## Next Steps

After successful migration:

1. **Monitor Performance**: Track query performance and optimize as needed
2. **Update Documentation**: Document any custom configurations or issues
3. **Train Team**: Ensure team members understand MySQL-specific operations
4. **Plan Rollback**: Keep PostgreSQL/SQLite backup for at least 30 days
5. **Schedule Maintenance**: Plan regular MySQL maintenance tasks

For rollback procedures, see [ROLLBACK.md](./ROLLBACK.md).
