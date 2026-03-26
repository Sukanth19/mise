"""Repository layer for MongoDB data access.

This module provides repository classes that encapsulate MongoDB operations
for each collection in the database. Repositories follow the repository pattern
to separate data access logic from business logic.
"""

from .base import BaseRepository
from .user_repository import UserRepository
from .recipe_repository import RecipeRepository
from .recipe_rating_repository import RecipeRatingRepository
from .recipe_note_repository import RecipeNoteRepository
from .collection_repository import CollectionRepository
from .meal_plan_repository import MealPlanRepository
from .meal_plan_template_repository import MealPlanTemplateRepository
from .shopping_list_repository import ShoppingListRepository
from .user_follow_repository import UserFollowRepository
from .recipe_like_repository import RecipeLikeRepository
from .recipe_comment_repository import RecipeCommentRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "RecipeRepository",
    "RecipeRatingRepository",
    "RecipeNoteRepository",
    "CollectionRepository",
    "MealPlanRepository",
    "MealPlanTemplateRepository",
    "ShoppingListRepository",
    "UserFollowRepository",
    "RecipeLikeRepository",
    "RecipeCommentRepository",
]
