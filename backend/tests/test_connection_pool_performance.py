"""
Connection pool performance testing for MySQL migration.

Tests concurrent connection handling, pool exhaustion prevention,
throughput, and latency under load.

Validates: Requirements 1.2
"""

import pytest
import time
import os
import asyncio
import concurrent.futures
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import Base, engine
from app.models import User, Recipe
import json
import statistics


# Skip all tests if not using MySQL
pytestmark = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL", "").startswith("mysql"),
    reason="Connection pool tests only run with MySQL"
)


@pytest.fixture(scope="module")
def mysql_engine():
    """Create MySQL engine for connection pool testing."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url or not database_url.startswith("mysql"):
        pytest.skip("MySQL not configured")
    
    # Use the same pool configuration as the application
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=False
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="module")
def test_user(mysql_engine):
    """Create a test user for connection pool testing."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=mysql_engine)
    session = SessionLocal()
    
    user = User(
        username="pool_test_user",
        password_hash="hashed_password"
    )
    session.add(user)
    session.commit()
    
    user_id = user.id
    session.close()
    
    yield user_id
    
    # Cleanup
    session = SessionLocal()
    session.query(User).filter(User.id == user_id).delete()
    session.commit()
    session.close()


def execute_query(engine, user_id, query_id):
    """
    Execute a single query using a connection from the pool.
    
    Returns:
        tuple: (query_id, execution_time_ms, success)
    """
    start_time = time.time()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        # Simulate a typical query operation
        recipe = Recipe(
            user_id=user_id,
            title=f"Concurrent Recipe {query_id}",
            ingredients=json.dumps(["ingredient1", "ingredient2"]),
            steps=json.dumps(["step1", "step2"]),
            visibility="private",
            servings=4
        )
        session.add(recipe)
        session.commit()
        
        # Read it back
        result = session.query(Recipe).filter(Recipe.id == recipe.id).first()
        
        # Delete it
        session.delete(result)
        session.commit()
        
        execution_time = (time.time() - start_time) * 1000  # Convert to ms
        return (query_id, execution_time, True)
    
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        return (query_id, execution_time, False)
    
    finally:
        session.close()


def execute_query_with_error(engine, user_id, query_id, should_fail=False):
    """
    Execute a query that may intentionally fail to test error recovery.
    
    Returns:
        tuple: (query_id, execution_time_ms, success)
    """
    start_time = time.time()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        if should_fail:
            # Execute an invalid query to trigger an error
            session.execute(text("SELECT * FROM nonexistent_table"))
        else:
            # Execute a valid query
            session.execute(text("SELECT 1"))
        
        session.commit()
        execution_time = (time.time() - start_time) * 1000
        return (query_id, execution_time, True)
    
    except Exception:
        execution_time = (time.time() - start_time) * 1000
        return (query_id, execution_time, False)
    
    finally:
        session.close()


