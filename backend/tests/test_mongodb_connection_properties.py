"""
Property-based tests for MongoDB connection management.

Feature: mongodb-migration
"""

import pytest
from hypothesis import given, strategies as st
from pydantic import ValidationError
from app.config import Settings


# Feature: mongodb-migration, Property 15: Connection String Validation
@given(
    invalid_url=st.one_of(
        # Empty string
        st.just(""),
        # Whitespace only
        st.just("   "),
        # Invalid schemes
        st.text(min_size=1, max_size=50).filter(
            lambda x: not x.startswith("mongodb://") and not x.startswith("mongodb+srv://")
        ),
        # Valid scheme but empty remainder
        st.just("mongodb://"),
        st.just("mongodb+srv://"),
        st.just("mongodb://   "),
        st.just("mongodb+srv://   "),
        # Common mistakes
        st.just("mongo://localhost:27017"),
        st.just("http://localhost:27017"),
        st.just("https://localhost:27017"),
        st.just("mongodb:/"),
        st.just("mongodb:"),
    )
)
def test_invalid_mongodb_connection_string_fails_validation(invalid_url: str):
    """
    **Validates: Requirements 7.6**
    
    Property: For any invalid MongoDB connection string, the backend should fail 
    to start with a descriptive error.
    
    This property verifies that:
    1. Invalid connection strings are rejected during configuration validation
    2. The error message is descriptive and indicates what's wrong
    3. The backend cannot start with an invalid MongoDB URL
    """
    # Attempt to create settings with invalid MongoDB URL
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            database_url="sqlite:///./test.db",
            secret_key="test-secret-key",
            mongodb_url=invalid_url,
            mongodb_database="test_db"
        )
    
    # Verify that the error is descriptive
    error_message = str(exc_info.value)
    
    # The error should mention MongoDB or connection string
    assert any(keyword in error_message.lower() for keyword in [
        "mongodb", "connection", "string", "invalid", "format"
    ]), f"Error message should be descriptive. Got: {error_message}"


# Feature: mongodb-migration, Property 15: Connection String Validation
@given(
    valid_url=st.one_of(
        # Valid local MongoDB URLs
        st.just("mongodb://localhost:27017"),
        st.just("mongodb://127.0.0.1:27017"),
        st.just("mongodb://localhost:27017/mydb"),
        st.just("mongodb://user:pass@localhost:27017"),
        st.just("mongodb://user:pass@localhost:27017/mydb"),
        st.just("mongodb://host1:27017,host2:27017,host3:27017"),
        # Valid MongoDB Atlas URLs
        st.just("mongodb+srv://cluster.mongodb.net"),
        st.just("mongodb+srv://user:pass@cluster.mongodb.net"),
        st.just("mongodb+srv://user:pass@cluster.mongodb.net/mydb"),
        st.just("mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true"),
        # Valid with various options
        st.just("mongodb://localhost:27017/?replicaSet=rs0"),
        st.just("mongodb://localhost:27017/mydb?authSource=admin"),
    )
)
def test_valid_mongodb_connection_string_passes_validation(valid_url: str):
    """
    **Validates: Requirements 7.6**
    
    Property: For any valid MongoDB connection string, the backend should accept 
    it without validation errors.
    
    This property verifies that:
    1. Valid connection strings are accepted during configuration validation
    2. No false positives occur (valid URLs are not rejected)
    3. Both mongodb:// and mongodb+srv:// schemes are supported
    """
    # Should not raise any validation errors
    settings = Settings(
        database_url="sqlite:///./test.db",
        secret_key="test-secret-key",
        mongodb_url=valid_url,
        mongodb_database="test_db"
    )
    
    # Verify the URL was accepted
    assert settings.mongodb_url == valid_url


def test_mongodb_connection_string_validation_error_messages():
    """
    Unit test to verify specific error messages for common invalid formats.
    
    **Validates: Requirements 7.6**
    """
    test_cases = [
        ("", "cannot be empty"),
        ("http://localhost:27017", "mongodb://"),
        ("mongo://localhost:27017", "mongodb://"),
        ("mongodb://", "Missing host"),
        ("mongodb+srv://", "Missing host"),
    ]
    
    for invalid_url, expected_error_fragment in test_cases:
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                database_url="sqlite:///./test.db",
                secret_key="test-secret-key",
                mongodb_url=invalid_url,
                mongodb_database="test_db"
            )
        
        error_message = str(exc_info.value)
        assert expected_error_fragment.lower() in error_message.lower(), (
            f"Expected error message to contain '{expected_error_fragment}' "
            f"for invalid URL '{invalid_url}'. Got: {error_message}"
        )
