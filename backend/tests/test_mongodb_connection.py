"""
Unit tests for MongoDB connection management.
"""

import pytest
from app.database import MongoDB


@pytest.mark.asyncio
async def test_mongodb_get_database_before_connect_raises_error():
    """Test that getting database before connecting raises an error."""
    mongodb = MongoDB()
    
    with pytest.raises(RuntimeError, match="Database not connected"):
        await mongodb.get_database()


@pytest.mark.asyncio
async def test_mongodb_ping_before_connect_raises_error():
    """Test that pinging before connecting raises an error."""
    mongodb = MongoDB()
    
    with pytest.raises(RuntimeError, match="Client not connected"):
        await mongodb.ping()


@pytest.mark.asyncio
async def test_mongodb_disconnect_when_not_connected():
    """Test that disconnecting when not connected is safe."""
    mongodb = MongoDB()
    
    # Should not raise an error
    await mongodb.disconnect()
    
    # Verify state is clean
    assert mongodb.client is None
    assert mongodb.database is None
    assert mongodb._database_name is None