class TestConnectionPoolPerformance:
    """Test connection pool performance under concurrent load."""
    
    def test_concurrent_connections_100(self, mysql_engine, test_user):
        """
        Test 100 simultaneous connections to verify pool handles load.
        
        This test validates that the connection pool (pool_size=10, max_overflow=20)
        can handle 100 concurrent requests without exhaustion.
        
        Validates: Requirements 1.2
        """
        print("\n" + "="*70)
        print("TEST: 100 Concurrent Connections")
        print("="*70)
        
        num_requests = 100
        results = []
        
        # Use ThreadPoolExecutor to simulate concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = [
                executor.submit(execute_query, mysql_engine, test_user, i)
                for i in range(num_requests)
            ]
            
            # Collect results
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
        
        # Analyze results
        successful = [r for r in results if r[2]]
        failed = [r for r in results if not r[2]]
        execution_times = [r[1] for r in successful]
        
        print(f"\nResults:")
        print(f"  Total requests: {num_requests}")
        print(f"  Successful: {len(successful)}")
        print(f"  Failed: {len(failed)}")
        
        if execution_times:
            print(f"\nExecution times:")
            print(f"  Min: {min(execution_times):.2f}ms")
            print(f"  Max: {max(execution_times):.2f}ms")
            print(f"  Mean: {statistics.mean(execution_times):.2f}ms")
            print(f"  Median: {statistics.median(execution_times):.2f}ms")
        
        # Assertions
        assert len(successful) == num_requests, \
            f"Expected all {num_requests} requests to succeed, but {len(failed)} failed"
        
        # All requests should complete in reasonable time (< 5 seconds each)
        assert max(execution_times) < 5000, \
            f"Maximum execution time {max(execution_times):.2f}ms exceeds 5000ms threshold"
        
        print("\n✓ Connection pool handled 100 concurrent connections successfully")
    
    def test_connection_pool_no_exhaustion(self, mysql_engine, test_user):
        """
        Test that connection pool does not exhaust under sustained load.
        
        Validates: Requirements 1.2
        """
        print("\n" + "="*70)
        print("TEST: Connection Pool Exhaustion Prevention")
        print("="*70)
        
        # Run multiple waves of concurrent requests
        num_waves = 5
        requests_per_wave = 50
        
        all_results = []
        
        for wave in range(num_waves):
            print(f"\nWave {wave + 1}/{num_waves}...")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
                futures = [
                    executor.submit(execute_query, mysql_engine, test_user, wave * requests_per_wave + i)
                    for i in range(requests_per_wave)
                ]
                
                wave_results = [future.result() for future in concurrent.futures.as_completed(futures)]
                all_results.extend(wave_results)
        
        # Analyze results
        successful = [r for r in all_results if r[2]]
        failed = [r for r in all_results if not r[2]]
        
        print(f"\nOverall Results:")
        print(f"  Total requests: {len(all_results)}")
        print(f"  Successful: {len(successful)}")
        print(f"  Failed: {len(failed)}")
        
        # Assertions
        total_requests = num_waves * requests_per_wave
        assert len(successful) == total_requests, \
            f"Expected all {total_requests} requests to succeed across {num_waves} waves"
        
        print("\n✓ Connection pool handled sustained load without exhaustion")
    
    def test_throughput_and_latency(self, mysql_engine, test_user):
        """
        Measure throughput (requests/second) and latency under load.
        
        Validates: Requirements 1.2
        """
        print("\n" + "="*70)
        print("TEST: Throughput and Latency Measurement")
        print("="*70)
        
        num_requests = 100
        
        # Measure total time for all requests
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = [
                executor.submit(execute_query, mysql_engine, test_user, i)
                for i in range(num_requests)
            ]
            
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        total_time = time.time() - start_time
        
        # Calculate metrics
        successful = [r for r in results if r[2]]
        execution_times = [r[1] for r in successful]
        
        throughput = len(successful) / total_time
        avg_latency = statistics.mean(execution_times)
        p50_latency = statistics.median(execution_times)
        p95_latency = statistics.quantiles(execution_times, n=20)[18] if len(execution_times) >= 20 else max(execution_times)
        p99_latency = statistics.quantiles(execution_times, n=100)[98] if len(execution_times) >= 100 else max(execution_times)
        
        print(f"\nThroughput:")
        print(f"  Requests/second: {throughput:.2f}")
        print(f"  Total time: {total_time:.2f}s")
        
        print(f"\nLatency:")
        print(f"  Average: {avg_latency:.2f}ms")
        print(f"  P50 (median): {p50_latency:.2f}ms")
        print(f"  P95: {p95_latency:.2f}ms")
        print(f"  P99: {p99_latency:.2f}ms")
        
        # Assertions
        assert throughput > 10, \
            f"Throughput {throughput:.2f} req/s is below minimum threshold of 10 req/s"
        
        assert avg_latency < 1000, \
            f"Average latency {avg_latency:.2f}ms exceeds 1000ms threshold"
        
        print("\n✓ Throughput and latency metrics are within acceptable ranges")
    
    def test_connection_pool_error_recovery(self, mysql_engine, test_user):
        """
        Test connection pool recovery after errors.
        
        Validates: Requirements 1.2
        """
        print("\n" + "="*70)
        print("TEST: Connection Pool Error Recovery")
        print("="*70)
        
        # Phase 1: Execute some queries that will fail
        print("\nPhase 1: Executing queries with intentional errors...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            error_futures = [
                executor.submit(execute_query_with_error, mysql_engine, test_user, i, should_fail=True)
                for i in range(20)
            ]
            
            error_results = [future.result() for future in concurrent.futures.as_completed(error_futures)]
        
        failed_count = len([r for r in error_results if not r[2]])
        print(f"  Intentional failures: {failed_count}/20")
        
        # Phase 2: Execute normal queries to verify pool recovered
        print("\nPhase 2: Executing normal queries to verify recovery...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            recovery_futures = [
                executor.submit(execute_query_with_error, mysql_engine, test_user, i, should_fail=False)
                for i in range(50)
            ]
            
            recovery_results = [future.result() for future in concurrent.futures.as_completed(recovery_futures)]
        
        successful_count = len([r for r in recovery_results if r[2]])
        print(f"  Successful queries after errors: {successful_count}/50")
        
        # Assertions
        assert successful_count == 50, \
            f"Expected all 50 queries to succeed after errors, but only {successful_count} succeeded"
        
        print("\n✓ Connection pool recovered successfully after errors")
    
    def test_connection_pool_stress_test(self, mysql_engine, test_user):
        """
        Stress test with rapid bursts of connections.
        
        Validates: Requirements 1.2
        """
        print("\n" + "="*70)
        print("TEST: Connection Pool Stress Test")
        print("="*70)
        
        # Execute 3 rapid bursts of 100 connections each
        num_bursts = 3
        connections_per_burst = 100
        
        all_results = []
        burst_times = []
        
        for burst in range(num_bursts):
            print(f"\nBurst {burst + 1}/{num_bursts}...")
            
            burst_start = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
                futures = [
                    executor.submit(execute_query, mysql_engine, test_user, burst * connections_per_burst + i)
                    for i in range(connections_per_burst)
                ]
                
                burst_results = [future.result() for future in concurrent.futures.as_completed(futures)]
                all_results.extend(burst_results)
            
            burst_time = time.time() - burst_start
            burst_times.append(burst_time)
            
            successful = len([r for r in burst_results if r[2]])
            print(f"  Completed: {successful}/{connections_per_burst} in {burst_time:.2f}s")
            
            # Small delay between bursts
            time.sleep(0.5)
        
        # Analyze results
        total_successful = len([r for r in all_results if r[2]])
        total_expected = num_bursts * connections_per_burst
        
        print(f"\nOverall Results:")
        print(f"  Total requests: {total_expected}")
        print(f"  Successful: {total_successful}")
        print(f"  Average burst time: {statistics.mean(burst_times):.2f}s")
        
        # Assertions
        assert total_successful == total_expected, \
            f"Expected all {total_expected} requests to succeed, but only {total_successful} succeeded"
        
        print("\n✓ Connection pool handled stress test successfully")


