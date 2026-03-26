# MySQL Rollback Guide

## Overview

This guide provides procedures for rolling back from MySQL to PostgreSQL or SQLite if issues arise after migration. The rollback process ensures you can quickly restore the application to its previous state with minimal data loss.

## When to Rollback

Consider rolling back if you encounter:

- **Critical Performance Issues**: MySQL queries are significantly slower than expected
- **Data Integrity Problems**: Missing or corrupted data after migration
- **Application Errors**: Persistent errors that cannot be resolved quickly
- **Compatibility Issues**: Third-party integrations that don't work with MySQL
- **Operational Concerns**: Team lacks MySQL expertise or tooling

## Rollback Prerequisites

Before initiating a rollback, ensure you have:

1. **Database Backup**: Recent backup of the original database (PostgreSQL/SQLite)
2. **Migration Log**: Complete migration log file for reference
3. **Downtime Window**: Scheduled maintenance window for rollback
4. **Team Notification**: All stakeholders informed of rollback plan
5. **Reverse Migration Script**: `migrate_from_mysql.py` script available

---

## Rollback Strategy

Choose the appropriate rollback strategy based on your situation:

### Strategy A: Restore from Backup (Fastest)

**Use when:**
- No data changes occurred in MySQL after migration
- You have a recent backup of the original database
- You need to rollback immediately

**Pros:**
- Fastest rollback method (minutes)
- Guaranteed data consistency
- No risk of data loss

**Cons:**
- Loses any data created after migration
- Requires recent backup

### Strategy B: Reverse Migration (Data Preservation)

**Use when:**
- Data was created/modified in MySQL after migration
- You need to preserve all recent changes
- You have time for a full reverse migration

**Pros:**
- Preserves all data including recent changes
- No data loss

**Cons:**
- Takes longer (similar to forward migration time)
- Requires reverse migration script
- More complex process

### Strategy C: Hybrid Approach

**Use when:**
- You have a backup but also need recent changes
- You can identify and export recent changes separately

**Pros:**
- Fast baseline restore from backup
- Preserves critical recent changes

**Cons:**
- Requires manual data reconciliation
- More complex process

---

## Strategy A: Restore from Backup

### Step 1: Stop the Application

```bash
# Stop backend
pkill -f "uvicorn app.main:app"

# Or if using systemd
sudo systemctl stop recipe-saver-backend

# Stop frontend
pkill -f "next"
```

### Step 2: Restore Database Backup

**PostgreSQL:**

```bash
# Drop existing database (if it exists)
dropdb recipe_saver

# Create fresh database
createdb recipe_saver

# Restore from backup
psql -U postgres recipe_saver < backup_YYYYMMDD_HHMMSS.sql

# Verify restoration
psql -U postgres recipe_saver -c "SELECT COUNT(*) FROM users;"
```

**SQLite:**

```bash
# Remove current database (if exists)
rm -f recipe_saver.db

# Restore from backup
cp backup_YYYYMMDD_HHMMSS.db recipe_saver.db

# Verify restoration
sqlite3 recipe_saver.db "SELECT COUNT(*) FROM users;"
```

### Step 3: Update Application Configuration

Edit `backend/.env`:

```env
# Restore PostgreSQL connection
DATABASE_URL=postgresql://user:password@localhost:5432/recipe_saver

# Or restore SQLite connection
# DATABASE_URL=sqlite:///./recipe_saver.db

# Comment out MySQL
# DATABASE_URL=mysql+pymysql://recipe_user:recipe_password@localhost:3306/recipe_saver
```

### Step 4: Restart Application

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### Step 5: Verify Application

```bash
# Check health endpoint
curl http://localhost:8000/health

# Test authentication
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "existing_user", "password": "password"}'

# Test recipe retrieval
curl http://localhost:8000/api/recipes \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Step 6: Start Frontend

```bash
cd frontend
npm run dev
```

Test the application at http://localhost:3000

---

## Strategy B: Reverse Migration

### Step 1: Prepare Target Database

**PostgreSQL:**

```bash
# Create fresh database
createdb recipe_saver

# Or clear existing database
psql -U postgres recipe_saver -c "
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
"

# Create schema
psql -U postgres recipe_saver -f database/init.sql
```

**SQLite:**

```bash
# Remove existing database
rm -f recipe_saver.db

# Schema will be created by SQLAlchemy
```

### Step 2: Run Reverse Migration Script

The reverse migration script transfers data from MySQL back to PostgreSQL/SQLite:

```bash
cd backend

# Dry-run first
python migrate_from_mysql.py \
  --source-url "mysql+pymysql://recipe_user:recipe_password@localhost:3306/recipe_saver" \
  --target-url "postgresql://user:password@localhost:5432/recipe_saver" \
  --dry-run

# Run actual migration
python migrate_from_mysql.py \
  --source-url "mysql+pymysql://recipe_user:recipe_password@localhost:3306/recipe_saver" \
  --target-url "postgresql://user:password@localhost:5432/recipe_saver"
