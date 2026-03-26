#!/usr/bin/env python3
"""
Query Optimization Script for MySQL Migration

This script:
1. Enables MySQL slow query logging
2. Analyzes existing queries for optimization opportunities
3. Identifies missing indexes
4. Optimizes JOIN operations
5. Generates optimization recommendations

Validates: Requirements 9.4, 9.7
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from typing import List, Dict, Any
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base
from app.models import (
    User, Recipe, Collection, CollectionRecipe, MealPlan, 
    RecipeRating, RecipeNote, NutritionFacts, DietaryLabel, 
    AllergenWarning, ShoppingList, ShoppingListItem
)


class QueryOptimizer:
    """Analyzes and optimizes MySQL queries."""
    
    def __init__(self, database_url: str):
        """Initialize optimizer with database connection."""
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.inspector = inspect(self.engine)
    
    def enable_slow_query_log(self, threshold_seconds: float = 1.0):
        """
        Enable MySQL slow query logging.
        
        Args:
            threshold_seconds: Queries slower than this will be logged
        """
        print(f"\n{'='*70}")
        print("ENABLING SLOW QUERY LOGGING")
        print(f"{'='*70}")
        
        with self.engine.connect() as conn:
            try:
                # Enable slow query log
                conn.execute(text("SET GLOBAL slow_query_log = 'ON'"))
                
                # Set threshold
                conn.execute(text(f"SET GLOBAL long_query_time = {threshold_seconds}"))
                
                # Get log file location
                result = conn.execute(text("SHOW VARIABLES LIKE 'slow_query_log_file'"))
                log_file = result.fetchone()
                
                print(f"✓ Slow query logging enabled")
                print(f"  Threshold: {threshold_seconds} seconds")
                print(f"  Log file: {log_file[1] if log_file else 'default location'}")
                
                # Show current settings
                result = conn.execute(text("SHOW VARIABLES LIKE 'slow_query%'"))
                print(f"\nCurrent settings:")
                for row in result:
                    print(f"  {row[0]}: {row[1]}")
                
                conn.commit()
                
            except Exception as e:
                print(f"✗ Failed to enable slow query logging: {e}")
                print(f"  Note: You may need SUPER privilege to modify global variables")
                print(f"  Alternative: Add to my.cnf:")
                print(f"    slow_query_log = 1")
                print(f"    long_query_time = {threshold_seconds}")
    
    def analyze_table_indexes(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Analyze indexes on all tables.
        
        Returns:
            Dictionary mapping table names to their indexes
        """
        print(f"\n{'='*70}")
        print("ANALYZING TABLE INDEXES")
        print(f"{'='*70}")
        
        table_indexes = {}
        
        for table_name in self.inspector.get_table_names():
            indexes = self.inspector.get_indexes(table_name)
            foreign_keys = self.inspector.get_foreign_keys(table_name)
            
            table_indexes[table_name] = {
                'indexes': indexes,
                'foreign_keys': foreign_keys
            }
            
            print(f"\nTable: {table_name}")
            print(f"  Indexes: {len(indexes)}")
            for idx in indexes:
                cols = ', '.join(idx['column_names'])
                unique = " (UNIQUE)" if idx.get('unique') else ""
                print(f"    - {idx['name']}: {cols}{unique}")
            
            print(f"  Foreign Keys: {len(foreign_keys)}")
            for fk in foreign_keys:
                print(f"    - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
        
        return table_indexes
    
    def check_missing_indexes(self, table_indexes: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Identify missing indexes based on foreign keys and common query patterns.
        
        Args:
            table_indexes: Dictionary of table indexes from analyze_table_indexes
            
        Returns:
            List of recommended indexes to add
        """
        print(f"\n{'='*70}")
        print("CHECKING FOR MISSING INDEXES")
        print(f"{'='*70}")
        
        recommendations = []
        
        # Check each table
        for table_name, info in table_indexes.items():
            indexed_columns = set()
            
            # Collect all indexed columns
            for idx in info['indexes']:
                for col in idx['column_names']:
                    indexed_columns.add(col)
            
            # Check foreign keys are indexed
            for fk in info['foreign_keys']:
                for col in fk['constrained_columns']:
                    if col not in indexed_columns:
                        recommendations.append({
                            'table': table_name,
                            'column': col,
                            'reason': f'Foreign key to {fk["referred_table"]}.{fk["referred_columns"]}',
                            'type': 'single',
                            'priority': 'HIGH'
                        })
        
        # Check for common query patterns that need indexes
        common_patterns = [
            # Recipes table
            {'table': 'recipes', 'columns': ['user_id', 'created_at'], 'reason': 'User recipes sorted by date', 'type': 'compound'},
            {'table': 'recipes', 'columns': ['visibility'], 'reason': 'Public recipe queries', 'type': 'single'},
            {'table': 'recipes', 'columns': ['user_id', 'visibility'], 'reason': 'User recipes by visibility', 'type': 'compound'},
            
            # Collections table
            {'table': 'collections', 'columns': ['user_id', 'created_at'], 'reason': 'User collections sorted by date', 'type': 'compound'},
            {'table': 'collections', 'columns': ['share_token'], 'reason': 'Shared collection lookup', 'type': 'single'},
            
            # Meal plans table
            {'table': 'meal_plans', 'columns': ['user_id', 'meal_date'], 'reason': 'User meal plans by date range', 'type': 'compound'},
            {'table': 'meal_plans', 'columns': ['meal_date'], 'reason': 'Meal plans by date', 'type': 'single'},
            
            # Recipe ratings table
            {'table': 'recipe_ratings', 'columns': ['recipe_id', 'user_id'], 'reason': 'Unique rating constraint', 'type': 'compound'},
            
            # Recipe notes table
            {'table': 'recipe_notes', 'columns': ['recipe_id', 'user_id'], 'reason': 'User notes on recipe', 'type': 'compound'},
            
            # Shopping lists table
            {'table': 'shopping_lists', 'columns': ['share_token'], 'reason': 'Shared list lookup', 'type': 'single'},
        ]
        
        for pattern in common_patterns:
            table_name = pattern['table']
            if table_name not in table_indexes:
                continue
            
            columns = pattern['columns'] if isinstance(pattern['columns'], list) else [pattern['columns']]
            
            # Check if this index exists
            index_exists = False
            for idx in table_indexes[table_name]['indexes']:
                idx_cols = idx['column_names']
                if pattern['type'] == 'compound':
                    # For compound indexes, check if columns match in order
                    if idx_cols == columns:
                        index_exists = True
                        break
                else:
                    # For single column indexes
                    if columns[0] in idx_cols:
                        index_exists = True
                        break
            
            if not index_exists:
                recommendations.append({
                    'table': table_name,
                    'columns': columns,
                    'reason': pattern['reason'],
                    'type': pattern['type'],
                    'priority': 'MEDIUM'
                })
        
        # Print recommendations
        if recommendations:
            print(f"\n✗ Found {len(recommendations)} missing indexes:")
            for rec in recommendations:
                cols = ', '.join(rec['columns']) if isinstance(rec['columns'], list) else rec['column']
                print(f"\n  [{rec['priority']}] {rec['table']}")
                print(f"    Columns: {cols}")
                print(f"    Reason: {rec['reason']}")
                print(f"    Type: {rec['type']}")
        else:
            print(f"\n✓ All recommended indexes are present")
        
        return recommendations
    
    def analyze_join_queries(self) -> List[Dict[str, Any]]:
        """
        Analyze common JOIN queries for optimization opportunities.
        
        Returns:
            List of JOIN optimization recommendations
        """
        print(f"\n{'='*70}")
        print("ANALYZING JOIN OPERATIONS")
        print(f"{'='*70}")
        
        optimizations = []
        
        # Common JOIN patterns in the application
        join_queries = [
            {
                'name': 'Collection with Recipes',
                'query': """
                    SELECT c.*, cr.*, r.*
                    FROM collections c
                    LEFT JOIN collection_recipes cr ON c.id = cr.collection_id
                    LEFT JOIN recipes r ON cr.recipe_id = r.id
                    WHERE c.user_id = 1
                    LIMIT 10
                """,
                'expected_indexes': ['collections.user_id', 'collection_recipes.collection_id', 'collection_recipes.recipe_id']
            },
            {
                'name': 'Meal Plans with Recipes',
                'query': """
                    SELECT mp.*, r.*
                    FROM meal_plans mp
                    INNER JOIN recipes r ON mp.recipe_id = r.id
                    WHERE mp.user_id = 1 AND mp.meal_date >= CURDATE()
                    ORDER BY mp.meal_date
                    LIMIT 20
                """,
                'expected_indexes': ['meal_plans.user_id', 'meal_plans.meal_date', 'meal_plans.recipe_id']
            },
            {
                'name': 'Recipe with Nutrition Facts',
                'query': """
                    SELECT r.*, nf.*
                    FROM recipes r
                    LEFT JOIN nutrition_facts nf ON r.id = nf.recipe_id
                    WHERE r.user_id = 1
                    LIMIT 20
                """,
                'expected_indexes': ['recipes.user_id', 'nutrition_facts.recipe_id']
            },
            {
                'name': 'Recipe with Ratings (Aggregate)',
                'query': """
                    SELECT r.id, r.title, AVG(rr.rating) as avg_rating, COUNT(rr.id) as rating_count
                    FROM recipes r
                    LEFT JOIN recipe_ratings rr ON r.id = rr.recipe_id
                    WHERE r.user_id = 1
                    GROUP BY r.id, r.title
                    HAVING avg_rating >= 4.0
                """,
                'expected_indexes': ['recipes.user_id', 'recipe_ratings.recipe_id']
            },
            {
                'name': 'Shopping List with Items',
                'query': """
                    SELECT sl.*, sli.*
                    FROM shopping_lists sl
                    LEFT JOIN shopping_list_items sli ON sl.id = sli.shopping_list_id
                    WHERE sl.user_id = 1
                """,
                'expected_indexes': ['shopping_lists.user_id', 'shopping_list_items.shopping_list_id']
            }
        ]
        
        with self.engine.connect() as conn:
            for join_info in join_queries:
                print(f"\n{join_info['name']}:")
                print(f"  Query: {join_info['query'].strip()[:100]}...")
                
                try:
                    # Get EXPLAIN output
                    explain_query = text(f"EXPLAIN {join_info['query']}")
                    result = conn.execute(explain_query)
                    explain_rows = result.fetchall()
                    
                    # Analyze EXPLAIN output
                    issues = []
                    for row in explain_rows:
                        table = row[2] if len(row) > 2 else row[0]
                        type_val = row[3] if len(row) > 3 else 'unknown'
                        key = row[5] if len(row) > 5 else None
                        rows = row[8] if len(row) > 8 else 0
                        
                        # Check for full table scans
                        if type_val == 'ALL':
                            issues.append(f"Full table scan on {table} ({rows} rows)")
                        
                        # Check if index is used
                        if key is None and type_val not in ['const', 'system']:
                            issues.append(f"No index used on {table}")
                    
                    if issues:
                        print(f"  ✗ Issues found:")
                        for issue in issues:
                            print(f"    - {issue}")
                        
                        optimizations.append({
                            'query': join_info['name'],
                            'issues': issues,
                            'expected_indexes': join_info['expected_indexes']
                        })
                    else:
                        print(f"  ✓ Query is optimized")
                    
                    # Print EXPLAIN details
                    print(f"  EXPLAIN output:")
                    for row in explain_rows:
                        table = row[2] if len(row) > 2 else row[0]
                        type_val = row[3] if len(row) > 3 else 'unknown'
                        key = row[5] if len(row) > 5 else 'NULL'
                        rows = row[8] if len(row) > 8 else 0
                        print(f"    {table}: type={type_val}, key={key}, rows={rows}")
                
                except Exception as e:
                    print(f"  ✗ Error analyzing query: {e}")
        
        return optimizations
    
    def generate_index_sql(self, recommendations: List[Dict[str, Any]]) -> List[str]:
        """
        Generate SQL statements to create missing indexes.
        
        Args:
            recommendations: List of index recommendations
            
        Returns:
            List of SQL CREATE INDEX statements
        """
        print(f"\n{'='*70}")
        print("GENERATING INDEX CREATION SQL")
        print(f"{'='*70}")
        
        sql_statements = []
        
        for rec in recommendations:
            table = rec['table']
            
            if rec['type'] == 'compound':
                columns = rec['columns']
                col_str = ', '.join(columns)
                index_name = f"idx_{table}_{'_'.join(columns)}"
                sql = f"CREATE INDEX {index_name} ON {table} ({col_str});"
            else:
                column = rec['columns'][0] if isinstance(rec['columns'], list) else rec['column']
                index_name = f"idx_{table}_{column}"
                sql = f"CREATE INDEX {index_name} ON {table} ({column});"
            
            sql_statements.append(sql)
            print(f"\n{sql}")
            print(f"  -- {rec['reason']}")
        
        return sql_statements
    
    def check_fulltext_indexes(self):
        """Check if FULLTEXT indexes exist for search functionality."""
        print(f"\n{'='*70}")
        print("CHECKING FULLTEXT INDEXES")
        print(f"{'='*70}")
        
        with self.engine.connect() as conn:
            # Check for FULLTEXT index on recipes table
            result = conn.execute(text("""
                SELECT INDEX_NAME, COLUMN_NAME, INDEX_TYPE
                FROM INFORMATION_SCHEMA.STATISTICS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'recipes'
                AND INDEX_TYPE = 'FULLTEXT'
            """))
            
            fulltext_indexes = result.fetchall()
            
            if fulltext_indexes:
                print(f"\n✓ Found {len(fulltext_indexes)} FULLTEXT indexes:")
                for idx in fulltext_indexes:
                    print(f"  - {idx[0]}: {idx[1]}")
            else:
                print(f"\n✗ No FULLTEXT indexes found")
                print(f"\nRecommendation:")
                print(f"  CREATE FULLTEXT INDEX idx_recipe_search ON recipes(title, ingredients);")
                print(f"  -- Enables fast full-text search on recipe titles and ingredients")
    
    def generate_optimization_report(self, 
                                    table_indexes: Dict[str, List[Dict[str, Any]]],
                                    missing_indexes: List[Dict[str, Any]],
                                    join_optimizations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate comprehensive optimization report.
        
        Returns:
            Dictionary containing optimization report
        """
        print(f"\n{'='*70}")
        print("OPTIMIZATION REPORT SUMMARY")
        print(f"{'='*70}")
        
        report = {
            'total_tables': len(table_indexes),
            'total_indexes': sum(len(info['indexes']) for info in table_indexes.values()),
            'missing_indexes': len(missing_indexes),
            'join_issues': len(join_optimizations),
            'recommendations': []
        }
        
        # Add missing index recommendations
        for rec in missing_indexes:
            report['recommendations'].append({
                'type': 'missing_index',
                'priority': rec['priority'],
                'table': rec['table'],
                'columns': rec['columns'] if isinstance(rec['columns'], list) else [rec['column']],
                'reason': rec['reason']
            })
        
        # Add JOIN optimization recommendations
        for opt in join_optimizations:
            report['recommendations'].append({
                'type': 'join_optimization',
                'priority': 'HIGH',
                'query': opt['query'],
                'issues': opt['issues'],
                'expected_indexes': opt['expected_indexes']
            })
        
        # Print summary
        print(f"\nTables analyzed: {report['total_tables']}")
        print(f"Existing indexes: {report['total_indexes']}")
        print(f"Missing indexes: {report['missing_indexes']}")
        print(f"JOIN issues: {report['join_issues']}")
        print(f"\nTotal recommendations: {len(report['recommendations'])}")
        
        # Priority breakdown
        high_priority = sum(1 for r in report['recommendations'] if r['priority'] == 'HIGH')
        medium_priority = sum(1 for r in report['recommendations'] if r['priority'] == 'MEDIUM')
        
        print(f"  HIGH priority: {high_priority}")
        print(f"  MEDIUM priority: {medium_priority}")
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: str = "query_optimization_report.json"):
        """Save optimization report to JSON file."""
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n✓ Report saved to {filename}")


def main():
    """Main execution function."""
    # Get database URL from environment
    database_url = os.environ.get("DATABASE_URL")
    
    if not database_url:
        print("Error: DATABASE_URL environment variable not set")
        print("Please set DATABASE_URL to your MySQL connection string")
        sys.exit(1)
    
    if not database_url.startswith("mysql"):
        print("Error: This script is for MySQL databases only")
        print(f"Current DATABASE_URL: {database_url}")
        sys.exit(1)
    
    print(f"\n{'='*70}")
    print("MYSQL QUERY OPTIMIZATION ANALYSIS")
    print(f"{'='*70}")
    print(f"\nDatabase: {database_url.split('@')[1] if '@' in database_url else 'MySQL'}")
    
    # Initialize optimizer
    optimizer = QueryOptimizer(database_url)
    
    # Step 1: Enable slow query logging
    optimizer.enable_slow_query_log(threshold_seconds=1.0)
    
    # Step 2: Analyze table indexes
    table_indexes = optimizer.analyze_table_indexes()
    
    # Step 3: Check for missing indexes
    missing_indexes = optimizer.check_missing_indexes(table_indexes)
    
    # Step 4: Check FULLTEXT indexes
    optimizer.check_fulltext_indexes()
    
    # Step 5: Analyze JOIN queries
    join_optimizations = optimizer.analyze_join_queries()
    
    # Step 6: Generate SQL for missing indexes
    if missing_indexes:
        sql_statements = optimizer.generate_index_sql(missing_indexes)
    
    # Step 7: Generate comprehensive report
    report = optimizer.generate_optimization_report(
        table_indexes,
        missing_indexes,
        join_optimizations
    )
    
    # Step 8: Save report
    optimizer.save_report(report)
    
    print(f"\n{'='*70}")
    print("OPTIMIZATION ANALYSIS COMPLETE")
    print(f"{'='*70}")
    print(f"\nNext steps:")
    print(f"1. Review the generated SQL statements above")
    print(f"2. Apply the recommended indexes to your database")
    print(f"3. Monitor slow query log for additional optimization opportunities")
    print(f"4. Re-run performance tests to verify improvements")


if __name__ == "__main__":
    main()
