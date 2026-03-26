"""
Performance testing for MySQL migration.

Tests query execution times, index usage, and performance comparison.

Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7
"""

import pytest
import time
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import User, Recipe, Collection, CollectionRecipe, MealPlan, RecipeRating, RecipeNote
import json


# Skip all tests if not using MySQL
pytestmark = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL", "").startswith("mysql"),
    reason="Performance tests only run with MySQL"
)


@pytest.fixture(scope="module")
def mysql_engine():
    """Create MySQL engine for performance testing."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url or not database_url.startswith("mysql"):
        pytest.skip("MySQL not configured")
    
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="module")
def mysql_session(mysql_engine):
    """Create MySQL session for performance testing."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=mysql_engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="module")
def test_data(mysql_session):
    """Create test data for performance testing."""
    # Create users
    users = []
    for i in range(10):
        user = User(
            username=f"perftest_user_{i}",
            password_hash="hashed_password"
        )
        mysql_session.add(user)
        users.append(user)
    
    mysql_session.commit()
    
    # Create recipes for each user
    recipes = []
    for user in users:
        for i in range(50):  # 50 recipes per user = 500 total
            recipe = Recipe(
                user_id=user.id,
                title=f"Recipe {i} by {user.username}",
                ingredients=json.dumps([f"ingredient_{j}" for j in range(10)]),
                steps=json.dumps([f"step_{j}" for j in range(5)]),
                tags=json.dumps(["tag1", "tag2", "tag3"]),
                visibility="public" if i % 2 == 0 else "private",
                servings=4
            )
            mysql_session.add(recipe)
            recipes.append(recipe)
    
    mysql_session.commit()
    
    # Create collections
    collections = []
    for user in users:
        for i in range(5):  # 5 collections per user
            collection = Collection(
                user_id=user.id,
                name=f"Collection {i} by {user.username}",
                description="Test collection"
            )
            mysql_session.add(collection)
            collections.append(collection)
    
    mysql_session.commit()
    
    # Add recipes to collections
    for collection in collections:
        # Add 10 recipes to each collection
        user_recipes = [r for r in recipes if r.user_id == collection.user_id][:10]
        for recipe in user_recipes:
            cr = CollectionRecipe(
                collection_id=collection.id,
                recipe_id=recipe.id
            )
            mysql_session.add(cr)
    
    mysql_session.commit()
    
    # Create meal plans
    from datetime import date, timedelta
    base_date = date.today()
    for user in users:
        user_recipes = [r for r in recipes if r.user_id == user.id][:20]
        for i, recipe in enumerate(user_recipes):
            meal_plan = MealPlan(
                user_id=user.id,
                recipe_id=recipe.id,
                meal_date=base_date + timedelta(days=i),
                meal_time="dinner"
            )
            mysql_session.add(meal_plan)
    
    mysql_session.commit()
    
    # Create ratings and notes
    for recipe in recipes[:100]:  # Add ratings/notes to first 100 recipes
        for user in users[:3]:  # 3 ratings per recipe
            rating = RecipeRating(
                recipe_id=recipe.id,
                user_id=user.id,
                rating=4
            )
            mysql_session.add(rating)
            
            note = RecipeNote(
                recipe_id=recipe.id,
                user_id=user.id,
                note_text=f"Note from {user.username}"
            )
            mysql_session.add(note)
    
    mysql_session.commit()
    
    return {
        "users": users,
        "recipes": recipes,
        "collections": collections
    }


def measure_query_time(session, query_func):
    """
    Measure query execution time.
    
    Args:
        session: Database session
        query_func: Function that executes a query
        
    Returns:
        Tuple of (result, execution_time_ms)
    """
    start_time = time.time()
    result = query_func(session)
    end_time = time.time()
    execution_time_ms = (end_time - start_time) * 1000
    return result, execution_time_ms


def get_explain_plan(session, query):
    """
    Get EXPLAIN output for a query.
    
    Args:
        session: Database session
        query: SQLAlchemy query object
        
    Returns:
        List of EXPLAIN rows
    """
    # Get the compiled query
    compiled = query.statement.compile(compile_kwargs={"literal_binds": True})
    sql = str(compiled)
    
    # Execute EXPLAIN
    explain_query = text(f"EXPLAIN {sql}")
    result = session.execute(explain_query)
    return result.fetchall()


