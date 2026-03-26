"""Property-based tests for UserRepository.

Feature: mongodb-migration
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from datetime import datetime
from bson import ObjectId

from app.repositories.user_repository import UserRepository
from app.database import mongodb
from tests.conftest import clean_all_collections


# Hypothesis strategies for generating test data
@st.composite
def user_document_strategy(draw):
    """Generate valid user document data."""
    return {
        "username": draw(st.text(min_size=1, max_size=255, alphabet=st.characters(blacklist_categories=('Cs',), blacklist_characters=['\x00']))),
        "password_hash": draw(st.text(min_size=1, max_size=255, alphabet=st.characters(blacklist_categories=('Cs',), blacklist_characters=['\x00']))),
        "created_at": datetime.utcnow()
    }


# Property 2: Insert-Retrieve Round Trip
# **Validates: Requirements 3.2**
@given(user_data=user_document_strategy())
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@pytest.mark.asyncio
async def test_user_insert_retrieve_round_trip(user_data, setup_mongodb):
    """
    Property 2: Insert-Retrieve Round Trip
    
    For any valid user document, inserting it into MongoDB and then 
    retrieving it by ID should return equivalent data.
    """
    await clean_all_collections()
    
    db = await mongodb.get_database()
    user_repo = UserRepository(db)
    await user_repo.ensure_indexes()
    
    # Insert
    user_id = await user_repo.create(user_data)
    assert user_id is not None
    assert ObjectId.is_valid(user_id)
    
    # Retrieve
    retrieved = await user_repo.find_by_id(user_id)
    
    # Assert equivalence
    assert retrieved is not None
    assert retrieved["username"] == user_data["username"]
    assert retrieved["password_hash"] == user_data["password_hash"]
    assert str(retrieved["_id"]) == user_id


# Property 3: Update-Retrieve Round Trip
# **Validates: Requirements 3.3**
@given(
    user_data=user_document_strategy(),
    new_password=st.text(min_size=1, max_size=255, alphabet=st.characters(blacklist_characters=['\x00']))
)
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@pytest.mark.asyncio
async def test_user_update_retrieve_round_trip(user_data, new_password, setup_mongodb):
    """
    Property 3: Update-Retrieve Round Trip
    
    For any existing user document and valid update data, updating the 
    document and then retrieving it should reflect all changes.
    """
    await clean_all_collections()
    
    db = await mongodb.get_database()
    user_repo = UserRepository(db)
    await user_repo.ensure_indexes()
    
    # Insert initial document
    user_id = await user_repo.create(user_data)
    
    # Update
    update_data = {"password_hash": new_password}
    updated = await user_repo.update(user_id, update_data)
    
    # Update returns False if no changes were made (new password same as old)
    # This is expected behavior, not an error
    if new_password == user_data["password_hash"]:
        assert updated is False or updated is True  # Either is acceptable
    else:
        assert updated is True
    
    # Retrieve
    retrieved = await user_repo.find_by_id(user_id)
    
    # Assert changes are reflected
    assert retrieved is not None
    assert retrieved["password_hash"] == new_password
    assert retrieved["username"] == user_data["username"]  # Unchanged field


# Property 4: Delete Removes Document
# **Validates: Requirements 3.4**
@given(user_data=user_document_strategy())
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@pytest.mark.asyncio
async def test_user_delete_removes_document(user_data, setup_mongodb):
    """
    Property 4: Delete Removes Document
    
    For any existing user document, deleting it should result in the 
    document no longer being retrievable.
    """
    await clean_all_collections()
    
    db = await mongodb.get_database()
    user_repo = UserRepository(db)
    await user_repo.ensure_indexes()
    
    # Insert
    user_id = await user_repo.create(user_data)
    
    # Verify it exists
    retrieved = await user_repo.find_by_id(user_id)
    assert retrieved is not None
    
    # Delete
    deleted = await user_repo.delete(user_id)
    assert deleted is True
    
    # Verify it no longer exists
    retrieved_after_delete = await user_repo.find_by_id(user_id)
    assert retrieved_after_delete is None
