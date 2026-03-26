from typing import List, Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from bson import ObjectId
from app.repositories.recipe_repository import RecipeRepository
from app.repositories.meal_plan_repository import MealPlanRepository
from app.schemas import NutritionCreate, NutritionUpdate


class NutritionTracker:
    """Service for managing nutrition facts, dietary labels, and allergen warnings (embedded in recipes)."""
    
    # Valid dietary labels
    VALID_DIETARY_LABELS = {
        'vegan', 'vegetarian', 'gluten-free', 'dairy-free', 'keto', 'paleo', 'low-carb'
    }
    
    # Valid allergens
    VALID_ALLERGENS = {
        'nuts', 'dairy', 'eggs', 'soy', 'wheat', 'fish', 'shellfish'
    }
    
    def __init__(self, recipe_repository: RecipeRepository, meal_plan_repository: MealPlanRepository):
        """
        Initialize nutrition tracker with repositories.
        
        Args:
            recipe_repository: RecipeRepository instance for data access
            meal_plan_repository: MealPlanRepository instance for meal plan data
        """
        self.recipe_repository = recipe_repository
        self.meal_plan_repository = meal_plan_repository
    
    @staticmethod
    def validate_nutrition_values(nutrition_data: dict) -> bool:
        """
        Validate that all nutrition values are non-negative.
        
        Args:
            nutrition_data: Dictionary of nutrition values
            
        Returns:
            True if valid, False otherwise
        """
        for key, value in nutrition_data.items():
            if value is not None and value < 0:
                return False
        return True
    
    async def add_nutrition_facts(
        self,
        recipe_id: str,
        nutrition_data: NutritionCreate,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Add nutrition facts to a recipe (embedded document).
        Validates user ownership and non-negative values.
        
        Args:
            recipe_id: Recipe's ObjectId as string
            nutrition_data: Nutrition facts data
            user_id: User's ObjectId as string
            
        Returns:
            Updated recipe document if successful, None if validation fails or recipe not found
        """
        # Verify recipe exists and belongs to user
        recipe = await self.recipe_repository.find_by_id(recipe_id)
        
        if not recipe or str(recipe["user_id"]) != user_id:
            return None
        
        # Validate non-negative values
        nutrition_dict = nutrition_data.model_dump(exclude_unset=True)
        if not NutritionTracker.validate_nutrition_values(nutrition_dict):
            return None
        
        # Create nutrition facts embedded document
        nutrition_facts = {
            "calories": nutrition_data.calories,
            "protein_g": nutrition_data.protein_g,
            "carbs_g": nutrition_data.carbs_g,
            "fat_g": nutrition_data.fat_g,
            "fiber_g": nutrition_data.fiber_g
        }
        
        # Update recipe with embedded nutrition facts
        await self.recipe_repository.update(recipe_id, {
            "nutrition_facts": nutrition_facts,
            "updated_at": datetime.utcnow()
        })
        
        return await self.recipe_repository.find_by_id(recipe_id)
    
    async def update_nutrition_facts(
        self,
        recipe_id: str,
        nutrition_data: NutritionUpdate,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Update nutrition facts for a recipe (embedded document).
        Validates user ownership and non-negative values.
        
        Args:
            recipe_id: Recipe's ObjectId as string
            nutrition_data: Nutrition facts update data
            user_id: User's ObjectId as string
            
        Returns:
            Updated recipe document if successful, None if validation fails or recipe not found
        """
        # Verify recipe exists and belongs to user
        recipe = await self.recipe_repository.find_by_id(recipe_id)
        
        if not recipe or str(recipe["user_id"]) != user_id:
            return None
        
        # Validate non-negative values
        nutrition_dict = nutrition_data.model_dump(exclude_unset=True)
        if not NutritionTracker.validate_nutrition_values(nutrition_dict):
            return None
        
        # Get existing nutrition facts or create new
        nutrition_facts = recipe.get("nutrition_facts", {})
        
        # Update fields
        if nutrition_data.calories is not None:
            nutrition_facts["calories"] = nutrition_data.calories
        if nutrition_data.protein_g is not None:
            nutrition_facts["protein_g"] = nutrition_data.protein_g
        if nutrition_data.carbs_g is not None:
            nutrition_facts["carbs_g"] = nutrition_data.carbs_g
        if nutrition_data.fat_g is not None:
            nutrition_facts["fat_g"] = nutrition_data.fat_g
        if nutrition_data.fiber_g is not None:
            nutrition_facts["fiber_g"] = nutrition_data.fiber_g
        
        # Update recipe with embedded nutrition facts
        await self.recipe_repository.update(recipe_id, {
            "nutrition_facts": nutrition_facts,
            "updated_at": datetime.utcnow()
        })
        
        return await self.recipe_repository.find_by_id(recipe_id)
    
    async def get_nutrition_facts(self, recipe_id: str) -> Optional[Dict[str, Any]]:
        """
        Get nutrition facts for a recipe (from embedded document).
        
        Args:
            recipe_id: Recipe's ObjectId as string
            
        Returns:
            Nutrition facts dictionary if found, None otherwise
        """
        recipe = await self.recipe_repository.find_by_id(recipe_id)
        
        if not recipe:
            return None
        
        return recipe.get("nutrition_facts")
    
    @staticmethod
    def calculate_per_serving(
        nutrition: Dict[str, Any],
        servings: int
    ) -> Dict[str, Optional[float]]:
        """
        Calculate per-serving nutrition values by dividing total by servings.
        
        Args:
            nutrition: Nutrition facts dictionary
            servings: Number of servings
            
        Returns:
            Dictionary with per-serving values
        """
        if servings <= 0:
            servings = 1
        
        return {
            'calories': float(nutrition.get("calories", 0) / servings) if nutrition.get("calories") else None,
            'protein_g': float(nutrition.get("protein_g", 0) / servings) if nutrition.get("protein_g") else None,
            'carbs_g': float(nutrition.get("carbs_g", 0) / servings) if nutrition.get("carbs_g") else None,
            'fat_g': float(nutrition.get("fat_g", 0) / servings) if nutrition.get("fat_g") else None,
            'fiber_g': float(nutrition.get("fiber_g", 0) / servings) if nutrition.get("fiber_g") else None
        }
    
    async def add_dietary_labels(
        self,
        recipe_id: str,
        labels: List[str],
        user_id: str
    ) -> Optional[List[str]]:
        """
        Add dietary labels to a recipe (embedded array).
        Validates user ownership and label values.
        Replaces existing labels with new ones.
        
        Args:
            recipe_id: Recipe's ObjectId as string
            labels: List of dietary labels
            user_id: User's ObjectId as string
            
        Returns:
            List of labels if successful, None if validation fails
        """
        # Verify recipe exists and belongs to user
        recipe = await self.recipe_repository.find_by_id(recipe_id)
        
        if not recipe or str(recipe["user_id"]) != user_id:
            return None
        
        # Validate all labels
        for label in labels:
            if label not in NutritionTracker.VALID_DIETARY_LABELS:
                return None
        
        # Update recipe with dietary labels
        await self.recipe_repository.update(recipe_id, {
            "dietary_labels": labels,
            "updated_at": datetime.utcnow()
        })
        
        return labels
    
    async def add_allergen_warnings(
        self,
        recipe_id: str,
        allergens: List[str],
        user_id: str
    ) -> Optional[List[str]]:
        """
        Add allergen warnings to a recipe (embedded array).
        Validates user ownership and allergen values.
        Replaces existing allergens with new ones.
        
        Args:
            recipe_id: Recipe's ObjectId as string
            allergens: List of allergen warnings
            user_id: User's ObjectId as string
            
        Returns:
            List of allergens if successful, None if validation fails
        """
        # Verify recipe exists and belongs to user
        recipe = await self.recipe_repository.find_by_id(recipe_id)
        
        if not recipe or str(recipe["user_id"]) != user_id:
            return None
        
        # Validate all allergens
        for allergen in allergens:
            if allergen not in NutritionTracker.VALID_ALLERGENS:
                return None
        
        # Update recipe with allergen warnings
        await self.recipe_repository.update(recipe_id, {
            "allergen_warnings": allergens,
            "updated_at": datetime.utcnow()
        })
        
        return allergens
    
    async def get_meal_plan_nutrition_summary(
        self,
        user_id: str,
        start_date: date,
        end_date: date
    ) -> Dict:
        """
        Calculate nutrition summary for a meal plan date range.
        Returns daily totals, weekly total, and count of recipes with missing nutrition.
        
        Args:
            user_id: User's ObjectId as string
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            Dictionary with daily_totals, weekly_total, and missing_nutrition_count
        """
        # Get meal plans for date range
        meal_plans = await self.meal_plan_repository.find_by_user_and_date_range(
            user_id, start_date, end_date
        )
        
        # Group meal plans by date
        daily_meals = {}
        for meal_plan in meal_plans:
            date_str = meal_plan["meal_date"].isoformat()
            if date_str not in daily_meals:
                daily_meals[date_str] = []
            daily_meals[date_str].append(meal_plan)
        
        # Calculate daily totals
        daily_totals = []
        weekly_total = {
            'calories': Decimal(0),
            'protein_g': Decimal(0),
            'carbs_g': Decimal(0),
            'fat_g': Decimal(0),
            'fiber_g': Decimal(0)
        }
        missing_nutrition_count = 0
        
        for date_str in sorted(daily_meals.keys()):
            daily_total = {
                'date': date_str,
                'calories': Decimal(0),
                'protein_g': Decimal(0),
                'carbs_g': Decimal(0),
                'fat_g': Decimal(0),
                'fiber_g': Decimal(0)
            }
            
            for meal_plan in daily_meals[date_str]:
                # Get nutrition facts for recipe (embedded in recipe document)
                nutrition = await self.get_nutrition_facts(str(meal_plan["recipe_id"]))
                
                if not nutrition:
                    missing_nutrition_count += 1
                    continue
                
                # Add to daily total
                if nutrition.get("calories"):
                    daily_total['calories'] += Decimal(str(nutrition["calories"]))
                if nutrition.get("protein_g"):
                    daily_total['protein_g'] += Decimal(str(nutrition["protein_g"]))
                if nutrition.get("carbs_g"):
                    daily_total['carbs_g'] += Decimal(str(nutrition["carbs_g"]))
                if nutrition.get("fat_g"):
                    daily_total['fat_g'] += Decimal(str(nutrition["fat_g"]))
                if nutrition.get("fiber_g"):
                    daily_total['fiber_g'] += Decimal(str(nutrition["fiber_g"]))
            
            # Convert to float for response
            daily_total_float = {
                'date': date_str,
                'calories': float(daily_total['calories']),
                'protein_g': float(daily_total['protein_g']),
                'carbs_g': float(daily_total['carbs_g']),
                'fat_g': float(daily_total['fat_g']),
                'fiber_g': float(daily_total['fiber_g'])
            }
            daily_totals.append(daily_total_float)
            
            # Add to weekly total
            weekly_total['calories'] += daily_total['calories']
            weekly_total['protein_g'] += daily_total['protein_g']
            weekly_total['carbs_g'] += daily_total['carbs_g']
            weekly_total['fat_g'] += daily_total['fat_g']
            weekly_total['fiber_g'] += daily_total['fiber_g']
        
        # Convert weekly total to float
        weekly_total_float = {
            'calories': float(weekly_total['calories']),
            'protein_g': float(weekly_total['protein_g']),
            'carbs_g': float(weekly_total['carbs_g']),
            'fat_g': float(weekly_total['fat_g']),
            'fiber_g': float(weekly_total['fiber_g'])
        }
        
        return {
            'daily_totals': daily_totals,
            'weekly_total': weekly_total_float,
            'missing_nutrition_count': missing_nutrition_count
        }
