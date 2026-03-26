import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"
os.environ["MONGODB_URL"] = "mongodb://localhost:27017"
os.environ["MONGODB_DATABASE"] = "recipe_saver_test"

import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db, mongodb
from app.main import app
from fastapi.testclient import TestClient

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# MongoDB test fixtures
@pytest.fixture(scope="function")
async def setup_mongodb():
    """Setup MongoDB connection for tests (only if MongoDB is available)."""
    try:
        # Create a fresh connection for each test function
        await mongodb.connect(
            os.environ.get("MONGODB_URL", "mongodb://localhost:27017"),
            os.environ.get("MONGODB_DATABASE", "recipe_saver_test")
        )
        yield
        # Disconnect after each test to ensure clean state
        await mongodb.disconnect()
    except Exception as e:
        # MongoDB not available, skip MongoDB tests
        pytest.skip(f"MongoDB not available: {e}")


async def clean_all_collections():
    """Helper function to clean all MongoDB collections."""
    db = await mongodb.get_database()
    for collection_name in await db.list_collection_names():
        await db[collection_name].delete_many({})
