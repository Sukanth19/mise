# MySQL Query Optimization Guide

## Overview

This guide documents the query optimization process for the MySQL migration, including slow query identification, index optimization, and JOIN operation improvements.

**Validates:** Requirements 9.4, 9.7

## Table of Contents

1. [Slow Query Logging](#slow-query-logging)
2. [Index Analysis](#index-analysis)
3. [JOIN Optimization](#join-optimization)
4. [Optimization Recommendations](#optimization-recommendations)
5. [Performance Monitoring](#performance-monitoring)

## Slow Query Logging

### Enabling Slow Query Log

MySQL's slow query log captures queries that exceed a specified execution time threshold.

#### Method 1: Using the Optimization Script

```bash
cd backend
python scripts/optimize_slow_queries.py
```

This script automatically:
- Enables slow query logging
- Sets threshold to 1 second
- Analyzes existing indexes
- Identifies optimization opportunities
- Generates SQL for missing indexes

#### Method 2: Manual Configuration

**Temporary (session-level):**

```sql
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1.0;
```

**Permanent (my.cnf):**

```ini
[mysqld]
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow-query.log
long_query_time = 1.0
log_queries_not_using_indexes = 1
```

### Viewing Slow Query Log

```bash
# View slow query log
sudo tail -f /var/log/mysql/slow-query.log

# Analyze with mysqldumpslow
mysqldumpslow -s t -t 10 /var/log/mysql/slow-query.log
```

## Index Analysis

### Current Index Strategy

The application uses three types of indexes:

1. **Single-column indexes**: For frequently queried fields
2. **Compound indexes**: For multi-column queries
3. **FULLTEXT indexes**: For text search functionality

### Recommended Indexes

#### Recipes Table

```sql
-- User's recipes sorted by date
CREATE INDEX idx_recipes_user_id_created_at ON recipes(user_id, created_at);

-- Public recipe queries
CREATE INDEX idx_recipes_visibility ON recipes(visibility);

-- User recipes by visibility
CREATE INDEX idx_recipes_user_id_visibility ON recipes(user_id, visibility);

-- Full-text search
CREATE FULLTEXT INDEX idx_recipe_search ON recipes(title, ingredients);
```

#### Collections Table

```sql
-- User collections sorted by date
CREATE INDEX idx_collections_user_id_created_at ON collections(user_id, created_at);

-- Shared collection lookup
CREATE INDEX idx_collections_share_token ON collections(share_token);
```

#### Meal Plans Table

```sql
-- User meal plans by date range
CREATE INDEX idx_meal_plans_user_id_meal_date ON meal_plans(user_id, meal_date);

-- Meal plans by date
CREATE INDEX idx_meal_plans_meal_date ON meal_plans(meal_date);
```

#### Recipe Ratings Table

```sql
-- Unique rating constraint and lookup
CREATE UNIQUE INDEX idx_recipe_ratings_recipe_user ON recipe_ratings(recipe_id, user_id);
```

#### Recipe Notes Table

```sql
-- User notes on recipe
CREATE INDEX idx_recipe_notes_recipe_user ON recipe_notes(recipe_id, user_id);
```

#### Shopping Lists Table

```sql
-- Shared list lookup
CREATE INDEX idx_shopping_lists_share_token ON shopping_lists(share_token);
```

### Verifying Index Usage

Use `EXPLAIN` to verify indexes are being used:

```sql
-- Check if user_id index is used
EXPLAIN SELECT * FROM recipes WHERE user_id = 1;

-- Check if compound index is used
EXPLAIN SELECT * FROM recipes 
WHERE user_id = 1 
ORDER BY created_at DESC;

-- Check JOIN efficiency
EXPLAIN SELECT c.*, r.* 
FROM collections c
LEFT JOIN collection_recipes cr ON c.id = cr.collection_id
LEFT JOIN recipes r ON cr.recipe_id = r.id
WHERE c.user_id = 1;
```

**What to look for in EXPLAIN output:**

- `type`: Should be `ref`, `eq_ref`, or `range` (avoid `ALL` which means full table scan)
- `key`: Should show the index name being used
- `rows`: Lower is better (indicates fewer rows scanned)
- `Extra`: Look for "Using index" (covering index) or "Using where"

## JOIN Optimization

### Common JOIN Patterns

#### 1. Collection with Recipes

**Query:**
```sql
SELECT c.*, cr.*, r.*
FROM collections c
LEFT JOIN collection_recipes cr ON c.id = cr.collection_id
LEFT JOIN recipes r ON cr.recipe_id = r.id
WHERE c.user_id = 1
LIMIT 10;
```

**Required Indexes:**
- `collections.user_id`
- `collection_recipes.collection_id`
- `collection_recipes.recipe_id`

**SQLAlchemy (Eager Loading):**
```python
from sqlalchemy.orm import joinedload

collection = session.query(Collection).options(
    joinedload(Collection.collection_recipes).joinedload(CollectionRecipe.recipe)
).filter(Collection.user_id == user_id).first()
```

#### 2. Meal Plans with Recipes

**Query:**
```sql
SELECT mp.*, r.*
FROM meal_plans mp
INNER JOIN recipes r ON mp.recipe_id = r.id
WHERE mp.user_id = 1 AND mp.meal_date >= CURDATE()
ORDER BY mp.meal_date
LIMIT 20;
```

**Required Indexes:**
- `meal_plans.user_id`
- `meal_plans.meal_date`
- `meal_plans.recipe_id` (foreign key)
- Compound: `(user_id, meal_date)`

**SQLAlchemy:**
```python
from sqlalchemy.orm import joinedload
from datetime import date

meal_plans = session.query(MealPlan).options(
    joinedload(MealPlan.recipe)
).filter(
    MealPlan.user_id == user_id,
    MealPlan.meal_date >= date.today()
).order_by(MealPlan.meal_date).limit(20).all()
```

#### 3. Recipe with Nutrition Facts (One-to-One)

**Query:**
```sql
SELECT r.*, nf.*
FROM recipes r
LEFT JOIN nutrition_facts nf ON r.id = nf.recipe_id
WHERE r.user_id = 1
LIMIT 20;
```

**Required Indexes:**
- `recipes.user_id`
- `nutrition_facts.recipe_id` (unique)

**SQLAlchemy:**
```python
from sqlalchemy.orm import joinedload

recipes = session.query(Recipe).options(
    joinedload(Recipe.nutrition_facts)
).filter(Recipe.user_id == user_id).limit(20).all()
```

#### 4. Recipe with Ratings (Aggregate)

**Query:**
```sql
SELECT r.id, r.title, AVG(rr.rating) as avg_rating, COUNT(rr.id) as rating_count
FROM recipes r
LEFT JOIN recipe_ratings rr ON r.id = rr.recipe_id
WHERE r.user_id = 1
GROUP BY r.id, r.title
HAVING avg_rating >= 4.0;
```

**Required Indexes:**
- `recipes.user_id`
- `recipe_ratings.recipe_id`

**SQLAlchemy:**
```python
from sqlalchemy import func

results = session.query(
    Recipe.id,
    Recipe.title,
    func.avg(RecipeRating.rating).label('avg_rating'),
    func.count(RecipeRating.id).label('rating_count')
).outerjoin(RecipeRating).filter(
    Recipe.user_id == user_id
).group_by(Recipe.id, Recipe.title).having(
    func.avg(RecipeRating.rating) >= 4.0
).all()
```

### JOIN Type Selection

**INNER JOIN vs LEFT JOIN:**

- **INNER JOIN**: Use when you only want records that have matches in both tables
  - Example: Meal plans with recipes (every meal plan must have a recipe)
  
- **LEFT JOIN**: Use when you want all records from the left table, even if no match exists
  - Example: Recipes with nutrition facts (not all recipes have nutrition data)

**Performance Tip:** INNER JOIN is typically faster than LEFT JOIN because it can stop searching once a match is found.

### Avoiding N+1 Query Problem

**Bad (N+1 queries):**
```python
# Fetches collections (1 query)
collections = session.query(Collection).filter(Collection.user_id == user_id).all()

# Then fetches recipes for each collection (N queries)
for collection in collections:
    recipes = collection.collection_recipes  # Triggers separate query
```

**Good (Eager loading):**
```python
# Single query with JOINs
collections = session.query(Collection).options(
    joinedload(Collection.collection_recipes).joinedload(CollectionRecipe.recipe)
).filter(Collection.user_id == user_id).all()
```

## Optimization Recommendations

### Priority 1: High-Impact Optimizations

1. **Add compound indexes for common query patterns**
   - `recipes(user_id, created_at)` - User's recent recipes
   - `meal_plans(user_id, meal_date)` - User's meal plans by date
   - `collections(user_id, created_at)` - User's recent collections

2. **Ensure all foreign keys are indexed**
   - Check with: `python scripts/optimize_slow_queries.py`
   - Foreign key columns without indexes cause slow JOINs

3. **Add FULLTEXT index for search**
   - `recipes(title, ingredients)` - Fast text search
   - Use with `MATCH() AGAINST()` syntax

### Priority 2: Query-Level Optimizations

1. **Use eager loading for relationships**
   - Prevents N+1 query problem
   - Use `joinedload()` for one-to-one and small one-to-many
   - Use `subqueryload()` for large one-to-many

2. **Select only needed columns**
   ```python
   # Instead of:
   recipes = session.query(Recipe).all()
   
   # Use:
   recipes = session.query(Recipe.id, Recipe.title, Recipe.user_id).all()
   ```

3. **Use pagination consistently**
   ```python
   # Always limit results
   recipes = session.query(Recipe).limit(20).offset(skip).all()
   ```

### Priority 3: Database Configuration

1. **Connection pooling** (already configured)
   - `pool_size=10`
   - `max_overflow=20`
   - `pool_pre_ping=True`

2. **Query cache** (MySQL configuration)
   ```ini
   [mysqld]
   query_cache_type = 1
   query_cache_size = 64M
   ```

3. **InnoDB buffer pool** (MySQL configuration)
   ```ini
   [mysqld]
   innodb_buffer_pool_size = 1G  # Adjust based on available RAM
   ```

## Performance Monitoring

### Running the Optimization Script

```bash
cd backend

# Set database URL
export DATABASE_URL="mysql+pymysql://user:password@localhost:3306/recipe_saver"

# Run optimization analysis
python scripts/optimize_slow_queries.py
```

**Output includes:**
- Current index analysis
- Missing index recommendations
- JOIN query analysis with EXPLAIN
- SQL statements to create missing indexes
- JSON report: `query_optimization_report.json`

### Performance Testing

```bash
# Run performance tests
pytest tests/test_mysql_performance.py -v -s

# Run specific test
pytest tests/test_mysql_performance.py::TestQueryPerformance::test_user_recipes_query_performance -v
```

### Monitoring in Production

1. **Enable slow query log** (see above)

2. **Monitor query execution times**
   ```python
   # Application-level logging (already implemented)
   from app.utils.mysql_logger import log_query_operation
   
   log_query_operation("SELECT", "recipes", "Query completed", "debug")
   ```

3. **Use MySQL Performance Schema**
   ```sql
   -- Enable performance schema
   SET GLOBAL performance_schema = ON;
   
   -- View slow queries
   SELECT * FROM performance_schema.events_statements_summary_by_digest
   ORDER BY SUM_TIMER_WAIT DESC
   LIMIT 10;
   ```

4. **Regular EXPLAIN analysis**
   - Run EXPLAIN on slow queries from the log
   - Verify indexes are being used
   - Look for full table scans

### Performance Benchmarks

| Query Type | Target | Acceptable | Action Required |
|------------|--------|------------|-----------------|
| User recipes | < 50ms | < 100ms | > 100ms |
| Recipe search | < 100ms | < 150ms | > 150ms |
| Collection with recipes | < 50ms | < 100ms | > 100ms |
| Meal plan range | < 50ms | < 100ms | > 100ms |
| Aggregate query | < 30ms | < 50ms | > 50ms |
| Paginated query | < 50ms | < 100ms | > 100ms |

## Troubleshooting

### Query is slow despite indexes

1. **Check if index is being used**
   ```sql
   EXPLAIN SELECT * FROM recipes WHERE user_id = 1;
   ```

2. **Check index selectivity**
   ```sql
   SELECT COUNT(DISTINCT user_id) / COUNT(*) as selectivity
   FROM recipes;
   ```
   - Selectivity should be > 0.01 (1%) for index to be useful

3. **Check table statistics**
   ```sql
   ANALYZE TABLE recipes;
   ```

### JOIN is slow

1. **Verify foreign key indexes exist**
   ```sql
   SHOW INDEX FROM collection_recipes;
   ```

2. **Check JOIN order**
   - MySQL optimizer usually chooses the best order
   - Use `STRAIGHT_JOIN` to force specific order if needed

3. **Consider denormalization**
   - For frequently accessed data
   - Trade-off: storage vs. query speed

### Full table scan on small table

- This is often acceptable for small tables (< 1000 rows)
- MySQL optimizer may choose full scan over index if table is small
- Focus optimization efforts on large tables

## Summary

**Key Optimizations Implemented:**

✓ Compound indexes for common query patterns  
✓ Foreign key indexes for efficient JOINs  
✓ FULLTEXT indexes for search functionality  
✓ Eager loading to prevent N+1 queries  
✓ Connection pooling for resource efficiency  
✓ Slow query logging for monitoring  

**Performance Improvements:**

- User recipe queries: < 100ms
- Collection JOINs: < 100ms
- Meal plan queries: < 100ms
- Search queries: < 150ms
- Aggregate queries: < 50ms

**Monitoring Tools:**

- `scripts/optimize_slow_queries.py` - Automated analysis
- `tests/test_mysql_performance.py` - Performance testing
- MySQL slow query log - Production monitoring
- EXPLAIN analysis - Query optimization

## References

- [MySQL EXPLAIN Documentation](https://dev.mysql.com/doc/refman/8.0/en/explain.html)
- [MySQL Index Optimization](https://dev.mysql.com/doc/refman/8.0/en/optimization-indexes.html)
- [SQLAlchemy Query Performance](https://docs.sqlalchemy.org/en/14/orm/loading_relationships.html)
- Requirements 9.4: Efficient JOIN operations
- Requirements 9.7: Appropriate JOIN types to minimize query time
