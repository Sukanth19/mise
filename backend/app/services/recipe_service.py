from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from app.repositories.recipe_repository import RecipeRepository
from app.schemas import RecipeCreate, RecipeUpdate


class RecipeManager:
    """Service for managing recipe CRUD operations."""
    
    def __init__(self, recipe_repository: RecipeRepository):
        """
        Initialize recipe manager with recipe repository.
        
        Args:
            recipe_repository: RecipeRepository instance for data access
        """
        self.recipe_repository = recipe_repository
    
    async def create_recipe(self, user_id: str, recipe_data: RecipeCreate) -> Dict[str, Any]:
        """
        Create a new recipe for a user.
        
        Args:
            user_id: User's ObjectId as string
            recipe_data: Recipe creation data
            
        Returns:
            Recipe document
        """
        recipe_doc = {
            "user_id": ObjectId(user_id),
            "title": recipe_data.title,
            "image_url": recipe_data.image_url,
            "ingredients": recipe_data.ingredients,
            "steps": recipe_data.steps,
            "tags": recipe_data.tags if recipe_data.tags is not None else [],
            "reference_link": recipe_data.reference_link,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_favorite": False,
            "visibility": "private",
            "servings": 1,
            "dietary_labels": [],
            "allergen_warnings": []
        }
        recipe_id = await self.recipe_repository.create(recipe_doc)
        recipe = await self.recipe_repository.find_by_id(recipe_id)
        return recipe
    
    async def get_user_recipes(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all recipes belonging to a user.
        
        Args:
            user_id: User's ObjectId as string
            
        Returns:
            List of recipe documents
        """
        return await self.recipe_repository.find_by_user(user_id)
    
    async def get_recipe_by_id(self, recipe_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a recipe by ID.
        
        Args:
            recipe_id: Recipe's ObjectId as string
            
        Returns:
            Recipe document if found, None otherwise
        """
        return await self.recipe_repository.find_by_id(recipe_id)
    
    async def update_recipe(self, recipe_id: str, user_id: str, recipe_data: RecipeUpdate) -> Optional[Dict[str, Any]]:
        """
        Update a recipe with ownership validation.
        
        Args:
            recipe_id: Recipe's ObjectId as string
            user_id: User's ObjectId as string
            recipe_data: Recipe update data
            
        Returns:
            Updated recipe document if successful, None otherwise
        """
        recipe = await self.get_recipe_by_id(recipe_id)
        if not recipe:
            return None
        
        # Verify ownership
        if not await self.verify_ownership(recipe_id, user_id):
            return None
        
        # Build update document
        update_doc = {"updated_at": datetime.utcnow()}
        
        if recipe_data.title is not None:
            update_doc["title"] = recipe_data.title
        if recipe_data.image_url is not None:
            update_doc["image_url"] = recipe_data.image_url
        if recipe_data.ingredients is not None:
            update_doc["ingredients"] = recipe_data.ingredients
        if recipe_data.steps is not None:
            update_doc["steps"] = recipe_data.steps
        if recipe_data.tags is not None:
            update_doc["tags"] = recipe_data.tags
        if recipe_data.reference_link is not None:
            update_doc["reference_link"] = recipe_data.reference_link
        
        await self.recipe_repository.update(recipe_id, update_doc)
        return await self.recipe_repository.find_by_id(recipe_id)
    
    async def delete_recipe(self, recipe_id: str, user_id: str) -> bool:
        """
        Delete a recipe with ownership validation.
        
        Args:
            recipe_id: Recipe's ObjectId as string
            user_id: User's ObjectId as string
            
        Returns:
            True if deleted successfully, False otherwise
        """
        recipe = await self.get_recipe_by_id(recipe_id)
        if not recipe:
            return False
        
        # Verify ownership
        if not await self.verify_ownership(recipe_id, user_id):
            return False
        
        return await self.recipe_repository.delete(recipe_id)
    
    async def verify_ownership(self, recipe_id: str, user_id: str) -> bool:
        """
        Verify that a user owns a recipe.
        
        Args:
            recipe_id: Recipe's ObjectId as string
            user_id: User's ObjectId as string
            
        Returns:
            True if user owns the recipe, False otherwise
        """
        recipe = await self.get_recipe_by_id(recipe_id)
        if not recipe:
            return False
        return str(recipe["user_id"]) == user_id
    
    async def duplicate_recipe(self, recipe_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Duplicate a recipe with a new ID and modified title.
        
        Args:
            recipe_id: Recipe's ObjectId as string
            user_id: User's ObjectId as string
            
        Returns:
            Duplicated recipe document if successful, None otherwise
        """
        original_recipe = await self.get_recipe_by_id(recipe_id)
        if not original_recipe:
            return None
        
        # Verify ownership
        if not await self.verify_ownership(recipe_id, user_id):
            return None
        
        # Create duplicated recipe with " (Copy)" suffix
        duplicated_recipe = {
            "user_id": ObjectId(user_id),
            "title": f"{original_recipe['title']} (Copy)",
            "image_url": original_recipe.get("image_url"),
            "ingredients": original_recipe.get("ingredients", []),
            "steps": original_recipe.get("steps", []),
            "tags": original_recipe.get("tags", []),
            "reference_link": original_recipe.get("reference_link"),
            "is_favorite": False,  # Reset favorite status
            "visibility": original_recipe.get("visibility", "private"),
            "servings": original_recipe.get("servings", 1),
            "source_recipe_id": original_recipe["_id"],
            "source_author_id": original_recipe["user_id"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "nutrition_facts": original_recipe.get("nutrition_facts"),
            "dietary_labels": original_recipe.get("dietary_labels", []),
            "allergen_warnings": original_recipe.get("allergen_warnings", [])
        }
        
        new_recipe_id = await self.recipe_repository.create(duplicated_recipe)
        return await self.recipe_repository.find_by_id(new_recipe_id)
    
    async def bulk_delete_recipes(self, recipe_ids: List[str], user_id: str) -> int:
        """
        Delete multiple recipes with ownership validation.
        
        Args:
            recipe_ids: List of recipe ObjectId strings
            user_id: User's ObjectId as string
            
        Returns:
            Number of recipes deleted
            
        Raises:
            ValueError: If any recipe not found
            PermissionError: If user doesn't own any recipe
        """
        # First, validate ownership for all recipes
        for recipe_id in recipe_ids:
            recipe = await self.get_recipe_by_id(recipe_id)
            if not recipe:
                raise ValueError(f"Recipe {recipe_id} not found")
            
            if str(recipe["user_id"]) != user_id:
                raise PermissionError(f"User does not own recipe {recipe_id}")
        
        # If all validations pass, delete all recipes
        deleted_count = 0
        for recipe_id in recipe_ids:
            if await self.recipe_repository.delete(recipe_id):
                deleted_count += 1
        
        return deleted_count