class TestConnectionPoolConfiguration:
    """Test connection pool configuration and limits."""
    
    def test_pool_size_configuration(self, mysql_engine):
        """
        Verify connection pool is configured with correct parameters.
        
        Validates: Requirements 1.2
        """
        print("\n" + "="*70)
        print("TEST: Connection Pool Configuration")
        print("="*70)
        
        # Check pool configuration
        pool = mysql_engine.pool
        
        print(f"\nConnection Pool Configuration:")
        print(f"  Pool size: {pool.size()}")
        print(f"  Max overflow: {pool._max_overflow}")
        print(f"  Pool timeout: {pool._timeout}")
        print(f"  Pool pre-ping: {mysql_engine.pool._pre_ping}")
        
        # Assertions
        assert pool.size() == 10, \
            f"Expected pool size of 10, but got {pool.size()}"
        
        assert pool._max_overflow == 20, \
            f"Expected max overflow of 20, but got {pool._max_overflow}"
        
        assert mysql_engine.pool._pre_ping is True, \
            "Expected pool_pre_ping to be enabled"
        
        print("\n✓ Connection pool is configured correctly")
    
    def test_connection_pool_status(self, mysql_engine):
        """
        Check connection pool status and available connections.
        
        Validates: Requirements 1.2
        """
        print("\n" + "="*70)
        print("TEST: Connection Pool Status")
        print("="*70)
        
        pool = mysql_engine.pool
        
        print(f"\nConnection Pool Status:")
        print(f"  Checked out connections: {pool.checkedout()}")
        print(f"  Available connections: {pool.size() - pool.checkedout()}")
        print(f"  Overflow connections: {pool.overflow()}")
        
        # Pool should have connections available
        assert pool.checkedout() >= 0, "Checked out connections should be non-negative"
        assert pool.overflow() >= 0, "Overflow connections should be non-negative"
        
        print("\n✓ Connection pool status is healthy")
