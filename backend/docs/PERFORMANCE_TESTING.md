# MySQL Performance Testing Documentation

This document describes the performance testing approach for the MySQL migration, including query benchmarks, index verification, and optimization strategies.

**Validates Requirements:** 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7

## Overview

The MySQL migration includes comprehensive performance testing to ensure that query execution times meet acceptable thresholds and that database indexes are being used effectively.

## Test Files

### 1. `tests/test_mysql_performance.py`
Comprehensive pytest-based performance tests that run when MySQL is configured.

**Features:**
- Measures query execution times for common operations
- Verifies index usage with EXPLAIN queries
- Compares performance across different query patterns
- Validates pagination and result limits

**Usage:**
```bash
# Set DATABASE_URL to MySQL in .env
export DATABASE_URL="mysql+pymysql://user:password@localhost:3306/recipe_saver"

# Run performance tests
pytest tests/test_mysql_performance.py -v -s
```

### 2. `scripts/test_mysql_performance.py`
Standalone performance testing script that can be run independently.

**Features:**
- Creates test data automatically
- Measures and reports query performance
- Verifies index usage
- Generates JSON performance report
- Cleans up test data after completion

**Usage:**
```bash
# Ensure MySQL is configured in .env
python scripts/test_mysql_performance.py
```

## Performance Benchmarks

### Query Performance Thresholds

| Query Type | Description | Threshold | Requirements |
|------------|-------------|-----------|--------------|
| User Recipes | Fetch user's recipes with pagination | < 100ms | 9.1, 9.5 |
| Recipe Search | Full-text search on title/ingredients | < 150ms | 9.2 |
| Collection Load | Load collection with recipes via JOIN | < 100ms | 9.4, 9.7 |
| Meal Plan Range | Fetch meal plans for date range | < 100ms | 9.1, 9.3 |
| Aggregate Query | Calculate average ratings | < 50ms | 9.6 |
| Paginated Query | Fetch paginated results | < 100ms | 9.5 |

### Index Verification

The following indexes must be present and used by queries:

#### 1. user_id Indexes (Requirement 9.1)
**Tables:** recipes, collections, meal_plans, recipe_ratings, recipe_notes, shopping_lists

**Verification:**
```sql
EXPLAIN SELECT * FROM recipes WHERE user_id = 1;
-- Should show: key = 'user_id' or 'idx_user_id'
```

#### 2. FULLTEXT Indexes (Requirement 9.2)
**Table:** recipes  
**Columns:** title, ingredients

**Verification:**
```sql
SHOW INDEX FROM recipes WHERE Index_type = 'FULLTEXT';
-- Should return FULLTEXT index on title and ingredients

-- Usage example:
SELECT * FROM recipes 
WHERE MATCH(title, ingredients) AGAINST('pasta tomato' IN NATURAL LANGUAGE MODE);
```

#### 3. Compound Indexes (Requirement 9.3)
**Indexes:**
- `recipes(user_id, created_at)` - For user's recent recipes
- `collections(user_id, created_at)` - For user's recent collections
- `meal_plans(user_id, meal_date)` - For user's meal plans by date

**Verification:**
```sql
EXPLAIN SELECT * FROM recipes 
WHERE user_id = 1 
ORDER BY created_at DESC;
-- Should show: key = 'idx_recipe_user_created'
```

#### 4. Other Indexes
- `recipes.visibility` - For filtering public/private recipes
- `recipes.title` - For sorting by title
- `collections.share_token` - For shared collection lookup
- `shopping_lists.share_token` - For shared shopping list lookup

## Query Optimization Strategies

### 1. Pagination (Requirement 9.5)
**Strategy:** Use LIMIT and OFFSET with appropriate defaults

```python
# Default pagination
recipes = session.query(Recipe).limit(20).all()

# Custom pagination (max 100)
recipes = session.query(Recipe).offset(skip).limit(min(limit, 100)).all()
```

**Validation:**
- Default limit: 20 records
- Maximum limit: 100 records
- Queries should never return more than 100 records

### 2. Column Selection (Requirement 9.6)
**Strategy:** SELECT specific columns instead of SELECT *

```python
# Less efficient - loads all columns
recipes = session.query(Recipe).all()

# More efficient - loads only needed columns
recipes = session.query(Recipe.id, Recipe.title, Recipe.user_id).all()
```

**Performance Impact:**
- Reduces data transfer
- Faster query execution
- Lower memory usage

### 3. JOIN Optimization (Requirement 9.7)
**Strategy:** Use appropriate JOIN types and eager loading

```python
# Efficient eager loading with joinedload
from sqlalchemy.orm import joinedload

collection = session.query(Collection).options(
    joinedload(Collection.collection_recipes).joinedload(CollectionRecipe.recipe)
).filter(Collection.id == collection_id).first()
```

**JOIN Types:**
- `INNER JOIN` - For required relationships
- `LEFT JOIN` - For optional relationships
- Use `joinedload()` to avoid N+1 query problems

### 4. Index Usage (Requirements 9.1, 9.2, 9.3)
**Strategy:** Ensure queries use appropriate indexes

```python
# Uses user_id index
recipes = session.query(Recipe).filter(Recipe.user_id == user_id).all()

# Uses compound index (user_id, created_at)
recipes = session.query(Recipe).filter(
    Recipe.user_id == user_id
).order_by(Recipe.created_at.desc()).all()

# Uses FULLTEXT index
recipes = session.query(Recipe).filter(
    text("MATCH(title, ingredients) AGAINST(:search IN NATURAL LANGUAGE MODE)")
).params(search="pasta").all()
```

