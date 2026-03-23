from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from app.models import Recipe, RecipeRating, DietaryLabel, AllergenWarning
import json


class FilterEngine:
    """Service for filtering and sorting recipes."""
    
    @staticmethod
    def filter_recipes(
        db: Session,
        user_id: int,
        favorites: Optional[bool] = None,
        min_rating: Optional[float] = None,
        tags: Optional[List[str]] = None,
        dietary_labels: Optional[List[str]] = None,
        exclude_allergens: Optional[List[str]] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = "asc"
    ) -> List[Recipe]:
        """
        Main entry point for filtering and sorting recipes.
        
        Args:
            db: Database session
            user_id: User ID to filter recipes for
            favorites: Filter by favorite status (True/False)
            min_rating: Minimum average rating threshold
            tags: List of tags (recipes with any of these tags)
            dietary_labels: List of dietary labels (recipes with matching labels)
            exclude_allergens: List of allergens to exclude
            sort_by: Field to sort by ('date', 'rating', 'title')
            sort_order: Sort order ('asc' or 'desc')
        
        Returns:
            List of filtered and sorted recipes
        """
        # Start with user's recipes
        query = db.query(Recipe).filter(Recipe.user_id == user_id)
        
        # Apply favorite filter
        if favorites is not None:
            query = query.filter(Recipe.is_favorite == favorites)
        
        # Get initial results
        recipes = query.all()
        
        # Apply rating filter
        if min_rating is not None:
            recipes = FilterEngine.apply_rating_filter(db, recipes, min_rating)
        
        # Apply tag filter
        if tags:
            recipes = FilterEngine.apply_tag_filter(recipes, tags)
        
        # Apply dietary label filter
        if dietary_labels:
            recipes = FilterEngine.apply_dietary_filter(db, recipes, dietary_labels)
        
        # Apply allergen exclusion
        if exclude_allergens:
            recipes = FilterEngine.apply_allergen_exclusion(db, recipes, exclude_allergens)
        
        # Apply sorting
        if sort_by:
            recipes = FilterEngine.sort_recipes(db, recipes, sort_by, sort_order)
        
        return recipes
    
    @staticmethod
    def apply_favorite_filter(recipes: List[Recipe]) -> List[Recipe]:
        """Filter recipes by favorite status."""
        return [recipe for recipe in recipes if recipe.is_favorite]
    
    @staticmethod
    def apply_rating_filter(db: Session, recipes: List[Recipe], min_rating: float) -> List[Recipe]:
        """
        Filter recipes by minimum average rating threshold.
        
        Args:
            db: Database session
            recipes: List of recipes to filter
            min_rating: Minimum average rating threshold
        
        Returns:
            List of recipes with average rating >= min_rating
        """
        filtered_recipes = []
        
        for recipe in recipes:
            # Calculate average rating for this recipe
            avg_rating = db.query(func.avg(RecipeRating.rating)).filter(
                RecipeRating.recipe_id == recipe.id
            ).scalar()
            
            # Include recipe if it has ratings and meets threshold
            if avg_rating is not None and avg_rating >= min_rating:
                filtered_recipes.append(recipe)
        
        return filtered_recipes
    
    @staticmethod
    def apply_tag_filter(recipes: List[Recipe], tags: List[str]) -> List[Recipe]:
        """
        Filter recipes by tags (any of selected tags).
        
        Args:
            recipes: List of recipes to filter
            tags: List of tags to match (case-insensitive)
        
        Returns:
            List of recipes containing at least one of the specified tags
        """
        filtered_recipes = []
        # Normalize tags to lowercase for case-insensitive matching
        normalized_tags = [tag.lower() for tag in tags]
        
        for recipe in recipes:
            if recipe.tags:
                # Parse tags from JSON string
                try:
                    recipe_tags = json.loads(recipe.tags)
                    # Normalize recipe tags to lowercase
                    recipe_tags_lower = [t.lower() for t in recipe_tags]
                    
                    # Check if any of the filter tags match
                    if any(tag in recipe_tags_lower for tag in normalized_tags):
                        filtered_recipes.append(recipe)
                except (json.JSONDecodeError, TypeError):
                    # Skip recipes with invalid tag data
                    continue
        
        return filtered_recipes
    
    @staticmethod
    def apply_dietary_filter(db: Session, recipes: List[Recipe], labels: List[str]) -> List[Recipe]:
        """
        Filter recipes by dietary labels (recipes with matching labels).
        
        Args:
            db: Database session
            recipes: List of recipes to filter
            labels: List of dietary labels to match
        
        Returns:
            List of recipes that have all specified dietary labels
        """
        filtered_recipes = []
        
        for recipe in recipes:
            # Get all dietary labels for this recipe
            recipe_labels = db.query(DietaryLabel).filter(
                DietaryLabel.recipe_id == recipe.id
            ).all()
            
            recipe_label_names = [label.label for label in recipe_labels]
            
            # Check if recipe has all required labels
            if all(label in recipe_label_names for label in labels):
                filtered_recipes.append(recipe)
        
        return filtered_recipes
    
    @staticmethod
    def apply_allergen_exclusion(db: Session, recipes: List[Recipe], allergens: List[str]) -> List[Recipe]:
        """
        Exclude recipes with specified allergens.
        
        Args:
            db: Database session
            recipes: List of recipes to filter
            allergens: List of allergens to exclude
        
        Returns:
            List of recipes that do not contain any of the specified allergens
        """
        filtered_recipes = []
        
        for recipe in recipes:
            # Get all allergen warnings for this recipe
            recipe_allergens = db.query(AllergenWarning).filter(
                AllergenWarning.recipe_id == recipe.id
            ).all()
            
            recipe_allergen_names = [allergen.allergen for allergen in recipe_allergens]
            
            # Include recipe only if it doesn't have any of the excluded allergens
            if not any(allergen in recipe_allergen_names for allergen in allergens):
                filtered_recipes.append(recipe)
        
        return filtered_recipes
    
    @staticmethod
    def sort_recipes(db: Session, recipes: List[Recipe], sort_by: str, sort_order: str = "asc") -> List[Recipe]:
        """
        Sort recipes by specified field.
        
        Args:
            db: Database session
            recipes: List of recipes to sort
            sort_by: Field to sort by ('date', 'rating', 'title')
            sort_order: Sort order ('asc' or 'desc')
        
        Returns:
            Sorted list of recipes
        """
        reverse = (sort_order.lower() == "desc")
        
        if sort_by == "date":
            # Sort by created_at timestamp
            return sorted(recipes, key=lambda r: r.created_at, reverse=reverse)
        
        elif sort_by == "rating":
            # Sort by average rating
            def get_avg_rating(recipe):
                avg_rating = db.query(func.avg(RecipeRating.rating)).filter(
                    RecipeRating.recipe_id == recipe.id
                ).scalar()
                # Return 0 for recipes without ratings so they appear at the bottom
                return avg_rating if avg_rating is not None else 0
            
            return sorted(recipes, key=get_avg_rating, reverse=reverse)
        
        elif sort_by == "title":
            # Sort by title (case-insensitive)
            return sorted(recipes, key=lambda r: r.title.lower(), reverse=reverse)
        
        else:
            # Unknown sort field, return unsorted
            return recipes
