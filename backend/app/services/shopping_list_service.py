from typing import List, Optional, Dict, Any
from datetime import date, datetime
import secrets
import re
from bson import ObjectId
from app.repositories.shopping_list_repository import ShoppingListRepository
from app.repositories.recipe_repository import RecipeRepository
from app.repositories.meal_plan_repository import MealPlanRepository
from app.schemas import ShoppingListCreate, CustomItemCreate


class ShoppingListGenerator:
    """Service for managing shopping lists with embedded items."""
    
    # Category keywords for ingredient categorization
    CATEGORY_KEYWORDS = {
        'produce': [
            'lettuce', 'tomato', 'onion', 'garlic', 'potato', 'carrot', 'celery',
            'pepper', 'cucumber', 'spinach', 'kale', 'broccoli', 'cauliflower',
            'zucchini', 'squash', 'mushroom', 'avocado', 'apple', 'banana',
            'orange', 'lemon', 'lime', 'berry', 'strawberry', 'blueberry',
            'grape', 'melon', 'peach', 'pear', 'plum', 'cherry', 'pineapple',
            'mango', 'cilantro', 'parsley', 'basil', 'thyme', 'rosemary',
            'mint', 'dill', 'oregano', 'sage', 'arugula', 'cabbage', 'corn',
            'bean', 'pea', 'asparagus', 'eggplant', 'radish', 'beet', 'turnip'
        ],
        'dairy': [
            'milk', 'cream', 'butter', 'cheese', 'yogurt', 'sour cream',
            'cottage cheese', 'ricotta', 'mozzarella', 'cheddar', 'parmesan',
            'feta', 'goat cheese', 'cream cheese', 'whipped cream', 'half and half',
            'buttermilk', 'ice cream', 'custard', 'pudding'
        ],
        'meat': [
            'chicken', 'beef', 'pork', 'turkey', 'lamb', 'duck', 'bacon',
            'sausage', 'ham', 'steak', 'ground beef', 'ground turkey',
            'ground pork', 'ribs', 'chop', 'breast', 'thigh', 'wing',
            'fish', 'salmon', 'tuna', 'cod', 'tilapia', 'shrimp', 'crab',
            'lobster', 'scallop', 'clam', 'mussel', 'oyster', 'anchovy',
            'sardine', 'trout', 'halibut', 'mahi mahi', 'swordfish'
        ],
        'pantry': [
            'flour', 'sugar', 'salt', 'pepper', 'oil', 'vinegar', 'rice',
            'pasta', 'bread', 'cereal', 'oats', 'quinoa', 'couscous',
            'noodle', 'spaghetti', 'macaroni', 'penne', 'fettuccine',
            'sauce', 'ketchup', 'mustard', 'mayonnaise', 'soy sauce',
            'worcestershire', 'hot sauce', 'salsa', 'honey', 'syrup',
            'jam', 'jelly', 'peanut butter', 'almond butter', 'nutella',
            'chocolate', 'cocoa', 'vanilla', 'extract', 'baking powder',
            'baking soda', 'yeast', 'cornstarch', 'gelatin', 'broth',
            'stock', 'bouillon', 'soup', 'can', 'canned', 'dried',
            'spice', 'seasoning', 'cumin', 'paprika', 'chili powder',
            'cinnamon', 'nutmeg', 'ginger', 'turmeric', 'curry', 'cayenne'
        ]
    }
    
    def __init__(
        self,
        shopping_list_repository: ShoppingListRepository,
        recipe_repository: RecipeRepository,
        meal_plan_repository: MealPlanRepository
    ):
        """
        Initialize shopping list generator with repositories.
        
        Args:
            shopping_list_repository: ShoppingListRepository instance
            recipe_repository: RecipeRepository instance
            meal_plan_repository: MealPlanRepository instance
        """
        self.shopping_list_repository = shopping_list_repository
        self.recipe_repository = recipe_repository
        self.meal_plan_repository = meal_plan_repository
    
    async def create_shopping_list(
        self,
        user_id: str,
        shopping_list_data: ShoppingListCreate
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new shopping list from recipes or meal plan date range.
        Extracts ingredients, consolidates duplicates, and categorizes items.
        
        Args:
            user_id: User's ObjectId as string
            shopping_list_data: Shopping list creation data
            
        Returns:
            Shopping list document if successful, None if validation fails
        """
        recipe_ids = []
        
        # Get recipe IDs from direct list or meal plan date range
        if shopping_list_data.recipe_ids:
            recipe_ids = shopping_list_data.recipe_ids
        elif shopping_list_data.meal_plan_start_date and shopping_list_data.meal_plan_end_date:
            # Extract recipes from meal plan date range
            try:
                start_date = datetime.strptime(shopping_list_data.meal_plan_start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(shopping_list_data.meal_plan_end_date, '%Y-%m-%d').date()
            except ValueError:
                return None
            
            recipe_ids = await self.extract_ingredients_from_meal_plan(
                user_id, start_date, end_date
            )
        
        if not recipe_ids:
            return None
        
        # Extract and consolidate ingredients
        ingredients = await self.extract_ingredients_from_recipes(recipe_ids, user_id)
        consolidated_items = ShoppingListGenerator.consolidate_ingredients(ingredients)
        
        # Create shopping list items (embedded)
        items = []
        for item_data in consolidated_items:
            category = ShoppingListGenerator.categorize_ingredient(item_data['ingredient_name'])
            
            item = {
                "ingredient_name": item_data['ingredient_name'],
                "quantity": item_data.get('quantity'),
                "category": category,
                "is_checked": False,
                "is_custom": False,
                "recipe_id": ObjectId(item_data['recipe_id']) if item_data.get('recipe_id') else None
            }
            items.append(item)
        
        # Create shopping list with embedded items
        shopping_list_doc = {
            "user_id": ObjectId(user_id),
            "name": shopping_list_data.name,
            "share_token": None,
            "items": items,
            "created_at": datetime.utcnow()
        }
        
        list_id = await self.shopping_list_repository.create(shopping_list_doc)
        return await self.shopping_list_repository.find_by_id(list_id)
    
    async def extract_ingredients_from_meal_plan(
        self,
        user_id: str,
        start_date: date,
        end_date: date
    ) -> List[str]:
        """
        Extract recipe IDs from meal plans within a date range.
        
        Args:
            user_id: User's ObjectId as string
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            List of unique recipe ID strings
        """
        meal_plans = await self.meal_plan_repository.find_by_user_and_date_range(
            user_id, start_date, end_date
        )
        
        # Get unique recipe IDs
        recipe_ids = list(set([str(mp["recipe_id"]) for mp in meal_plans]))
        return recipe_ids
    
    async def extract_ingredients_from_recipes(
        self,
        recipe_ids: List[str],
        user_id: str
    ) -> List[dict]:
        """
        Extract ingredients from multiple recipes.
        
        Args:
            recipe_ids: List of recipe ObjectId strings
            user_id: User's ObjectId as string
            
        Returns:
            List of ingredient dictionaries with name, quantity, and recipe_id
        """
        all_ingredients = []
        
        for recipe_id in recipe_ids:
            # Verify recipe exists and belongs to user
            recipe = await self.recipe_repository.find_by_id(recipe_id)
            
            if not recipe or str(recipe["user_id"]) != user_id:
                continue
            
            # Get ingredients array (already parsed in MongoDB)
            ingredients = recipe.get("ingredients", [])
            
            # Extract each ingredient
            for ingredient in ingredients:
                # Parse ingredient string to extract quantity and name
                parsed = ShoppingListGenerator.parse_ingredient(ingredient)
                parsed['recipe_id'] = recipe_id
                all_ingredients.append(parsed)
        
        return all_ingredients
    
    @staticmethod
    def parse_ingredient(ingredient_str: str) -> dict:
        """
        Parse an ingredient string to extract quantity and name.
        Examples:
          "2 cups flour" -> {"quantity": "2 cups", "ingredient_name": "flour"}
          "1 large onion" -> {"quantity": "1 large", "ingredient_name": "onion"}
          "salt" -> {"quantity": None, "ingredient_name": "salt"}
        """
        # Pattern to match quantity at the start (numbers, fractions, units)
        pattern = r'^([\d\s\/\.\-]+(?:cup|cups|tbsp|tsp|oz|lb|lbs|g|kg|ml|l|large|medium|small|whole|clove|cloves|can|cans|package|packages|bunch|bunches)?)\s+(.+)$'
        
        match = re.match(pattern, ingredient_str.strip(), re.IGNORECASE)
        
        if match:
            return {
                'quantity': match.group(1).strip(),
                'ingredient_name': match.group(2).strip()
            }
        else:
            return {
                'quantity': None,
                'ingredient_name': ingredient_str.strip()
            }
    
    @staticmethod
    def consolidate_ingredients(ingredients: List[dict]) -> List[dict]:
        """
        Consolidate duplicate ingredients (case-insensitive).
        Sum quantities when units match, otherwise list separately.
        
        Args:
            ingredients: List of ingredient dictionaries
            
        Returns:
            List of consolidated ingredient dictionaries
        """
        consolidated = {}
        
        for ingredient in ingredients:
            name = ingredient['ingredient_name'].lower()
            quantity = ingredient.get('quantity')
            recipe_id = ingredient.get('recipe_id')
            
            if name not in consolidated:
                consolidated[name] = {
                    'ingredient_name': ingredient['ingredient_name'],
                    'quantity': quantity,
                    'recipe_id': recipe_id
                }
            else:
                # Try to sum quantities if both exist and have compatible units
                existing_qty = consolidated[name]['quantity']
                
                if existing_qty and quantity:
                    # Try to sum numeric quantities
                    summed = ShoppingListGenerator.sum_quantities(existing_qty, quantity)
                    if summed:
                        consolidated[name]['quantity'] = summed
                    else:
                        # Can't sum, append to quantity
                        consolidated[name]['quantity'] = f"{existing_qty}, {quantity}"
                elif quantity:
                    # Only new quantity exists
                    consolidated[name]['quantity'] = quantity
        
        return list(consolidated.values())
    
    @staticmethod
    def sum_quantities(qty1: str, qty2: str) -> Optional[str]:
        """
        Attempt to sum two quantity strings if they have the same unit.
        
        Args:
            qty1: First quantity string
            qty2: Second quantity string
            
        Returns:
            Summed quantity string or None if incompatible
        """
        # Extract number and unit from each quantity
        pattern = r'^([\d\.\s\/]+)\s*([a-zA-Z]+)?$'
        
        match1 = re.match(pattern, qty1.strip())
        match2 = re.match(pattern, qty2.strip())
        
        if not match1 or not match2:
            return None
        
        num1_str = match1.group(1).strip()
        unit1 = match1.group(2) or ''
        
        num2_str = match2.group(1).strip()
        unit2 = match2.group(2) or ''
        
        # Units must match
        if unit1.lower() != unit2.lower():
            return None
        
        # Try to convert to float and sum
        try:
            # Handle fractions like "1/2"
            num1 = ShoppingListGenerator.parse_number(num1_str)
            num2 = ShoppingListGenerator.parse_number(num2_str)
            
            total = num1 + num2
            
            # Format result
            if unit1:
                return f"{total} {unit1}"
            else:
                return str(total)
        except (ValueError, ZeroDivisionError):
            return None
    
    @staticmethod
    def parse_number(num_str: str) -> float:
        """
        Parse a number string that may contain fractions.
        Examples: "2", "1.5", "1/2", "2 1/2"
        """
        num_str = num_str.strip()
        
        # Check for mixed fraction like "2 1/2"
        if ' ' in num_str:
            parts = num_str.split()
            whole = float(parts[0])
            frac = ShoppingListGenerator.parse_number(parts[1])
            return whole + frac
        
        # Check for fraction like "1/2"
        if '/' in num_str:
            parts = num_str.split('/')
            return float(parts[0]) / float(parts[1])
        
        # Regular number
        return float(num_str)
    
    @staticmethod
    def categorize_ingredient(ingredient_name: str) -> str:
        """
        Categorize an ingredient into produce, dairy, meat, pantry, or other.
        Uses keyword matching on ingredient name.
        """
        name_lower = ingredient_name.lower()
        
        for category, keywords in ShoppingListGenerator.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in name_lower:
                    return category
        
        return 'other'
    
    async def get_user_shopping_lists(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all shopping lists for a user.
        
        Args:
            user_id: User's ObjectId as string
            
        Returns:
            List of shopping list documents
        """
        return await self.shopping_list_repository.find_by_user(user_id)
    
    async def get_shopping_list_by_id(
        self,
        list_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a shopping list by ID with ownership validation.
        
        Args:
            list_id: Shopping list's ObjectId as string
            user_id: User's ObjectId as string
            
        Returns:
            Shopping list document if found and owned by user, None otherwise
        """
        shopping_list = await self.shopping_list_repository.find_by_id(list_id)
        
        if not shopping_list or str(shopping_list["user_id"]) != user_id:
            return None
        
        return shopping_list
    
    async def delete_shopping_list(self, list_id: str, user_id: str) -> bool:
        """
        Delete a shopping list with ownership validation.
        
        Args:
            list_id: Shopping list's ObjectId as string
            user_id: User's ObjectId as string
            
        Returns:
            True if deleted, False if not found
        """
        shopping_list = await self.get_shopping_list_by_id(list_id, user_id)
        
        if not shopping_list:
            return False
        
        return await self.shopping_list_repository.delete(list_id)
    
    async def update_item_status(
        self,
        list_id: str,
        item_index: int,
        is_checked: bool,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Update the checked status of a shopping list item.
        Validates user ownership of the shopping list.
        
        Args:
            list_id: Shopping list's ObjectId as string
            item_index: Index of the item in the items array
            is_checked: New checked status
            user_id: User's ObjectId as string
            
        Returns:
            Updated shopping list document if successful, None if not found or access denied
        """
        # Verify shopping list ownership
        shopping_list = await self.get_shopping_list_by_id(list_id, user_id)
        
        if not shopping_list:
            return None
        
        # Update the item
        await self.shopping_list_repository.update_item_checked(list_id, item_index, is_checked)
        return await self.shopping_list_repository.find_by_id(list_id)
    
    async def add_custom_item(
        self,
        list_id: str,
        item_data: CustomItemCreate,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Add a custom item to a shopping list.
        Validates user ownership of the shopping list.
        
        Args:
            list_id: Shopping list's ObjectId as string
            item_data: Custom item data
            user_id: User's ObjectId as string
            
        Returns:
            Updated shopping list document if successful, None if not found or access denied
        """
        # Verify shopping list ownership
        shopping_list = await self.get_shopping_list_by_id(list_id, user_id)
        
        if not shopping_list:
            return None
        
        # Determine category
        category = item_data.category if item_data.category else ShoppingListGenerator.categorize_ingredient(item_data.ingredient_name)
        
        # Create custom item
        item = {
            "ingredient_name": item_data.ingredient_name,
            "quantity": item_data.quantity,
            "category": category,
            "is_checked": False,
            "is_custom": True,
            "recipe_id": None
        }
        
        await self.shopping_list_repository.add_item(list_id, item)
        return await self.shopping_list_repository.find_by_id(list_id)
    
    async def delete_item(self, list_id: str, item_index: int, user_id: str) -> bool:
        """
        Delete a shopping list item by removing it from the items array.
        Validates user ownership through the shopping list.
        
        Args:
            list_id: Shopping list's ObjectId as string
            item_index: Index of the item in the items array
            user_id: User's ObjectId as string
            
        Returns:
            True if deleted, False if not found or access denied
        """
        # Verify shopping list ownership
        shopping_list = await self.get_shopping_list_by_id(list_id, user_id)
        
        if not shopping_list:
            return False
        
        # Remove item from array by pulling it
        items = shopping_list.get("items", [])
        if item_index < 0 or item_index >= len(items):
            return False
        
        # Remove the item at the index
        items.pop(item_index)
        
        # Update the shopping list with the new items array
        await self.shopping_list_repository.update(list_id, {"items": items})
        return True
    
    async def generate_share_token(self, list_id: str, user_id: str) -> Optional[str]:
        """
        Generate a unique share token for a shopping list.
        
        Args:
            list_id: Shopping list's ObjectId as string
            user_id: User's ObjectId as string
            
        Returns:
            Share token string if successful, None if shopping list not found
        """
        shopping_list = await self.get_shopping_list_by_id(list_id, user_id)
        
        if not shopping_list:
            return None
        
        # Generate a unique token
        share_token = secrets.token_urlsafe(32)
        
        # Ensure uniqueness (very unlikely to collide, but check anyway)
        while await self.shopping_list_repository.find_by_share_token(share_token):
            share_token = secrets.token_urlsafe(32)
        
        await self.shopping_list_repository.update(list_id, {"share_token": share_token})
        return share_token
    
    async def get_shared_list(self, share_token: str) -> Optional[Dict[str, Any]]:
        """
        Get a shopping list by its share token (public access, no auth required).
        
        Args:
            share_token: Share token to search for
            
        Returns:
            Shopping list document if found, None otherwise
        """
        return await self.shopping_list_repository.find_by_share_token(share_token)
    
    async def update_shared_item_status(
        self,
        share_token: str,
        item_index: int,
        is_checked: bool
    ) -> Optional[Dict[str, Any]]:
        """
        Update item status via share token (public access).
        Allows anyone with the share token to check/uncheck items.
        
        Args:
            share_token: Share token for the shopping list
            item_index: Index of the item in the items array
            is_checked: New checked status
            
        Returns:
            Updated shopping list document if successful, None if share token invalid or item not found
        """
        # Verify share token is valid
        shopping_list = await self.get_shared_list(share_token)
        
        if not shopping_list:
            return None
        
        # Update the item
        list_id = str(shopping_list["_id"])
        await self.shopping_list_repository.update_item_checked(list_id, item_index, is_checked)
        return await self.shopping_list_repository.find_by_id(list_id)