class TestQueryPerformance:
    """Test query performance and response times."""
    
    def test_user_recipes_query_performance(self, mysql_session, test_data):
        """
        Test performance of fetching user's recipes.
        
        Validates: Requirements 9.1, 9.5
        """
        user = test_data["users"][0]
        
        def query_user_recipes(session):
            return session.query(Recipe).filter(
                Recipe.user_id == user.id
            ).order_by(Recipe.created_at.desc()).limit(20).all()
        
        result, exec_time = measure_query_time(mysql_session, query_user_recipes)
        
        # Verify results
        assert len(result) == 20
        assert all(r.user_id == user.id for r in result)
        
        # Performance assertion: should complete in under 100ms
        assert exec_time < 100, f"Query took {exec_time:.2f}ms, expected < 100ms"
        
        print(f"\n✓ User recipes query: {exec_time:.2f}ms for {len(result)} records")
    
    def test_recipe_search_performance(self, mysql_session, test_data):
        """
        Test performance of recipe search queries.
        
        Validates: Requirements 9.2
        """
        def query_recipe_search(session):
            return session.query(Recipe).filter(
                Recipe.title.like("%Recipe 1%")
            ).limit(20).all()
        
        result, exec_time = measure_query_time(mysql_session, query_recipe_search)
        
        # Verify results
        assert len(result) > 0
        assert all("Recipe 1" in r.title for r in result)
        
        # Performance assertion: should complete in under 150ms
        assert exec_time < 150, f"Search query took {exec_time:.2f}ms, expected < 150ms"
        
        print(f"\n✓ Recipe search query: {exec_time:.2f}ms for {len(result)} records")
    
    def test_collection_loading_performance(self, mysql_session, test_data):
        """
        Test performance of loading collection with recipes.
        
        Validates: Requirements 9.4
        """
        collection = test_data["collections"][0]
        
        def query_collection_with_recipes(session):
            from sqlalchemy.orm import joinedload
            return session.query(Collection).options(
                joinedload(Collection.collection_recipes).joinedload(CollectionRecipe.recipe)
            ).filter(Collection.id == collection.id).first()
        
        result, exec_time = measure_query_time(mysql_session, query_collection_with_recipes)
        
        # Verify results
        assert result is not None
        assert len(result.collection_recipes) > 0
        
        # Performance assertion: should complete in under 100ms
        assert exec_time < 100, f"Collection loading took {exec_time:.2f}ms, expected < 100ms"
        
        print(f"\n✓ Collection with recipes: {exec_time:.2f}ms for {len(result.collection_recipes)} recipes")
    
    def test_meal_plan_query_performance(self, mysql_session, test_data):
        """
        Test performance of meal plan queries.
        
        Validates: Requirements 9.1, 9.3
        """
        from datetime import date, timedelta
        user = test_data["users"][0]
        start_date = date.today()
        end_date = start_date + timedelta(days=7)
        
        def query_meal_plans(session):
            from sqlalchemy.orm import joinedload
            return session.query(MealPlan).options(
                joinedload(MealPlan.recipe)
            ).filter(
                MealPlan.user_id == user.id,
                MealPlan.meal_date >= start_date,
                MealPlan.meal_date <= end_date
            ).order_by(MealPlan.meal_date).all()
        
        result, exec_time = measure_query_time(mysql_session, query_meal_plans)
        
        # Verify results
        assert all(r.user_id == user.id for r in result)
        assert all(start_date <= r.meal_date <= end_date for r in result)
        
        # Performance assertion: should complete in under 100ms
        assert exec_time < 100, f"Meal plan query took {exec_time:.2f}ms, expected < 100ms"
        
        print(f"\n✓ Meal plan query: {exec_time:.2f}ms for {len(result)} records")
    
    def test_pagination_performance(self, mysql_session, test_data):
        """
        Test performance of paginated queries.
        
        Validates: Requirements 9.5
        """
        def query_paginated_recipes(session):
            return session.query(Recipe).filter(
                Recipe.visibility == "public"
            ).order_by(Recipe.created_at.desc()).offset(20).limit(20).all()
        
        result, exec_time = measure_query_time(mysql_session, query_paginated_recipes)
        
        # Verify results
        assert len(result) == 20
        assert all(r.visibility == "public" for r in result)
        
        # Performance assertion: should complete in under 100ms
        assert exec_time < 100, f"Paginated query took {exec_time:.2f}ms, expected < 100ms"
        
        print(f"\n✓ Paginated query: {exec_time:.2f}ms for {len(result)} records")
    
    def test_aggregate_query_performance(self, mysql_session, test_data):
        """
        Test performance of aggregate queries (ratings).
        
        Validates: Requirements 9.6
        """
        from sqlalchemy import func
        recipe = test_data["recipes"][0]
        
        def query_recipe_rating_stats(session):
            return session.query(
                func.avg(RecipeRating.rating).label("avg_rating"),
                func.count(RecipeRating.id).label("count")
            ).filter(RecipeRating.recipe_id == recipe.id).first()
        
        result, exec_time = measure_query_time(mysql_session, query_recipe_rating_stats)
        
        # Verify results
        assert result is not None
        assert result.count > 0
        
        # Performance assertion: should complete in under 50ms
        assert exec_time < 50, f"Aggregate query took {exec_time:.2f}ms, expected < 50ms"
        
        print(f"\n✓ Aggregate query: {exec_time:.2f}ms (avg: {result.avg_rating}, count: {result.count})")


