# MySQL Performance Testing - Quick Start Guide

Quick reference for running MySQL performance tests.

## Prerequisites

1. **MySQL Running:**
   ```bash
   # Check MySQL is running
   mysql -u root -p -e "SELECT VERSION();"
   ```

2. **Database Configured:**
   ```bash
   # In backend/.env
   DATABASE_URL=mysql+pymysql://user:password@localhost:3306/recipe_saver
   ```

3. **Dependencies Installed:**
   ```bash
   pip install -r requirements.txt
   ```

## Quick Test Options

### Option 1: Standalone Script (Recommended for Quick Check)
```bash
cd backend
python scripts/test_mysql_performance.py
```

**Output:**
- Real-time performance metrics
- Index usage verification
- Pass/fail status
- JSON report: `mysql_performance_report.json`

**Time:** ~30 seconds

### Option 2: Pytest Suite (Comprehensive Testing)
```bash
cd backend
pytest tests/test_mysql_performance.py -v -s
```

**Output:**
- Detailed test results
- Individual test timing
- Index verification
- Performance comparisons

**Time:** ~45 seconds

### Option 3: Specific Test
```bash
cd backend
pytest tests/test_mysql_performance.py::TestQueryPerformance::test_user_recipes_query_performance -v
```

**Time:** ~5 seconds per test

## What Gets Tested

### Query Performance (6 tests)
- ✓ User recipes query (< 100ms)
- ✓ Recipe search (< 150ms)
- ✓ Collection with JOIN (< 100ms)
- ✓ Meal plan date range (< 100ms)
- ✓ Aggregate query (< 50ms)
- ✓ Paginated query (< 100ms)

### Index Usage (4 tests)
- ✓ user_id indexes
- ✓ Compound indexes
- ✓ FULLTEXT indexes
- ✓ Other indexes (visibility, etc.)

### Optimization (3 tests)
- ✓ Query limits enforcement
- ✓ Column selection comparison
- ✓ Overall performance baseline

## Expected Results

```
======================================================================
MYSQL PERFORMANCE TESTING
======================================================================

Setting up test data...
✓ Created 10 users, 500 recipes, 50 collections

----------------------------------------------------------------------
QUERY PERFORMANCE TESTS
----------------------------------------------------------------------
  ✓ User recipes query: 45.23ms (threshold: 100ms)
  ✓ Recipe search query: 89.45ms (threshold: 150ms)
  ✓ Collection with recipes: 67.12ms (threshold: 100ms)
  ✓ Meal plan date range: 34.56ms (threshold: 100ms)
  ✓ Aggregate ratings query: 12.34ms (threshold: 50ms)
  ✓ Paginated query: 56.78ms (threshold: 100ms)

----------------------------------------------------------------------
INDEX USAGE VERIFICATION
----------------------------------------------------------------------
  ✓ user_id index on recipes: Used
  ✓ compound index (user_id, created_at): Used
  ✓ visibility index: Used

----------------------------------------------------------------------
FULLTEXT INDEX VERIFICATION
----------------------------------------------------------------------
  ✓ FULLTEXT indexes found on recipes table

======================================================================
PERFORMANCE SUMMARY
======================================================================

Tests Passed: 9/9

✓ Report saved to: mysql_performance_report.json
======================================================================
```

## Troubleshooting

### Tests Skipped
**Problem:** "Performance tests only run with MySQL"

**Solution:**
```bash
# Check DATABASE_URL in .env
cat backend/.env | grep DATABASE_URL

# Should start with: mysql+pymysql://
# If not, update .env:
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/recipe_saver
```

### Connection Error
**Problem:** "Failed to connect to MySQL"

**Solution:**
```bash
# Test MySQL connection
mysql -u user -p -h localhost -P 3306 recipe_saver

# If fails, check:
# 1. MySQL is running
# 2. Database exists
# 3. Credentials are correct
```

### Slow Performance
**Problem:** Queries exceed thresholds

**Solution:**
```bash
# Check indexes exist
mysql -u user -p recipe_saver -e "SHOW INDEX FROM recipes;"

# Create missing indexes if needed
mysql -u user -p recipe_saver < backend/migrations/create_indexes.sql
```

### FULLTEXT Index Missing
**Problem:** "No FULLTEXT indexes found"

**Solution:**
```sql
-- Create FULLTEXT index
CREATE FULLTEXT INDEX idx_search ON recipes(title, ingredients);

-- Verify
SHOW INDEX FROM recipes WHERE Index_type = 'FULLTEXT';
```

## Quick Commands

```bash
# Run all performance tests
pytest tests/test_mysql_performance.py -v -s

# Run standalone script
python scripts/test_mysql_performance.py

# Run specific test class
pytest tests/test_mysql_performance.py::TestQueryPerformance -v

# Run with coverage
pytest tests/test_mysql_performance.py --cov=app --cov-report=html

# Generate report only
python tests/test_mysql_performance_report.py
```

## Performance Thresholds

| Query | Threshold | Validates |
|-------|-----------|-----------|
| User Recipes | 100ms | 9.1, 9.5 |
| Recipe Search | 150ms | 9.2 |
| Collection JOIN | 100ms | 9.4, 9.7 |
| Meal Plan Range | 100ms | 9.1, 9.3 |
| Aggregate | 50ms | 9.6 |
| Pagination | 100ms | 9.5 |

## Documentation

- **Full Guide:** `docs/PERFORMANCE_TESTING.md`
- **Results:** `docs/PERFORMANCE_TEST_RESULTS.md`
- **Summary:** `docs/TASK_15_1_SUMMARY.md`

## Requirements Validated

- ✓ 9.1: Indexes on user_id
- ✓ 9.2: FULLTEXT indexes
- ✓ 9.3: Compound indexes
- ✓ 9.4: Efficient JOINs
- ✓ 9.5: Query limits
- ✓ 9.6: Column selection
- ✓ 9.7: JOIN types

---

**Need Help?** See full documentation in `docs/PERFORMANCE_TESTING.md`
