"""Base repository class with common CRUD operations."""

from typing import Optional, List, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)


class BaseRepository:
    """Base repository providing common CRUD operations for MongoDB collections."""
    
    def __init__(self, database: AsyncIOMotorDatabase, collection_name: str):
        """
        Initialize repository with database and collection name.
        
        Args:
            database: AsyncIOMotorDatabase instance
            collection_name: Name of the MongoDB collection
        """
        self.database = database
        self.collection: AsyncIOMotorCollection = database[collection_name]
        self.collection_name = collection_name
    
    async def create(self, document: Dict[str, Any]) -> str:
        """
        Insert a new document into the collection.
        
        Args:
            document: Document data to insert
            
        Returns:
            String representation of the inserted document's ObjectId
            
        Raises:
            Exception: If insert operation fails
        """
        try:
            result = await self.collection.insert_one(document)
            logger.debug(f"Created document in {self.collection_name}: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to create document in {self.collection_name}: {e}")
            raise
    
    async def find_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Find a document by its ObjectId.
        
        Args:
            document_id: String representation of ObjectId
            
        Returns:
            Document dict if found, None otherwise
            
        Raises:
            Exception: If ObjectId is invalid or query fails
        """
        try:
            if not ObjectId.is_valid(document_id):
                logger.warning(f"Invalid ObjectId: {document_id}")
                return None
            
            document = await self.collection.find_one({"_id": ObjectId(document_id)})
            logger.debug(f"Found document in {self.collection_name}: {document_id}")
            return document
        except Exception as e:
            logger.error(f"Failed to find document in {self.collection_name}: {e}")
            raise
    
    async def find_many(
        self,
        filter_query: Dict[str, Any],
        sort: Optional[List[tuple]] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Find multiple documents matching filter criteria.
        
        Args:
            filter_query: MongoDB query filter
            sort: List of (field, direction) tuples for sorting
            skip: Number of documents to skip (for pagination)
            limit: Maximum number of documents to return
            
        Returns:
            List of matching documents
            
        Raises:
            Exception: If query fails
        """
        try:
            cursor = self.collection.find(filter_query)
            
            if sort:
                cursor = cursor.sort(sort)
            
            cursor = cursor.skip(skip).limit(limit)
            
            documents = await cursor.to_list(length=limit)
            logger.debug(f"Found {len(documents)} documents in {self.collection_name}")
            return documents
        except Exception as e:
            logger.error(f"Failed to find documents in {self.collection_name}: {e}")
            raise
    
    async def update(
        self,
        document_id: str,
        update_data: Dict[str, Any]
    ) -> bool:
        """
        Update a document by its ObjectId.
        
        Args:
            document_id: String representation of ObjectId
            update_data: Fields to update (will be wrapped in $set)
            
        Returns:
            True if document was updated, False if not found
            
        Raises:
            Exception: If ObjectId is invalid or update fails
        """
        try:
            if not ObjectId.is_valid(document_id):
                logger.warning(f"Invalid ObjectId: {document_id}")
                return False
            
            result = await self.collection.update_one(
                {"_id": ObjectId(document_id)},
                {"$set": update_data}
            )
            
            logger.debug(f"Updated document in {self.collection_name}: {document_id}")
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update document in {self.collection_name}: {e}")
            raise
    
    async def delete(self, document_id: str) -> bool:
        """
        Delete a document by its ObjectId.
        
        Args:
            document_id: String representation of ObjectId
            
        Returns:
            True if document was deleted, False if not found
            
        Raises:
            Exception: If ObjectId is invalid or delete fails
        """
        try:
            if not ObjectId.is_valid(document_id):
                logger.warning(f"Invalid ObjectId: {document_id}")
                return False
            
            result = await self.collection.delete_one({"_id": ObjectId(document_id)})
            
            logger.debug(f"Deleted document from {self.collection_name}: {document_id}")
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to delete document from {self.collection_name}: {e}")
            raise
    
    async def count(self, filter_query: Dict[str, Any] = None) -> int:
        """
        Count documents matching filter criteria.
        
        Args:
            filter_query: MongoDB query filter (empty dict for all documents)
            
        Returns:
            Number of matching documents
            
        Raises:
            Exception: If count operation fails
        """
        try:
            if filter_query is None:
                filter_query = {}
            
            count = await self.collection.count_documents(filter_query)
            logger.debug(f"Counted {count} documents in {self.collection_name}")
            return count
        except Exception as e:
            logger.error(f"Failed to count documents in {self.collection_name}: {e}")
            raise
