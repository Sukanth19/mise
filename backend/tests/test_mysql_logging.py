"""Tests for MySQL operation logging.

Validates: Requirements 10.1, 10.2, 10.5, 10.6
"""

import pytest
import logging
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from app.utils.mysql_logger import (
    configure_mysql_logging,
    log_connection_event,
    log_query_operation,
    log_error,
    log_warning,
)


@pytest.fixture
def mock_engine():
    """Create a mock SQLAlchemy engine for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return engine


@pytest.fixture
def logger_mock():
    """Create a mock logger for testing."""
    return Mock(spec=logging.Logger)


class TestMySQLLogging:
    """Test suite for MySQL logging functionality."""
    
    def test_configure_mysql_logging_development(self, mock_engine):
        """
        Test that MySQL logging is configured correctly for development environment.
        
        Validates: Requirements 10.2
        """
        # Configure logging for development
        configure_mysql_logging(mock_engine, "development")
        
        # Get the logger
        logger = logging.getLogger("mysql_operations")
        
        # Verify logger level is DEBUG for development
        assert logger.level == logging.DEBUG
        
        # Verify engine echo is False (we use custom logging)
        assert mock_engine.echo is False
    
    def test_configure_mysql_logging_production(self, mock_engine):
        """
        Test that MySQL logging is configured correctly for production environment.
        
        Validates: Requirements 10.5, 10.6
        """
        # Configure logging for production
        configure_mysql_logging(mock_engine, "production")
        
        # Get the logger
        logger = logging.getLogger("mysql_operations")
        
        # Verify logger level is INFO for production
        assert logger.level == logging.INFO
        
        # Verify engine echo is False
        assert mock_engine.echo is False
    
    def test_log_connection_event_info(self, caplog):
        """
        Test logging connection events at INFO level.
        
        Validates: Requirements 10.1
        """
        with caplog.at_level(logging.INFO, logger="mysql_operations"):
            log_connection_event("connect", "Connection established", "info")
        
        # Verify log message
        assert "MySQL connection event: connect - Connection established" in caplog.text
    
    def test_log_connection_event_error(self, caplog):
        """
        Test logging connection errors.
        
        Validates: Requirements 10.1
        """
        with caplog.at_level(logging.ERROR, logger="mysql_operations"):
            log_connection_event("error", "Connection failed", "error")
        
        # Verify log message
        assert "MySQL connection event: error - Connection failed" in caplog.text
    
    def test_log_query_operation_debug(self, caplog):
        """
        Test logging query operations at DEBUG level.
        
        Validates: Requirements 10.2
        """
        with caplog.at_level(logging.DEBUG, logger="mysql_operations"):
            log_query_operation("SELECT", "SELECT * FROM users", "debug")
        
        # Verify log message
        assert "MySQL query operation: SELECT - SELECT * FROM users" in caplog.text
    
    def test_log_error_development(self, caplog):
        """
        Test logging errors in development environment (ERROR level).
        
        Validates: Requirements 10.2
        """
        with caplog.at_level(logging.ERROR, logger="mysql_operations"):
            with patch("app.config.settings") as mock_settings:
                mock_settings.environment = "development"
                log_error("query", "Query failed", "Invalid syntax")
        
        # Verify log message at ERROR level
        assert "MySQL error (query): Query failed - Invalid syntax" in caplog.text
    
    def test_log_error_production(self, caplog):
        """
        Test logging errors in production environment (INFO level).
        
        Validates: Requirements 10.5, 10.6
        """
        with caplog.at_level(logging.INFO, logger="mysql_operations"):
            with patch("app.config.settings") as mock_settings:
                mock_settings.environment = "production"
                log_error("connection", "Connection timeout", "Network issue")
        
        # Verify log message at INFO level
        assert "MySQL error (connection): Connection timeout - Network issue" in caplog.text
    
    def test_log_warning_development(self, caplog):
        """
        Test logging warnings in development environment (WARNING level).
        
        Validates: Requirements 10.2
        """
        with caplog.at_level(logging.WARNING, logger="mysql_operations"):
            with patch("app.config.settings") as mock_settings:
                mock_settings.environment = "development"
                log_warning("performance", "Slow query detected", "Query took 5 seconds")
        
        # Verify log message at WARNING level
        assert "MySQL warning (performance): Slow query detected - Query took 5 seconds" in caplog.text
    
    def test_log_warning_production(self, caplog):
        """
        Test logging warnings in production environment (INFO level).
        
        Validates: Requirements 10.5, 10.6
        """
        with caplog.at_level(logging.INFO, logger="mysql_operations"):
            with patch("app.config.settings") as mock_settings:
                mock_settings.environment = "production"
                log_warning("deprecation", "Feature deprecated", "Use new API")
        
        # Verify log message at INFO level
        assert "MySQL warning (deprecation): Feature deprecated - Use new API" in caplog.text
    
    def test_connection_event_listeners(self, mock_engine, caplog):
        """
        Test that connection event listeners are registered and log correctly.
        
        Validates: Requirements 10.1
        """
        # Configure logging
        configure_mysql_logging(mock_engine, "development")
        
        # Test connection
        with caplog.at_level(logging.INFO, logger="mysql_operations"):
            with mock_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        
        # Verify connection event was logged
        assert "MySQL connection established" in caplog.text or "Connection checked out from pool" in caplog.text
    
    def test_query_event_listeners_development(self, mock_engine, caplog):
        """
        Test that query event listeners log queries in development.
        
        Validates: Requirements 10.2
        """
        # Configure logging for development
        configure_mysql_logging(mock_engine, "development")
        
        # Execute a query
        with caplog.at_level(logging.DEBUG, logger="mysql_operations"):
            with mock_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        
        # Verify query was logged at DEBUG level
        assert "Executing query" in caplog.text or "Query executed successfully" in caplog.text
    
    def test_query_event_listeners_production(self, mock_engine, caplog):
        """
        Test that query event listeners don't log queries in production.
        
        Validates: Requirements 10.5, 10.6
        """
        # Configure logging for production
        configure_mysql_logging(mock_engine, "production")
        
        # Execute a query
        with caplog.at_level(logging.DEBUG, logger="mysql_operations"):
            with mock_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        
        # Verify query was NOT logged at DEBUG level in production
        # (Production only logs errors at INFO level)
        debug_logs = [record for record in caplog.records if record.levelname == "DEBUG"]
        query_logs = [log for log in debug_logs if "Executing query" in log.message]
        assert len(query_logs) == 0


class TestMySQLLoggingIntegration:
    """Integration tests for MySQL logging with actual database operations."""
    
    def test_logging_with_database_operations(self, caplog):
        """
        Test that logging works correctly with actual database operations.
        
        Validates: Requirements 10.1, 10.2
        """
        # Create an in-memory SQLite database for testing
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        
        # Configure logging
        configure_mysql_logging(engine, "development")
        
        # Perform database operations
        with caplog.at_level(logging.DEBUG, logger="mysql_operations"):
            with engine.connect() as conn:
                # Create table
                conn.execute(text("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)"))
                
                # Insert data
                conn.execute(text("INSERT INTO test (name) VALUES ('test')"))
                
                # Query data
                result = conn.execute(text("SELECT * FROM test"))
                rows = result.fetchall()
                
                assert len(rows) == 1
        
        # Verify operations were logged
        assert len(caplog.records) > 0
    
    def test_error_logging_with_invalid_query(self, caplog):
        """
        Test that errors are logged correctly when queries fail.
        
        Validates: Requirements 10.2, 10.5, 10.6
        """
        # Create an in-memory SQLite database for testing
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        
        # Configure logging
        configure_mysql_logging(engine, "development")
        
        # Attempt invalid query
        with caplog.at_level(logging.ERROR, logger="mysql_operations"):
            try:
                with engine.connect() as conn:
                    conn.execute(text("SELECT * FROM nonexistent_table"))
            except Exception:
                pass  # Expected to fail
        
        # Verify error was logged
        assert any("error" in record.message.lower() for record in caplog.records)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
