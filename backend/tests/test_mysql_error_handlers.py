"""Unit tests for MySQL error handlers.

Tests all error handling scenarios including:
- Connection errors (authentication, database not found, connection refused, timeout)
- Query errors (syntax errors, timeouts, lock wait timeout)
- Constraint violations (foreign key, unique, not null, check)
- Missing record errors (404 responses)
- Transaction errors (deadlock, timeout, rollback)

Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.7
"""

import pytest
from fastapi import status
from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
    ProgrammingError,
    TimeoutError as SQLAlchemyTimeoutError,
)
from pymysql.err import (
    OperationalError as PyMySQLOperationalError,
    IntegrityError as PyMySQLIntegrityError,
    ProgrammingError as PyMySQLProgrammingError,
)
from app.utils.mysql_error_handler import MySQLErrorHandler


class TestConnectionErrorHandling:
    """Test connection error handling with descriptive messages."""
    
    def test_access_denied_error(self):
        """Test authentication failure error handling."""
        error = Exception("Access denied for user 'root'@'localhost'")
        result = MySQLErrorHandler.handle_connection_error(error)
        
        assert result.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "authentication failed" in result.detail.lower()
    
    def test_unknown_database_error(self):
        """Test database not found error handling."""
        error = Exception("Unknown database 'recipe_saver'")
        result = MySQLErrorHandler.handle_connection_error(error)
        
        assert result.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "database not found" in result.detail.lower()
    
    def test_connection_refused_error(self):
        """Test MySQL server not running error handling."""
        error = Exception("Connection refused")
        result = MySQLErrorHandler.handle_connection_error(error)
        
        assert result.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "not accessible" in result.detail.lower()
    
    def test_connection_timeout_error(self):
        """Test connection timeout error handling."""
        error = Exception("Connection timeout after 30 seconds")
        result = MySQLErrorHandler.handle_connection_error(error)
        
        assert result.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "timeout" in result.detail.lower()
    
    def test_generic_connection_error(self):
        """Test generic connection error handling."""
        error = Exception("Some other connection error")
        result = MySQLErrorHandler.handle_connection_error(error)
        
        assert result.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "connection error" in result.detail.lower()


