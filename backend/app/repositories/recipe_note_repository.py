"""Recipe note repository for MongoDB data access."""

from typing import List, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING, DESCENDING
import logging

from .base import BaseRepository

logger = logging.getLogger(__name__)


class RecipeNoteRepository(BaseRepository):
    """Repository for recipe note collection operations."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Initialize recipe note repository.
        
        Args:
            database: AsyncIOMotorDatabase instance
        """
        super().__init__(database, "recipe_notes")
    
    async def ensure_indexes(self):
        """Create indexes for the recipe_notes collection."""
        try:
            indexes = [
                IndexModel([("recipe_id", ASCENDING)]),
                IndexModel([("user_id", ASCENDING)]),
                IndexModel([("recipe_id", ASCENDING), ("user_id", ASCENDING)])
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
        Find notes for a specific recipe.
        
        Args:
            recipe_id: Recipe's ObjectId as string
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            
        Returns:
            List of note documents
        """
        try:
            if not ObjectId.is_valid(recipe_id):
                logger.warning(f"Invalid recipe_id: {recipe_id}")
                return []
            
            filter_query = {"recipe_id": ObjectId(recipe_id)}
            sort = [("created_at", DESCENDING)]
            
            return await self.find_many(filter_query, sort=sort, skip=skip, limit=limit)
        except Exception as e:
            logger.error(f"Failed to find notes for recipe {recipe_id}: {e}")
            raise
    
    async def find_by_user_and_recipe(
        self,
        user_id: str,
        recipe_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Find notes by user and recipe.
        
        Args:
            user_id: User's ObjectId as string
            recipe_id: Recipe's ObjectId as string
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            
        Returns:
            List of note documents
        """
        try:
            if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(recipe_id):
                logger.warning(f"Invalid ObjectId: user_id={user_id}, recipe_id={recipe_id}")
                return []
            
            filter_query = {
                "user_id": ObjectId(user_id),
                "recipe_id": ObjectId(recipe_id)
            }
            sort = [("created_at", DESCENDING)]
            
            return await self.find_many(filter_query, sort=sort, skip=skip, limit=limit)
        except Exception as e:
            logger.error(f"Failed to find notes for user {user_id} and recipe {recipe_id}: {e}")
            raise
