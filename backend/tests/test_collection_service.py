"""Unit tests for CollectionManager service."""
import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"
os.environ["MONGODB_URL"] = "mongodb://localhost:27017"
os.environ["MONGODB_DATABASE"] = "recipe_saver_test"

import pytest
from bson import ObjectId
from app.services.collection_service import CollectionManager
from app.schemas import CollectionCreate, CollectionUpdate
from app.repositories.collection_repository import CollectionRepository
from app.repositories.recipe_repository import RecipeRepository
from app.repositories.user_repository import UserRepository
from app.database import mongodb


@pytest.fixture
async def collection_manager():
    """Create CollectionManager with MongoDB repositories."""
    await mongodb.connect(
        os.environ.get("MONGODB_URL", "mongodb://localhost:27017"),
        os.environ.get("MONGODB_DATABASE", "recipe_saver_test")
    )
    db = await mongodb.get_database()
    
    # Clean all collections before test
    for collection_name in await db.list_collection_names():
        await db[collection_name].delete_many({})
    
    collection_repo = CollectionRepository(db)
    recipe_repo = RecipeRepository(db)
    user_repo = UserRepository(db)
    
    yield CollectionManager(collection_repo, recipe_repo), user_repo, recipe_repo
    
    # Clean up after test
    for collection_name in await db.list_collection_names():
        await db[collection_name].delete_many({})
    await mongodb.disconnect()


@pytest.mark.asyncio
async def test_create_collection_success(collection_manager):
    """Test creating a collection successfully."""
    manager, user_repo, _ = collection_manager
    
    # Create a user
    user_id = await user_repo.create({
        "username": "testuser",
        "password_hash": "hashed"
    })
    
    # Create collection
    collection_data = CollectionCreate(
        name="My Recipes",
        description="A collection of my favorite recipes"
    )
    
    collection = await manager.create_collection(user_id, collection_data)
    
    assert collection["_id"] is not None
    assert str(collection["user_id"]) == user_id
    assert collection["name"] == "My Recipes"
    assert collection["description"] == "A collection of my favorite recipes"
    assert collection["nesting_level"] == 0
    assert collection["parent_collection_id"] is None


@pytest.mark.asyncio
async def test_create_nested_collection(collection_manager):
    """Test creating a nested collection."""
    manager, user_repo, _ = collection_manager
    
    # Create a user
    user_id = await user_repo.create({
        "username": "testuser",
        "password_hash": "hashed"
    })
    
    # Create parent collection
    parent_data = CollectionCreate(name="Parent Collection")
    parent = await manager.create_collection(user_id, parent_data)
    
    # Create nested collection
    child_data = CollectionCreate(
        name="Child Collection",
        parent_collection_id=str(parent["_id"])
    )
    child = await manager.create_collection(user_id, child_data)
    
    assert child["parent_collection_id"] == parent["_id"]
    assert child["nesting_level"] == 1


def test_validate_nesting_level():
    """Test nesting level validation."""
    assert CollectionManager.validate_nesting_level(0) == True
    assert CollectionManager.validate_nesting_level(1) == True
    assert CollectionManager.validate_nesting_level(2) == True
    assert CollectionManager.validate_nesting_level(3) == True
    assert CollectionManager.validate_nesting_level(4) == False


@pytest.mark.asyncio
async def test_create_collection_exceeds_nesting_level(collection_manager):
    """Test that creating a collection beyond max nesting level fails."""
    manager, user_repo, _ = collection_manager
    
    # Create a user
    user_id = await user_repo.create({
        "username": "testuser",
        "password_hash": "hashed"
    })
    
    # Create level 0 collection
    level0_data = CollectionCreate(name="Level 0")
    level0 = await manager.create_collection(user_id, level0_data)
    
    # Create level 1 collection
    level1_data = CollectionCreate(name="Level 1", parent_collection_id=str(level0["_id"]))
    level1 = await manager.create_collection(user_id, level1_data)
    
    # Create level 2 collection
    level2_data = CollectionCreate(name="Level 2", parent_collection_id=str(level1["_id"]))
    level2 = await manager.create_collection(user_id, level2_data)
    
    # Create level 3 collection (should succeed)
    level3_data = CollectionCreate(name="Level 3", parent_collection_id=str(level2["_id"]))
    level3 = await manager.create_collection(user_id, level3_data)
    assert level3["nesting_level"] == 3
    
    # Try to create level 4 collection (should fail)
    level4_data = CollectionCreate(name="Level 4", parent_collection_id=str(level3["_id"]))
    with pytest.raises(ValueError, match="Maximum nesting level"):
        await manager.create_collection(user_id, level4_data)


