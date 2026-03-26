"""
Unit tests for ShoppingListGenerator service.
Tests core functionality of shopping list generation and management.
"""
import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"
os.environ["MONGODB_URL"] = "mongodb://localhost:27017"
os.environ["MONGODB_DATABASE"] = "recipe_saver_test"

import pytest
from datetime import date, timedelta
from bson import ObjectId
from app.services.shopping_list_service import ShoppingListGenerator
from app.schemas import ShoppingListCreate, CustomItemCreate
from app.repositories.shopping_list_repository import ShoppingListRepository
from app.repositories.recipe_repository import RecipeRepository
from app.repositories.meal_plan_repository import MealPlanRepository
from app.repositories.user_repository import UserRepository
from app.database import mongodb


@pytest.fixture
async def shopping_list_generator():
    """Create ShoppingListGenerator with MongoDB repositories."""
    await mongodb.connect(
        os.environ.get("MONGODB_URL", "mongodb://localhost:27017"),
        os.environ.get("MONGODB_DATABASE", "recipe_saver_test")
    )
    db = await mongodb.get_database()
    
    # Clean all collections before test
    for collection_name in await db.list_collection_names():
        await db[collection_name].delete_many({})
    
    shopping_list_repo = ShoppingListRepository(db)
    recipe_repo = RecipeRepository(db)
    meal_plan_repo = MealPlanRepository(db)
    user_repo = UserRepository(db)
    
    generator = ShoppingListGenerator(shopping_list_repo, recipe_repo, meal_plan_repo)
    
    yield generator, user_repo, recipe_repo, meal_plan_repo
    
    # Clean up after test
    for collection_name in await db.list_collection_names():
        await db[collection_name].delete_many({})
    await mongodb.disconnect()


@pytest.mark.asyncio
async def test_create_shopping_list_from_recipes(shopping_list_generator):
    """Test creating a shopping list from recipe IDs."""
    generator, user_repo, recipe_repo, _ = shopping_list_generator
    
    # Create a user
    user_id = await user_repo.create({
        "username": "testuser",
        "password_hash": "hashed_password"
    })
    
    # Create a recipe
    recipe_id = await recipe_repo.create({
        "user_id": ObjectId(user_id),
        "title": "Test Recipe",
        "ingredients": ["2 cups flour", "1 egg", "salt"],
        "steps": ["Mix ingredients", "Cook"]
    })
    
    shopping_list_data = ShoppingListCreate(
        name="Weekly Shopping",
        recipe_ids=[recipe_id]
    )
    
    shopping_list = await generator.create_shopping_list(user_id, shopping_list_data)
    
    assert shopping_list is not None
    assert shopping_list["name"] == "Weekly Shopping"
    assert str(shopping_list["user_id"]) == user_id
    
    # Verify items were created (embedded in the shopping list)
    items = shopping_list.get("items", [])
    assert len(items) > 0


@pytest.mark.asyncio
async def test_create_shopping_list_from_meal_plan(shopping_list_generator):
    """Test creating a shopping list from meal plan date range."""
    generator, user_repo, recipe_repo, meal_plan_repo = shopping_list_generator
    
    # Create a user
    user_id = await user_repo.create({
        "username": "testuser",
        "password_hash": "hashed_password"
    })
    
    # Create a recipe
    recipe_id = await recipe_repo.create({
        "user_id": ObjectId(user_id),
        "title": "Test Recipe",
        "ingredients": ["2 cups flour", "1 egg", "salt"],
        "steps": ["Mix ingredients", "Cook"]
    })
    
    # Create a meal plan
    today = date.today()
    await meal_plan_repo.create({
        "user_id": ObjectId(user_id),
        "recipe_id": ObjectId(recipe_id),
        "meal_date": today,
        "meal_time": "dinner"
    })
    
    # Create shopping list from meal plan
    shopping_list_data = ShoppingListCreate(
        name="Meal Plan Shopping",
        meal_plan_start_date=today.strftime('%Y-%m-%d'),
        meal_plan_end_date=(today + timedelta(days=7)).strftime('%Y-%m-%d')
    )
    
    shopping_list = await generator.create_shopping_list(user_id, shopping_list_data)
    
    assert shopping_list is not None
    assert shopping_list["name"] == "Meal Plan Shopping"