## Running Performance Tests

### Prerequisites
1. MySQL server running
2. Database created and configured
3. Environment variables set in `.env`:
   ```
   DATABASE_URL=mysql+pymysql://user:password@localhost:3306/recipe_saver
   ```

### Test Execution

#### Option 1: Pytest (Integrated Tests)
```bash
# Run all performance tests
pytest tests/test_mysql_performance.py -v -s

# Run specific test class
pytest tests/test_mysql_performance.py::TestQueryPerformance -v -s

# Run specific test
pytest tests/test_mysql_performance.py::TestQueryPerformance::test_user_recipes_query_performance -v
```

#### Option 2: Standalone Script
```bash
# Run standalone performance test
python scripts/test_mysql_performance.py

# Output will include:
# - Query execution times
# - Index usage verification
# - Performance summary
# - JSON report file
```

### Expected Output

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
COLUMN SELECTION COMPARISON
----------------------------------------------------------------------
  All columns: 78.90ms
  Specific columns: 45.67ms
  Improvement: 42.1%

----------------------------------------------------------------------
INDEX USAGE VERIFICATION
----------------------------------------------------------------------
  ✓ user_id index on recipes: Used
  ✓ compound index (user_id, created_at): Used
  ✓ visibility index: Used

----------------------------------------------------------------------
FULLTEXT INDEX VERIFICATION
----------------------------------------------------------------------
  ✓ FULLTEXT indexes found on recipes table:
    - idx_search on (title, ingredients)

======================================================================
PERFORMANCE SUMMARY
======================================================================

Tests Passed: 9/9

✓ Report saved to: mysql_performance_report.json
======================================================================
```

## Performance Report

The standalone script generates a JSON report with detailed results:

```json
{
  "timestamp": "2024-01-15T10:30:00",
  "database_url": "localhost:3306/recipe_saver",
  "tests_passed": 9,
  "tests_total": 9,
  "results": [
    {
      "name": "User recipes query",
      "execution_time_ms": 45.23,
      "threshold_ms": 100,
      "passed": true,
      "result_count": 20
    },
    ...
  ]
}
```

## Troubleshooting

### Tests Skipped
**Issue:** Tests are skipped with message "Performance tests only run with MySQL"

**Solution:** Ensure DATABASE_URL in `.env` starts with `mysql+pymysql://`

### Slow Query Performance
**Issue:** Queries exceed performance thresholds

**Possible Causes:**
1. Indexes not created - Run migrations to create indexes
2. Large dataset - Performance tests use 500 recipes, adjust if needed
3. MySQL not optimized - Check MySQL configuration

**Solutions:**
```sql
-- Verify indexes exist
SHOW INDEX FROM recipes;
SHOW INDEX FROM collections;
SHOW INDEX FROM meal_plans;

-- Create missing indexes
CREATE INDEX idx_user_id ON recipes(user_id);
CREATE INDEX idx_recipe_user_created ON recipes(user_id, created_at);
CREATE FULLTEXT INDEX idx_search ON recipes(title, ingredients);
```

### FULLTEXT Index Not Found
**Issue:** FULLTEXT index verification fails

**Solution:**
```sql
-- Create FULLTEXT index manually
CREATE FULLTEXT INDEX idx_search ON recipes(title, ingredients);

-- Verify creation
SHOW INDEX FROM recipes WHERE Index_type = 'FULLTEXT';
```

## Comparison with SQLite

### Performance Characteristics

| Aspect | SQLite | MySQL |
|--------|--------|-------|
| Simple queries | Fast | Fast |
| Complex JOINs | Moderate | Fast | Fast |
| Full-text search | Limited | Excellent | Good |
| Concurrent writes | Limited | Excellent | Good |
| Index types | Basic | Advanced | Good |

### Migration Performance Impact

**Expected Changes:**
- Similar or better performance for most queries
- Better concurrent access handling
- Improved full-text search with FULLTEXT indexes
- Better scalability for large datasets

**Baseline Comparison:**
The performance tests establish MySQL baselines that can be compared with SQLite performance if needed.

## Continuous Performance Monitoring

### Integration with CI/CD

Add performance tests to CI pipeline:

```yaml
# .github/workflows/performance.yml
name: Performance Tests

on: [push, pull_request]

jobs:
  performance:
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: testpassword
          MYSQL_DATABASE: recipe_saver_test
        ports:
          - 3306:3306
    
    steps:
      - uses: actions/checkout@v2
      - name: Run performance tests
        env:
          DATABASE_URL: mysql+pymysql://root:testpassword@localhost:3306/recipe_saver_test
        run: |
          pytest tests/test_mysql_performance.py -v
```

### Performance Regression Detection

Monitor query execution times over time:
1. Run performance tests on each commit
2. Compare results with baseline
3. Alert if queries exceed thresholds by >20%
4. Track performance trends

## Conclusion

The MySQL migration includes comprehensive performance testing to ensure:
- ✓ All queries meet performance thresholds
- ✓ Indexes are properly created and used
- ✓ Query optimization strategies are applied
- ✓ Performance is comparable or better than baseline

For questions or issues, refer to the main migration documentation or contact the development team.
