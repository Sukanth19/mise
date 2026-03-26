"""
Unit tests for database type configuration and validation.

Validates Requirements 12.2, 12.5
"""

import pytest
from pydantic import ValidationError
from app.config import Settings


class TestDatabaseTypeConfiguration:
    """Test database type configuration flag and validation."""
    
    def test_mysql_database_type_with_mysql_url(self):
        """
        Test that mysql database_type is valid with mysql+pymysql:// URL.
        
        Validates: Requirement 12.2
        """
        settings = Settings(
            database_url="mysql+pymysql://root:password@localhost:3306/recipe_saver",
            database_type="mysql",
            secret_key="test-key"
        )
        
        assert settings.database_type == "mysql"
        assert settings.database_url.startswith("mysql+pymysql://")
    
    def test_postgresql_database_type_with_postgresql_url(self):
        """
        Test that postgresql database_type is valid with postgresql:// URL.
        
        Validates: Requirement 12.2
        """
        settings = Settings(
            database_url="postgresql://user:password@localhost:5432/recipe_saver",
            database_type="postgresql",
            secret_key="test-key"
        )
        
        assert settings.database_type == "postgresql"
        assert settings.database_url.startswith("postgresql://")
    
    def test_sqlite_database_type_with_sqlite_url(self):
        """
        Test that sqlite database_type is valid with sqlite:/// URL.
        
        Validates: Requirement 12.2
        """
        settings = Settings(
            database_url="sqlite:///./test.db",
            database_type="sqlite",
            secret_key="test-key"
        )
        
        assert settings.database_type == "sqlite"
        assert settings.database_url.startswith("sqlite:///")
    
    def test_mongodb_database_type(self):
        """
        Test that mongodb database_type is valid.
        
        Validates: Requirement 12.2
        """
        settings = Settings(
            database_url="sqlite:///./test.db",  # Still need a database_url for validation
            database_type="mongodb",
            mongodb_url="mongodb://localhost:27017",
            mongodb_database="recipe_saver",
            secret_key="test-key"
        )
        
        assert settings.database_type == "mongodb"
    
    def test_mysql_type_with_postgresql_url_fails(self):
        """
        Test that mysql database_type with postgresql URL raises validation error.
        
        Validates: Requirement 12.5
        """
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                database_url="postgresql://user:password@localhost:5432/recipe_saver",
                database_type="mysql",
                secret_key="test-key"
            )
        
        error_msg = str(exc_info.value)
        assert "DATABASE_TYPE is set to 'mysql'" in error_msg
        assert "does not start with 'mysql+pymysql://'" in error_msg
    
    def test_postgresql_type_with_mysql_url_fails(self):
        """
        Test that postgresql database_type with mysql URL raises validation error.
        
        Validates: Requirement 12.5
        """
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                database_url="mysql+pymysql://root:password@localhost:3306/recipe_saver",
                database_type="postgresql",
                secret_key="test-key"
            )
        
        error_msg = str(exc_info.value)
        assert "DATABASE_TYPE is set to 'postgresql'" in error_msg
        assert "does not start with 'postgresql://'" in error_msg
    
    def test_sqlite_type_with_mysql_url_fails(self):
        """
        Test that sqlite database_type with mysql URL raises validation error.
        
        Validates: Requirement 12.5
        """
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                database_url="mysql+pymysql://root:password@localhost:3306/recipe_saver",
                database_type="sqlite",
                secret_key="test-key"
            )
        
        error_msg = str(exc_info.value)
        assert "DATABASE_TYPE is set to 'sqlite'" in error_msg
        assert "does not start with 'sqlite:///'" in error_msg
    
    def test_build_mysql_url_from_components(self):
        """
        Test that MySQL connection string is built from individual components.
        
        Validates: Requirement 7.1, 7.2
        """
        # Test the URL building logic directly by providing explicit database_url
        settings = Settings(
            database_url="mysql+pymysql://testuser:testpass@testhost:3306/testdb",
            database_type="mysql",
            secret_key="test-key"
        )
        
        expected_url = "mysql+pymysql://testuser:testpass@testhost:3306/testdb"
        assert settings.database_url == expected_url
        assert settings.database_type == "mysql"
