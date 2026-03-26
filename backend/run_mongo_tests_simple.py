#!/usr/bin/env python3
"""Simple script to run MongoDB repository tests."""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment to test mode
os.environ.setdefault("TESTING", "1")

import asyncio
from app.database import mongodb
from app.config import MONGODB_URL, MONGODB_DATABASE

async def check_mongodb_connection():
    """Check if MongoDB is accessible."""
    try:
        await mongodb.connect(MONGODB_URL, MONGODB_DATABASE)
        is_connected = await mongodb.ping()
        await mongodb.disconnect()
        return is_connected
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        return False

async def main():
    print("=" * 80)
    print("MongoDB Repository Tests - Checkpoint 4")
    print("=" * 80)
    print()
    
    # Check MongoDB connection
    print("Checking MongoDB connection...")
    is_connected = await check_mongodb_connection()
    
    if not is_connected:
        print("❌ MongoDB is not accessible!")
        print("   Please ensure MongoDB is running on:", MONGODB_URL)
        return 1
    
    print("✅ MongoDB is accessible")
    print()
    
    # Run pytest programmatically
    print("Running repository property tests...")
    print("-" * 80)
    
    import pytest
    
    test_files = [
        "tests/test_user_repository_properties.py",
        "tests/test_recipe_repository_properties.py",
        "tests/test_join_equivalence_property.py"
    ]
    
    # Run tests with pytest
    exit_code = pytest.main([
        "-v",
        "--tb=short",
        "--no-header",
        *test_files
    ])
    
    print()
    print("=" * 80)
    if exit_code == 0:
        print("✅ All repository tests PASSED!")
    else:
        print("⚠️  Some tests FAILED (exit code:", exit_code, ")")
    print("=" * 80)
    
    return exit_code

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
