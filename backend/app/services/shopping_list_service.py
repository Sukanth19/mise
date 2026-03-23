from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from datetime import date, datetime
import secrets
import re
import json
from app.models import ShoppingList, ShoppingListItem, Recipe, MealPlan
from app.schemas import ShoppingListCreate, CustomItemCreate


class ShoppingListGenerator:
    """Service for managing shopping lists and items."""
    
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
    
    @staticmethod
    def create_shopping_list(
        db: Session,
        user_id: int,
        shopping_list_data: ShoppingListCreate
    ) -> Optional[ShoppingList]:
        """
        Create a new shopping list from recipes or meal plan date range.
        Extracts ingredients, consolidates duplicates, and categorizes items.
        Returns None if validation fails.
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
            
            recipe_ids = ShoppingListGenerator.extract_ingredients_from_meal_plan(
                db, user_id, start_date, end_date
            )
        
        if not recipe_ids:
            return None
        
        # Create shopping list
        shopping_list = ShoppingList(
            user_id=user_id,
            name=shopping_list_data.name
        )
        db.add(shopping_list)
        db.flush()  # Get shopping list ID
        
        # Extract and consolidate ingredients
        ingredients = ShoppingListGenerator.extract_ingredients_from_recipes(db, recipe_ids, user_id)
        consolidated_items = ShoppingListGenerator.consolidate_ingredients(ingredients)
        
        # Create shopping list items
        for item_data in consolidated_items:
            category = ShoppingListGenerator.categorize_ingredient(item_data['ingredient_name'])
            
            item = ShoppingListItem(
                shopping_list_id=shopping_list.id,
                ingredient_name=item_data['ingredient_name'],
                quantity=item_data.get('quantity'),
                category=category,
                is_checked=False,
                is_custom=False,
                recipe_id=item_data.get('recipe_id')
            )
            db.add(item)
        
        db.commit()
        db.refresh(shopping_list)
        return shopping_list
    
    @staticmethod
    def extract_ingredients_from_meal_plan(
        db: Session,
        user_id: int,
        start_date: date,
        end_date: date
    ) -> List[int]:
        """
        Extract recipe IDs from meal plans within a date range.
        Returns list of unique recipe IDs.
        """
        meal_plans = db.query(MealPlan).filter(
            MealPlan.user_id == user_id,
            MealPlan.meal_date >= start_date,
            MealPlan.meal_date <= end_date
        ).all()
        
        # Get unique recipe IDs
        recipe_ids = list(set([mp.recipe_id for mp in meal_plans]))
        return recipe_ids
    
    @staticmethod
    def extract_ingredients_from_recipes(
        db: Session,
        recipe_ids: List[int],
        user_id: int
    ) -> List[dict]:
        """
        Extract ingredients from multiple recipes.
        Returns list of ingredient dictionaries with name, quantity, and recipe_id.
        """
        all_ingredients = []
        
        for recipe_id in recipe_ids:
            # Verify recipe exists and belongs to user
            recipe = db.query(Recipe).filter(
                Recipe.id == recipe_id,
                Recipe.user_id == user_id
            ).first()
            
            if not recipe:
                continue
            
            # Parse ingredients JSON
            try:
                ingredients = json.loads(recipe.ingredients)
            except (json.JSONDecodeError, TypeError):
                continue
            
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
        Returns list of consolidated ingredient dictionaries.
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
        Returns summed quantity string or None if incompatible.
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
    
    @staticmethod
    def get_user_shopping_lists(db: Session, user_id: int) -> List[ShoppingList]:
        """Get all shopping lists for a user."""
        return db.query(ShoppingList).filter(
            ShoppingList.user_id == user_id
        ).order_by(ShoppingList.created_at.desc()).all()
    
    @staticmethod
    def get_shopping_list_by_id(
        db: Session,
        list_id: int,
        user_id: int
    ) -> Optional[ShoppingList]:
        """
        Get a shopping list by ID with ownership validation.
        Returns None if not found or user doesn't own it.
        """
        shopping_list = db.query(ShoppingList).filter(
            ShoppingList.id == list_id,
            ShoppingList.user_id == user_id
        ).first()
        
        return shopping_list
    
    @staticmethod
    def delete_shopping_list(db: Session, list_id: int, user_id: int) -> bool:
        """
        Delete a shopping list with ownership validation.
        Cascading delete will remove all items.
        Returns True if deleted, False if not found.
        """
        shopping_list = ShoppingListGenerator.get_shopping_list_by_id(db, list_id, user_id)
        
        if not shopping_list:
            return False
        
        db.delete(shopping_list)
        db.commit()
        return True
    
    @staticmethod
    def update_item_status(
        db: Session,
        item_id: int,
        is_checked: bool,
        user_id: int
    ) -> Optional[ShoppingListItem]:
        """
        Update the checked status of a shopping list item.
        Validates user ownership of the parent shopping list.
        Returns None if item not found or access denied.
        """
        # Get item and verify ownership through shopping list
        item = db.query(ShoppingListItem).filter(
            ShoppingListItem.id == item_id
        ).first()
        
        if not item:
            return None
        
        # Verify user owns the shopping list
        shopping_list = db.query(ShoppingList).filter(
            ShoppingList.id == item.shopping_list_id,
            ShoppingList.user_id == user_id
        ).first()
        
        if not shopping_list:
            return None
        
        item.is_checked = is_checked
        db.commit()
        db.refresh(item)
        return item
    
    @staticmethod
    def add_custom_item(
        db: Session,
        list_id: int,
        item_data: CustomItemCreate,
        user_id: int
    ) -> Optional[ShoppingListItem]:
        """
        Add a custom item to a shopping list.
        Validates user ownership of the shopping list.
        Returns None if shopping list not found or access denied.
        """
        # Verify shopping list ownership
        shopping_list = ShoppingListGenerator.get_shopping_list_by_id(db, list_id, user_id)
        
        if not shopping_list:
            return None
        
        # Determine category
        category = item_data.category if item_data.category else ShoppingListGenerator.categorize_ingredient(item_data.ingredient_name)
        
        # Create custom item
        item = ShoppingListItem(
            shopping_list_id=list_id,
            ingredient_name=item_data.ingredient_name,
            quantity=item_data.quantity,
            category=category,
            is_checked=False,
            is_custom=True,
            recipe_id=None
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
    
    @staticmethod
    def delete_item(db: Session, item_id: int, user_id: int) -> bool:
        """
        Delete a shopping list item.
        Validates user ownership through the parent shopping list.
        Returns True if deleted, False if not found or access denied.
        """
        # Get item and verify ownership through shopping list
        item = db.query(ShoppingListItem).filter(
            ShoppingListItem.id == item_id
        ).first()
        
        if not item:
            return False
        
        # Verify user owns the shopping list
        shopping_list = db.query(ShoppingList).filter(
            ShoppingList.id == item.shopping_list_id,
            ShoppingList.user_id == user_id
        ).first()
        
        if not shopping_list:
            return False
        
        db.delete(item)
        db.commit()
        return True
    
    @staticmethod
    def generate_share_token(db: Session, list_id: int, user_id: int) -> Optional[str]:
        """
        Generate a unique share token for a shopping list.
        Returns the share token or None if shopping list not found.
        """
        shopping_list = ShoppingListGenerator.get_shopping_list_by_id(db, list_id, user_id)
        
        if not shopping_list:
            return None
        
        # Generate a unique token
        share_token = secrets.token_urlsafe(32)
        
        # Ensure uniqueness (very unlikely to collide, but check anyway)
        while db.query(ShoppingList).filter(ShoppingList.share_token == share_token).first():
            share_token = secrets.token_urlsafe(32)
        
        shopping_list.share_token = share_token
        db.commit()
        db.refresh(shopping_list)
        return share_token
    
    @staticmethod
    def get_shared_list(db: Session, share_token: str) -> Optional[ShoppingList]:
        """
        Get a shopping list by its share token (public access, no auth required).
        Returns None if token is invalid or shopping list not found.
        """
        shopping_list = db.query(ShoppingList).filter(
            ShoppingList.share_token == share_token
        ).first()
        
        return shopping_list
    
    @staticmethod
    def update_shared_item_status(
        db: Session,
        share_token: str,
        item_id: int,
        is_checked: bool
    ) -> Optional[ShoppingListItem]:
        """
        Update item status via share token (public access).
        Allows anyone with the share token to check/uncheck items.
        Returns None if share token invalid or item not found.
        """
        # Verify share token is valid
        shopping_list = ShoppingListGenerator.get_shared_list(db, share_token)
        
        if not shopping_list:
            return None
        
        # Get item and verify it belongs to this shopping list
        item = db.query(ShoppingListItem).filter(
            ShoppingListItem.id == item_id,
            ShoppingListItem.shopping_list_id == shopping_list.id
        ).first()
        
        if not item:
            return None
        
        item.is_checked = is_checked
        db.commit()
        db.refresh(item)
        return item
