"""User repository for MongoDB data access."""

from typing import Optional, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING
import logging

from .base import BaseRepository

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository):
    """Repository for user collection operations."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Initialize user repository.
        
        Args:
            database: AsyncIOMotorDatabase instance
        """
        super().__init__(database, "users")
    
    async def ensure_indexes(self):
        """Create indexes for the users collection."""
        try:
            indexes = [
                IndexModel([("username", ASCENDING)], unique=True),
                IndexModel([("created_at", ASCENDING)])
            ]
            await self.collection.create_indexes(indexes)
            logger.info(f"Created indexes for {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to create indexes for {self.collection_name}: {e}")
            raise
    
    async def find_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Find a user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            User document if found, None otherwise
        """
        try:
            user = await self.collection.find_one({"username": username})
            if user:
                logger.debug(f"Found user by username: {username}")
            return user
        except Exception as e:
            logger.error(f"Failed to find user by username {username}: {e}")
            raise
