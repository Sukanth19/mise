"""
Property-based tests for MySQL connection string validation.

Feature: mongodb-migration
"""

import pytest
from hypothesis import given, strategies as st
from pydantic import ValidationError
from app.config import Settings


# Feature: mongodb-migration, Property 15: Connection String Validation
@given(
    invalid_url=st.one_of(
        # Invalid MySQL connection string formats
        st.just("mysql://user:pass@localhost:3306/db"),  # Missing +pymysql
        st.just("mysql+pymysql://localhost:3306/db"),  # Missing credentials
        st.just("mysql+pymysql://user@localhost:3306/db"),  # Missing password
        st.just("mysql+pymysql://user:pass@localhost/db"),  # Missing port
        st.just("mysql+pymysql://user:pass@localhost:3306"),  # Missing database
        st.just("mysql+pymysql://user:pass@:3306/db"),  # Missing host
        st.just("mysql+pymysql://:pass@localhost:3306/db"),  # Missing user
        st.just("mysql+pymysql://user:@localhost:3306/db"),  # Empty password
        st.just("mysql+pymysql://user:pass@localhost:abc/db"),  # Invalid port
        st.just("mysql+pymysql://user:pass@localhost:3306/"),  # Empty database
        # Common mistakes
        st.just("postgresql://user:pass@localhost:5432/db"),
        st.just("sqlite:///./test.db"),
        st.just("mysql+mysqldb://user:pass@localhost:3306/db"),  # Wrong driver
        st.just("mysql+pymysql://"),
        st.just(""),
    )
)
def test_invalid_mysql_connection_string_fails_validation(invalid_url: str):
    """
    **Validates: Requirements 7.6**
    
    Property: For any invalid MySQL connection string, the backend should fail 
    to start with a descriptive error.
    
    This property verifies that:
    1. Invalid MySQL connection strings are rejected during configuration validation
    2. The error message is descriptive and indicates what's wrong
    3. The backend cannot start with an invalid MySQL connection string
    """
    # Attempt to create settings with invalid MySQL connection string
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            database_url=invalid_url,
            secret_key="test-secret-key",
            mongodb_url="mongodb://localhost:27017",
            mongodb_database="test_db"
        )
    
    # Verify that the error is descriptive
    error_message = str(exc_info.value)
    
    # The error should mention MySQL or connection string or format
    assert any(keyword in error_message.lower() for keyword in [
        "mysql", "connection", "string", "invalid", "format", "expected"
    ]), f"Error message should be descriptive. Got: {error_message}"


# Feature: mongodb-migration, Property 15: Connection String Validation
@given(
    valid_components=st.tuples(
        st.text(min_size=1, max_size=50, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_-'
        )),  # user
        st.text(min_size=1, max_size=50, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_-!@#$%'
        )),  # password
        st.one_of(
            st.just("localhost"),
            st.just("127.0.0.1"),
            st.text(min_size=1, max_size=50, alphabet=st.characters(
                whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='.-'
            ))
        ),  # host
        st.integers(min_value=1024, max_value=65535),  # port
        st.text(min_size=1, max_size=50, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_-'
        ))  # database
    )
)
def test_valid_mysql_connection_string_passes_validation(valid_components):
    """
    **Validates: Requirements 7.6**
    
    Property: For any valid MySQL connection string, the backend should accept 
    it without validation errors.
    
    This property verifies that:
    1. Valid MySQL connection strings are accepted during configuration validation
    2. No false positives occur (valid URLs are not rejected)
    3. The mysql+pymysql:// scheme is properly supported
    """
    user, password, host, port, database = valid_components
    valid_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    
    # Should not raise any validation errors
    settings = Settings(
        database_url=valid_url,
        secret_key="test-secret-key",
        mongodb_url="mongodb://localhost:27017",
        mongodb_database="test_db"
    )
    
    # Verify the URL was accepted
    assert settings.database_url == valid_url


def test_mysql_connection_string_validation_specific_cases():
    """
    Unit test to verify specific valid MySQL connection string formats.
    
    **Validates: Requirements 7.6**
    """
    valid_urls = [
        "mysql+pymysql://root:password@localhost:3306/recipe_saver",
        "mysql+pymysql://user:pass123@127.0.0.1:3306/testdb",
        "mysql+pymysql://admin:secret@db.example.com:3306/production",
        "mysql+pymysql://app_user:complex_pass123@mysql-server:3306/app_db",
    ]
    
    for valid_url in valid_urls:
        # Should not raise any validation errors
        settings = Settings(
            database_url=valid_url,
            secret_key="test-secret-key",
            mongodb_url="mongodb://localhost:27017",
            mongodb_database="test_db"
        )
        assert settings.database_url == valid_url


def test_mysql_connection_string_validation_error_messages():
    """
    Unit test to verify specific error messages for common invalid formats.
    
    **Validates: Requirements 7.6**
    """
    test_cases = [
        ("mysql://user:pass@localhost:3306/db", "mysql+pymysql://"),
        ("mysql+pymysql://localhost:3306/db", "user:password"),
        ("mysql+pymysql://user:pass@localhost/db", "expected format"),
        ("", "DATABASE_URL must be provided"),
    ]
    
    for invalid_url, expected_error_fragment in test_cases:
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                database_url=invalid_url,
                secret_key="test-secret-key",
                mongodb_url="mongodb://localhost:27017",
                mongodb_database="test_db"
            )
        
        error_message = str(exc_info.value)
        assert expected_error_fragment.lower() in error_message.lower(), (
            f"Expected error message to contain '{expected_error_fragment}' "
            f"for invalid URL '{invalid_url}'. Got: {error_message}"
        )


def test_mysql_connection_from_components():
    """
    Unit test to verify MySQL connection string can be built from components.
    
    **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**
    """
    settings = Settings(
        database_url=None,
        secret_key="test-secret-key",
        mysql_user="testuser",
        mysql_password="testpass",
        mysql_host="localhost",
        mysql_port=3306,
        mysql_database="testdb",
        mongodb_url="mongodb://localhost:27017",
        mongodb_database="test_db"
    )
    
    expected_url = "mysql+pymysql://testuser:testpass@localhost:3306/testdb"
    assert settings.database_url == expected_url


def test_mysql_connection_missing_components_fails():
    """
    Unit test to verify that missing MySQL components cause validation error.
    
    **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**
    """
    # Missing some MySQL components should fail
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            database_url=None,
            secret_key="test-secret-key",
            mysql_user="testuser",
            mysql_password="testpass",
            # Missing mysql_host, mysql_port, mysql_database
            mongodb_url="mongodb://localhost:27017",
            mongodb_database="test_db"
        )
    
    error_message = str(exc_info.value)
    assert "DATABASE_URL must be provided" in error_message or "MySQL connection parameters" in error_message
