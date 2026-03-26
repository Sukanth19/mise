from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from app.repositories.recipe_rating_repository import RecipeRatingRepository
from app.repositories.recipe_repository import RecipeRepository


class RatingSystem:
    """Service for managing recipe ratings."""
    
    def __init__(self, rating_repository: RecipeRatingRepository, recipe_repository: RecipeRepository):
        """
        Initialize rating system with repositories.
        
        Args:
            rating_repository: RecipeRatingRepository instance for data access
            recipe_repository: RecipeRepository instance for recipe validation
        """
        self.rating_repository = rating_repository
        self.recipe_repository = recipe_repository
    
    @staticmethod
    def validate_rating(rating: int) -> bool:
        """Validate that rating is within 1-5 range."""
        return 1 <= rating <= 5
    
    async def add_rating(self, recipe_id: str, user_id: str, rating: int) -> Optional[Dict[str, Any]]:
        """
        Add a new rating for a recipe.
        
        Args:
            recipe_id: Recipe's ObjectId as string
            user_id: User's ObjectId as string
            rating: Rating value (1-5)
            
        Returns:
            Rating document if successful, None if validation fails or recipe doesn't exist
        """
        # Validate rating range
        if not RatingSystem.validate_rating(rating):
            return None
        
        # Verify recipe exists
        recipe = await self.recipe_repository.find_by_id(recipe_id)
        if not recipe:
            return None
        
        # Check if rating already exists
        existing_rating = await self.rating_repository.find_by_user_and_recipe(user_id, recipe_id)
        
        if existing_rating:
            return None  # Rating already exists, use update_rating instead
        
        # Create new rating
        rating_doc = {
            "recipe_id": ObjectId(recipe_id),
            "user_id": ObjectId(user_id),
            "rating": rating,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        rating_id = await self.rating_repository.create(rating_doc)
        return await self.rating_repository.find_by_id(rating_id)
    
    async def update_rating(self, recipe_id: str, user_id: str, rating: int) -> Optional[Dict[str, Any]]:
        """
        Update an existing rating for a recipe.
        
        Args:
            recipe_id: Recipe's ObjectId as string
            user_id: User's ObjectId as string
            rating: New rating value (1-5)
            
        Returns:
            Updated rating document if successful, None if validation fails or rating doesn't exist
        """
        # Validate rating range
        if not RatingSystem.validate_rating(rating):
            return None
        
        # Find existing rating
        existing_rating = await self.rating_repository.find_by_user_and_recipe(user_id, recipe_id)
        
        if not existing_rating:
            return None  # Rating doesn't exist, use add_rating instead
        
        # Update rating
        update_doc = {
            "rating": rating,
            "updated_at": datetime.utcnow()
        }
        await self.rating_repository.update(str(existing_rating["_id"]), update_doc)
        return await self.rating_repository.find_by_id(str(existing_rating["_id"]))
    
    async def get_user_rating(self, recipe_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a user's rating for a specific recipe.
        
        Args:
            recipe_id: Recipe's ObjectId as string
            user_id: User's ObjectId as string
            
        Returns:
            Rating document if found, None otherwise
        """
        return await self.rating_repository.find_by_user_and_recipe(user_id, recipe_id)
    
    async def get_average_rating(self, recipe_id: str) -> Optional[float]:
        """
        Calculate the average rating for a recipe using aggregation.
        
        Args:
            recipe_id: Recipe's ObjectId as string
            
        Returns:
            Average rating as float, None if no ratings exist
        """
        return await self.rating_repository.get_average_rating(recipe_id)