@pytest.mark.asyncio
async def test_get_user_collections(collection_manager):
    """Test retrieving all collections for a user."""
    manager, user_repo, _ = collection_manager
    
    # Create users
    user1_id = await user_repo.create({
        "username": "user1",
        "password_hash": "hashed"
    })
    user2_id = await user_repo.create({
        "username": "user2",
        "password_hash": "hashed"
    })
    
    # Create collections for user1
    col1_data = CollectionCreate(name="Collection 1")
    col2_data = CollectionCreate(name="Collection 2")
    await manager.create_collection(user1_id, col1_data)
    await manager.create_collection(user1_id, col2_data)
    
    # Create collection for user2
    col3_data = CollectionCreate(name="Collection 3")
    await manager.create_collection(user2_id, col3_data)
    
    # Get user1's collections
    user1_collections = await manager.get_user_collections(user1_id)
    assert len(user1_collections) == 2
    
    # Get user2's collections
    user2_collections = await manager.get_user_collections(user2_id)
    assert len(user2_collections) == 1


@pytest.mark.asyncio
async def test_update_collection(collection_manager):
    """Test updating a collection."""
    manager, user_repo, _ = collection_manager
    
    # Create a user
    user_id = await user_repo.create({
        "username": "testuser",
        "password_hash": "hashed"
    })
    
    # Create collection
    collection_data = CollectionCreate(name="Original Name")
    collection = await manager.create_collection(user_id, collection_data)
    
    # Update collection
    update_data = CollectionUpdate(
        name="Updated Name",
        description="New description"
    )
    updated = await manager.update_collection(str(collection["_id"]), user_id, update_data)
    
    assert updated["name"] == "Updated Name"
    assert updated["description"] == "New description"


@pytest.mark.asyncio
async def test_delete_collection(collection_manager):
    """Test deleting a collection."""
    manager, user_repo, _ = collection_manager
    
    # Create a user
    user_id = await user_repo.create({
        "username": "testuser",
        "password_hash": "hashed"
    })
    
    # Create collection
    collection_data = CollectionCreate(name="To Delete")
    collection = await manager.create_collection(user_id, collection_data)
    collection_id = str(collection["_id"])
    
    # Delete collection
    result = await manager.delete_collection(collection_id, user_id)
    assert result == True
    
    # Verify deletion
    deleted = await manager.get_collection_by_id(collection_id, user_id)
    assert deleted is None


@pytest.mark.asyncio
async def test_add_recipes_to_collection(collection_manager):
    """Test adding recipes to a collection."""
    manager, user_repo, recipe_repo = collection_manager
    
    # Create a user
    user_id = await user_repo.create({
        "username": "testuser",
        "password_hash": "hashed"
    })
    
    # Create recipes
    recipe1_id = await recipe_repo.create({
        "user_id": ObjectId(user_id),
        "title": "Recipe 1",
        "ingredients": ["ingredient1"],
        "steps": ["step1"]
    })
    recipe2_id = await recipe_repo.create({
        "user_id": ObjectId(user_id),
        "title": "Recipe 2",
        "ingredients": ["ingredient2"],
        "steps": ["step2"]
    })
    
    # Create collection
    collection_data = CollectionCreate(name="My Collection")
    collection = await manager.create_collection(user_id, collection_data)
    
    # Add recipes to collection
    added_count = await manager.add_recipes_to_collection(
        str(collection["_id"]), [recipe1_id, recipe2_id], user_id
    )
    
    assert added_count == 2


