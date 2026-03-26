"""Meal plan repository for MongoDB data access."""

from typing import List, Dict, Any
from datetime import date
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING
import logging

from .base import BaseRepository

logger = logging.getLogger(__name__)


class MealPlanRepository(BaseRepository):
    """Repository for meal plan collection operations."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Initialize meal plan repository.
        
        Args:
            database: AsyncIOMotorDatabase instance
        """
        super().__init__(database, "meal_plans")
    
    async def ensure_indexes(self):
        """Create indexes for the meal_plans collection."""
        try:
            indexes = [
                IndexModel([("user_id", ASCENDING)]),
                IndexModel([("meal_date", ASCENDING)]),
                IndexModel([("user_id", ASCENDING), ("meal_date", ASCENDING)])
            ]
            await self.collection.create_indexes(indexes)
            logger.info(f"Created indexes for {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to create indexes for {self.collection_name}: {e}")
            raise
    
    async def find_by_user_and_date_range(
        self,
        user_id: str,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """
        Find meal plans for a user within a date range.
        
        Args:
            user_id: User's ObjectId as string
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            List of meal plan documents
        """
        try:
            if not ObjectId.is_valid(user_id):
                logger.warning(f"Invalid user_id: {user_id}")
                return []
            
            filter_query = {
                "user_id": ObjectId(user_id),
                "meal_date": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
            
            sort = [("meal_date", ASCENDING)]
            
            # Use a higher limit for meal plans (typically 7-30 days)
            return await self.find_many(filter_query, sort=sort, limit=1000)
        except Exception as e:
            logger.error(f"Failed to find meal plans for user {user_id}: {e}")
            raise