def test_extract_ingredients_from_recipes(db, test_user):
    """Test extracting ingredients from multiple recipes."""
    # Create recipes with ingredients
    recipe1 = Recipe(
        user_id=test_user.id,
        title="Pasta",
        ingredients=json.dumps(["2 cups flour", "1 egg", "salt"]),
        steps=json.dumps(["Mix", "Cook"])
    )
    recipe2 = Recipe(
        user_id=test_user.id,
        title="Salad",
        ingredients=json.dumps(["1 head lettuce", "2 tomatoes", "salt"]),
        steps=json.dumps(["Chop", "Mix"])
    )
    db.add_all([recipe1, recipe2])
    db.commit()
    
    ingredients = ShoppingListGenerator.extract_ingredients_from_recipes(
        db, [recipe1.id, recipe2.id], test_user.id
    )
    
    assert len(ingredients) == 5  # 3 from recipe1 + 2 from recipe2
    assert any(ing['ingredient_name'] == 'flour' for ing in ingredients)
    assert any(ing['ingredient_name'] == 'lettuce' for ing in ingredients)


def test_consolidate_ingredients():
    """Test consolidating duplicate ingredients."""
    ingredients = [
        {'ingredient_name': 'flour', 'quantity': '2 cups', 'recipe_id': 1},
        {'ingredient_name': 'Flour', 'quantity': '1 cup', 'recipe_id': 2},
        {'ingredient_name': 'salt', 'quantity': None, 'recipe_id': 1},
        {'ingredient_name': 'Salt', 'quantity': None, 'recipe_id': 2}
    ]
    
    consolidated = ShoppingListGenerator.consolidate_ingredients(ingredients)
    
    # Should consolidate case-insensitive
    assert len(consolidated) == 2
    
    # Find flour entry
    flour_entry = next(ing for ing in consolidated if ing['ingredient_name'].lower() == 'flour')
    assert flour_entry['quantity'] == '3.0 cups'  # 2 + 1


def test_categorize_ingredient():
    """Test ingredient categorization."""
    assert ShoppingListGenerator.categorize_ingredient('tomato') == 'produce'
    assert ShoppingListGenerator.categorize_ingredient('chicken breast') == 'meat'
    assert ShoppingListGenerator.categorize_ingredient('milk') == 'dairy'
    assert ShoppingListGenerator.categorize_ingredient('flour') == 'pantry'
    assert ShoppingListGenerator.categorize_ingredient('unknown item') == 'other'


def test_parse_ingredient():
    """Test parsing ingredient strings."""
    result = ShoppingListGenerator.parse_ingredient("2 cups flour")
    assert result['quantity'] == '2 cups'
    assert result['ingredient_name'] == 'flour'
    
    result = ShoppingListGenerator.parse_ingredient("1 large onion")
    assert result['quantity'] == '1 large'
    assert result['ingredient_name'] == 'onion'
    
    result = ShoppingListGenerator.parse_ingredient("salt")
    assert result['quantity'] is None
    assert result['ingredient_name'] == 'salt'


def test_get_user_shopping_lists(db, test_user):
    """Test retrieving user's shopping lists."""
    # Create shopping lists
    list1 = ShoppingList(user_id=test_user.id, name="List 1")
    list2 = ShoppingList(user_id=test_user.id, name="List 2")
    db.add_all([list1, list2])
    db.commit()
    
    lists = ShoppingListGenerator.get_user_shopping_lists(db, test_user.id)
    
    assert len(lists) == 2
    assert all(lst.user_id == test_user.id for lst in lists)


def test_delete_shopping_list(db, test_user):
    """Test deleting a shopping list."""
    shopping_list = ShoppingList(user_id=test_user.id, name="To Delete")
    db.add(shopping_list)
    db.commit()
    list_id = shopping_list.id
    
    result = ShoppingListGenerator.delete_shopping_list(db, list_id, test_user.id)
    
    assert result is True
    assert db.query(ShoppingList).filter(ShoppingList.id == list_id).first() is None