```

**For SQLite target:**

```bash
python migrate_from_mysql.py \
  --source-url "mysql+pymysql://recipe_user:recipe_password@localhost:3306/recipe_saver" \
  --target-url "sqlite:///./recipe_saver.db"
```

### Step 3: Verify Migration

```bash
# Check record counts
psql -U postgres recipe_saver -c "
SELECT 'users' as table_name, COUNT(*) FROM users
UNION ALL SELECT 'recipes', COUNT(*) FROM recipes
UNION ALL SELECT 'collections', COUNT(*) FROM collections;
"

# Compare with MySQL
mysql -u recipe_user -p recipe_saver -e "
SELECT 'users' as table_name, COUNT(*) FROM users
UNION ALL SELECT 'recipes', COUNT(*) FROM recipes
UNION ALL SELECT 'collections', COUNT(*) FROM collections;
"
```

All counts should match.

### Step 4: Update Application Configuration

Edit `backend/.env`:

```env
# Restore PostgreSQL connection
DATABASE_URL=postgresql://user:password@localhost:5432/recipe_saver

# Comment out MySQL
# DATABASE_URL=mysql+pymysql://recipe_user:recipe_password@localhost:3306/recipe_saver
```

### Step 5: Restart and Verify

Follow Steps 4-6 from Strategy A.

---

## Strategy C: Hybrid Approach

### Step 1: Identify Recent Changes

Query MySQL for data created after migration:

```sql
-- Find users created after migration
SELECT * FROM users WHERE created_at > 'YYYY-MM-DD HH:MM:SS';

-- Find recipes created after migration
SELECT * FROM recipes WHERE created_at > 'YYYY-MM-DD HH:MM:SS';

-- Export to CSV
SELECT * FROM recipes WHERE created_at > 'YYYY-MM-DD HH:MM:SS'
INTO OUTFILE '/tmp/new_recipes.csv'
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n';
```

### Step 2: Restore from Backup

Follow Strategy A, Steps 1-3.

### Step 3: Import Recent Changes

**PostgreSQL:**

```bash
# Import CSV data
psql -U postgres recipe_saver -c "
COPY recipes(user_id, title, ingredients, steps, created_at, ...)
FROM '/tmp/new_recipes.csv'
DELIMITER ','
CSV HEADER;
"
```

**SQLite:**

```bash
sqlite3 recipe_saver.db <<EOF
.mode csv
.import /tmp/new_recipes.csv recipes
EOF
```

### Step 4: Verify and Restart

Follow Strategy A, Steps 4-6.

---

## Post-Rollback Tasks

### 1. Verify Data Integrity

Run comprehensive tests:

```bash
cd backend
pytest tests/ -v
```

### 2. Check Application Logs

Monitor logs for any errors:

```bash
tail -f backend/app.log
```

### 3. Test Critical Workflows

Manually test:
- User authentication
- Recipe creation and editing
- Search functionality
- Collections management
- Meal planning
- Shopping lists

### 4. Notify Stakeholders

Inform team and users:
- Rollback completion time
- Any data loss (if applicable)
- Next steps and timeline

### 5. Document Issues

Record:
- Reason for rollback
- Issues encountered with MySQL
- Lessons learned
- Recommendations for future migration attempts

---

## Switching Between Database Backends

The application supports switching between database backends using the `DATABASE_TYPE` environment variable.

### Configuration

Edit `backend/.env`:

```env
# Set database type
DATABASE_TYPE=postgresql  # or mysql, sqlite

# Provide connection strings for all backends
DATABASE_URL_POSTGRESQL=postgresql://user:password@localhost:5432/recipe_saver
DATABASE_URL_MYSQL=mysql+pymysql://recipe_user:recipe_password@localhost:3306/recipe_saver
DATABASE_URL_SQLITE=sqlite:///./recipe_saver.db

# Active connection (based on DATABASE_TYPE)
DATABASE_URL=${DATABASE_URL_POSTGRESQL}
```

### Switching Backends

1. **Stop the application**
2. **Update DATABASE_TYPE** in `.env`
3. **Update DATABASE_URL** to match the selected backend
4. **Restart the application**

The application will automatically use the specified database backend.

### Validation

The application validates that only one database is active at startup:

```python
# app/config.py
def validate_database_config(self):
    if self.DATABASE_TYPE not in ['postgresql', 'mysql', 'sqlite']:
        raise ValueError(f"Invalid DATABASE_TYPE: {self.DATABASE_TYPE}")
    
    # Ensure DATABASE_URL matches DATABASE_TYPE
    if self.DATABASE_TYPE == 'mysql' and 'mysql' not in self.DATABASE_URL:
        raise ValueError("DATABASE_URL must be a MySQL connection string")
