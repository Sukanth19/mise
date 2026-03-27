from pydantic_settings import BaseSettings
from pydantic import field_validator, model_validator
from typing import Literal, Optional
import re


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_hours: int = 24
    upload_dir: str = "uploads"
    
    # Environment configuration (development or production)
    # Controls logging levels for MySQL operations
    environment: Literal["development", "production"] = "development"
    
    # Database type selection
    # - mysql: Use SQLAlchemy with MySQL
    # - sqlite: Use SQLAlchemy with SQLite
    database_type: Literal["mysql", "sqlite"] = "sqlite"
    
    # MySQL connection parameters (optional - used to build DATABASE_URL if not provided)
    mysql_user: Optional[str] = None
    mysql_password: Optional[str] = None
    mysql_host: Optional[str] = None
    mysql_port: Optional[int] = None
    mysql_database: Optional[str] = None

    @field_validator("database_url", mode="before")
    @classmethod
    def build_database_url(cls, v: Optional[str], info) -> str:
        """
        Build MySQL connection string from components if DATABASE_URL not provided.
        Validates MySQL connection string format.
        
        Args:
            v: DATABASE_URL value (may be None)
            info: Validation info containing other field values
            
        Returns:
            Validated or constructed connection string
            
        Raises:
            ValueError: If connection string format is invalid
        """
        # If DATABASE_URL is provided, validate it
        if v:
            # Validate MySQL connection string format
            if v.startswith("mysql+pymysql://"):
                pattern = r"^mysql\+pymysql://[^:]+:[^@]+@[^:]+:\d+/[^/]+$"
                if not re.match(pattern, v):
                    raise ValueError(
                        "Invalid MySQL connection string format. "
                        "Expected format: mysql+pymysql://user:password@host:port/database"
                    )
            return v
        
        # If DATABASE_URL not provided, try to build from MySQL components
        data = info.data if hasattr(info, 'data') else {}
        mysql_user = data.get('mysql_user')
        mysql_password = data.get('mysql_password')
        mysql_host = data.get('mysql_host')
        mysql_port = data.get('mysql_port')
        mysql_database = data.get('mysql_database')
        
        # If all MySQL components are provided, build connection string
        if all([mysql_user, mysql_password, mysql_host, mysql_port, mysql_database]):
            return (
                f"mysql+pymysql://{mysql_user}:{mysql_password}"
                f"@{mysql_host}:{mysql_port}/{mysql_database}"
            )
        
        # If no DATABASE_URL and incomplete MySQL components, raise error
        if v is None:
            raise ValueError(
                "DATABASE_URL must be provided, or all MySQL connection parameters "
                "(MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE) must be set"
            )
        
        return v

    @model_validator(mode='after')
    def validate_database_type_matches_url(self):
        """
        Validate that database_type matches the configured database_url.
        Ensures only one database backend is active.
        
        Provides helpful migration guidance when mismatch is detected.
        
        Validates: Requirements 12.2, 12.5
        """
        database_type = self.database_type
        database_url = self.database_url
        
        # Map database_type to expected URL prefixes
        type_to_prefix = {
            'mysql': 'mysql+pymysql://',
            'sqlite': 'sqlite:///'
        }
        
        # For SQLAlchemy databases (mysql, sqlite)
        if database_type in ['mysql', 'sqlite']:
            expected_prefix = type_to_prefix[database_type]
            if database_url and not database_url.startswith(expected_prefix):
                migration_guide = (
                    f"\n\nMigration Guide:"
                    f"\n- If migrating from SQLite to MySQL, run: python backend/run_migrations.py"
                    f"\n- If using SQLite, set DATABASE_TYPE=sqlite and DATABASE_URL=sqlite:///./recipe_saver.db"
                    f"\n- If using MySQL, set DATABASE_TYPE=mysql and provide MySQL connection details"
                )
                raise ValueError(
                    f"DATABASE_TYPE is set to '{database_type}' but DATABASE_URL does not start with '{expected_prefix}'. "
                    f"Ensure DATABASE_TYPE matches your DATABASE_URL configuration.{migration_guide}"
                )
        
        return self

    class Config:
        env_file = ".env"


settings = Settings()
