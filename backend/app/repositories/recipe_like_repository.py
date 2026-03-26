"""Recipe like repository for MongoDB data access."""

from typing import List, Dict, Any, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING, DESCENDING
import logging

from .base import BaseRepository

logger = logging.getLogger(__name__)


class RecipeLikeRepository(BaseRepository):
    """Repository for recipe like collection operations."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Initialize recipe like repository.
        
        Args:
            database: AsyncIOMotorDatabase instance
        """
        super().__init__(database, "recipe_likes")
    
    async def ensure_indexes(self):
        """Create indexes for the recipe_likes collection."""
        try:
            indexes = [
                IndexModel([("recipe_id", ASCENDING)]),
                IndexModel([("user_id", ASCENDING)]),
                IndexModel([("recipe_id", ASCENDING), ("user_id", ASCENDING)], unique=True)
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
        Find likes for a specific recipe.
        
        Args:
            recipe_id: Recipe's ObjectId as string
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            
        Returns:
            List of like documents
        """
        try:
            if not ObjectId.is_valid(recipe_id):
                logger.warning(f"Invalid recipe_id: {recipe_id}")
                return []
            
            filter_query = {"recipe_id": ObjectId(recipe_id)}
            sort = [("created_at", DESCENDING)]
            
            return await self.find_many(filter_query, sort=sort, skip=skip, limit=limit)
        except Exception as e:
            logger.error(f"Failed to find likes for recipe {recipe_id}: {e}")
            raise
    
    async def find_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Find recipes liked by a user.
        
        Args:
            user_id: User's ObjectId as string
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            
        Returns:
            List of like documents
        """
        try:
            if not ObjectId.is_valid(user_id):
                logger.warning(f"Invalid user_id: {user_id}")
                return []
            
            filter_query = {"user_id": ObjectId(user_id)}
            sort = [("created_at", DESCENDING)]
            
            return await self.find_many(filter_query, sort=sort, skip=skip, limit=limit)
        except Exception as e:
            logger.error(f"Failed to find likes by user {user_id}: {e}")
            raise
    
    async def has_liked(self, user_id: str, recipe_id: str) -> bool:
        """
        Check if a user has liked a recipe.
        
        Args:
            user_id: User's ObjectId as string
            recipe_id: Recipe's ObjectId as string
            
        Returns:
            True if user has liked the recipe, False otherwise
        """
        try:
            if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(recipe_id):
                logger.warning(f"Invalid ObjectId: user_id={user_id}, recipe_id={recipe_id}")
                return False
            
            like = await self.collection.find_one({
                "user_id": ObjectId(user_id),
                "recipe_id": ObjectId(recipe_id)
            })
            
            return like is not None
        except Exception as e:
            logger.error(f"Failed to check if user {user_id} liked recipe {recipe_id}: {e}")
            raise
    
    async def count_likes(self, recipe_id: str) -> int:
        """
        Count the number of likes for a recipe.
        
        Args:
            recipe_id: Recipe's ObjectId as string
            
        Returns:
            Number of likes
        """
        try:
            if not ObjectId.is_valid(recipe_id):
                logger.warning(f"Invalid recipe_id: {recipe_id}")
                return 0
            
            return await self.count({"recipe_id": ObjectId(recipe_id)})
        except Exception as e:
            logger.error(f"Failed to count likes for recipe {recipe_id}: {e}")
            raise
