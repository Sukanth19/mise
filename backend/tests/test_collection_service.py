"""Unit tests for CollectionManager service."""
import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"

import pytest
from app.services.collection_service import CollectionManager
from app.schemas import CollectionCreate, CollectionUpdate
from app.models import User, Recipe, Collection


def test_create_collection_success(db):
    """Test creating a collection successfully."""
    # Create a user
    user = User(username="testuser", password_hash="hashed")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create collection
    collection_data = CollectionCreate(
        name="My Recipes",
        description="A collection of my favorite recipes"
    )
    
    collection = CollectionManager.create_collection(db, user.id, collection_data)
    
    assert collection.id is not None
    assert collection.user_id == user.id
    assert collection.name == "My Recipes"
    assert collection.description == "A collection of my favorite recipes"
    assert collection.nesting_level == 0
    assert collection.parent_collection_id is None


def test_create_nested_collection(db):
    """Test creating a nested collection."""
    # Create a user
    user = User(username="testuser", password_hash="hashed")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create parent collection
    parent_data = CollectionCreate(name="Parent Collection")
    parent = CollectionManager.create_collection(db, user.id, parent_data)
    
    # Create nested collection
    child_data = CollectionCreate(
        name="Child Collection",
        parent_collection_id=parent.id
    )
    child = CollectionManager.create_collection(db, user.id, child_data)
    
    assert child.parent_collection_id == parent.id
    assert child.nesting_level == 1


def test_validate_nesting_level(db):
    """Test nesting level validation."""
    assert CollectionManager.validate_nesting_level(0) == True
    assert CollectionManager.validate_nesting_level(1) == True
    assert CollectionManager.validate_nesting_level(2) == True
    assert CollectionManager.validate_nesting_level(3) == True
    assert CollectionManager.validate_nesting_level(4) == False


def test_create_collection_exceeds_nesting_level(db):
    """Test that creating a collection beyond max nesting level fails."""
    # Create a user
    user = User(username="testuser", password_hash="hashed")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create level 0 collection
    level0_data = CollectionCreate(name="Level 0")
    level0 = CollectionManager.create_collection(db, user.id, level0_data)
    
    # Create level 1 collection
    level1_data = CollectionCreate(name="Level 1", parent_collection_id=level0.id)
    level1 = CollectionManager.create_collection(db, user.id, level1_data)
    
    # Create level 2 collection
    level2_data = CollectionCreate(name="Level 2", parent_collection_id=level1.id)
    level2 = CollectionManager.create_collection(db, user.id, level2_data)
    
    # Create level 3 collection (should succeed)
    level3_data = CollectionCreate(name="Level 3", parent_collection_id=level2.id)
    level3 = CollectionManager.create_collection(db, user.id, level3_data)
    assert level3.nesting_level == 3
    
    # Try to create level 4 collection (should fail)
    level4_data = CollectionCreate(name="Level 4", parent_collection_id=level3.id)
    with pytest.raises(ValueError, match="Maximum nesting level"):
        CollectionManager.create_collection(db, user.id, level4_data)


def test_get_user_collections(db):
    """Test retrieving all collections for a user."""
    # Create users
    user1 = User(username="user1", password_hash="hashed")
    user2 = User(username="user2", password_hash="hashed")
    db.add(user1)
    db.add(user2)
    db.commit()
    db.refresh(user1)
    db.refresh(user2)
    
    # Create collections for user1
    col1_data = CollectionCreate(name="Collection 1")
    col2_data = CollectionCreate(name="Collection 2")
    CollectionManager.create_collection(db, user1.id, col1_data)
    CollectionManager.create_collection(db, user1.id, col2_data)
    
    # Create collection for user2
    col3_data = CollectionCreate(name="Collection 3")
    CollectionManager.create_collection(db, user2.id, col3_data)
    
    # Get user1's collections
    user1_collections = CollectionManager.get_user_collections(db, user1.id)
    assert len(user1_collections) == 2
    
    # Get user2's collections
    user2_collections = CollectionManager.get_user_collections(db, user2.id)
    assert len(user2_collections) == 1


def test_update_collection(db):
    """Test updating a collection."""
    # Create a user
    user = User(username="testuser", password_hash="hashed")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create collection
    collection_data = CollectionCreate(name="Original Name")
    collection = CollectionManager.create_collection(db, user.id, collection_data)
    
    # Update collection
    update_data = CollectionUpdate(
        name="Updated Name",
        description="New description"
    )
    updated = CollectionManager.update_collection(db, collection.id, user.id, update_data)
    
    assert updated.name == "Updated Name"
    assert updated.description == "New description"


def test_delete_collection(db):
    """Test deleting a collection."""
    # Create a user
    user = User(username="testuser", password_hash="hashed")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create collection
    collection_data = CollectionCreate(name="To Delete")
    collection = CollectionManager.create_collection(db, user.id, collection_data)
    collection_id = collection.id
    
    # Delete collection
    result = CollectionManager.delete_collection(db, collection_id, user.id)
    assert result == True
    
    # Verify deletion
    deleted = CollectionManager.get_collection_by_id(db, collection_id, user.id)
    assert deleted is None