class TestQueryErrorHandling:
    """Test query error handling (syntax errors, timeouts)."""
    
    def test_query_timeout_error(self):
        """Test query timeout error handling."""
        error = SQLAlchemyTimeoutError("Query timeout")
        result = MySQLErrorHandler.handle_query_error(error)
        
        assert result.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "timeout" in result.detail.lower()
    
    def test_syntax_error(self):
        """Test SQL syntax error handling."""
        error = ProgrammingError("statement", "params", "orig")
        result = MySQLErrorHandler.handle_query_error(error)
        
        assert result.status_code == status.HTTP_400_BAD_REQUEST
        assert "syntax" in result.detail.lower()
    
    def test_pymysql_syntax_error(self):
        """Test PyMySQL syntax error handling."""
        error = PyMySQLProgrammingError(1064, "You have an error in your SQL syntax")
        result = MySQLErrorHandler.handle_query_error(error)
        
        assert result.status_code == status.HTTP_400_BAD_REQUEST
        assert "syntax" in result.detail.lower()
    
    def test_generic_query_error(self):
        """Test generic query error handling."""
        error = Exception("Some query error")
        result = MySQLErrorHandler.handle_query_error(error)
        
        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestConstraintViolationHandling:
    """Test constraint violation error handling."""
    
    def test_foreign_key_constraint_insert(self):
        """Test foreign key constraint violation on insert."""
        # Simulate IntegrityError with foreign key violation
        orig_error = PyMySQLIntegrityError(
            1452,
            "Cannot add or update a child row: a foreign key constraint fails "
            "(`recipe_saver`.`recipes`, CONSTRAINT `recipes_ibfk_1` FOREIGN KEY (`user_id`) "
            "REFERENCES `users` (`id`))"
        )
        error = IntegrityError("statement", "params", orig_error)
        result = MySQLErrorHandler.handle_constraint_violation(error)
        
        assert result.status_code == status.HTTP_400_BAD_REQUEST
        assert "referenced record does not exist" in result.detail.lower()
    
    def test_foreign_key_constraint_delete(self):
        """Test foreign key constraint violation on delete."""
        orig_error = PyMySQLIntegrityError(
            1451,
            "Cannot delete or update a parent row: a foreign key constraint fails "
            "(`recipe_saver`.`recipes`, CONSTRAINT `recipes_ibfk_1` FOREIGN KEY (`user_id`) "
            "REFERENCES `users` (`id`))"
        )
        error = IntegrityError("statement", "params", orig_error)
        result = MySQLErrorHandler.handle_constraint_violation(error)
        
        assert result.status_code == status.HTTP_400_BAD_REQUEST
        assert "cannot delete" in result.detail.lower()
        assert "referenced by other records" in result.detail.lower()
    
    def test_unique_constraint_username(self):
        """Test unique constraint violation for username."""
        orig_error = PyMySQLIntegrityError(
            1062,
            "Duplicate entry 'john_doe' for key 'users.username'"
        )
        error = IntegrityError("statement", "params", orig_error)
        result = MySQLErrorHandler.handle_constraint_violation(error)
        
        assert result.status_code == status.HTTP_409_CONFLICT
        assert "username already exists" in result.detail.lower()
    
    def test_unique_constraint_email(self):
        """Test unique constraint violation for email."""
        orig_error = PyMySQLIntegrityError(
            1062,
            "Duplicate entry 'john@example.com' for key 'users.email'"
        )
        error = IntegrityError("statement", "params", orig_error)
        result = MySQLErrorHandler.handle_constraint_violation(error)
        
        assert result.status_code == status.HTTP_409_CONFLICT
        assert "email already exists" in result.detail.lower()
    
    def test_unique_constraint_rating(self):
        """Test unique constraint violation for recipe rating."""
        orig_error = PyMySQLIntegrityError(
            1062,
            "Duplicate entry '1-5' for key 'recipe_ratings.unique_user_recipe_rating'"
        )
        error = IntegrityError("statement", "params", orig_error)
        result = MySQLErrorHandler.handle_constraint_violation(error)
        
        assert result.status_code == status.HTTP_409_CONFLICT
        assert "already rated" in result.detail.lower()
    
    def test_unique_constraint_generic(self):
        """Test generic unique constraint violation."""
        orig_error = PyMySQLIntegrityError(
            1062,
            "Duplicate entry 'value' for key 'some_table.some_key'"
        )
        error = IntegrityError("statement", "params", orig_error)
        result = MySQLErrorHandler.handle_constraint_violation(error)
        
        assert result.status_code == status.HTTP_409_CONFLICT
        assert "already exists" in result.detail.lower()
    
    def test_not_null_constraint(self):
        """Test not null constraint violation."""
        orig_error = PyMySQLIntegrityError(
            1048,
            "Column 'title' cannot be null"
        )
        error = IntegrityError("statement", "params", orig_error)
        result = MySQLErrorHandler.handle_constraint_violation(error)
        
        assert result.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "title" in result.detail.lower()
        assert "cannot be empty" in result.detail.lower()
    
    def test_check_constraint_rating(self):
        """Test check constraint violation for rating."""
        orig_error = PyMySQLIntegrityError(
            3819,
            "Check constraint 'recipe_ratings_chk_1' is violated."
        )
        error = IntegrityError("statement", "params", orig_error)
        result = MySQLErrorHandler.handle_constraint_violation(error)
        
        assert result.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "validation failed" in result.detail.lower()
    
    def test_generic_integrity_error(self):
        """Test generic integrity error."""
        orig_error = Exception("Some integrity error")
        error = IntegrityError("statement", "params", orig_error)
        result = MySQLErrorHandler.handle_constraint_violation(error)
        
        assert result.status_code == status.HTTP_400_BAD_REQUEST
        assert "integrity constraint" in result.detail.lower()


class TestNotFoundHandling:
    """Test missing record error handling (404 responses)."""
    
    def test_recipe_not_found(self):
        """Test recipe not found error."""
        result = MySQLErrorHandler.handle_not_found("Recipe", 123)
        
        assert result.status_code == status.HTTP_404_NOT_FOUND
        assert "recipe not found" in result.detail.lower()
    
    def test_user_not_found(self):
        """Test user not found error."""
        result = MySQLErrorHandler.handle_not_found("User", 456)
        
        assert result.status_code == status.HTTP_404_NOT_FOUND
        assert "user not found" in result.detail.lower()
    
    def test_collection_not_found(self):
        """Test collection not found error."""
        result = MySQLErrorHandler.handle_not_found("Collection", 789)
        
        assert result.status_code == status.HTTP_404_NOT_FOUND
        assert "collection not found" in result.detail.lower()