@pytest.mark.asyncio
async def test_add_recipes_validates_ownership(collection_manager):
    """Test that adding recipes validates user ownership."""
    manager, user_repo, recipe_repo = collection_manager
    
    # Create users
    user1_id = await user_repo.create({
        "username": "user1",
        "password_hash": "hashed"
    })
    user2_id = await user_repo.create({
        "username": "user2",
        "password_hash": "hashed"
    })
    
    # User1 creates a recipe
    recipe_id = await recipe_repo.create({
        "user_id": ObjectId(user1_id),
        "title": "User1's Recipe",
        "ingredients": ["ingredient1"],
        "steps": ["step1"]
    })
    
    # User2 creates a collection
    collection_data = CollectionCreate(name="User2's Collection")
    collection = await manager.create_collection(user2_id, collection_data)
    
    # User2 tries to add User1's recipe to their collection (should fail)
    with pytest.raises(ValueError, match="access denied"):
        await manager.add_recipes_to_collection(
            str(collection["_id"]), [recipe_id], user2_id
        )


@pytest.mark.asyncio
async def test_remove_recipe_from_collection(collection_manager):
    """Test removing a recipe from a collection."""
    manager, user_repo, recipe_repo = collection_manager
    
    # Create a user
    user_id = await user_repo.create({
        "username": "testuser",
        "password_hash": "hashed"
    })
    
    # Create recipe
    recipe_id = await recipe_repo.create({
        "user_id": ObjectId(user_id),
        "title": "Recipe",
        "ingredients": ["ingredient1"],
        "steps": ["step1"]
    })
    
    # Create collection and add recipe
    collection_data = CollectionCreate(name="My Collection")
    collection = await manager.create_collection(user_id, collection_data)
    await manager.add_recipes_to_collection(str(collection["_id"]), [recipe_id], user_id)
    
    # Remove recipe from collection
    result = await manager.remove_recipe_from_collection(
        str(collection["_id"]), recipe_id, user_id
    )
    
    assert result == True
    
    # Verify recipe still exists (not deleted)
    recipe_still_exists = await recipe_repo.find_by_id(recipe_id)
    assert recipe_still_exists is not None


@pytest.mark.asyncio
async def test_generate_share_token(collection_manager):
    """Test generating a share token for a collection."""
    manager, user_repo, _ = collection_manager
    
    # Create a user
    user_id = await user_repo.create({
        "username": "testuser",
        "password_hash": "hashed"
    })
    
    # Create collection
    collection_data = CollectionCreate(name="Shared Collection")
    collection = await manager.create_collection(user_id, collection_data)
    
    # Generate share token
    token = await manager.generate_share_token(str(collection["_id"]), user_id)
    
    assert token is not None
    assert len(token) > 0
    
    # Verify token is stored
    updated_collection = await manager.get_collection_by_id(str(collection["_id"]), user_id)
    assert updated_collection["share_token"] == token


@pytest.mark.asyncio
async def test_revoke_share_token(collection_manager):
    """Test revoking a share token."""
    manager, user_repo, _ = collection_manager
    
    # Create a user
    user_id = await user_repo.create({
        "username": "testuser",
        "password_hash": "hashed"
    })
    
    # Create collection and generate share token
    collection_data = CollectionCreate(name="Shared Collection")
    collection = await manager.create_collection(user_id, collection_data)
    token = await manager.generate_share_token(str(collection["_id"]), user_id)
    assert token is not None
    
    # Revoke share token
    result = await manager.revoke_share_token(str(collection["_id"]), user_id)
    assert result == True
    
    # Verify token is removed
    updated_collection = await manager.get_collection_by_id(str(collection["_id"]), user_id)
    assert updated_collection["share_token"] is None


@pytest.mark.asyncio
async def test_get_shared_collection(collection_manager):
    """Test accessing a collection via share token."""
    manager, user_repo, _ = collection_manager
    
    # Create a user
    user_id = await user_repo.create({
        "username": "testuser",
        "password_hash": "hashed"
    })
    
    # Create collection and generate share token
    collection_data = CollectionCreate(name="Shared Collection")
    collection = await manager.create_collection(user_id, collection_data)
    token = await manager.generate_share_token(str(collection["_id"]), user_id)
    
    # Access collection via share token (no auth required)
    shared_collection = await manager.get_shared_collection(token)
    
    assert shared_collection is not None
    assert shared_collection["_id"] == collection["_id"]
    assert shared_collection["name"] == "Shared Collection"


@pytest.mark.asyncio
async def test_get_shared_collection_invalid_token(collection_manager):
    """Test accessing a collection with invalid share token."""
    manager, _, _ = collection_manager
    shared_collection = await manager.get_shared_collection("invalid-token")
    assert shared_collection is None
