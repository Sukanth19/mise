"""Recipe repository for MongoDB data access."""

from typing import Optional, List, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING, DESCENDING, TEXT
import logging

from .base import BaseRepository

logger = logging.getLogger(__name__)


class RecipeRepository(BaseRepository):
    """Repository for recipe collection operations."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Initialize recipe repository.
        
        Args:
            database: AsyncIOMotorDatabase instance
        """
        super().__init__(database, "recipes")
    
    async def ensure_indexes(self):
        """Create indexes for the recipes collection."""
        try:
            indexes = [
                IndexModel([("user_id", ASCENDING)]),
                IndexModel([("title", TEXT), ("ingredients", TEXT)]),
                IndexModel([("created_at", DESCENDING)]),
                IndexModel([("visibility", ASCENDING)]),
                IndexModel([("tags", ASCENDING)]),
                IndexModel([("user_id", ASCENDING), ("created_at", DESCENDING)])
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
        limit: int = 20,
        sort_by: str = "created_at",
        sort_order: int = DESCENDING
    ) -> List[Dict[str, Any]]:
        """
        Find recipes by user ID.
        
        Args:
            user_id: User's ObjectId as string
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            sort_by: Field to sort by
            sort_order: Sort direction (ASCENDING or DESCENDING)
            
        Returns:
            List of recipe documents
        """
        try:
            if not ObjectId.is_valid(user_id):
                logger.warning(f"Invalid user_id: {user_id}")
                return []
            
            filter_query = {"user_id": ObjectId(user_id)}
            sort = [(sort_by, sort_order)]
            
            return await self.find_many(filter_query, sort=sort, skip=skip, limit=limit)
        except Exception as e:
            logger.error(f"Failed to find recipes by user {user_id}: {e}")
            raise
    
    async def search(
        self,
        search_text: str,
        filters: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search recipes using text index.
        
        Args:
            search_text: Text to search for in title and ingredients
            filters: Additional filter criteria (tags, dietary_labels, etc.)
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            
        Returns:
            List of matching recipe documents
        """
        try:
            query = {"$text": {"$search": search_text}}
            
            if filters:
                query.update(filters)
            
            # Sort by text score for relevance
            cursor = self.collection.find(
                query,
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})])
            
            cursor = cursor.skip(skip).limit(limit)
            
            documents = await cursor.to_list(length=limit)
            logger.debug(f"Found {len(documents)} recipes matching search: {search_text}")
            return documents
        except Exception as e:
            logger.error(f"Failed to search recipes: {e}")
            raise
    
    async def find_with_filters(
        self,
        tags: Optional[List[str]] = None,
        dietary_labels: Optional[List[str]] = None,
        allergen_warnings: Optional[List[str]] = None,
        visibility: Optional[str] = None,
        user_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "created_at",
        sort_order: int = DESCENDING
    ) -> List[Dict[str, Any]]:
        """
        Find recipes with multiple filter criteria.
        
        Args:
            tags: Filter by tags (recipes must have all specified tags)
            dietary_labels: Filter by dietary labels
            allergen_warnings: Filter by allergen warnings
            visibility: Filter by visibility (private, public, unlisted)
            user_id: Filter by user ID
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            sort_by: Field to sort by
            sort_order: Sort direction
            
        Returns:
            List of matching recipe documents
        """
        try:
            filter_query = {}
            
            if tags:
                filter_query["tags"] = {"$all": tags}
            
            if dietary_labels:
                filter_query["dietary_labels"] = {"$all": dietary_labels}
            
            if allergen_warnings:
                filter_query["allergen_warnings"] = {"$all": allergen_warnings}
            
            if visibility:
                filter_query["visibility"] = visibility
            
            if user_id:
                if not ObjectId.is_valid(user_id):
                    logger.warning(f"Invalid user_id: {user_id}")
                    return []
                filter_query["user_id"] = ObjectId(user_id)
            
            sort = [(sort_by, sort_order)]
            
            return await self.find_many(filter_query, sort=sort, skip=skip, limit=limit)
        except Exception as e:
            logger.error(f"Failed to find recipes with filters: {e}")
            raise