class TestTransactionErrorHandling:
    """Test transaction error handling (deadlock, timeout, rollback)."""
    
    def test_deadlock_error(self):
        """Test deadlock detection error handling."""
        orig_error = PyMySQLOperationalError(
            1213,
            "Deadlock found when trying to get lock; try restarting transaction"
        )
        error = OperationalError("statement", "params", orig_error)
        result = MySQLErrorHandler.handle_transaction_error(error)
        
        assert result.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "deadlock" in result.detail.lower()
        assert "retry" in result.detail.lower()
    
    def test_lock_wait_timeout_error(self):
        """Test lock wait timeout error handling."""
        orig_error = PyMySQLOperationalError(
            1205,
            "Lock wait timeout exceeded; try restarting transaction"
        )
        error = OperationalError("statement", "params", orig_error)
        result = MySQLErrorHandler.handle_transaction_error(error)
        
        assert result.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "busy" in result.detail.lower()
    
    def test_transaction_timeout_error(self):
        """Test transaction timeout error handling."""
        error = Exception("Transaction timeout after 60 seconds")
        result = MySQLErrorHandler.handle_transaction_error(error)
        
        assert result.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "timeout" in result.detail.lower()
    
    def test_rollback_failure_error(self):
        """Test rollback failure error handling."""
        error = Exception("Failed to rollback transaction")
        result = MySQLErrorHandler.handle_transaction_error(error)
        
        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "rollback failed" in result.detail.lower()
    
    def test_generic_transaction_error(self):
        """Test generic transaction error handling."""
        error = Exception("Some transaction error")
        result = MySQLErrorHandler.handle_transaction_error(error)
        
        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "transaction error" in result.detail.lower()


class TestGenericDatabaseErrorHandling:
    """Test generic database error handler routing."""
    
    def test_operational_error_routing_to_connection(self):
        """Test OperationalError with connection issue routes to connection handler."""
        error = OperationalError("statement", "params", Exception("Can't connect to MySQL"))
        result = MySQLErrorHandler.handle_database_error(error)
        
        assert result.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    
    def test_operational_error_routing_to_transaction(self):
        """Test OperationalError with deadlock routes to transaction handler."""
        orig_error = PyMySQLOperationalError(1213, "Deadlock found")
        error = OperationalError("statement", "params", orig_error)
        result = MySQLErrorHandler.handle_database_error(error)
        
        assert result.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "deadlock" in result.detail.lower()
    
    def test_integrity_error_routing(self):
        """Test IntegrityError routes to constraint handler."""
        orig_error = PyMySQLIntegrityError(1062, "Duplicate entry")
        error = IntegrityError("statement", "params", orig_error)
        result = MySQLErrorHandler.handle_database_error(error)
        
        assert result.status_code == status.HTTP_409_CONFLICT
    
    def test_programming_error_routing(self):
        """Test ProgrammingError routes to query handler."""
        error = ProgrammingError("statement", "params", "orig")
        result = MySQLErrorHandler.handle_database_error(error)
        
        assert result.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_timeout_error_routing(self):
        """Test TimeoutError routes to query handler."""
        error = SQLAlchemyTimeoutError("Timeout")
        result = MySQLErrorHandler.handle_database_error(error)
        
        assert result.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    
    def test_unhandled_error(self):
        """Test unhandled error returns generic 500 error."""
        error = Exception("Some unknown error")
        result = MySQLErrorHandler.handle_database_error(error)
        
        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "database error" in result.detail.lower()


class TestErrorMessageDescriptiveness:
    """Test that error messages are descriptive and user-friendly."""
    
    def test_foreign_key_error_message_clarity(self):
        """Test foreign key error message is clear and actionable."""
        orig_error = PyMySQLIntegrityError(
            1452,
            "Cannot add or update a child row: a foreign key constraint fails"
        )
        error = IntegrityError("statement", "params", orig_error)
        result = MySQLErrorHandler.handle_constraint_violation(error)
        
        # Message should not expose internal database details
        assert "constraint" not in result.detail.lower() or "referenced record" in result.detail.lower()
        # Message should be actionable
        assert "does not exist" in result.detail.lower() or "verify" in result.detail.lower()
    
    def test_unique_constraint_error_message_specificity(self):
        """Test unique constraint error message is specific to the field."""
        orig_error = PyMySQLIntegrityError(
            1062,
            "Duplicate entry 'test_user' for key 'users.username'"
        )
        error = IntegrityError("statement", "params", orig_error)
        result = MySQLErrorHandler.handle_constraint_violation(error)
        
        # Message should mention the specific field
        assert "username" in result.detail.lower()
        # Message should suggest action
        assert "choose" in result.detail.lower() or "different" in result.detail.lower()
    
    def test_not_null_error_message_field_identification(self):
        """Test not null error message identifies the missing field."""
        orig_error = PyMySQLIntegrityError(
            1048,
            "Column 'ingredients' cannot be null"
        )
        error = IntegrityError("statement", "params", orig_error)
        result = MySQLErrorHandler.handle_constraint_violation(error)
        
        # Message should identify the field
        assert "ingredients" in result.detail.lower()
        # Message should indicate it's required
        assert "required" in result.detail.lower() or "cannot be empty" in result.detail.lower()
    
    def test_connection_error_message_no_credentials(self):
        """Test connection error message doesn't expose credentials."""
        error = Exception("Access denied for user 'admin'@'localhost' (using password: YES)")
        result = MySQLErrorHandler.handle_connection_error(error)
        
        # Message should not contain password information
        assert "password" not in result.detail.lower()
        # Message should be helpful
        assert "authentication" in result.detail.lower() or "credentials" in result.detail.lower()
