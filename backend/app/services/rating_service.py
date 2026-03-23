from sqlalchemy.orm import Session
from typing import Optional
from app.models import RecipeRating, Recipe


class RatingSystem:
    """Service for managing recipe ratings."""
    
    @staticmethod
    def validate_rating(rating: int) -> bool:
        """Validate that rating is within 1-5 range."""
        return 1 <= rating <= 5
    
    @staticmethod
    def add_rating(db: Session, recipe_id: int, user_id: int, rating: int) -> Optional[RecipeRating]:
        """
        Add a new rating for a recipe.
        Returns None if validation fails or recipe doesn't exist.
        """
        # Validate rating range
        if not RatingSystem.validate_rating(rating):
            return None
        
        # Verify recipe exists
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if not recipe:
            return None
        
        # Check if rating already exists
        existing_rating = db.query(RecipeRating).filter(
            RecipeRating.recipe_id == recipe_id,
            RecipeRating.user_id == user_id
        ).first()
        
        if existing_rating:
            return None  # Rating already exists, use update_rating instead
        
        # Create new rating
        new_rating = RecipeRating(
            recipe_id=recipe_id,
            user_id=user_id,
            rating=rating
        )
        db.add(new_rating)
        db.commit()
        db.refresh(new_rating)
        return new_rating
    
    @staticmethod
    def update_rating(db: Session, recipe_id: int, user_id: int, rating: int) -> Optional[RecipeRating]:
        """
        Update an existing rating for a recipe.
        Returns None if validation fails or rating doesn't exist.
        """
        # Validate rating range
        if not RatingSystem.validate_rating(rating):
            return None
        
        # Find existing rating
        existing_rating = db.query(RecipeRating).filter(
            RecipeRating.recipe_id == recipe_id,
            RecipeRating.user_id == user_id
        ).first()
        
        if not existing_rating:
            return None  # Rating doesn't exist, use add_rating instead
        
        # Update rating
        existing_rating.rating = rating
        db.commit()
        db.refresh(existing_rating)
        return existing_rating
    
    @staticmethod
    def get_user_rating(db: Session, recipe_id: int, user_id: int) -> Optional[RecipeRating]:
        """Get a user's rating for a specific recipe."""
        return db.query(RecipeRating).filter(
            RecipeRating.recipe_id == recipe_id,
            RecipeRating.user_id == user_id
        ).first()
    
    @staticmethod
    def get_average_rating(db: Session, recipe_id: int) -> Optional[float]:
        """
        Calculate the average rating for a recipe.
        Returns None if no ratings exist.
        """
        from sqlalchemy import func
        
        result = db.query(func.avg(RecipeRating.rating)).filter(
            RecipeRating.recipe_id == recipe_id
        ).scalar()
        
        return float(result) if result is not None else None
