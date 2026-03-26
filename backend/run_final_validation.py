#!/usr/bin/env python3
"""
Final validation script for Task 16: MySQL Migration
Runs comprehensive test suite and generates validation report.
"""

import subprocess
import sys
import time
from datetime import datetime

def run_command(cmd, description, timeout=300):
    """Run a command and return results."""
    print(f"\n{'='*80}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*80}\n")
    
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        elapsed = time.time() - start_time
        
        return {
            'description': description,
            'command': cmd,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'elapsed': elapsed,
            'success': result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        return {
            'description': description,
            'command': cmd,
            'returncode': -1,
            'stdout': '',
            'stderr': f'Command timed out after {timeout} seconds',
            'elapsed': elapsed,
            'success': False
        }

def main():
    """Run all validation tests."""
    print(f"\n{'#'*80}")
    print(f"# MySQL Migration - Final Validation (Task 16)")
    print(f"# Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*80}\n")
    
    results = []
    
    # 1. Run unit tests with MySQL
    results.append(run_command(
        'python -m pytest tests/test_mysql_crud_operations.py -v --tb=short',
        '1. MySQL CRUD Unit Tests',
        timeout=60
    ))
    
    # 2. Run property-based tests with MySQL (limited iterations for speed)
    results.append(run_command(
        'python -m pytest tests/test_mysql_crud_properties.py -v --tb=short --hypothesis-max-examples=20',
        '2. MySQL CRUD Property Tests (20 iterations)',
        timeout=120
    ))
    
    # 3. Run query operation tests
    results.append(run_command(
        'python -m pytest tests/test_mysql_query_operations.py -v --tb=short',
        '3. MySQL Query Operations Tests',
        timeout=60
    ))
    
    # 4. Run query property tests
    results.append(run_command(
        'python -m pytest tests/test_mysql_query_properties.py -v --tb=short --hypothesis-max-examples=20',
        '4. MySQL Query Property Tests (20 iterations)',
        timeout=120
    ))
    
    # 5. Run relationship loading tests
    results.append(run_command(
        'python -m pytest tests/test_mysql_relationship_loading.py -v --tb=short',
        '5. MySQL Relationship Loading Tests',
        timeout=60
    ))
    
    # 6. Run error handling tests
    results.append(run_command(
        'python -m pytest tests/test_mysql_error_handlers.py -v --tb=short',
        '6. MySQL Error Handling Tests',
        timeout=60
    ))
    
    # 7. Run error handling property tests
    results.append(run_command(
        'python -m pytest tests/test_mysql_error_handling_properties.py -v --tb=short --hypothesis-max-examples=20',
        '7. MySQL Error Handling Property Tests (20 iterations)',
        timeout=120
    ))
    
    # 8. Run API endpoint tests
    results.append(run_command(
        'python -m pytest tests/test_mysql_api_endpoints.py -v --tb=short',
        '8. MySQL API Endpoint Tests',
        timeout=120
    ))
    
    # 9. Run integration tests
    results.append(run_command(
        'python -m pytest tests/test_integration_workflows.py -v --tb=short',
        '9. Integration Workflow Tests',
        timeout=120
    ))
    
    # 10. Run performance tests
    results.append(run_command(
        'python -m pytest tests/test_mysql_performance.py -v --tb=short',
        '10. MySQL Performance Tests',
        timeout=120
    ))
    
    # 11. Run connection pool performance tests
    results.append(run_command(
        'python -m pytest tests/test_connection_pool_performance.py -v --tb=short',
        '11. Connection Pool Performance Tests',
        timeout=120
    ))
    
    # 12. Check migration script exists and is executable
    results.append(run_command(
        'python migrate_to_mysql.py --help',
        '12. Migration Script Validation',
        timeout=10
    ))
    
    # Print summary
    print(f"\n\n{'#'*80}")
    print(f"# VALIDATION SUMMARY")
    print(f"{'#'*80}\n")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['success'])
    failed_tests = total_tests - passed_tests
    
    print(f"Total Test Suites: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Print detailed results
    print(f"\n{'='*80}")
    print("DETAILED RESULTS")
    print(f"{'='*80}\n")
    
    for i, result in enumerate(results, 1):
        status = "✓ PASS" if result['success'] else "✗ FAIL"
        print(f"{i}. {status} - {result['description']}")
        print(f"   Elapsed: {result['elapsed']:.2f}s")
        if not result['success']:
            print(f"   Error: {result['stderr'][:200]}")
        print()
    
    # Return exit code
    return 0 if failed_tests == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
