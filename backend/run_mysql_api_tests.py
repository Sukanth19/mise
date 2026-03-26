#!/usr/bin/env python3
"""
Test runner for API compatibility with MySQL backend.

This script runs all existing API endpoint tests against MySQL to verify:
- All endpoint paths and HTTP methods work correctly (Requirement 6.1)
- Request payloads are accepted as before (Requirement 6.2)
- Response structures match expected schemas (Requirement 6.3)
- HTTP status codes are correct (Requirement 6.4)
- Pagination, filtering, and sorting work correctly (Requirement 6.5)
- Authentication and authorization work correctly (Requirement 6.6)

Task 9.1: Run existing API tests against MySQL
"""
import os
import sys
import subprocess
from sqlalchemy import create_engine, text


def check_mysql_connection():
    """Check if MySQL is accessible."""
    mysql_url = os.environ.get(
        "MYSQL_TEST_URL",
        "mysql+pymysql://root:password@localhost:3306/recipe_saver_test"
    )
    
    try:
        engine = create_engine(mysql_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"✓ MySQL connection successful: {mysql_url}")
        return True
    except Exception as e:
        print(f"✗ MySQL connection failed: {e}")
        print(f"\nPlease ensure MySQL is running and accessible at: {mysql_url}")
        print("\nTo start MySQL with Docker:")
        print("  docker run --name mysql-test -e MYSQL_ROOT_PASSWORD=password -e MYSQL_DATABASE=recipe_saver_test -p 3306:3306 -d mysql:8.0")
        return False


def setup_mysql_schema():
    """Create MySQL schema for testing."""
    mysql_url = os.environ.get(
        "MYSQL_TEST_URL",
        "mysql+pymysql://root:password@localhost:3306/recipe_saver_test"
    )
    
    try:
        from app.database import Base
        
        engine = create_engine(mysql_url)
        
        # Drop all tables
        print("Dropping existing tables...")
        Base.metadata.drop_all(bind=engine)
        
        # Create all tables
        print("Creating MySQL schema...")
        Base.metadata.create_all(bind=engine)
        
        print("✓ MySQL schema created successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to create MySQL schema: {e}")
        return False


def run_endpoint_tests():
    """Run all endpoint tests against MySQL."""
    print("\n" + "="*80)
    print("RUNNING API ENDPOINT TESTS AGAINST MYSQL")
    print("="*80 + "\n")
    
    # List of endpoint test files to run
    endpoint_tests = [
        "tests/test_auth_endpoints.py",
        "tests/test_recipe_endpoints.py",
        "tests/test_collection_endpoints.py",
        "tests/test_rating_endpoints.py",
        "tests/test_note_endpoints.py",
        "tests/test_nutrition_endpoints.py",
        "tests/test_meal_plan_endpoints.py",
        "tests/test_shopping_list_endpoints.py",
        "tests/test_sharing_endpoints.py",
        "tests/test_image_endpoints.py",
    ]
    
    # Set environment to use MySQL
    env = os.environ.copy()
    env["DATABASE_URL"] = env.get(
        "MYSQL_TEST_URL",
        "mysql+pymysql://root:password@localhost:3306/recipe_saver_test"
    )
    env["DATABASE_TYPE"] = "mysql"
    
    results = {}
    total_passed = 0
    total_failed = 0
    
    for test_file in endpoint_tests:
        print(f"\nRunning {test_file}...")
        print("-" * 80)
        
        try:
            result = subprocess.run(
                ["pytest", test_file, "-v", "--tb=short"],
                env=env,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Parse output for pass/fail counts
            output = result.stdout + result.stderr
            
            if result.returncode == 0:
                print(f"✓ {test_file} - ALL TESTS PASSED")
                results[test_file] = "PASSED"
            else:
                print(f"✗ {test_file} - SOME TESTS FAILED")
                results[test_file] = "FAILED"
                print("\nFailure details:")
                print(output[-1000:])  # Print last 1000 chars of output
            
            # Count passed/failed
            if "passed" in output:
                import re
                match = re.search(r'(\d+) passed', output)
                if match:
                    total_passed += int(match.group(1))
            
            if "failed" in output:
                import re
                match = re.search(r'(\d+) failed', output)
                if match:
                    total_failed += int(match.group(1))
        
        except subprocess.TimeoutExpired:
            print(f"✗ {test_file} - TIMEOUT")
            results[test_file] = "TIMEOUT"
        except Exception as e:
            print(f"✗ {test_file} - ERROR: {e}")
            results[test_file] = "ERROR"
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_file, status in results.items():
        status_symbol = "✓" if status == "PASSED" else "✗"
        print(f"{status_symbol} {test_file}: {status}")
    
    print(f"\nTotal: {total_passed} passed, {total_failed} failed")
    
    if total_failed == 0:
        print("\n✓ ALL API ENDPOINT TESTS PASSED WITH MYSQL!")
        return True
    else:
        print(f"\n✗ {total_failed} tests failed. Please review the failures above.")
        return False


def main():
    """Main test runner."""
    print("MySQL API Compatibility Test Runner")
    print("=" * 80)
    
    # Step 1: Check MySQL connection
    print("\nStep 1: Checking MySQL connection...")
    if not check_mysql_connection():
        sys.exit(1)
    
    # Step 2: Setup MySQL schema
    print("\nStep 2: Setting up MySQL schema...")
    if not setup_mysql_schema():
        sys.exit(1)
    
    # Step 3: Run endpoint tests
    print("\nStep 3: Running endpoint tests...")
    success = run_endpoint_tests()
    
    if success:
        print("\n" + "="*80)
        print("✓ TASK 9.1 COMPLETE: All API endpoint tests passed with MySQL!")
        print("="*80)
        sys.exit(0)
    else:
        print("\n" + "="*80)
        print("✗ TASK 9.1 INCOMPLETE: Some tests failed. Please review and fix.")
        print("="*80)
        sys.exit(1)


if __name__ == "__main__":
    main()
