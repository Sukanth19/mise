"""Recipe comment repository for MongoDB data access."""

from typing import List, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING, DESCENDING
import logging

from .base import BaseRepository

logger = logging.getLogger(__name__)


class RecipeCommentRepository(BaseRepository):
    """Repository for recipe comment collection operations."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Initialize recipe comment repository.
        
        Args:
            database: AsyncIOMotorDatabase instance
        """
        super().__init__(database, "recipe_comments")
    
    async def ensure_indexes(self):
        """Create indexes for the recipe_comments collection."""
        try:
            indexes = [
                IndexModel([("recipe_id", ASCENDING)]),
                IndexModel([("user_id", ASCENDING)]),
                IndexModel([("recipe_id", ASCENDING), ("created_at", DESCENDING)])
            ]
            await self.collection.create_indexes(indexes)
            logger.info(f"Created indexes for {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to create indexes for {self.collection_name}: {e}")
            raise
    
    async def find_by_recipe(
        self,
        recipe_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Find comments for a specific recipe.
        
        Args:
            recipe_id: Recipe's ObjectId as string
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            
        Returns:
            List of comment documents
        """
        try:
            if not ObjectId.is_valid(recipe_id):
                logger.warning(f"Invalid recipe_id: {recipe_id}")
                return []
            
            filter_query = {"recipe_id": ObjectId(recipe_id)}
            sort = [("created_at", DESCENDING)]
            
            return await self.find_many(filter_query, sort=sort, skip=skip, limit=limit)
        except Exception as e:
            logger.error(f"Failed to find comments for recipe {recipe_id}: {e}")
            raise
    
    async def find_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Find comments by a specific user.
        
        Args:
            user_id: User's ObjectId as string
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            
        Returns:
            List of comment documents
        """
        try:
            if not ObjectId.is_valid(user_id):
                logger.warning(f"Invalid user_id: {user_id}")
                return []
            
            filter_query = {"user_id": ObjectId(user_id)}
            sort = [("created_at", DESCENDING)]
            
            return await self.find_many(filter_query, sort=sort, skip=skip, limit=limit)
        except Exception as e:
            logger.error(f"Failed to find comments by user {user_id}: {e}")
            raise
