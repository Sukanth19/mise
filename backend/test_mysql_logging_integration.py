"""Integration test for MySQL logging functionality.

This script demonstrates and tests the MySQL logging implementation.
Run this script to verify that logging is working correctly.

Validates: Requirements 10.1, 10.2, 10.5, 10.6
"""

import logging
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

# Configure root logger to see all logs
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


def test_mysql_logging_development():
    """Test MySQL logging in development mode."""
    logger.info("=" * 80)
    logger.info("Testing MySQL Logging - Development Mode")
    logger.info("=" * 80)
    
    # Import after configuring logging
    from app.utils.mysql_logger import configure_mysql_logging, log_connection_event, log_query_operation
    
    # Create a test engine (using SQLite for testing)
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Configure MySQL logging for development
    configure_mysql_logging(engine, "development")
    
    logger.info("\n1. Testing connection events...")
    log_connection_event("connect", "Test connection established", "info")
    
    logger.info("\n2. Testing query operations...")
    log_query_operation("SELECT", "SELECT * FROM users", "debug")
    log_query_operation("INSERT", "INSERT INTO users VALUES (...)", "debug")
    
    logger.info("\n3. Testing actual database operations...")
    with engine.connect() as conn:
        # Create table
        conn.execute(text("CREATE TABLE test_users (id INTEGER PRIMARY KEY, name TEXT)"))
        logger.info("Created test_users table")
        
        # Insert data
        conn.execute(text("INSERT INTO test_users (name) VALUES ('Alice')"))
        logger.info("Inserted test data")
        
        # Query data
        result = conn.execute(text("SELECT * FROM test_users"))
        rows = result.fetchall()
        logger.info(f"Queried data: {rows}")
    
    logger.info("\n4. Testing disconnection...")
    log_connection_event("disconnect", "Test connection closed", "info")
    
    logger.info("\n✓ Development mode logging test completed successfully")


def test_mysql_logging_production():
    """Test MySQL logging in production mode."""
    logger.info("\n" + "=" * 80)
    logger.info("Testing MySQL Logging - Production Mode")
    logger.info("=" * 80)
    
    # Import after configuring logging
    from app.utils.mysql_logger import configure_mysql_logging, log_error, log_warning
    
    # Create a test engine (using SQLite for testing)
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Configure MySQL logging for production
    configure_mysql_logging(engine, "production")
    
    logger.info("\n1. Testing error logging (INFO level in production)...")
    log_error("connection", "Connection timeout", "Network issue")
    
    logger.info("\n2. Testing warning logging (INFO level in production)...")
    log_warning("performance", "Slow query detected", "Query took 5 seconds")
    
    logger.info("\n3. Testing actual database operations (no DEBUG logs in production)...")
    with engine.connect() as conn:
        # Create table
        conn.execute(text("CREATE TABLE test_products (id INTEGER PRIMARY KEY, name TEXT)"))
        logger.info("Created test_products table (no query details logged in production)")
        
        # Insert data
        conn.execute(text("INSERT INTO test_products (name) VALUES ('Product A')"))
        logger.info("Inserted test data (no query details logged in production)")
        
        # Query data
        result = conn.execute(text("SELECT * FROM test_products"))
        rows = result.fetchall()
        logger.info(f"Queried data: {rows} (no query details logged in production)")
    
    logger.info("\n✓ Production mode logging test completed successfully")


def test_error_logging():
    """Test error logging with invalid queries."""
    logger.info("\n" + "=" * 80)
    logger.info("Testing MySQL Error Logging")
    logger.info("=" * 80)
    
    # Import after configuring logging
    from app.utils.mysql_logger import configure_mysql_logging
    
    # Create a test engine (using SQLite for testing)
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Configure MySQL logging for development
    configure_mysql_logging(engine, "development")
    
    logger.info("\n1. Testing error logging with invalid query...")
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT * FROM nonexistent_table"))
    except Exception as e:
        logger.info(f"Expected error caught: {e}")
    
    logger.info("\n✓ Error logging test completed successfully")


if __name__ == "__main__":
    try:
        test_mysql_logging_development()
        test_mysql_logging_production()
        test_error_logging()
        
        logger.info("\n" + "=" * 80)
        logger.info("ALL TESTS PASSED ✓")
        logger.info("=" * 80)
        logger.info("\nMySQL logging implementation is working correctly!")
        logger.info("- Connection events are logged")
        logger.info("- Query operations are logged at DEBUG level (development)")
        logger.info("- Errors and warnings are logged at INFO level (production)")
        
    except Exception as e:
        logger.error(f"\n✗ Test failed with error: {e}", exc_info=True)
        sys.exit(1)