```

---

## Troubleshooting Rollback Issues

### Issue: Backup File Corrupted

**Symptom:**
```
ERROR: invalid input syntax for type integer
```

**Solution:**
1. Try an older backup file
2. Verify backup file integrity:
   ```bash
   # PostgreSQL
   pg_restore --list backup.sql
   
   # SQLite
   sqlite3 backup.db "PRAGMA integrity_check;"
   ```

### Issue: Schema Mismatch

**Symptom:**
```
ERROR: column "new_column" does not exist
```

**Solution:**
1. Ensure you're using the correct schema version
2. Run migrations to update schema:
   ```bash
   # PostgreSQL
   psql -U postgres recipe_saver -f database/migrations/001_add_column.sql
   ```

### Issue: Foreign Key Violations

**Symptom:**
```
ERROR: insert or update on table violates foreign key constraint
```

**Solution:**
1. Temporarily disable foreign key checks:
   ```sql
   -- PostgreSQL
   SET session_replication_role = 'replica';
   -- Import data
   SET session_replication_role = 'origin';
   
   -- SQLite
   PRAGMA foreign_keys = OFF;
   -- Import data
   PRAGMA foreign_keys = ON;
   ```

### Issue: Reverse Migration Fails

**Symptom:**
```
Failed to migrate table: recipes
```

**Solution:**
1. Check migration log for specific errors
2. Verify source database (MySQL) is accessible
3. Ensure target database has sufficient space
4. Try incremental migration:
   ```bash
   python migrate_from_mysql.py --incremental ...
   ```

### Issue: Application Won't Start After Rollback

**Symptom:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**
1. Verify database is running:
   ```bash
   # PostgreSQL
   pg_isready
   
   # SQLite
   ls -la recipe_saver.db
   ```

2. Check connection string in `.env`
3. Test connection manually:
   ```bash
   psql -U postgres recipe_saver -c "SELECT 1;"
   ```

---

## Rollback Checklist

Use this checklist to track your rollback progress:

- [ ] Notify stakeholders of rollback plan
- [ ] Schedule maintenance window
- [ ] Stop application (backend and frontend)
- [ ] Backup current MySQL database (just in case)
- [ ] Choose rollback strategy (A, B, or C)
- [ ] Execute rollback procedure
- [ ] Verify database restoration
- [ ] Update application configuration
- [ ] Restart application
- [ ] Run automated tests
- [ ] Test critical workflows manually
- [ ] Monitor application logs
- [ ] Verify data integrity
- [ ] Notify stakeholders of completion
- [ ] Document issues and lessons learned
- [ ] Update team documentation

---

## Prevention for Future Migrations

To avoid needing rollbacks in future migrations:

1. **Thorough Testing**: Test migration on staging environment first
2. **Gradual Rollout**: Use blue-green deployment or canary releases
3. **Monitoring**: Set up comprehensive monitoring before migration
4. **Performance Baseline**: Establish performance benchmarks before migration
5. **Team Training**: Ensure team is trained on new database system
6. **Backup Strategy**: Maintain multiple backup points
7. **Rollback Plan**: Have rollback plan ready before migration
8. **Communication**: Keep stakeholders informed throughout process

---

## Support and Resources

If you encounter issues during rollback:

1. **Check Logs**: Review `migration.log` and application logs
2. **Consult Documentation**: Review [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)
3. **Database Documentation**: 
   - [PostgreSQL Docs](https://www.postgresql.org/docs/)
   - [SQLite Docs](https://www.sqlite.org/docs.html)
   - [MySQL Docs](https://dev.mysql.com/doc/)
4. **Team Support**: Contact database administrator or senior developer
5. **Community**: Search Stack Overflow or relevant forums

---

## Maintaining Multiple Database Backends

If you need to support multiple database backends long-term:

### Configuration Management

Use environment-specific configuration files:

```bash
# .env.postgresql
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://user:password@localhost:5432/recipe_saver

# .env.mysql
DATABASE_TYPE=mysql
DATABASE_URL=mysql+pymysql://recipe_user:recipe_password@localhost:3306/recipe_saver

# .env.sqlite
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///./recipe_saver.db
```

### Testing Strategy

Test against all supported databases:

```bash
# Test with PostgreSQL
cp .env.postgresql .env
pytest tests/

# Test with MySQL
cp .env.mysql .env
pytest tests/

# Test with SQLite
cp .env.sqlite .env
pytest tests/
```

### CI/CD Pipeline

Configure CI to test all database backends:

```yaml
# .github/workflows/test.yml
strategy:
  matrix:
    database: [postgresql, mysql, sqlite]
steps:
  - name: Test with ${{ matrix.database }}
    run: |
      cp .env.${{ matrix.database }} .env
      pytest tests/
```

---

## Conclusion

Rolling back from MySQL to PostgreSQL or SQLite is a straightforward process when you have proper backups and follow the procedures outlined in this guide. Choose the rollback strategy that best fits your situation, and always verify data integrity after rollback.

Remember: The best rollback is the one you never need to perform. Thorough testing and preparation before migration significantly reduces the likelihood of needing to rollback.
