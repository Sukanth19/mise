"""User follow repository for MongoDB data access."""

from typing import List, Dict, Any, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING, DESCENDING
import logging

from .base import BaseRepository

logger = logging.getLogger(__name__)


class UserFollowRepository(BaseRepository):
    """Repository for user follow collection operations."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Initialize user follow repository.
        
        Args:
            database: AsyncIOMotorDatabase instance
        """
        super().__init__(database, "user_follows")
    
    async def ensure_indexes(self):
        """Create indexes for the user_follows collection."""
        try:
            indexes = [
                IndexModel([("follower_id", ASCENDING)]),
                IndexModel([("following_id", ASCENDING)]),
                IndexModel([("follower_id", ASCENDING), ("following_id", ASCENDING)], unique=True)
            ]
            await self.collection.create_indexes(indexes)
            logger.info(f"Created indexes for {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to create indexes for {self.collection_name}: {e}")
            raise
    
    async def find_followers(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Find users who follow the specified user.
        
        Args:
            user_id: User's ObjectId as string
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            
        Returns:
            List of follow documents
        """
        try:
            if not ObjectId.is_valid(user_id):
                logger.warning(f"Invalid user_id: {user_id}")
                return []
            
            filter_query = {"following_id": ObjectId(user_id)}
            sort = [("created_at", DESCENDING)]
            
            return await self.find_many(filter_query, sort=sort, skip=skip, limit=limit)
        except Exception as e:
            logger.error(f"Failed to find followers for user {user_id}: {e}")
            raise
    
    async def find_following(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Find users that the specified user follows.
        
        Args:
            user_id: User's ObjectId as string
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            
        Returns:
            List of follow documents
        """
        try:
            if not ObjectId.is_valid(user_id):
                logger.warning(f"Invalid user_id: {user_id}")
                return []
            
            filter_query = {"follower_id": ObjectId(user_id)}
            sort = [("created_at", DESCENDING)]
            
            return await self.find_many(filter_query, sort=sort, skip=skip, limit=limit)
        except Exception as e:
            logger.error(f"Failed to find following for user {user_id}: {e}")
            raise
    
    async def is_following(self, follower_id: str, following_id: str) -> bool:
        """
        Check if one user follows another.
        
        Args:
            follower_id: Follower's ObjectId as string
            following_id: Following user's ObjectId as string
            
        Returns:
            True if follower follows following, False otherwise
        """
        try:
            if not ObjectId.is_valid(follower_id) or not ObjectId.is_valid(following_id):
                logger.warning(f"Invalid ObjectId: follower_id={follower_id}, following_id={following_id}")
                return False
            
            follow = await self.collection.find_one({
                "follower_id": ObjectId(follower_id),
                "following_id": ObjectId(following_id)
            })
            
            return follow is not None
        except Exception as e:
            logger.error(f"Failed to check if user {follower_id} follows {following_id}: {e}")
            raise
