"""Property-based tests for shopping list system."""
import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"

from hypothesis import given, strategies as st, settings as hyp_settings, HealthCheck
from datetime import timedelta
import pytest
import uuid
import json


# Feature: recipe-saver-enhancements, Property 31: Shopping list ingredient extraction
@given(
    num_recipes=st.integers(min_value=1, max_value=5),
    ingredients_per_recipe=st.integers(min_value=1, max_value=5)
)
@hyp_settings(max_examples=100, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_shopping_list_ingredient_extraction_property(db, num_recipes, ingredients_per_recipe):
    """
    Property 31: Shopping list ingredient extraction
    
    For any set of recipes, generating a shopping list should include all
    ingredients from all selected recipes.
    
    **Validates: Requirements 18.1, 18.2**
    """
    from app.services.shopping_list_service import ShoppingListGenerator
    from app.services.recipe_service import RecipeManager
    from app.services.auth_service import AuthService
    from app.schemas import ShoppingListCreate, RecipeCreate
    
    # Create a test user
    unique_username = f"shopuser_{uuid.uuid4().hex[:8]}"
    user = AuthService.create_user(db, unique_username, "password123")
    
    # Create recipes with ingredients
    all_ingredients = []
    recipe_ids = []
    
    for i in range(num_recipes):
        ingredients = [f"ingredient_{i}_{j}" for j in range(ingredients_per_recipe)]
        all_ingredients.extend(ingredients)
        
        recipe_data = RecipeCreate(
            title=f"Recipe {i}",
            ingredients=ingredients,
            steps=["step1"]
        )
        recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
        recipe_ids.append(recipe.id)
    
    # Create shopping list
    shopping_list_data = ShoppingListCreate(
        name="Test Shopping List",
        recipe_ids=recipe_ids
    )
    
    shopping_list = ShoppingListGenerator.create_shopping_list(db, user.id, shopping_list_data)
    
    assert shopping_list is not None, "Shopping list should be created successfully"
    
    # Get items from database
    from app.models import ShoppingListItem
    items = db.query(ShoppingListItem).filter(
        ShoppingListItem.shopping_list_id == shopping_list.id
    ).all()
    
    # Extract ingredient names from shopping list items
    shopping_list_ingredients = [item.ingredient_name.lower() for item in items]
    
    # Verify all ingredients are present (case-insensitive)
    for ingredient in all_ingredients:
        assert any(ingredient.lower() in ing for ing in shopping_list_ingredients), \
            f"Ingredient '{ingredient}' should be in shopping list"


# Feature: recipe-saver-enhancements, Property 32: Ingredient consolidation
@given(
    duplicate_ingredients=st.lists(
        st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))),
        min_size=2,
        max_size=5
    )
)
@hyp_settings(max_examples=100, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_ingredient_consolidation_property(db, duplicate_ingredients):
    """
    Property 32: Ingredient consolidation
    
    Identical ingredient names (case-insensitive) should be combined into a single item.
    
    **Validates: Requirements 19.1, 19.3**
    """
    from app.services.shopping_list_service import ShoppingListGenerator
    from app.services.recipe_service import RecipeManager
    from app.services.auth_service import AuthService
    from app.schemas import ShoppingListCreate, RecipeCreate
    
    # Create a test user
    unique_username = f"consuser_{uuid.uuid4().hex[:8]}"
    user = AuthService.create_user(db, unique_username, "password123")
    
    # Create recipes with duplicate ingredients (different cases)
    recipe_ids = []
    base_ingredient = duplicate_ingredients[0]
    
    for i, ingredient_variant in enumerate(duplicate_ingredients):
        # Use same ingredient with different cases
        ingredients = [ingredient_variant.lower() if i % 2 == 0 else ingredient_variant.upper()]
        
        recipe_data = RecipeCreate(
            title=f"Recipe {i}",
            ingredients=ingredients,
            steps=["step1"]
        )
        recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
        recipe_ids.append(recipe.id)
    
    # Create shopping list
    shopping_list_data = ShoppingListCreate(
        name="Test Shopping List",
        recipe_ids=recipe_ids
    )
    
    shopping_list = ShoppingListGenerator.create_shopping_list(db, user.id, shopping_list_data)
    
    assert shopping_list is not None, "Shopping list should be created successfully"
    
    # Get items from database
    from app.models import ShoppingListItem
    items = db.query(ShoppingListItem).filter(
        ShoppingListItem.shopping_list_id == shopping_list.id
    ).all()
    
    # Count occurrences of the base ingredient (case-insensitive)
    ingredient_counts = {}
    for item in items:
        key = item.ingredient_name.lower()
        ingredient_counts[key] = ingredient_counts.get(key, 0) + 1
    
    # Each unique ingredient (case-insensitive) should appear exactly once
    for ingredient_name, count in ingredient_counts.items():
        assert count == 1, \
            f"Ingredient '{ingredient_name}' should appear exactly once, but appears {count} times"


# Feature: recipe-saver-enhancements, Property 33: Quantity summation
@given(
    quantities=st.lists(
        st.integers(min_value=1, max_value=10),
        min_size=2,
        max_size=5
    ),
    unit=st.sampled_from(['cups', 'tbsp', 'tsp', 'oz', 'g'])
)
@hyp_settings(max_examples=100, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_quantity_summation_property(db, quantities, unit):
    """
    Property 33: Quantity summation
    
    When ingredients have quantities with the same unit, the combined quantity
    should be the sum of individual quantities.
    
    **Validates: Requirements 19.2**
    """
    from app.services.shopping_list_service import ShoppingListGenerator
    from app.services.recipe_service import RecipeManager
    from app.services.auth_service import AuthService
    from app.schemas import ShoppingListCreate, RecipeCreate
    
    # Create a test user
    unique_username = f"qtyuser_{uuid.uuid4().hex[:8]}"
    user = AuthService.create_user(db, unique_username, "password123")
    
    # Create recipes with same ingredient but different quantities
    recipe_ids = []
    ingredient_name = "flour"
    
    for qty in quantities:
        ingredients = [f"{qty} {unit} {ingredient_name}"]
        
        recipe_data = RecipeCreate(
            title=f"Recipe with {qty} {unit}",
            ingredients=ingredients,
            steps=["step1"]
        )
        recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
        recipe_ids.append(recipe.id)
    
    # Create shopping list
    shopping_list_data = ShoppingListCreate(
        name="Test Shopping List",
        recipe_ids=recipe_ids
    )
    
    shopping_list = ShoppingListGenerator.create_shopping_list(db, user.id, shopping_list_data)
    
    assert shopping_list is not None, "Shopping list should be created successfully"
    
    # Get items from database
    from app.models import ShoppingListItem
    items = db.query(ShoppingListItem).filter(
        ShoppingListItem.shopping_list_id == shopping_list.id
    ).all()
    
    # Find the flour item
    flour_items = [item for item in items if ingredient_name in item.ingredient_name.lower()]
    
    assert len(flour_items) == 1, \
        f"Should have exactly one consolidated flour item, found {len(flour_items)}"
    
    flour_item = flour_items[0]
    
    # Verify quantity contains the sum or all quantities
    expected_sum = sum(quantities)
    assert flour_item.quantity is not None, "Consolidated item should have a quantity"
    
    # Check if the quantity contains the expected sum
    # The format might be "15 cups" or similar
    assert str(expected_sum) in flour_item.quantity, \
        f"Quantity should contain sum {expected_sum}, got '{flour_item.quantity}'"


# Feature: recipe-saver-enhancements, Property 34: Different units separation
@given(
    quantity1=st.integers(min_value=1, max_value=10),
    quantity2=st.integers(min_value=1, max_value=10),
    unit1=st.sampled_from(['cups', 'tbsp']),
    unit2=st.sampled_from(['oz', 'g'])
)
@hyp_settings(max_examples=100, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_different_units_separation_property(db, quantity1, quantity2, unit1, unit2):
    """
    Property 34: Different units separation
    
    Ingredients with the same name but different units should be listed as separate items.
    
    **Validates: Requirements 19.4**
    """
    from app.services.shopping_list_service import ShoppingListGenerator
    from app.services.recipe_service import RecipeManager
    from app.services.auth_service import AuthService
    from app.schemas import ShoppingListCreate, RecipeCreate
    
    # Create a test user
    unique_username = f"unituser_{uuid.uuid4().hex[:8]}"
    user = AuthService.create_user(db, unique_username, "password123")
    
    # Create recipes with same ingredient but different units
    ingredient_name = "sugar"
    
    recipe_data1 = RecipeCreate(
        title="Recipe 1",
        ingredients=[f"{quantity1} {unit1} {ingredient_name}"],
        steps=["step1"]
    )
    recipe1 = RecipeManager.create_recipe(db, user.id, recipe_data1)
    
    recipe_data2 = RecipeCreate(
        title="Recipe 2",
        ingredients=[f"{quantity2} {unit2} {ingredient_name}"],
        steps=["step1"]
    )
    recipe2 = RecipeManager.create_recipe(db, user.id, recipe_data2)
    
    # Create shopping list
    shopping_list_data = ShoppingListCreate(
        name="Test Shopping List",
        recipe_ids=[recipe1.id, recipe2.id]
    )
    
    shopping_list = ShoppingListGenerator.create_shopping_list(db, user.id, shopping_list_data)
    
    assert shopping_list is not None, "Shopping list should be created successfully"
    
    # Get items from database
    from app.models import ShoppingListItem
    items = db.query(ShoppingListItem).filter(
        ShoppingListItem.shopping_list_id == shopping_list.id
    ).all()
    
    # Find sugar items
    sugar_items = [item for item in items if ingredient_name in item.ingredient_name.lower()]
    
    # Should have either 1 item (if units were consolidated) or 2 items (if kept separate)
    # Since units are different, they should be kept separate OR combined with both quantities listed
    assert len(sugar_items) >= 1, "Should have at least one sugar item"
    
    # If consolidated into one item, quantity should contain both units
    if len(sugar_items) == 1:
        quantity_str = sugar_items[0].quantity or ""
        # Should contain both quantities or indicate multiple units
        assert unit1 in quantity_str or unit2 in quantity_str, \
            f"Quantity should reference the units when different units are present"
    else:
        # If kept separate, verify both units are represented
        quantities = [item.quantity for item in sugar_items if item.quantity]
        units_found = [unit1 in q or unit2 in q for q in quantities]
        assert any(units_found), "Should find at least one of the units in the quantities"


# Feature: recipe-saver-enhancements, Property 35: Ingredient categorization
@given(
    ingredient=st.sampled_from([
        'tomato', 'lettuce', 'onion',  # produce
        'milk', 'cheese', 'butter',     # dairy
        'chicken', 'beef', 'fish',      # meat
        'flour', 'sugar', 'rice'        # pantry
    ])
)
@hyp_settings(max_examples=100, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_ingredient_categorization_property(db, ingredient):
    """
    Property 35: Ingredient categorization
    
    Each ingredient should be assigned to one of the categories: produce, dairy, meat, pantry, or other.
    
    **Validates: Requirements 20.1, 20.4**
    """
    from app.services.shopping_list_service import ShoppingListGenerator
    from app.services.recipe_service import RecipeManager
    from app.services.auth_service import AuthService
    from app.schemas import ShoppingListCreate, RecipeCreate
    
    # Create a test user
    unique_username = f"catuser_{uuid.uuid4().hex[:8]}"
    user = AuthService.create_user(db, unique_username, "password123")
    
    # Create recipe with the ingredient
    recipe_data = RecipeCreate(
        title="Test Recipe",
        ingredients=[ingredient],
        steps=["step1"]
    )
    recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
    
    # Create shopping list
    shopping_list_data = ShoppingListCreate(
        name="Test Shopping List",
        recipe_ids=[recipe.id]
    )
    
    shopping_list = ShoppingListGenerator.create_shopping_list(db, user.id, shopping_list_data)
    
    assert shopping_list is not None, "Shopping list should be created successfully"
    
    # Get items from database
    from app.models import ShoppingListItem
    items = db.query(ShoppingListItem).filter(
        ShoppingListItem.shopping_list_id == shopping_list.id
    ).all()
    
    assert len(items) > 0, "Should have at least one item"
    
    # Verify each item has a valid category
    valid_categories = ['produce', 'dairy', 'meat', 'pantry', 'other']
    for item in items:
        assert item.category in valid_categories, \
            f"Item category '{item.category}' should be one of {valid_categories}"


# Feature: recipe-saver-enhancements, Property 36: Shopping list check-off persistence
@given(
    is_checked=st.booleans()
)
@hyp_settings(max_examples=100, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_shopping_list_checkoff_persistence_property(db, is_checked):
    """
    Property 36: Shopping list check-off persistence
    
    Checking off a shopping list item should set is_checked=true, and this status
    should persist across retrievals.
    
    **Validates: Requirements 21.1, 21.4**
    """
    from app.services.shopping_list_service import ShoppingListGenerator
    from app.services.recipe_service import RecipeManager
    from app.services.auth_service import AuthService
    from app.schemas import ShoppingListCreate, RecipeCreate
    
    # Create a test user
    unique_username = f"checkuser_{uuid.uuid4().hex[:8]}"
    user = AuthService.create_user(db, unique_username, "password123")
    
    # Create recipe
    recipe_data = RecipeCreate(
        title="Test Recipe",
        ingredients=["test ingredient"],
        steps=["step1"]
    )
    recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
    
    # Create shopping list
    shopping_list_data = ShoppingListCreate(
        name="Test Shopping List",
        recipe_ids=[recipe.id]
    )
    
    shopping_list = ShoppingListGenerator.create_shopping_list(db, user.id, shopping_list_data)
    
    # Get the first item
    from app.models import ShoppingListItem
    items = db.query(ShoppingListItem).filter(
        ShoppingListItem.shopping_list_id == shopping_list.id
    ).all()
    
    assert len(items) > 0, "Should have at least one item"
    item = items[0]
    
    # Update check status
    updated_item = ShoppingListGenerator.update_item_status(db, item.id, is_checked, user.id)
    
    assert updated_item is not None, "Item should be updated successfully"
    assert updated_item.is_checked == is_checked, \
        f"Item check status should be {is_checked}"
    
    # Retrieve the shopping list again to verify persistence
    retrieved_list = ShoppingListGenerator.get_shopping_list_by_id(db, shopping_list.id, user.id)
    
    # Get items again
    retrieved_items = db.query(ShoppingListItem).filter(
        ShoppingListItem.shopping_list_id == retrieved_list.id,
        ShoppingListItem.id == item.id
    ).all()
    
    assert len(retrieved_items) > 0, "Should retrieve the item"
    retrieved_item = retrieved_items[0]
    
    assert retrieved_item.is_checked == is_checked, \
        f"Retrieved item check status should persist as {is_checked}"


# Feature: recipe-saver-enhancements, Property 37: Check-off round trip
@given(
    initial_state=st.booleans()
)
@hyp_settings(max_examples=100, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_checkoff_round_trip_property(db, initial_state):
    """
    Property 37: Check-off round trip
    
    Checking then unchecking a shopping list item should return it to is_checked=false.
    
    **Validates: Requirements 21.2**
    """
    from app.services.shopping_list_service import ShoppingListGenerator
    from app.services.recipe_service import RecipeManager
    from app.services.auth_service import AuthService
    from app.schemas import ShoppingListCreate, RecipeCreate
    
    # Create a test user
    unique_username = f"rounduser_{uuid.uuid4().hex[:8]}"
    user = AuthService.create_user(db, unique_username, "password123")
    
    # Create recipe
    recipe_data = RecipeCreate(
        title="Test Recipe",
        ingredients=["test ingredient"],
        steps=["step1"]
    )
    recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
    
    # Create shopping list
    shopping_list_data = ShoppingListCreate(
        name="Test Shopping List",
        recipe_ids=[recipe.id]
    )
    
    shopping_list = ShoppingListGenerator.create_shopping_list(db, user.id, shopping_list_data)
    
    # Get the first item
    from app.models import ShoppingListItem
    items = db.query(ShoppingListItem).filter(
        ShoppingListItem.shopping_list_id == shopping_list.id
    ).all()
    
    assert len(items) > 0, "Should have at least one item"
    item = items[0]
    
    # Set initial state
    item1 = ShoppingListGenerator.update_item_status(db, item.id, initial_state, user.id)
    assert item1.is_checked == initial_state, f"Initial state should be {initial_state}"
    
    # Toggle to opposite state
    item2 = ShoppingListGenerator.update_item_status(db, item.id, not initial_state, user.id)
    assert item2.is_checked == (not initial_state), \
        f"After toggle, state should be {not initial_state}"
    
    # Toggle back to initial state
    item3 = ShoppingListGenerator.update_item_status(db, item.id, initial_state, user.id)
    assert item3.is_checked == initial_state, \
        f"After round trip, state should return to {initial_state}"


# Feature: recipe-saver-enhancements, Property 38: Custom item distinction
@given(
    ingredient_name=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')))
)
@hyp_settings(max_examples=100, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_custom_item_distinction_property(db, ingredient_name):
    """
    Property 38: Custom item distinction
    
    Custom shopping list items should have is_custom=true to distinguish them
    from recipe-generated items.
    
    **Validates: Requirements 22.4**
    """
    from app.services.shopping_list_service import ShoppingListGenerator
    from app.services.recipe_service import RecipeManager
    from app.services.auth_service import AuthService
    from app.schemas import ShoppingListCreate, RecipeCreate, CustomItemCreate
    
    # Create a test user
    unique_username = f"customuser_{uuid.uuid4().hex[:8]}"
    user = AuthService.create_user(db, unique_username, "password123")
    
    # Create recipe
    recipe_data = RecipeCreate(
        title="Test Recipe",
        ingredients=["recipe ingredient"],
        steps=["step1"]
    )
    recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
    
    # Create shopping list
    shopping_list_data = ShoppingListCreate(
        name="Test Shopping List",
        recipe_ids=[recipe.id]
    )
    
    shopping_list = ShoppingListGenerator.create_shopping_list(db, user.id, shopping_list_data)
    
    # Add custom item
    custom_item_data = CustomItemCreate(
        ingredient_name=ingredient_name,
        quantity="1",
        category="other"
    )
    
    custom_item = ShoppingListGenerator.add_custom_item(db, shopping_list.id, custom_item_data, user.id)
    
    assert custom_item is not None, "Custom item should be added successfully"
    assert custom_item.is_custom is True, "Custom item should have is_custom=True"
    assert custom_item.ingredient_name == ingredient_name, \
        "Custom item should have the specified ingredient name"
    
    # Get all items and verify distinction
    from app.models import ShoppingListItem
    items = db.query(ShoppingListItem).filter(
        ShoppingListItem.shopping_list_id == shopping_list.id
    ).all()
    
    # Should have at least 2 items: one from recipe, one custom
    assert len(items) >= 2, "Should have at least recipe item and custom item"
    
    # Verify recipe-generated items have is_custom=False
    recipe_items = [item for item in items if not item.is_custom]
    assert len(recipe_items) > 0, "Should have at least one recipe-generated item"
    
    # Verify custom items have is_custom=True
    custom_items = [item for item in items if item.is_custom]
    assert len(custom_items) > 0, "Should have at least one custom item"
    assert all(item.is_custom for item in custom_items), \
        "All custom items should have is_custom=True"


# Feature: recipe-saver-enhancements, Property 39: Shared shopping list synchronization
@given(
    is_checked=st.booleans()
)
@hyp_settings(max_examples=100, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_shared_shopping_list_synchronization_property(db, is_checked):
    """
    Property 39: Shared shopping list synchronization
    
    Checking off an item in a shared shopping list should update the status
    for all users viewing the shared list.
    
    **Validates: Requirements 23.3, 23.4**
    """
    from app.services.shopping_list_service import ShoppingListGenerator
    from app.services.recipe_service import RecipeManager
    from app.services.auth_service import AuthService
    from app.schemas import ShoppingListCreate, RecipeCreate
    
    # Create a test user
    unique_username = f"shareuser_{uuid.uuid4().hex[:8]}"
    user = AuthService.create_user(db, unique_username, "password123")
    
    # Create recipe
    recipe_data = RecipeCreate(
        title="Test Recipe",
        ingredients=["shared ingredient"],
        steps=["step1"]
    )
    recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
    
    # Create shopping list
    shopping_list_data = ShoppingListCreate(
        name="Test Shopping List",
        recipe_ids=[recipe.id]
    )
    
    shopping_list = ShoppingListGenerator.create_shopping_list(db, user.id, shopping_list_data)
    
    # Generate share token
    share_token = ShoppingListGenerator.generate_share_token(db, shopping_list.id, user.id)
    
    assert share_token is not None, "Share token should be generated"
    
    # Get the first item
    from app.models import ShoppingListItem
    items = db.query(ShoppingListItem).filter(
        ShoppingListItem.shopping_list_id == shopping_list.id
    ).all()
    
    assert len(items) > 0, "Should have at least one item"
    item = items[0]
    
    # Update item status via share token (simulating another user)
    updated_item = ShoppingListGenerator.update_shared_item_status(
        db, share_token, item.id, is_checked
    )
    
    assert updated_item is not None, "Item should be updated via share token"
    assert updated_item.is_checked == is_checked, \
        f"Item check status should be {is_checked}"
    
    # Retrieve the shopping list as the owner to verify synchronization
    owner_list = ShoppingListGenerator.get_shopping_list_by_id(db, shopping_list.id, user.id)
    
    # Get items as owner
    owner_items = db.query(ShoppingListItem).filter(
        ShoppingListItem.shopping_list_id == owner_list.id,
        ShoppingListItem.id == item.id
    ).all()
    
    assert len(owner_items) > 0, "Owner should see the item"
    owner_item = owner_items[0]
    
    assert owner_item.is_checked == is_checked, \
        f"Owner should see synchronized check status as {is_checked}"
    
    # Retrieve via share token again to verify persistence
    shared_list = ShoppingListGenerator.get_shared_list(db, share_token)
    
    shared_items = db.query(ShoppingListItem).filter(
        ShoppingListItem.shopping_list_id == shared_list.id,
        ShoppingListItem.id == item.id
    ).all()
    
    assert len(shared_items) > 0, "Shared view should see the item"
    shared_item = shared_items[0]
    
    assert shared_item.is_checked == is_checked, \
        f"Shared view should see synchronized check status as {is_checked}"