def test_update_item_status(db, test_user):
    """Test updating shopping list item checked status."""
    shopping_list = ShoppingList(user_id=test_user.id, name="Test List")
    db.add(shopping_list)
    db.flush()
    
    item = ShoppingListItem(
        shopping_list_id=shopping_list.id,
        ingredient_name="milk",
        category="dairy",
        is_checked=False
    )
    db.add(item)
    db.commit()
    
    updated_item = ShoppingListGenerator.update_item_status(
        db, item.id, True, test_user.id
    )
    
    assert updated_item is not None
    assert updated_item.is_checked is True


def test_add_custom_item(db, test_user):
    """Test adding a custom item to shopping list."""
    shopping_list = ShoppingList(user_id=test_user.id, name="Test List")
    db.add(shopping_list)
    db.commit()
    
    item_data = CustomItemCreate(
        ingredient_name="paper towels",
        quantity="1 pack",
        category="other"
    )
    
    item = ShoppingListGenerator.add_custom_item(
        db, shopping_list.id, item_data, test_user.id
    )
    
    assert item is not None
    assert item.ingredient_name == "paper towels"
    assert item.is_custom is True
    assert item.category == "other"


def test_delete_item(db, test_user):
    """Test deleting a shopping list item."""
    shopping_list = ShoppingList(user_id=test_user.id, name="Test List")
    db.add(shopping_list)
    db.flush()
    
    item = ShoppingListItem(
        shopping_list_id=shopping_list.id,
        ingredient_name="milk",
        category="dairy"
    )
    db.add(item)
    db.commit()
    item_id = item.id
    
    result = ShoppingListGenerator.delete_item(db, item_id, test_user.id)
    
    assert result is True
    assert db.query(ShoppingListItem).filter(ShoppingListItem.id == item_id).first() is None


def test_generate_share_token(db, test_user):
    """Test generating a share token for shopping list."""
    shopping_list = ShoppingList(user_id=test_user.id, name="Shared List")
    db.add(shopping_list)
    db.commit()
    
    token = ShoppingListGenerator.generate_share_token(
        db, shopping_list.id, test_user.id
    )
    
    assert token is not None
    assert len(token) > 0
    
    # Verify token was saved
    db.refresh(shopping_list)
    assert shopping_list.share_token == token


def test_get_shared_list(db, test_user):
    """Test retrieving a shopping list by share token."""
    shopping_list = ShoppingList(
        user_id=test_user.id,
        name="Shared List",
        share_token="test_token_123"
    )
    db.add(shopping_list)
    db.commit()
    
    retrieved = ShoppingListGenerator.get_shared_list(db, "test_token_123")
    
    assert retrieved is not None
    assert retrieved.id == shopping_list.id
    assert retrieved.name == "Shared List"


def test_update_shared_item_status(db, test_user):
    """Test updating item status via share token."""
    shopping_list = ShoppingList(
        user_id=test_user.id,
        name="Shared List",
        share_token="test_token_456"
    )
    db.add(shopping_list)
    db.flush()
    
    item = ShoppingListItem(
        shopping_list_id=shopping_list.id,
        ingredient_name="milk",
        category="dairy",
        is_checked=False
    )
    db.add(item)
    db.commit()
    
    updated_item = ShoppingListGenerator.update_shared_item_status(
        db, "test_token_456", item.id, True
    )
    
    assert updated_item is not None
    assert updated_item.is_checked is True


def test_sum_quantities():
    """Test summing quantities with same units."""
    result = ShoppingListGenerator.sum_quantities("2 cups", "1 cups")
    assert result == "3.0 cups"
    
    result = ShoppingListGenerator.sum_quantities("1.5 tsp", "0.5 tsp")
    assert result == "2.0 tsp"
    
    # Different units should return None
    result = ShoppingListGenerator.sum_quantities("2 cups", "1 tbsp")
    assert result is None


def test_parse_number():
    """Test parsing various number formats."""
    assert ShoppingListGenerator.parse_number("2") == 2.0
    assert ShoppingListGenerator.parse_number("1.5") == 1.5
    assert ShoppingListGenerator.parse_number("1/2") == 0.5
    assert ShoppingListGenerator.parse_number("2 1/2") == 2.5
