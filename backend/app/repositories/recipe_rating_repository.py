"""Recipe rating repository for MongoDB data access."""

from typing import Optional, List, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING, DESCENDING
import logging

from .base import BaseRepository

logger = logging.getLogger(__name__)


class RecipeRatingRepository(BaseRepository):
    """Repository for recipe rating collection operations."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Initialize recipe rating repository.
        
        Args:
            database: AsyncIOMotorDatabase instance
        """
        super().__init__(database, "recipe_ratings")
    
    async def ensure_indexes(self):
        """Create indexes for the recipe_ratings collection."""
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
        Find ratings for a specific recipe.
        
        Args:
            recipe_id: Recipe's ObjectId as string
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            
        Returns:
            List of rating documents
        """
        try:
            if not ObjectId.is_valid(recipe_id):
                logger.warning(f"Invalid recipe_id: {recipe_id}")
                return []
            
            filter_query = {"recipe_id": ObjectId(recipe_id)}
            sort = [("created_at", DESCENDING)]
            
            return await self.find_many(filter_query, sort=sort, skip=skip, limit=limit)
        except Exception as e:
            logger.error(f"Failed to find ratings for recipe {recipe_id}: {e}")
            raise
    
    async def find_by_user_and_recipe(
        self,
        user_id: str,
        recipe_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find a rating by user and recipe.
        
        Args:
            user_id: User's ObjectId as string
            recipe_id: Recipe's ObjectId as string
            
        Returns:
            Rating document if found, None otherwise
        """
        try:
            if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(recipe_id):
                logger.warning(f"Invalid ObjectId: user_id={user_id}, recipe_id={recipe_id}")
                return None
            
            rating = await self.collection.find_one({
                "user_id": ObjectId(user_id),
                "recipe_id": ObjectId(recipe_id)
            })
            
            return rating
        except Exception as e:
            logger.error(f"Failed to find rating for user {user_id} and recipe {recipe_id}: {e}")
            raise
    
    async def get_average_rating(self, recipe_id: str) -> Optional[float]:
        """
        Calculate the average rating for a recipe.
        
        Args:
            recipe_id: Recipe's ObjectId as string
            
        Returns:
            Average rating as float, or None if no ratings exist
        """
        try:
            if not ObjectId.is_valid(recipe_id):
                logger.warning(f"Invalid recipe_id: {recipe_id}")
                return None
            
            pipeline = [
                {"$match": {"recipe_id": ObjectId(recipe_id)}},
                {"$group": {
                    "_id": "$recipe_id",
                    "avg_rating": {"$avg": "$rating"},
                    "count": {"$sum": 1}
                }}
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(1)
            
            if result:
                return result[0]["avg_rating"]
            return None
        except Exception as e:
            logger.error(f"Failed to calculate average rating for recipe {recipe_id}: {e}")
            raise
