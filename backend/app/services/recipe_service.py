from sqlalchemy.orm import Session
from typing import List, Optional
import json
from app.models import Recipe
from app.schemas import RecipeCreate, RecipeUpdate


class RecipeManager:
    """Service for managing recipe CRUD operations."""
    
    @staticmethod
    def create_recipe(db: Session, user_id: int, recipe_data: RecipeCreate) -> Recipe:
        """Create a new recipe for a user."""
        recipe = Recipe(
            user_id=user_id,
            title=recipe_data.title,
            image_url=recipe_data.image_url,
            ingredients=json.dumps(recipe_data.ingredients),
            steps=json.dumps(recipe_data.steps),
            tags=json.dumps(recipe_data.tags) if recipe_data.tags is not None else None,
            reference_link=recipe_data.reference_link
        )
        db.add(recipe)
        db.commit()
        db.refresh(recipe)
        return recipe
    
    @staticmethod
    def get_user_recipes(db: Session, user_id: int) -> List[Recipe]:
        """Get all recipes belonging to a user."""
        return db.query(Recipe).filter(Recipe.user_id == user_id).all()
    
    @staticmethod
    def get_recipe_by_id(db: Session, recipe_id: int) -> Optional[Recipe]:
        """Get a recipe by ID."""
        return db.query(Recipe).filter(Recipe.id == recipe_id).first()
    
    @staticmethod
    def update_recipe(db: Session, recipe_id: int, user_id: int, recipe_data: RecipeUpdate) -> Optional[Recipe]:
        """Update a recipe with ownership validation."""
        recipe = RecipeManager.get_recipe_by_id(db, recipe_id)
        if not recipe:
            return None
        
        # Verify ownership
        if not RecipeManager.verify_ownership(recipe_id, user_id, db):
            return None
        
        # Update fields if provided
        if recipe_data.title is not None:
            recipe.title = recipe_data.title
        if recipe_data.image_url is not None:
            recipe.image_url = recipe_data.image_url
        if recipe_data.ingredients is not None:
            recipe.ingredients = json.dumps(recipe_data.ingredients)
        if recipe_data.steps is not None:
            recipe.steps = json.dumps(recipe_data.steps)
        if recipe_data.tags is not None:
            recipe.tags = json.dumps(recipe_data.tags)
        if recipe_data.reference_link is not None:
            recipe.reference_link = recipe_data.reference_link
        
        db.commit()
        db.refresh(recipe)
        return recipe
    
    @staticmethod
    def delete_recipe(db: Session, recipe_id: int, user_id: int) -> bool:
        """Delete a recipe with ownership validation."""
        recipe = RecipeManager.get_recipe_by_id(db, recipe_id)
        if not recipe:
            return False
        
        # Verify ownership
        if not RecipeManager.verify_ownership(recipe_id, user_id, db):
            return False
        
        db.delete(recipe)
        db.commit()
        return True
    
    @staticmethod
    def verify_ownership(recipe_id: int, user_id: int, db: Session) -> bool:
        """Verify that a user owns a recipe."""
        recipe = RecipeManager.get_recipe_by_id(db, recipe_id)
        if not recipe:
            return False
        return recipe.user_id == user_id
