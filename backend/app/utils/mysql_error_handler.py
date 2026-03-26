"""MySQL-specific error handlers for Recipe Saver application.

This module provides comprehensive error handling for MySQL operations including:
- Connection errors with descriptive messages
- Query errors (syntax errors, timeouts)
- Constraint violations (foreign key, unique, not null, check)
- Missing record errors (404 responses)
- Transaction errors (deadlock, timeout, rollback)

Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.7
"""

from fastapi import HTTPException, status
from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
    DatabaseError,
    TimeoutError as SQLAlchemyTimeoutError,
    InvalidRequestError,
    ProgrammingError,
)
from pymysql.err import (
    OperationalError as PyMySQLOperationalError,
    IntegrityError as PyMySQLIntegrityError,
    ProgrammingError as PyMySQLProgrammingError,
    InternalError as PyMySQLInternalError,
)
import logging
import re
from typing import Optional, Any

logger = logging.getLogger(__name__)


class MySQLErrorHandler:
    """Centralized MySQL error handling with descriptive messages."""
    
    # MySQL error codes
    ER_DUP_ENTRY = 1062
    ER_NO_REFERENCED_ROW = 1452
    ER_NO_REFERENCED_ROW_2 = 1216
    ER_ROW_IS_REFERENCED = 1451
    ER_ROW_IS_REFERENCED_2 = 1217
    ER_BAD_NULL_ERROR = 1048
    ER_CHECK_CONSTRAINT_VIOLATED = 3819
    ER_LOCK_WAIT_TIMEOUT = 1205
    ER_LOCK_DEADLOCK = 1213
    ER_QUERY_TIMEOUT = 3024
    ER_ACCESS_DENIED = 1045
    ER_BAD_DB_ERROR = 1049
    ER_DBACCESS_DENIED = 1044
    ER_PARSE_ERROR = 1064
    
    @staticmethod
    def handle_connection_error(error: Exception, connection_string: Optional[str] = None) -> HTTPException:
        """
        Handle MySQL connection errors with descriptive messages.
        
        Args:
            error: The connection error exception
            connection_string: Optional connection string (sanitized for logging)
            
        Returns:
            HTTPException with appropriate status code and message
            
        Validates: Requirements 10.1
        """
        error_msg = str(error)
        
        # Access denied (authentication failure)
        if "Access denied" in error_msg or hasattr(error, 'args') and error.args[0] == MySQLErrorHandler.ER_ACCESS_DENIED:
            logger.error(f"MySQL authentication failed: {error_msg}")
            return HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database authentication failed. Please check credentials."
            )
        
        # Unknown database
        if "Unknown database" in error_msg or hasattr(error, 'args') and error.args[0] == MySQLErrorHandler.ER_BAD_DB_ERROR:
            logger.error(f"MySQL database not found: {error_msg}")
            return HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database not found. Please verify database configuration."
            )
        
        # Connection refused (MySQL server not running)
        if "Connection refused" in error_msg or "Can't connect" in error_msg:
            logger.error(f"MySQL server not accessible: {error_msg}")
            return HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database server is not accessible. Please try again later."
            )
        
        # Connection timeout
        if "timeout" in error_msg.lower():
            logger.error(f"MySQL connection timeout: {error_msg}")
            return HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection timeout. Please try again later."
            )
        
        # Generic connection error
        logger.error(f"MySQL connection error: {error_msg}")
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection error. Please try again later."
        )
    
    @staticmethod
    def handle_query_error(error: Exception, query: Optional[str] = None) -> HTTPException:
        """
        Handle MySQL query errors (syntax errors, timeouts).
        
        Args:
            error: The query error exception
            query: Optional query string (for logging)
            
        Returns:
            HTTPException with appropriate status code and message
            
        Validates: Requirements 10.2
        """
        error_msg = str(error)
        
        # Query timeout
        if isinstance(error, SQLAlchemyTimeoutError) or hasattr(error, 'args') and error.args[0] == MySQLErrorHandler.ER_QUERY_TIMEOUT:
            logger.error(f"MySQL query timeout: {error_msg}")
            return HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Query timeout. The operation took too long to complete."
            )
        
        # Syntax error
        if isinstance(error, (ProgrammingError, PyMySQLProgrammingError)) or hasattr(error, 'args') and error.args[0] == MySQLErrorHandler.ER_PARSE_ERROR:
            logger.error(f"MySQL syntax error: {error_msg}")
            if query:
                logger.debug(f"Query: {query}")
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid query syntax. Please check your request parameters."
            )
        
        # Lock wait timeout
        if hasattr(error, 'args') and error.args[0] == MySQLErrorHandler.ER_LOCK_WAIT_TIMEOUT:
            logger.error(f"MySQL lock wait timeout: {error_msg}")
            return HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database is busy. Please try again in a moment."
            )
        
        # Generic query error
        logger.error(f"MySQL query error: {error_msg}")
        if query:
            logger.debug(f"Query: {query}")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request."
        )
    
    @staticmethod
    def handle_constraint_violation(error: IntegrityError) -> HTTPException:
        """
        Handle MySQL constraint violations with descriptive messages.
        
        Handles:
        - Foreign key constraint violations
        - Unique constraint violations
        - Not null constraint violations
        - Check constraint violations
        
        Args:
            error: The IntegrityError exception
            
        Returns:
            HTTPException with appropriate status code and descriptive message
            
        Validates: Requirements 10.3
        """
        error_msg = str(error.orig) if hasattr(error, 'orig') else str(error)
        
        # Foreign key constraint violation
        if "foreign key constraint" in error_msg.lower() or \
           (hasattr(error.orig, 'args') and error.orig.args[0] in [
               MySQLErrorHandler.ER_NO_REFERENCED_ROW,
               MySQLErrorHandler.ER_NO_REFERENCED_ROW_2,
               MySQLErrorHandler.ER_ROW_IS_REFERENCED,
               MySQLErrorHandler.ER_ROW_IS_REFERENCED_2
           ]):
            
            # Extract constraint name if available
            constraint_match = re.search(r"CONSTRAINT `([^`]+)`", error_msg)
            constraint_name = constraint_match.group(1) if constraint_match else "unknown"
            
            # Extract table and column information
            table_match = re.search(r"table `([^`]+)`", error_msg)
            table_name = table_match.group(1) if table_match else "unknown"
            
            logger.error(f"Foreign key constraint violation: {constraint_name} on table {table_name}")
            
            # Provide user-friendly message based on constraint
            if "delete" in error_msg.lower() or str(MySQLErrorHandler.ER_ROW_IS_REFERENCED) in error_msg:
                detail = "Cannot delete this record because it is referenced by other records."
            else:
                detail = "Referenced record does not exist. Please verify the related data."
            
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=detail
            )
        
        # Unique constraint violation
        if "duplicate entry" in error_msg.lower() or "unique constraint" in error_msg.lower() or \
           (hasattr(error.orig, 'args') and error.orig.args[0] == MySQLErrorHandler.ER_DUP_ENTRY):
            
            # Extract the duplicate value and key name
            dup_match = re.search(r"Duplicate entry '([^']+)' for key '([^']+)'", error_msg)
            if dup_match:
                dup_value = dup_match.group(1)
                key_name = dup_match.group(2)
                logger.error(f"Unique constraint violation: {key_name} = {dup_value}")
                
                # Provide user-friendly message based on key name
                if "username" in key_name.lower():
                    detail = "Username already exists. Please choose a different username."
                elif "email" in key_name.lower():
                    detail = "Email already exists. Please use a different email."
                elif "rating" in key_name.lower():
                    detail = "You have already rated this recipe."
                elif "like" in key_name.lower():
                    detail = "You have already liked this recipe."
                else:
                    detail = f"A record with this {key_name} already exists."
            else:
                logger.error(f"Unique constraint violation: {error_msg}")
                detail = "A record with this value already exists."
            
            return HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=detail
            )
        
        # Not null constraint violation
        if "cannot be null" in error_msg.lower() or \
           (hasattr(error.orig, 'args') and error.orig.args[0] == MySQLErrorHandler.ER_BAD_NULL_ERROR):
            
            # Extract column name
            column_match = re.search(r"Column '([^']+)'", error_msg)
            column_name = column_match.group(1) if column_match else "unknown"
            
            logger.error(f"Not null constraint violation: {column_name}")
            
            return HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Required field '{column_name}' cannot be empty."
            )
        
        # Check constraint violation
        if "check constraint" in error_msg.lower() or \
           (hasattr(error.orig, 'args') and error.orig.args[0] == MySQLErrorHandler.ER_CHECK_CONSTRAINT_VIOLATED):
            
            # Extract constraint name
            constraint_match = re.search(r"constraint `([^`]+)`", error_msg)
            constraint_name = constraint_match.group(1) if constraint_match else "unknown"
            
            logger.error(f"Check constraint violation: {constraint_name}")
            
            # Provide user-friendly message based on constraint
            if "rating" in constraint_name.lower():
                detail = "Rating must be between 1 and 5."
            else:
                detail = f"Data validation failed: {constraint_name}"
            
            return HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=detail
            )
        
        # Generic integrity error
        logger.error(f"Integrity constraint violation: {error_msg}")
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data integrity constraint violated. Please check your input."
        )
    
    @staticmethod
    def handle_not_found(resource_type: str, resource_id: Any) -> HTTPException:
        """
        Handle missing record errors with 404 responses.
        
        Args:
            resource_type: Type of resource (e.g., "Recipe", "User", "Collection")
            resource_id: ID of the missing resource
            
        Returns:
            HTTPException with 404 status code and descriptive message
            
        Validates: Requirements 10.4
        """
        logger.warning(f"{resource_type} not found: id={resource_id}")
        
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource_type} not found."
        )
    
    @staticmethod
    def handle_transaction_error(error: Exception) -> HTTPException:
        """
        Handle MySQL transaction errors (deadlock, timeout, rollback).
        
        Args:
            error: The transaction error exception
            
        Returns:
            HTTPException with appropriate status code and message
            
        Validates: Requirements 10.7
        """
        error_msg = str(error.orig) if hasattr(error, 'orig') else str(error)
        
        # Deadlock detected
        if "deadlock" in error_msg.lower() or \
           (hasattr(error, 'orig') and hasattr(error.orig, 'args') and error.orig.args[0] == MySQLErrorHandler.ER_LOCK_DEADLOCK):
            logger.error(f"MySQL deadlock detected: {error_msg}")
            return HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database deadlock detected. Please retry your request."
            )
        
        # Lock wait timeout
        if "lock wait timeout" in error_msg.lower() or \
           (hasattr(error, 'orig') and hasattr(error.orig, 'args') and error.orig.args[0] == MySQLErrorHandler.ER_LOCK_WAIT_TIMEOUT):
            logger.error(f"MySQL lock wait timeout: {error_msg}")
            return HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database is busy. Please try again in a moment."
            )
        
        # Transaction timeout
        if "timeout" in error_msg.lower():
            logger.error(f"MySQL transaction timeout: {error_msg}")
            return HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Transaction timeout. Please try again."
            )
        
        # Rollback failure
        if "rollback" in error_msg.lower():
            logger.critical(f"MySQL rollback failure: {error_msg}")
            return HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Transaction rollback failed. Please contact support."
            )
        
        # Generic transaction error
        logger.error(f"MySQL transaction error: {error_msg}")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transaction error. Please try again."
        )
    
    @staticmethod
    def handle_database_error(error: Exception) -> HTTPException:
        """
        Generic database error handler that routes to specific handlers.
        
        This is the main entry point for handling database errors. It examines
        the error type and routes to the appropriate specific handler.
        
        Args:
            error: Any database-related exception
            
        Returns:
            HTTPException with appropriate status code and message
        """
        # Connection errors
        if isinstance(error, (OperationalError, PyMySQLOperationalError)):
            if "can't connect" in str(error).lower() or "connection" in str(error).lower():
                return MySQLErrorHandler.handle_connection_error(error)
            elif "deadlock" in str(error).lower() or "lock" in str(error).lower():
                return MySQLErrorHandler.handle_transaction_error(error)
            else:
                return MySQLErrorHandler.handle_query_error(error)
        
        # Integrity constraint violations
        if isinstance(error, (IntegrityError, PyMySQLIntegrityError)):
            return MySQLErrorHandler.handle_constraint_violation(error)
        
        # Query syntax errors
        if isinstance(error, (ProgrammingError, PyMySQLProgrammingError)):
            return MySQLErrorHandler.handle_query_error(error)
        
        # Timeout errors
        if isinstance(error, SQLAlchemyTimeoutError):
            return MySQLErrorHandler.handle_query_error(error)
        
        # Generic database error
        logger.error(f"Unhandled database error: {type(error).__name__}: {error}")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="A database error occurred. Please try again later."
        )


def handle_db_operation(operation_name: str):
    """
    Decorator for handling database operations with automatic error handling.
    
    Usage:
        @handle_db_operation("create_recipe")
        def create_recipe(db: Session, recipe_data: dict):
            # Database operations here
            pass
    
    Args:
        operation_name: Name of the operation for logging purposes
        
    Returns:
        Decorated function with error handling
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {operation_name}: {type(e).__name__}: {e}")
                raise MySQLErrorHandler.handle_database_error(e)
        return wrapper
    return decorator
