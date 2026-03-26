"""MySQL operation logging for Recipe Saver application.

This module provides comprehensive logging for MySQL operations including:
- Connection events (connect, disconnect, errors)
- Query operations at DEBUG level
- Errors and warnings at INFO level for production

Validates: Requirements 10.1, 10.2, 10.5, 10.6
"""

import logging
import os
from typing import Optional
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.pool import Pool


def configure_mysql_logging(engine: Engine, environment: str = "development") -> None:
    """
    Configure logging for MySQL operations based on environment.
    
    Args:
        engine: SQLAlchemy engine instance
        environment: Environment name ("development" or "production")
        
    Validates: Requirements 10.1, 10.2, 10.5, 10.6
    """
    logger = logging.getLogger("mysql_operations")
    
    # Set log level based on environment
    if environment == "production":
        # Production: Only log errors and warnings at INFO level
        logger.setLevel(logging.INFO)
        engine.echo = False
    else:
        # Development: Log all operations at DEBUG level
        logger.setLevel(logging.DEBUG)
        engine.echo = False  # We'll use custom logging instead of SQLAlchemy's echo
    
    # Add handler if not already present
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    # Register event listeners for connection and query logging
    _register_connection_listeners(engine)
    _register_query_listeners(engine, environment)


def _register_connection_listeners(engine: Engine) -> None:
    """
    Register SQLAlchemy event listeners for connection events.
    
    Logs:
    - Connection pool checkout (DEBUG)
    - Connection pool checkin (DEBUG)
    - Connection creation (INFO)
    - Connection errors (ERROR)
    
    Args:
        engine: SQLAlchemy engine instance
        
    Validates: Requirements 10.1
    """
    logger = logging.getLogger("mysql_operations")
    
    @event.listens_for(engine, "connect")
    def receive_connect(dbapi_conn, connection_record):
        """Log when a new connection is established."""
        logger.info(f"MySQL connection established: {dbapi_conn}")
    
    @event.listens_for(Pool, "checkout")
    def receive_checkout(dbapi_conn, connection_record, connection_proxy):
        """Log when a connection is checked out from the pool."""
        logger.debug(f"Connection checked out from pool: {dbapi_conn}")
    
    @event.listens_for(Pool, "checkin")
    def receive_checkin(dbapi_conn, connection_record):
        """Log when a connection is returned to the pool."""
        logger.debug(f"Connection returned to pool: {dbapi_conn}")
    
    @event.listens_for(engine, "close")
    def receive_close(dbapi_conn, connection_record):
        """Log when a connection is closed."""
        logger.info(f"MySQL connection closed: {dbapi_conn}")
    
    @event.listens_for(engine, "close_detached")
    def receive_close_detached(dbapi_conn):
        """Log when a detached connection is closed."""
        logger.info(f"MySQL detached connection closed: {dbapi_conn}")


def _register_query_listeners(engine: Engine, environment: str) -> None:
    """
    Register SQLAlchemy event listeners for query operations.
    
    Logs:
    - Query execution at DEBUG level (development)
    - Query errors at INFO level (production)
    - Query warnings at INFO level (production)
    
    Args:
        engine: SQLAlchemy engine instance
        environment: Environment name ("development" or "production")
        
    Validates: Requirements 10.2, 10.5, 10.6
    """
    logger = logging.getLogger("mysql_operations")
    
    @event.listens_for(engine, "before_cursor_execute")
    def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        """Log query before execution (DEBUG level)."""
        if environment == "development":
            # Log full query details in development
            logger.debug(f"Executing query: {statement}")
            if parameters:
                logger.debug(f"Parameters: {parameters}")
        # In production, we don't log queries at DEBUG level
    
    @event.listens_for(engine, "after_cursor_execute")
    def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        """Log query after execution (DEBUG level)."""
        if environment == "development":
            logger.debug(f"Query executed successfully: {statement[:100]}...")
    
    @event.listens_for(engine, "handle_error")
    def receive_handle_error(exception_context):
        """Log query errors (INFO level for production, ERROR for development)."""
        error = exception_context.original_exception
        statement = exception_context.statement
        
        if environment == "production":
            # Production: Log errors at INFO level
            logger.info(f"MySQL query error: {error}")
            logger.info(f"Failed statement: {statement[:200] if statement else 'N/A'}...")
        else:
            # Development: Log errors at ERROR level with full details
            logger.error(f"MySQL query error: {error}")
            if statement:
                logger.error(f"Failed statement: {statement}")
            if exception_context.parameters:
                logger.error(f"Parameters: {exception_context.parameters}")


def log_connection_event(event_type: str, details: Optional[str] = None, level: str = "info") -> None:
    """
    Log a MySQL connection event.
    
    Args:
        event_type: Type of event (e.g., "connect", "disconnect", "error")
        details: Optional details about the event
        level: Log level ("debug", "info", "warning", "error")
        
    Validates: Requirements 10.1
    """
    logger = logging.getLogger("mysql_operations")
    
    message = f"MySQL connection event: {event_type}"
    if details:
        message += f" - {details}"
    
    log_method = getattr(logger, level.lower(), logger.info)
    log_method(message)


def log_query_operation(operation: str, details: Optional[str] = None, level: str = "debug") -> None:
    """
    Log a MySQL query operation.
    
    Args:
        operation: Type of operation (e.g., "SELECT", "INSERT", "UPDATE", "DELETE")
        details: Optional details about the operation
        level: Log level ("debug", "info", "warning", "error")
        
    Validates: Requirements 10.2
    """
    logger = logging.getLogger("mysql_operations")
    
    message = f"MySQL query operation: {operation}"
    if details:
        message += f" - {details}"
    
    log_method = getattr(logger, level.lower(), logger.debug)
    log_method(message)


def log_error(error_type: str, error_message: str, details: Optional[str] = None) -> None:
    """
    Log a MySQL error at INFO level for production.
    
    Args:
        error_type: Type of error (e.g., "connection", "query", "constraint")
        error_message: Error message
        details: Optional additional details
        
    Validates: Requirements 10.5, 10.6
    """
    logger = logging.getLogger("mysql_operations")
    
    message = f"MySQL error ({error_type}): {error_message}"
    if details:
        message += f" - {details}"
    
    # Determine environment from settings
    try:
        from app.config import settings
        environment = settings.environment
    except Exception:
        environment = "development"
    
    if environment == "production":
        # Production: Log at INFO level
        logger.info(message)
    else:
        # Development: Log at ERROR level
        logger.error(message)


def log_warning(warning_type: str, warning_message: str, details: Optional[str] = None) -> None:
    """
    Log a MySQL warning at INFO level for production.
    
    Args:
        warning_type: Type of warning (e.g., "performance", "deprecation")
        warning_message: Warning message
        details: Optional additional details
        
    Validates: Requirements 10.5, 10.6
    """
    logger = logging.getLogger("mysql_operations")
    
    message = f"MySQL warning ({warning_type}): {warning_message}"
    if details:
        message += f" - {details}"
    
    # Determine environment from settings
    try:
        from app.config import settings
        environment = settings.environment
    except Exception:
        environment = "development"
    
    if environment == "production":
        # Production: Log at INFO level
        logger.info(message)
    else:
        # Development: Log at WARNING level
        logger.warning(message)
