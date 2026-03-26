#!/usr/bin/env python3
"""
Standalone MySQL Performance Testing Script.

This script measures query performance, verifies index usage, and generates
a comprehensive performance report for the MySQL migration.

Usage:
    python scripts/test_mysql_performance.py

Requirements:
    - MySQL database must be running and configured in .env
    - DATABASE_URL must point to MySQL instance
    
Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7
"""

import sys
import os
import time
import json
from datetime import datetime, date, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker, joinedload
from app.database import Base
from app.models import User, Recipe, Collection, CollectionRecipe, MealPlan, RecipeRating, RecipeNote
from app.config import settings


class PerformanceTester:
    """MySQL performance testing utility."""
    
    def __init__(self, database_url: str):
        """Initialize performance tester with database connection."""
        if not database_url.startswith("mysql"):
            raise ValueError("This script requires a MySQL database URL")
        
        self.engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.session = SessionLocal()
        self.results = []
    
    def measure_query(self, name: str, query_func, threshold_ms: float):
        """
        Measure query execution time.
        
        Args:
            name: Query name for reporting
            query_func: Function that executes the query
            threshold_ms: Expected maximum execution time in milliseconds
            
        Returns:
            Dict with query results
        """
        start_time = time.time()
        result = query_func(self.session)
        end_time = time.time()
        exec_time_ms = (end_time - start_time) * 1000
        
        passed = exec_time_ms < threshold_ms
        
        result_data = {
            "name": name,
            "execution_time_ms": round(exec_time_ms, 2),
            "threshold_ms": threshold_ms,
            "passed": passed,
            "result_count": len(result) if isinstance(result, list) else 1
        }
        
        self.results.append(result_data)
        return result_data
    
    def verify_index_usage(self, name: str, query, expected_index: str):
        """
        Verify that a query uses the expected index.
        
        Args:
            name: Query name for reporting
            query: SQLAlchemy query object
            expected_index: Expected index name or column
            
        Returns:
            Dict with index verification results
        """
        try:
            # Get compiled SQL
            compiled = query.statement.compile(
                dialect=self.engine.dialect,
                compile_kwargs={"literal_binds": True}
            )
            sql = str(compiled)
            
            # Execute EXPLAIN
            explain_query = text(f"EXPLAIN {sql}")
            result = self.session.execute(explain_query)
            explain_rows = result.fetchall()
            
            # Check if expected index is mentioned
            explain_str = str(explain_rows).lower()
            index_used = expected_index.lower() in explain_str
            
            result_data = {
                "name": name,
                "expected_index": expected_index,
                "index_used": index_used,
                "explain_output": str(explain_rows)
            }
            
            self.results.append(result_data)
            return result_data
            
        except Exception as e:
            return {
                "name": name,
                "expected_index": expected_index,
                "index_used": False,
                "error": str(e)
            }
    
    def setup_test_data(self):
        """Create test data for performance testing."""
        print("Setting up test data...")
        
        # Create users
        users = []
        for i in range(10):
            user = User(
                username=f"perftest_user_{i}_{int(time.time())}",
                password_hash="hashed_password"
            )
            self.session.add(user)
            users.append(user)
        
        self.session.commit()
        
        # Create recipes
        recipes = []
        for user in users:
            for i in range(50):
                recipe = Recipe(
                    user_id=user.id,
                    title=f"Performance Test Recipe {i} by {user.username}",
                    ingredients=json.dumps([f"ingredient_{j}" for j in range(10)]),
                    steps=json.dumps([f"step_{j}" for j in range(5)]),
                    tags=json.dumps(["performance", "test", "mysql"]),
                    visibility="public" if i % 2 == 0 else "private",
                    servings=4
                )
                self.session.add(recipe)
                recipes.append(recipe)
        
        self.session.commit()
        
        # Create collections
        collections = []
        for user in users:
            for i in range(5):
                collection = Collection(
                    user_id=user.id,
                    name=f"Test Collection {i}",
                    description="Performance test collection"
                )
                self.session.add(collection)
                collections.append(collection)
        
        self.session.commit()
        
        # Add recipes to collections
        for collection in collections:
            user_recipes = [r for r in recipes if r.user_id == collection.user_id][:10]
            for recipe in user_recipes:
                cr = CollectionRecipe(
                    collection_id=collection.id,
                    recipe_id=recipe.id
                )
                self.session.add(cr)
        
        self.session.commit()
        
        # Create meal plans
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
                self.session.add(meal_plan)
        
        self.session.commit()
        
        # Create ratings
        for recipe in recipes[:100]:
            for user in users[:3]:
                rating = RecipeRating(
                    recipe_id=recipe.id,
                    user_id=user.id,
                    rating=4
                )
                self.session.add(rating)
        
        self.session.commit()
        
        print(f"✓ Created {len(users)} users, {len(recipes)} recipes, {len(collections)} collections")
        return users, recipes, collections
    
    def cleanup_test_data(self, users):
        """Remove test data."""
        print("\nCleaning up test data...")
        for user in users:
            self.session.query(User).filter(User.id == user.id).delete()
        self.session.commit()
        print("✓ Test data cleaned up")
    
    def run_performance_tests(self):
        """Run all performance tests."""
        print("\n" + "="*70)
        print("MYSQL PERFORMANCE TESTING")
        print("="*70)
        
        # Setup test data
        users, recipes, collections = self.setup_test_data()
        
        try:
            print("\n" + "-"*70)
            print("QUERY PERFORMANCE TESTS")
            print("-"*70)
            
            # Test 1: User recipes query (Requirement 9.1, 9.5)
            user = users[0]
            result = self.measure_query(
                "User recipes query",
                lambda s: s.query(Recipe).filter(
                    Recipe.user_id == user.id
                ).order_by(Recipe.created_at.desc()).limit(20).all(),
                100
            )
            print(f"  {'✓' if result['passed'] else '✗'} {result['name']}: {result['execution_time_ms']}ms (threshold: {result['threshold_ms']}ms)")
            
            # Test 2: Recipe search (Requirement 9.2)
            result = self.measure_query(
                "Recipe search query",
                lambda s: s.query(Recipe).filter(
                    Recipe.title.like("%Recipe 1%")
                ).limit(20).all(),
                150
            )
            print(f"  {'✓' if result['passed'] else '✗'} {result['name']}: {result['execution_time_ms']}ms (threshold: {result['threshold_ms']}ms)")
            
            # Test 3: Collection with recipes JOIN (Requirement 9.4, 9.7)
            collection = collections[0]
            result = self.measure_query(
                "Collection with recipes",
                lambda s: s.query(Collection).options(
                    joinedload(Collection.collection_recipes).joinedload(CollectionRecipe.recipe)
                ).filter(Collection.id == collection.id).first(),
                100
            )
            print(f"  {'✓' if result['passed'] else '✗'} {result['name']}: {result['execution_time_ms']}ms (threshold: {result['threshold_ms']}ms)")
            
            # Test 4: Meal plan date range (Requirement 9.1, 9.3)
            start_date = date.today()
            end_date = start_date + timedelta(days=7)
            result = self.measure_query(
                "Meal plan date range",
                lambda s: s.query(MealPlan).filter(
                    MealPlan.user_id == user.id,
                    MealPlan.meal_date >= start_date,
                    MealPlan.meal_date <= end_date
                ).order_by(MealPlan.meal_date).all(),
                100
            )
            print(f"  {'✓' if result['passed'] else '✗'} {result['name']}: {result['execution_time_ms']}ms (threshold: {result['threshold_ms']}ms)")
            
            # Test 5: Aggregate query (Requirement 9.6)
            recipe = recipes[0]
            result = self.measure_query(
                "Aggregate ratings query",
                lambda s: s.query(
                    func.avg(RecipeRating.rating).label("avg_rating"),
                    func.count(RecipeRating.id).label("count")
                ).filter(RecipeRating.recipe_id == recipe.id).first(),
                50
            )
            print(f"  {'✓' if result['passed'] else '✗'} {result['name']}: {result['execution_time_ms']}ms (threshold: {result['threshold_ms']}ms)")
            
            # Test 6: Pagination (Requirement 9.5)
            result = self.measure_query(
                "Paginated query",
                lambda s: s.query(Recipe).filter(
                    Recipe.visibility == "public"
                ).order_by(Recipe.created_at.desc()).offset(20).limit(20).all(),
                100
            )
            print(f"  {'✓' if result['passed'] else '✗'} {result['name']}: {result['execution_time_ms']}ms (threshold: {result['threshold_ms']}ms)")
            
            # Test 7: Specific columns vs all columns (Requirement 9.6)
            print("\n" + "-"*70)
            print("COLUMN SELECTION COMPARISON")
            print("-"*70)
            
            result_all = self.measure_query(
                "Query all columns",
                lambda s: s.query(Recipe).limit(100).all(),
                200
            )
            
            result_specific = self.measure_query(
                "Query specific columns",
                lambda s: s.query(Recipe.id, Recipe.title, Recipe.user_id).limit(100).all(),
                200
            )
            
            improvement = ((result_all['execution_time_ms'] - result_specific['execution_time_ms']) / 
                          result_all['execution_time_ms'] * 100)
            
            print(f"  All columns: {result_all['execution_time_ms']}ms")
            print(f"  Specific columns: {result_specific['execution_time_ms']}ms")
            print(f"  Improvement: {improvement:.1f}%")
            
            # Test index usage
            print("\n" + "-"*70)
            print("INDEX USAGE VERIFICATION")
            print("-"*70)
            
            # Verify user_id index (Requirement 9.1)
            query = self.session.query(Recipe).filter(Recipe.user_id == user.id)
            result = self.verify_index_usage("user_id index on recipes", query, "user_id")
            print(f"  {'✓' if result['index_used'] else '✗'} {result['name']}: {'Used' if result['index_used'] else 'Not used'}")
            
            # Verify compound index (Requirement 9.3)
            query = self.session.query(Recipe).filter(
                Recipe.user_id == user.id
            ).order_by(Recipe.created_at.desc())
            result = self.verify_index_usage("compound index (user_id, created_at)", query, "idx_recipe_user_created")
            print(f"  {'✓' if result['index_used'] else '✗'} {result['name']}: {'Used' if result['index_used'] else 'Not used'}")
            
            # Verify visibility index (Requirement 9.1)
            query = self.session.query(Recipe).filter(Recipe.visibility == "public")
            result = self.verify_index_usage("visibility index", query, "visibility")
            print(f"  {'✓' if result['index_used'] else '✗'} {result['name']}: {'Used' if result['index_used'] else 'Not used'}")
            
            # Check for FULLTEXT index (Requirement 9.2)
            print("\n" + "-"*70)
            print("FULLTEXT INDEX VERIFICATION")
            print("-"*70)
            
            try:
                result = self.session.execute(text("SHOW INDEX FROM recipes WHERE Index_type = 'FULLTEXT'"))
                fulltext_indexes = result.fetchall()
                
                if fulltext_indexes:
                    print(f"  ✓ FULLTEXT indexes found on recipes table:")
                    for idx in fulltext_indexes:
                        print(f"    - {idx}")
                else:
                    print(f"  ✗ No FULLTEXT indexes found on recipes table")
                    print(f"    Note: FULLTEXT indexes should be created on title and ingredients columns")
            except Exception as e:
                print(f"  ✗ Error checking FULLTEXT indexes: {e}")
            
            # Generate summary report
            print("\n" + "="*70)
            print("PERFORMANCE SUMMARY")
            print("="*70)
            
            passed_tests = sum(1 for r in self.results if isinstance(r.get('passed'), bool) and r['passed'])
            total_tests = sum(1 for r in self.results if 'passed' in r)
            
            print(f"\nTests Passed: {passed_tests}/{total_tests}")
            print(f"\nDetailed Results:")
            
            for result in self.results:
                if 'execution_time_ms' in result:
                    status = '✓' if result['passed'] else '✗'
                    print(f"  {status} {result['name']}: {result['execution_time_ms']}ms (threshold: {result['threshold_ms']}ms)")
                elif 'index_used' in result:
                    status = '✓' if result['index_used'] else '✗'
                    print(f"  {status} {result['name']}: {'Index used' if result['index_used'] else 'Index NOT used'}")
            
            # Save report to file
            report = {
                "timestamp": datetime.now().isoformat(),
                "database_url": database_url.split('@')[1] if '@' in database_url else "mysql",
                "tests_passed": passed_tests,
                "tests_total": total_tests,
                "results": self.results
            }
            
            report_file = "mysql_performance_report.json"
            with open(report_file, "w") as f:
                json.dump(report, indent=2, fp=f)
            
            print(f"\n✓ Report saved to: {report_file}")
            print("="*70 + "\n")
            
        finally:
            # Cleanup
            self.cleanup_test_data(users)
    
    def cleanup_test_data(self, users):
        """Remove test data."""
        print("\nCleaning up test data...")
        try:
            for user in users:
                # Cascade delete will handle related records
                self.session.query(User).filter(User.id == user.id).delete()
            self.session.commit()
            print("✓ Test data cleaned up")
        except Exception as e:
            print(f"✗ Error cleaning up: {e}")
            self.session.rollback()
    
    def close(self):
        """Close database connection."""
        self.session.close()
        self.engine.dispose()


def main():
    """Main entry point."""
    print("\nMySQL Performance Testing Script")
    print("="*70)
    
    # Check database configuration
    database_url = os.environ.get("DATABASE_URL", settings.database_url)
    
    if not database_url.startswith("mysql"):
        print("\n✗ ERROR: MySQL database not configured")
        print(f"  Current DATABASE_URL: {database_url}")
        print("\n  To run performance tests:")
        print("  1. Set DATABASE_URL to a MySQL connection string in .env")
        print("  2. Example: DATABASE_URL=mysql+pymysql://user:password@localhost:3306/recipe_saver")
        print("  3. Run this script again")
        print("\n" + "="*70)
        return 1
    
    print(f"\nDatabase: {database_url.split('@')[1] if '@' in database_url else 'MySQL'}")
    print("="*70)
    
    # Run tests
    tester = PerformanceTester(database_url)
    
    try:
        tester.run_performance_tests()
        return 0
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        tester.close()


if __name__ == "__main__":
    sys.exit(main())
