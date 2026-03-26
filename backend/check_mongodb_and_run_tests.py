#!/usr/bin/env python3
"""Check MongoDB connection and run repository tests."""

import sys
import os
import asyncio

# Set environment variables
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"
os.environ["MONGODB_URL"] = "mongodb://localhost:27017"
os.environ["MONGODB_DATABASE"] = "recipe_saver_test"

from motor.motor_asyncio import AsyncIOMotorClient


async def check_mongodb():
    """Check if MongoDB is accessible."""
    try:
        client = AsyncIOMotorClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)
        # Ping the server
        await client.admin.command('ping')
        print("✅ MongoDB is running and accessible")
        
        # Check database
        db = client["recipe_saver_test"]
        collections = await db.list_collection_names()
        print(f"✅ Test database accessible, collections: {len(collections)}")
        
        client.close()
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False


async def main():
    print("=" * 80)
    print("MongoDB Repository Tests - Checkpoint 4")
    print("=" * 80)
    print()
    
    # Check MongoDB
    print("Step 1: Checking MongoDB connection...")
    is_connected = await check_mongodb()
    
    if not is_connected:
        print()
        print("MongoDB is not accessible. Please ensure:")
        print("  1. MongoDB is installed")
        print("  2. MongoDB service is running: sudo systemctl start mongod")
        print("  3. MongoDB is listening on localhost:27017")
        return 1
    
    print()
    print("Step 2: Running repository property tests...")
    print("-" * 80)
    
    # Import pytest and run tests
    import subprocess
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/test_user_repository_properties.py",
            "tests/test_recipe_repository_properties.py",
            "tests/test_join_equivalence_property.py",
            "-v", "--tb=short", "--no-header"
        ],
        capture_output=False,
        text=True
    )
    
    print()
    print("=" * 80)
    if result.returncode == 0:
        print("✅ All repository tests PASSED!")
        print("=" * 80)
        return 0
    else:
        print(f"⚠️  Some tests FAILED (exit code: {result.returncode})")
        print("=" * 80)
        return result.returncode


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
