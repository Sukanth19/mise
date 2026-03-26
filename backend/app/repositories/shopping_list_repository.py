"""Shopping list repository for MongoDB data access."""

from typing import Optional, List, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING, DESCENDING
import logging

from .base import BaseRepository

logger = logging.getLogger(__name__)


class ShoppingListRepository(BaseRepository):
    """Repository for shopping list collection operations."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Initialize shopping list repository.
        
        Args:
            database: AsyncIOMotorDatabase instance
        """
        super().__init__(database, "shopping_lists")
    
    async def ensure_indexes(self):
        """Create indexes for the shopping_lists collection."""
        try:
            indexes = [
                IndexModel([("user_id", ASCENDING)]),
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
        Find shopping lists by user ID.
        
        Args:
            user_id: User's ObjectId as string
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            
        Returns:
            List of shopping list documents
        """
        try:
            if not ObjectId.is_valid(user_id):
                logger.warning(f"Invalid user_id: {user_id}")
                return []
            
            filter_query = {"user_id": ObjectId(user_id)}
            sort = [("created_at", DESCENDING)]
            
            return await self.find_many(filter_query, sort=sort, skip=skip, limit=limit)
        except Exception as e:
            logger.error(f"Failed to find shopping lists by user {user_id}: {e}")
            raise
    
    async def find_by_share_token(self, share_token: str) -> Optional[Dict[str, Any]]:
        """
        Find a shopping list by its share token.
        
        Args:
            share_token: Share token to search for
            
        Returns:
            Shopping list document if found, None otherwise
        """
        try:
            shopping_list = await self.collection.find_one({"share_token": share_token})
            if shopping_list:
                logger.debug(f"Found shopping list by share_token: {share_token}")
            return shopping_list
        except Exception as e:
            logger.error(f"Failed to find shopping list by share_token {share_token}: {e}")
            raise
    
    async def update_item_checked(
        self,
        shopping_list_id: str,
        item_index: int,
        is_checked: bool
    ) -> bool:
        """
        Update the is_checked status of a specific item in the shopping list.
        
        Args:
            shopping_list_id: Shopping list's ObjectId as string
            item_index: Index of the item in the items array
            is_checked: New checked status
            
        Returns:
            True if item was updated, False if not found
        """
        try:
            if not ObjectId.is_valid(shopping_list_id):
                logger.warning(f"Invalid shopping_list_id: {shopping_list_id}")
                return False
            
            result = await self.collection.update_one(
                {"_id": ObjectId(shopping_list_id)},
                {"$set": {f"items.{item_index}.is_checked": is_checked}}
            )
            
            logger.debug(f"Updated item {item_index} in shopping list {shopping_list_id}")
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update item in shopping list {shopping_list_id}: {e}")
            raise
    
    async def add_item(
        self,
        shopping_list_id: str,
        item: Dict[str, Any]
    ) -> bool:
        """
        Add an item to the shopping list's items array.
        
        Args:
            shopping_list_id: Shopping list's ObjectId as string
            item: Item data to add
            
        Returns:
            True if item was added, False if shopping list not found
        """
        try:
            if not ObjectId.is_valid(shopping_list_id):
                logger.warning(f"Invalid shopping_list_id: {shopping_list_id}")
                return False
            
            result = await self.collection.update_one(
                {"_id": ObjectId(shopping_list_id)},
                {"$push": {"items": item}}
            )
            
            logger.debug(f"Added item to shopping list {shopping_list_id}")
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to add item to shopping list {shopping_list_id}: {e}")
            raise