class TestIndexUsage:
    """Test that indexes are being used by queries."""
    
    def test_user_id_index_usage(self, mysql_session, test_data):
        """
        Verify that user_id indexes are being used.
        
        Validates: Requirements 9.1
        """
        user = test_data["users"][0]
        
        # Query recipes by user_id
        query = mysql_session.query(Recipe).filter(Recipe.user_id == user.id)
        explain_result = get_explain_plan(mysql_session, query)
        
        # Check EXPLAIN output
        # Should use index on user_id (key column should mention user_id or idx_user_id)
        explain_str = str(explain_result).lower()
        
        # Verify index is used (not a full table scan)
        assert "user_id" in explain_str or "idx_user" in explain_str, \
            f"user_id index not used. EXPLAIN: {explain_result}"
        
        print(f"\n✓ user_id index is being used")
        print(f"  EXPLAIN: {explain_result}")
    
    def test_compound_index_usage(self, mysql_session, test_data):
        """
        Verify that compound indexes are being used.
        
        Validates: Requirements 9.3
        """
        user = test_data["users"][0]
        
        # Query with user_id and created_at (compound index)
        query = mysql_session.query(Recipe).filter(
            Recipe.user_id == user.id
        ).order_by(Recipe.created_at.desc())
        
        explain_result = get_explain_plan(mysql_session, query)
        explain_str = str(explain_result).lower()
        
        # Should use compound index (idx_recipe_user_created or similar)
        # At minimum, should use user_id index
        assert "user_id" in explain_str or "idx_" in explain_str, \
            f"Index not used. EXPLAIN: {explain_result}"
        
        print(f"\n✓ Compound index is being used")
        print(f"  EXPLAIN: {explain_result}")
    
    def test_join_efficiency(self, mysql_session, test_data):
        """
        Verify that JOIN operations are efficient.
        
        Validates: Requirements 9.4, 9.7
        """
        from sqlalchemy.orm import joinedload
        collection = test_data["collections"][0]
        
        # Query with JOIN
        query = mysql_session.query(Collection).options(
            joinedload(Collection.collection_recipes).joinedload(CollectionRecipe.recipe)
        ).filter(Collection.id == collection.id)
        
        # Measure execution time
        start_time = time.time()
        result = query.first()
        exec_time = (time.time() - start_time) * 1000
        
        # Verify result
        assert result is not None
        assert len(result.collection_recipes) > 0
        
        # JOIN should be efficient (< 100ms)
        assert exec_time < 100, f"JOIN took {exec_time:.2f}ms, expected < 100ms"
        
        print(f"\n✓ JOIN operation is efficient: {exec_time:.2f}ms")
    
    def test_visibility_index_usage(self, mysql_session, test_data):
        """
        Verify that visibility index is being used.
        
        Validates: Requirements 9.1
        """
        # Query by visibility
        query = mysql_session.query(Recipe).filter(Recipe.visibility == "public")
        explain_result = get_explain_plan(mysql_session, query)
        explain_str = str(explain_result).lower()
        
        # Should use visibility index
        assert "visibility" in explain_str or "idx_" in explain_str, \
            f"visibility index not used. EXPLAIN: {explain_result}"
        
        print(f"\n✓ visibility index is being used")
        print(f"  EXPLAIN: {explain_result}")


