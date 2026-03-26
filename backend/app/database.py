"""Database connection management for Recipe Saver application.

Supports SQLAlchemy with MySQL and SQLite.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Optional
import logging
import os
from app.config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy setup
Base = declarative_base()


def _create_engine_with_config(database_url: str):
    """
    Create SQLAlchemy engine with appropriate configuration based on database type.
    
    For MySQL connections, this function also configures comprehensive logging for:
    - Connection events (connect, disconnect, errors)
    - Query operations at DEBUG level
    - Errors and warnings at INFO level for production
    
    Validates: Requirements 10.1, 10.2, 10.5, 10.6
    """
    if database_url.startswith("sqlite"):
        # SQLite-specific configuration
        connect_args = {"check_same_thread": False}
        return create_engine(database_url, connect_args=connect_args)
    elif database_url.startswith("mysql"):
        # MySQL-specific configuration with connection pooling
        engine = create_engine(
            database_url,
            pool_pre_ping=True,  # Verify connections before using
            pool_size=10,
            max_overflow=20,
            echo=False  # We use custom logging instead
        )
        
        # Configure MySQL operation logging
        from app.utils.mysql_logger import configure_mysql_logging, log_connection_event
        
        # Get environment from settings
        environment = settings.environment
        
        try:
            configure_mysql_logging(engine, environment)
            log_connection_event("engine_created", f"MySQL engine created for {database_url.split('@')[1] if '@' in database_url else 'database'}", "info")
        except Exception as e:
            logger.error(f"Failed to configure MySQL logging: {e}")
        
        return engine
    else:
        raise ValueError(f"Unsupported database URL: {database_url}. Only MySQL and SQLite are supported.")


engine = _create_engine_with_config(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Get SQLAlchemy database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def health_check() -> bool:
    """
    Verify database connectivity.
    
    Logs connection health check results.
    
    Returns:
        True if database is accessible, False otherwise
        
    Validates: Requirements 10.1
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.debug("Database health check passed")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        
        # Log connection error with MySQL-specific logging if MySQL
        if settings.database_url.startswith("mysql"):
            from app.utils.mysql_logger import log_connection_event
            log_connection_event("health_check_failed", str(e), "error")
        
        return False

