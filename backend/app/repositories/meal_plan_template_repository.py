"""Meal plan template repository for MongoDB data access."""

from typing import List, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING, DESCENDING
import logging

from .base import BaseRepository

logger = logging.getLogger(__name__)


class MealPlanTemplateRepository(BaseRepository):
    """Repository for meal plan template collection operations."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Initialize meal plan template repository.
        
        Args:
            database: AsyncIOMotorDatabase instance
        """
        super().__init__(database, "meal_plan_templates")
    
    async def ensure_indexes(self):
        """Create indexes for the meal_plan_templates collection."""
        try:
            indexes = [
                IndexModel([("user_id", ASCENDING)])
            ]
            await self.collection.create_indexes(indexes)
            logger.info(f"Created indexes for {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to create indexes for {self.collection_name}: {e}")
            raise
    
    async def find_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Find meal plan templates by user ID.
        
        Args:
            user_id: User's ObjectId as string
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            
        Returns:
            List of meal plan template documents
        """
        try:
            if not ObjectId.is_valid(user_id):
                logger.warning(f"Invalid user_id: {user_id}")
                return []
            
            filter_query = {"user_id": ObjectId(user_id)}
            sort = [("created_at", DESCENDING)]
            
            return await self.find_many(filter_query, sort=sort, skip=skip, limit=limit)
        except Exception as e:
            logger.error(f"Failed to find meal plan templates by user {user_id}: {e}")
            raise