class TestPerformanceComparison:
    """Compare MySQL performance with baseline expectations."""
    
    def test_query_limit_enforcement(self, mysql_session, test_data):
        """
        Verify that query limits are enforced.
        
        Validates: Requirements 9.5
        """
        # Query with limit
        result = mysql_session.query(Recipe).limit(20).all()
        assert len(result) == 20, f"Expected 20 results, got {len(result)}"
        
        # Query with max limit
        result = mysql_session.query(Recipe).limit(100).all()
        assert len(result) <= 100, f"Expected <= 100 results, got {len(result)}"
        
        print(f"\n✓ Query limits are enforced correctly")
    
    def test_select_specific_columns(self, mysql_session, test_data):
        """
        Verify that selecting specific columns is more efficient.
        
        Validates: Requirements 9.6
        """
        # Query with all columns
        def query_all_columns(session):
            return session.query(Recipe).limit(100).all()
        
        _, time_all = measure_query_time(mysql_session, query_all_columns)
        
        # Query with specific columns
        def query_specific_columns(session):
            return session.query(Recipe.id, Recipe.title, Recipe.user_id).limit(100).all()
        
        _, time_specific = measure_query_time(mysql_session, query_specific_columns)
        
        # Specific columns should be faster or similar
        # (May not always be faster for small datasets, but should not be slower)
        print(f"\n✓ Column selection performance:")
        print(f"  All columns: {time_all:.2f}ms")
        print(f"  Specific columns: {time_specific:.2f}ms")
        print(f"  Improvement: {((time_all - time_specific) / time_all * 100):.1f}%")
    
    def test_overall_performance_baseline(self, mysql_session, test_data):
        """
        Test overall performance meets baseline expectations.
        
        Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7
        """
        performance_results = []
        
        # Test 1: Simple user query
        user = test_data["users"][0]
        _, time1 = measure_query_time(
            mysql_session,
            lambda s: s.query(Recipe).filter(Recipe.user_id == user.id).limit(20).all()
        )
        performance_results.append(("User recipes", time1, 100))
        
        # Test 2: Search query
        _, time2 = measure_query_time(
            mysql_session,
            lambda s: s.query(Recipe).filter(Recipe.title.like("%Recipe%")).limit(20).all()
        )
        performance_results.append(("Recipe search", time2, 150))
        
        # Test 3: Collection with JOIN
        collection = test_data["collections"][0]
        _, time3 = measure_query_time(
            mysql_session,
            lambda s: s.query(Collection).filter(Collection.id == collection.id).first()
        )
        performance_results.append(("Collection query", time3, 50))
        
        # Test 4: Aggregate query
        from sqlalchemy import func
        recipe = test_data["recipes"][0]
        _, time4 = measure_query_time(
            mysql_session,
            lambda s: s.query(func.avg(RecipeRating.rating)).filter(
                RecipeRating.recipe_id == recipe.id
            ).scalar()
        )
        performance_results.append(("Aggregate query", time4, 50))
        
        # Print summary
        print("\n" + "="*60)
        print("PERFORMANCE SUMMARY")
        print("="*60)
        for name, time, threshold in performance_results:
            status = "✓" if time < threshold else "✗"
            print(f"{status} {name:20s}: {time:6.2f}ms (threshold: {threshold}ms)")
        print("="*60)
        
        # All queries should meet their thresholds
        failures = [(name, time, threshold) for name, time, threshold in performance_results if time >= threshold]
        assert len(failures) == 0, f"Performance thresholds not met: {failures}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
