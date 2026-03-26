"""Collection repository for MongoDB data access."""

from typing import Optional, List, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING, DESCENDING
import logging

from .base import BaseRepository

logger = logging.getLogger(__name__)


class CollectionRepository(BaseRepository):
    """Repository for collection collection operations."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Initialize collection repository.
        
        Args:
            database: AsyncIOMotorDatabase instance
        """
        super().__init__(database, "collections")
    
    async def ensure_indexes(self):
        """Create indexes for the collections collection."""
        try:
            indexes = [
                IndexModel([("user_id", ASCENDING)]),
                IndexModel([("parent_collection_id", ASCENDING)]),
                IndexModel([("share_token", ASCENDING)], unique=True, sparse=True)
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
        Find collections by user ID.
        
        Args:
            user_id: User's ObjectId as string
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            
        Returns:
            List of collection documents
        """
        try:
            if not ObjectId.is_valid(user_id):
                logger.warning(f"Invalid user_id: {user_id}")
                return []
            
            filter_query = {"user_id": ObjectId(user_id)}
            sort = [("created_at", DESCENDING)]
            
            return await self.find_many(filter_query, sort=sort, skip=skip, limit=limit)
        except Exception as e:
            logger.error(f"Failed to find collections by user {user_id}: {e}")
            raise
    
    async def find_by_share_token(self, share_token: str) -> Optional[Dict[str, Any]]:
        """
        Find a collection by its share token.
        
        Args:
            share_token: Share token to search for
            
        Returns:
            Collection document if found, None otherwise
        """
        try:
            collection = await self.collection.find_one({"share_token": share_token})
            if collection:
                logger.debug(f"Found collection by share_token: {share_token}")
            return collection
        except Exception as e:
            logger.error(f"Failed to find collection by share_token {share_token}: {e}")
            raise
    
    async def add_recipes(self, collection_id: str, recipe_ids: List[str]) -> bool:
        """
        Add recipes to a collection's recipe_ids array.
        
        Args:
            collection_id: Collection's ObjectId as string
            recipe_ids: List of recipe ObjectIds as strings
            
        Returns:
            True if recipes were added, False if collection not found
        """
        try:
            if not ObjectId.is_valid(collection_id):
                logger.warning(f"Invalid collection_id: {collection_id}")
                return False
            
            # Convert recipe_ids to ObjectIds
            recipe_object_ids = []
            for recipe_id in recipe_ids:
                if ObjectId.is_valid(recipe_id):
                    recipe_object_ids.append(ObjectId(recipe_id))
                else:
                    logger.warning(f"Invalid recipe_id: {recipe_id}")
            
            if not recipe_object_ids:
                return False
            
            result = await self.collection.update_one(
                {"_id": ObjectId(collection_id)},
                {"$addToSet": {"recipe_ids": {"$each": recipe_object_ids}}}
            )
            
            logger.debug(f"Added {len(recipe_object_ids)} recipes to collection {collection_id}")
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to add recipes to collection {collection_id}: {e}")
            raise
    
    async def remove_recipes(self, collection_id: str, recipe_ids: List[str]) -> bool:
        """
        Remove recipes from a collection's recipe_ids array.
        
        Args:
            collection_id: Collection's ObjectId as string
            recipe_ids: List of recipe ObjectIds as strings to remove
            
        Returns:
            True if recipes were removed, False if collection not found
        """
        try:
            if not ObjectId.is_valid(collection_id):
                logger.warning(f"Invalid collection_id: {collection_id}")
                return False
            
            # Convert recipe_ids to ObjectIds
            recipe_object_ids = []
            for recipe_id in recipe_ids:
                if ObjectId.is_valid(recipe_id):
                    recipe_object_ids.append(ObjectId(recipe_id))
                else:
                    logger.warning(f"Invalid recipe_id: {recipe_id}")
            
            if not recipe_object_ids:
                return False
            
            result = await self.collection.update_one(
                {"_id": ObjectId(collection_id)},
                {"$pull": {"recipe_ids": {"$in": recipe_object_ids}}}
            )
            
            logger.debug(f"Removed {len(recipe_object_ids)} recipes from collection {collection_id}")
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to remove recipes from collection {collection_id}: {e}")
            raise
