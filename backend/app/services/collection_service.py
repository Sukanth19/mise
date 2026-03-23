from sqlalchemy.orm import Session
from typing import List, Optional
import secrets
from app.models import Collection, CollectionRecipe, Recipe
from app.schemas import CollectionCreate, CollectionUpdate


class CollectionManager:
    """Service for managing recipe collections."""
    
    @staticmethod
    def create_collection(db: Session, user_id: int, collection_data: CollectionCreate) -> Collection:
        """
        Create a new collection for a user.
        Validates nesting level if parent_collection_id is provided.
        """
        nesting_level = 0
        
        # Calculate nesting level if this is a nested collection
        if collection_data.parent_collection_id is not None:
            parent = CollectionManager.get_collection_by_id(
                db, collection_data.parent_collection_id, user_id
            )
            if not parent:
                raise ValueError("Parent collection not found")
            
            nesting_level = parent.nesting_level + 1
            
            # Validate nesting level (max 3 levels)
            if not CollectionManager.validate_nesting_level(nesting_level):
                raise ValueError("Maximum nesting level (3) exceeded")
        
        collection = Collection(
            user_id=user_id,
            name=collection_data.name,
            description=collection_data.description,
            cover_image_url=collection_data.cover_image_url,
            parent_collection_id=collection_data.parent_collection_id,
            nesting_level=nesting_level
        )
        db.add(collection)
        db.commit()
        db.refresh(collection)
        return collection
    
    @staticmethod
    def get_user_collections(db: Session, user_id: int) -> List[Collection]:
        """Get all collections belonging to a user."""
        return db.query(Collection).filter(Collection.user_id == user_id).all()
    
    @staticmethod
    def get_collection_by_id(db: Session, collection_id: int, user_id: int) -> Optional[Collection]:
        """
        Get a collection by ID with ownership validation.
        Returns None if collection doesn't exist or user doesn't own it.
        """
        collection = db.query(Collection).filter(Collection.id == collection_id).first()
        if not collection:
            return None
        
        # Verify ownership
        if collection.user_id != user_id:
            return None
        
        return collection
    
    @staticmethod
    def update_collection(
        db: Session, 
        collection_id: int, 
        user_id: int, 
        collection_data: CollectionUpdate
    ) -> Optional[Collection]:
        """Update a collection with ownership validation."""
        collection = CollectionManager.get_collection_by_id(db, collection_id, user_id)
        if not collection:
            return None
        
        # Update fields if provided
        if collection_data.name is not None:
            collection.name = collection_data.name
        if collection_data.description is not None:
            collection.description = collection_data.description
        if collection_data.cover_image_url is not None:
            collection.cover_image_url = collection_data.cover_image_url
        
        db.commit()
        db.refresh(collection)
        return collection
    
    @staticmethod
    def delete_collection(db: Session, collection_id: int, user_id: int) -> bool:
        """
        Delete a collection with ownership validation.
        Cascading delete will automatically remove sub-collections and collection-recipe associations.
        """
        collection = CollectionManager.get_collection_by_id(db, collection_id, user_id)
        if not collection:
            return False
        
        db.delete(collection)
        db.commit()
        return True
    
    @staticmethod
    def validate_nesting_level(nesting_level: int) -> bool:
        """Validate that nesting level does not exceed maximum (3 levels)."""
        return nesting_level <= 3
    
    @staticmethod
    def add_recipes_to_collection(
        db: Session, 
        collection_id: int, 
        recipe_ids: List[int], 
        user_id: int
    ) -> int:
        """
        Add multiple recipes to a collection.
        Validates user ownership of both collection and recipes.
        Returns count of recipes added.
        """
        # Verify collection ownership
        collection = CollectionManager.get_collection_by_id(db, collection_id, user_id)
        if not collection:
            raise ValueError("Collection not found or access denied")
        
        added_count = 0
        
        for recipe_id in recipe_ids:
            # Verify recipe ownership
            recipe = db.query(Recipe).filter(
                Recipe.id == recipe_id,
                Recipe.user_id == user_id
            ).first()
            
            if not recipe:
                raise ValueError(f"Recipe {recipe_id} not found or access denied")
            
            # Check if association already exists
            existing = db.query(CollectionRecipe).filter(
                CollectionRecipe.collection_id == collection_id,
                CollectionRecipe.recipe_id == recipe_id
            ).first()
            
            if not existing:
                # Create association
                collection_recipe = CollectionRecipe(
                    collection_id=collection_id,
                    recipe_id=recipe_id
                )
                db.add(collection_recipe)
                added_count += 1
        
        db.commit()
        return added_count
    
    @staticmethod
    def remove_recipe_from_collection(
        db: Session, 
        collection_id: int, 
        recipe_id: int, 
        user_id: int
    ) -> bool:
        """
        Remove a recipe from a collection.
        Validates user ownership of collection.
        Does not delete the recipe itself.
        """
        # Verify collection ownership
        collection = CollectionManager.get_collection_by_id(db, collection_id, user_id)
        if not collection:
            return False
        
        # Find and delete the association
        association = db.query(CollectionRecipe).filter(
            CollectionRecipe.collection_id == collection_id,
            CollectionRecipe.recipe_id == recipe_id
        ).first()
        
        if not association:
            return False
        
        db.delete(association)
        db.commit()
        return True
    
    @staticmethod
    def generate_share_token(db: Session, collection_id: int, user_id: int) -> Optional[str]:
        """
        Generate a unique share token for a collection.
        Returns the share token or None if collection not found.
        """
        collection = CollectionManager.get_collection_by_id(db, collection_id, user_id)
        if not collection:
            return None
        
        # Generate a unique token
        share_token = secrets.token_urlsafe(32)
        
        # Ensure uniqueness (very unlikely to collide, but check anyway)
        while db.query(Collection).filter(Collection.share_token == share_token).first():
            share_token = secrets.token_urlsafe(32)
        
        collection.share_token = share_token
        db.commit()
        db.refresh(collection)
        return share_token
    
    @staticmethod
    def revoke_share_token(db: Session, collection_id: int, user_id: int) -> bool:
        """
        Revoke the share token for a collection.
        Returns True if successful, False if collection not found.
        """
        collection = CollectionManager.get_collection_by_id(db, collection_id, user_id)
        if not collection:
            return False
        
        collection.share_token = None
        db.commit()
        return True
    
    @staticmethod
    def get_shared_collection(db: Session, share_token: str) -> Optional[Collection]:
        """
        Get a collection by its share token (public access, no auth required).
        Returns None if token is invalid or collection not found.
        """
        collection = db.query(Collection).filter(
            Collection.share_token == share_token
        ).first()
        
        return collection
