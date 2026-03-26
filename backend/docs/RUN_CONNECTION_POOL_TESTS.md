# Quick Start: Connection Pool Performance Tests

## Task 15.2 - Test Connection Pool Performance

This guide provides quick instructions for running the connection pool performance tests.

## Prerequisites

### Option 1: Local MySQL (Recommended for Testing)

```bash
# Install MySQL
sudo apt-get install mysql-server  # Ubuntu/Debian
brew install mysql                  # macOS

# Start MySQL
sudo systemctl start mysql          # Linux
brew services start mysql           # macOS

# Create database
mysql -u root -p
CREATE DATABASE recipe_saver;
EXIT;
```

### Option 2: Docker MySQL (Easiest)

```bash
docker run --name mysql-test \
  -e MYSQL_ROOT_PASSWORD=password \
  -e MYSQL_DATABASE=recipe_saver \
  -p 3306:3306 \
  -d mysql:8.0
```

## Configuration

Update `backend/.env`:

```bash
# For local MySQL
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/recipe_saver

# For Docker MySQL
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/recipe_saver
```

## Run Tests

```bash
cd backend

# Run all connection pool tests
python -m pytest tests/test_connection_pool_performance.py -v -s

# Run specific test
python -m pytest tests/test_connection_pool_performance.py::TestConnectionPoolPerformance::test_concurrent_connections_100 -v -s
```

## What Gets Tested

1. **100 Concurrent Connections** - Verifies pool handles load without exhaustion
2. **Sustained Load** - 250 requests across 5 waves
3. **Throughput & Latency** - Measures requests/second and response times
4. **Error Recovery** - Pool recovery after connection errors
5. **Stress Test** - 3 rapid bursts of 100 connections
6. **Configuration** - Verifies pool_size=10, max_overflow=20
7. **Pool Status** - Health check and connection availability

## Expected Results

```
✓ All 100 concurrent connections succeed
✓ Throughput > 10 requests/second (typically 40-50 req/s)
✓ Average latency < 1000ms (typically 80-100ms)
✓ Pool recovers from errors
✓ Configuration matches expected values
```

## If Tests Are Skipped

If you see `SKIPPED - Connection pool tests only run with MySQL`, it means:
- DATABASE_URL is not set to a MySQL connection string
- Update `.env` file with MySQL connection string (see Configuration above)

## Troubleshooting

### Connection Refused
```bash
# Check if MySQL is running
sudo systemctl status mysql  # Linux
brew services list           # macOS

# Start MySQL if not running
sudo systemctl start mysql   # Linux
brew services start mysql    # macOS
```

### Access Denied
```bash
# Test connection manually
mysql -u root -p

# If password is wrong, reset it or update .env
```

### Too Many Connections
```sql
-- Connect to MySQL
mysql -u root -p

-- Check current limit
SHOW VARIABLES LIKE 'max_connections';

-- Increase limit
SET GLOBAL max_connections = 200;
```

## Performance Benchmarks

| Metric | Target | Typical |
|--------|--------|---------|
| Concurrent connections | 100 | ✓ All succeed |
| Throughput | > 10 req/s | 40-50 req/s |
| Avg latency | < 1000ms | 80-100ms |
| P95 latency | < 2000ms | 150-200ms |
| Error recovery | 100% | ✓ Full recovery |

## Documentation

- **Full Documentation:** `backend/CONNECTION_POOL_PERFORMANCE_TEST.md`
- **Implementation Summary:** `backend/docs/TASK_15_2_CONNECTION_POOL_PERFORMANCE.md`
- **Test File:** `tests/test_connection_pool_performance.py`

## Validates

**Requirement 1.2:** "The Database_Layer SHALL provide connection pooling and session management for MySQL"

---

**Quick Command:**
```bash
# One-liner to run all tests
cd backend && python -m pytest tests/test_connection_pool_performance.py -v -s
```
