from typing import List, Optional, Dict, Any
from datetime import datetime
import secrets
from bson import ObjectId
from app.repositories.collection_repository import CollectionRepository
from app.repositories.recipe_repository import RecipeRepository
from app.schemas import CollectionCreate, CollectionUpdate


class CollectionManager:
    """Service for managing recipe collections."""
    
    def __init__(self, collection_repository: CollectionRepository, recipe_repository: RecipeRepository):
        """
        Initialize collection manager with repositories.
        
        Args:
            collection_repository: CollectionRepository instance for data access
            recipe_repository: RecipeRepository instance for recipe validation
        """
        self.collection_repository = collection_repository
        self.recipe_repository = recipe_repository
    
    async def create_collection(self, user_id: str, collection_data: CollectionCreate) -> Dict[str, Any]:
        """
        Create a new collection for a user.
        Validates nesting level if parent_collection_id is provided.
        
        Args:
            user_id: User's ObjectId as string
            collection_data: Collection creation data
            
        Returns:
            Collection document
            
        Raises:
            ValueError: If parent collection not found or nesting level exceeded
        """
        nesting_level = 0
        
        # Calculate nesting level if this is a nested collection
        if collection_data.parent_collection_id is not None:
            parent = await self.get_collection_by_id(
                str(collection_data.parent_collection_id), user_id
            )
            if not parent:
                raise ValueError("Parent collection not found")
            
            nesting_level = parent["nesting_level"] + 1
            
            # Validate nesting level (max 3 levels)
            if not CollectionManager.validate_nesting_level(nesting_level):
                raise ValueError("Maximum nesting level (3) exceeded")
        
        collection_doc = {
            "user_id": ObjectId(user_id),
            "name": collection_data.name,
            "description": collection_data.description,
            "cover_image_url": collection_data.cover_image_url,
            "parent_collection_id": ObjectId(collection_data.parent_collection_id) if collection_data.parent_collection_id else None,
            "nesting_level": nesting_level,
            "recipe_ids": [],
            "share_token": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        collection_id = await self.collection_repository.create(collection_doc)
        return await self.collection_repository.find_by_id(collection_id)
    
    async def get_user_collections(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all collections belonging to a user.
        
        Args:
            user_id: User's ObjectId as string
            
        Returns:
            List of collection documents
        """
        return await self.collection_repository.find_by_user(user_id)
    
    async def get_collection_by_id(self, collection_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a collection by ID with ownership validation.
        
        Args:
            collection_id: Collection's ObjectId as string
            user_id: User's ObjectId as string
            
        Returns:
            Collection document if found and owned by user, None otherwise
        """
        collection = await self.collection_repository.find_by_id(collection_id)
        if not collection:
            return None
        
        # Verify ownership
        if str(collection["user_id"]) != user_id:
            return None
        
        return collection
    
    async def update_collection(
        self, 
        collection_id: str, 
        user_id: str, 
        collection_data: CollectionUpdate
    ) -> Optional[Dict[str, Any]]:
        """
        Update a collection with ownership validation.
        
        Args:
            collection_id: Collection's ObjectId as string
            user_id: User's ObjectId as string
            collection_data: Collection update data
            
        Returns:
            Updated collection document if successful, None otherwise
        """
        collection = await self.get_collection_by_id(collection_id, user_id)
        if not collection:
            return None
        
        # Build update document
        update_doc = {"updated_at": datetime.utcnow()}
        
        if collection_data.name is not None:
            update_doc["name"] = collection_data.name
        if collection_data.description is not None:
            update_doc["description"] = collection_data.description
        if collection_data.cover_image_url is not None:
            update_doc["cover_image_url"] = collection_data.cover_image_url
        
        await self.collection_repository.update(collection_id, update_doc)
        return await self.collection_repository.find_by_id(collection_id)
    
    async def delete_collection(self, collection_id: str, user_id: str) -> bool:
        """
        Delete a collection with ownership validation.
        Note: Sub-collections should be handled separately if needed.
        
        Args:
            collection_id: Collection's ObjectId as string
            user_id: User's ObjectId as string
            
        Returns:
            True if deleted successfully, False otherwise
        """
        collection = await self.get_collection_by_id(collection_id, user_id)
        if not collection:
            return False
        
        return await self.collection_repository.delete(collection_id)
    
    @staticmethod
    def validate_nesting_level(nesting_level: int) -> bool:
        """Validate that nesting level does not exceed maximum (3 levels)."""
        return nesting_level <= 3
    
    async def add_recipes_to_collection(
        self, 
        collection_id: str, 
        recipe_ids: List[str], 
        user_id: str
    ) -> int:
        """
        Add multiple recipes to a collection.
        Validates user ownership of both collection and recipes.
        
        Args:
            collection_id: Collection's ObjectId as string
            recipe_ids: List of recipe ObjectIds as strings
            user_id: User's ObjectId as string
            
        Returns:
            Count of recipes added
            
        Raises:
            ValueError: If collection or any recipe not found or access denied
        """
        # Verify collection ownership
        collection = await self.get_collection_by_id(collection_id, user_id)
        if not collection:
            raise ValueError("Collection not found or access denied")
        
        # Verify recipe ownership for all recipes
        valid_recipe_ids = []
        for recipe_id in recipe_ids:
            recipe = await self.recipe_repository.find_by_id(recipe_id)
            
            if not recipe:
                raise ValueError(f"Recipe {recipe_id} not found or access denied")
            
            if str(recipe["user_id"]) != user_id:
                raise ValueError(f"Recipe {recipe_id} not found or access denied")
            
            # Check if recipe is not already in collection
            if ObjectId(recipe_id) not in collection.get("recipe_ids", []):
                valid_recipe_ids.append(recipe_id)
        
        if valid_recipe_ids:
            await self.collection_repository.add_recipes(collection_id, valid_recipe_ids)
        
        return len(valid_recipe_ids)
    
    async def remove_recipe_from_collection(
        self, 
        collection_id: str, 
        recipe_id: str, 
        user_id: str
    ) -> bool:
        """
        Remove a recipe from a collection.
        Validates user ownership of collection.
        Does not delete the recipe itself.
        
        Args:
            collection_id: Collection's ObjectId as string
            recipe_id: Recipe's ObjectId as string
            user_id: User's ObjectId as string
            
        Returns:
            True if removed successfully, False otherwise
        """
        # Verify collection ownership
        collection = await self.get_collection_by_id(collection_id, user_id)
        if not collection:
            return False
        
        # Remove the recipe from the collection
        return await self.collection_repository.remove_recipes(collection_id, [recipe_id])
    
    async def generate_share_token(self, collection_id: str, user_id: str) -> Optional[str]:
        """
        Generate a unique share token for a collection.
        
        Args:
            collection_id: Collection's ObjectId as string
            user_id: User's ObjectId as string
            
        Returns:
            Share token string if successful, None if collection not found
        """
        collection = await self.get_collection_by_id(collection_id, user_id)
        if not collection:
            return None
        
        # Generate a unique token
        share_token = secrets.token_urlsafe(32)
        
        # Ensure uniqueness (very unlikely to collide, but check anyway)
        while await self.collection_repository.find_by_share_token(share_token):
            share_token = secrets.token_urlsafe(32)
        
        await self.collection_repository.update(collection_id, {"share_token": share_token})
        return share_token
    
    async def revoke_share_token(self, collection_id: str, user_id: str) -> bool:
        """
        Revoke the share token for a collection.
        
        Args:
            collection_id: Collection's ObjectId as string
            user_id: User's ObjectId as string
            
        Returns:
            True if successful, False if collection not found
        """
        collection = await self.get_collection_by_id(collection_id, user_id)
        if not collection:
            return False
        
        await self.collection_repository.update(collection_id, {"share_token": None})
        return True
    
    async def get_shared_collection(self, share_token: str) -> Optional[Dict[str, Any]]:
        """
        Get a collection by its share token (public access, no auth required).
        
        Args:
            share_token: Share token to search for
            
        Returns:
            Collection document if found, None otherwise
        """
        return await self.collection_repository.find_by_share_token(share_token)