def test_add_recipes_to_collection(db):
    """Test adding recipes to a collection."""
    # Create a user
    user = User(username="testuser", password_hash="hashed")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create recipes
    recipe1 = Recipe(
        user_id=user.id,
        title="Recipe 1",
        ingredients='["ingredient1"]',
        steps='["step1"]'
    )
    recipe2 = Recipe(
        user_id=user.id,
        title="Recipe 2",
        ingredients='["ingredient2"]',
        steps='["step2"]'
    )
    db.add(recipe1)
    db.add(recipe2)
    db.commit()
    db.refresh(recipe1)
    db.refresh(recipe2)
    
    # Create collection
    collection_data = CollectionCreate(name="My Collection")
    collection = CollectionManager.create_collection(db, user.id, collection_data)
    
    # Add recipes to collection
    added_count = CollectionManager.add_recipes_to_collection(
        db, collection.id, [recipe1.id, recipe2.id], user.id
    )
    
    assert added_count == 2


def test_add_recipes_validates_ownership(db):
    """Test that adding recipes validates user ownership."""
    # Create users
    user1 = User(username="user1", password_hash="hashed")
    user2 = User(username="user2", password_hash="hashed")
    db.add(user1)
    db.add(user2)
    db.commit()
    db.refresh(user1)
    db.refresh(user2)
    
    # User1 creates a recipe
    recipe = Recipe(
        user_id=user1.id,
        title="User1's Recipe",
        ingredients='["ingredient1"]',
        steps='["step1"]'
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    
    # User2 creates a collection
    collection_data = CollectionCreate(name="User2's Collection")
    collection = CollectionManager.create_collection(db, user2.id, collection_data)
    
    # User2 tries to add User1's recipe to their collection (should fail)
    with pytest.raises(ValueError, match="access denied"):
        CollectionManager.add_recipes_to_collection(
            db, collection.id, [recipe.id], user2.id
        )


def test_remove_recipe_from_collection(db):
    """Test removing a recipe from a collection."""
    # Create a user
    user = User(username="testuser", password_hash="hashed")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create recipe
    recipe = Recipe(
        user_id=user.id,
        title="Recipe",
        ingredients='["ingredient1"]',
        steps='["step1"]'
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    
    # Create collection and add recipe
    collection_data = CollectionCreate(name="My Collection")
    collection = CollectionManager.create_collection(db, user.id, collection_data)
    CollectionManager.add_recipes_to_collection(db, collection.id, [recipe.id], user.id)
    
    # Remove recipe from collection
    result = CollectionManager.remove_recipe_from_collection(
        db, collection.id, recipe.id, user.id
    )
    
    assert result == True
    
    # Verify recipe still exists (not deleted)
    from app.models import Recipe as RecipeModel
    recipe_still_exists = db.query(RecipeModel).filter(RecipeModel.id == recipe.id).first()
    assert recipe_still_exists is not None


def test_generate_share_token(db):
    """Test generating a share token for a collection."""
    # Create a user
    user = User(username="testuser", password_hash="hashed")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create collection
    collection_data = CollectionCreate(name="Shared Collection")
    collection = CollectionManager.create_collection(db, user.id, collection_data)
    
    # Generate share token
    token = CollectionManager.generate_share_token(db, collection.id, user.id)
    
    assert token is not None
    assert len(token) > 0
    
    # Verify token is stored
    db.refresh(collection)
    assert collection.share_token == token


def test_revoke_share_token(db):
    """Test revoking a share token."""
    # Create a user
    user = User(username="testuser", password_hash="hashed")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create collection and generate share token
    collection_data = CollectionCreate(name="Shared Collection")
    collection = CollectionManager.create_collection(db, user.id, collection_data)
    token = CollectionManager.generate_share_token(db, collection.id, user.id)
    assert token is not None
    
    # Revoke share token
    result = CollectionManager.revoke_share_token(db, collection.id, user.id)
    assert result == True
    
    # Verify token is removed
    db.refresh(collection)
    assert collection.share_token is None


def test_get_shared_collection(db):
    """Test accessing a collection via share token."""
    # Create a user
    user = User(username="testuser", password_hash="hashed")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create collection and generate share token
    collection_data = CollectionCreate(name="Shared Collection")
    collection = CollectionManager.create_collection(db, user.id, collection_data)
    token = CollectionManager.generate_share_token(db, collection.id, user.id)
    
    # Access collection via share token (no auth required)
    shared_collection = CollectionManager.get_shared_collection(db, token)
    
    assert shared_collection is not None
    assert shared_collection.id == collection.id
    assert shared_collection.name == "Shared Collection"


def test_get_shared_collection_invalid_token(db):
    """Test accessing a collection with invalid share token."""
    shared_collection = CollectionManager.get_shared_collection(db, "invalid-token")
    assert shared_collection is None
