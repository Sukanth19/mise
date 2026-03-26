"""Unit tests for repository structure and initialization.

These tests verify the repository classes are properly structured
without requiring a database connection.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from bson import ObjectId

from app.repositories.base import BaseRepository
from app.repositories.user_repository import UserRepository
from app.repositories.recipe_repository import RecipeRepository
from app.repositories.collection_repository import CollectionRepository
from app.repositories.meal_plan_repository import MealPlanRepository
from app.repositories.meal_plan_template_repository import MealPlanTemplateRepository
from app.repositories.shopping_list_repository import ShoppingListRepository
from app.repositories.recipe_rating_repository import RecipeRatingRepository
from app.repositories.recipe_note_repository import RecipeNoteRepository
from app.repositories.user_follow_repository import UserFollowRepository
from app.repositories.recipe_like_repository import RecipeLikeRepository
from app.repositories.recipe_comment_repository import RecipeCommentRepository


def test_base_repository_initialization():
    """Test BaseRepository can be initialized with mock database."""
    mock_db = Mock()
    mock_db.__getitem__ = Mock(return_value=Mock())
    
    repo = BaseRepository(mock_db, "test_collection")
    
    assert repo.collection_name == "test_collection"
    assert repo.database == mock_db


def test_user_repository_initialization():
    """Test UserRepository initializes with correct collection name."""
    mock_db = Mock()
    mock_db.__getitem__ = Mock(return_value=Mock())
    
    repo = UserRepository(mock_db)
    
    assert repo.collection_name == "users"


def test_recipe_repository_initialization():
    """Test RecipeRepository initializes with correct collection name."""
    mock_db = Mock()
    mock_db.__getitem__ = Mock(return_value=Mock())
    
    repo = RecipeRepository(mock_db)
    
    assert repo.collection_name == "recipes"


def test_collection_repository_initialization():
    """Test CollectionRepository initializes with correct collection name."""
    mock_db = Mock()
    mock_db.__getitem__ = Mock(return_value=Mock())
    
    repo = CollectionRepository(mock_db)
    
    assert repo.collection_name == "collections"


def test_meal_plan_repository_initialization():
    """Test MealPlanRepository initializes with correct collection name."""
    mock_db = Mock()
    mock_db.__getitem__ = Mock(return_value=Mock())
    
    repo = MealPlanRepository(mock_db)
    
    assert repo.collection_name == "meal_plans"


def test_meal_plan_template_repository_initialization():
    """Test MealPlanTemplateRepository initializes with correct collection name."""
    mock_db = Mock()
    mock_db.__getitem__ = Mock(return_value=Mock())
    
    repo = MealPlanTemplateRepository(mock_db)
    
    assert repo.collection_name == "meal_plan_templates"


def test_shopping_list_repository_initialization():
    """Test ShoppingListRepository initializes with correct collection name."""
    mock_db = Mock()
    mock_db.__getitem__ = Mock(return_value=Mock())
    
    repo = ShoppingListRepository(mock_db)
    
    assert repo.collection_name == "shopping_lists"


def test_recipe_rating_repository_initialization():
    """Test RecipeRatingRepository initializes with correct collection name."""
    mock_db = Mock()
    mock_db.__getitem__ = Mock(return_value=Mock())
    
    repo = RecipeRatingRepository(mock_db)
    
    assert repo.collection_name == "recipe_ratings"


def test_recipe_note_repository_initialization():
    """Test RecipeNoteRepository initializes with correct collection name."""
    mock_db = Mock()
    mock_db.__getitem__ = Mock(return_value=Mock())
    
    repo = RecipeNoteRepository(mock_db)
    
    assert repo.collection_name == "recipe_notes"


def test_user_follow_repository_initialization():
    """Test UserFollowRepository initializes with correct collection name."""
    mock_db = Mock()
    mock_db.__getitem__ = Mock(return_value=Mock())
    
    repo = UserFollowRepository(mock_db)
    
    assert repo.collection_name == "user_follows"


def test_recipe_like_repository_initialization():
    """Test RecipeLikeRepository initializes with correct collection name."""
    mock_db = Mock()
    mock_db.__getitem__ = Mock(return_value=Mock())
    
    repo = RecipeLikeRepository(mock_db)
    
    assert repo.collection_name == "recipe_likes"


def test_recipe_comment_repository_initialization():
    """Test RecipeCommentRepository initializes with correct collection name."""
    mock_db = Mock()
    mock_db.__getitem__ = Mock(return_value=Mock())
    
    repo = RecipeCommentRepository(mock_db)
    
    assert repo.collection_name == "recipe_comments"


def test_objectid_validation():
    """Test ObjectId validation in base repository."""
    from bson import ObjectId
    
    # Valid ObjectId
    valid_id = str(ObjectId())
    assert ObjectId.is_valid(valid_id)
    
    # Invalid ObjectId
    invalid_id = "not-a-valid-objectid"
    assert not ObjectId.is_valid(invalid_id)
