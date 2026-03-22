from sqlalchemy.orm import Session
from typing import List
from app.models import Recipe


class SearchEngine:
    """Service for searching recipes."""
    
    @staticmethod
    def search_recipes(db: Session, user_id: int, query: str) -> List[Recipe]:
        """
        Search recipes by title with case-insensitive matching.
        
        Args:
            db: Database session
            user_id: ID of the user performing the search
            query: Search query string
            
        Returns:
            List of recipes matching the search query for the given user
        """
        # Use ILIKE for case-insensitive search in PostgreSQL
        # Filter by user_id to respect user boundaries
        return db.query(Recipe).filter(
            Recipe.user_id == user_id,
            Recipe.title.ilike(f"%{query}%")
        ).all()
