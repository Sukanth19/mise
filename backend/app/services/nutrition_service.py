from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import date
from decimal import Decimal
from app.models import NutritionFacts, DietaryLabel, AllergenWarning, Recipe, MealPlan
from app.schemas import NutritionCreate, NutritionUpdate


class NutritionTracker:
    """Service for managing nutrition facts, dietary labels, and allergen warnings."""
    
    # Valid dietary labels
    VALID_DIETARY_LABELS = {
        'vegan', 'vegetarian', 'gluten-free', 'dairy-free', 'keto', 'paleo', 'low-carb'
    }
    
    # Valid allergens
    VALID_ALLERGENS = {
        'nuts', 'dairy', 'eggs', 'soy', 'wheat', 'fish', 'shellfish'
    }
    
    @staticmethod
    def validate_nutrition_values(nutrition_data: dict) -> bool:
        """
        Validate that all nutrition values are non-negative.
        Returns True if valid, False otherwise.
        """
        for key, value in nutrition_data.items():
            if value is not None and value < 0:
                return False
        return True
    
    @staticmethod
    def add_nutrition_facts(
        db: Session,
        recipe_id: int,
        nutrition_data: NutritionCreate,
        user_id: int
    ) -> Optional[NutritionFacts]:
        """
        Add nutrition facts to a recipe.
        Validates user ownership and non-negative values.
        Returns None if validation fails or recipe not found.
        """
        # Verify recipe exists and belongs to user
        recipe = db.query(Recipe).filter(
            Recipe.id == recipe_id,
            Recipe.user_id == user_id
        ).first()
        
        if not recipe:
            return None
        
        # Validate non-negative values
        nutrition_dict = nutrition_data.model_dump(exclude_unset=True)
        if not NutritionTracker.validate_nutrition_values(nutrition_dict):
            return None
        
        # Check if nutrition facts already exist
        existing = db.query(NutritionFacts).filter(
            NutritionFacts.recipe_id == recipe_id
        ).first()
        
        if existing:
            # Update existing instead of creating new
            return NutritionTracker.update_nutrition_facts(db, recipe_id, nutrition_data, user_id)
        
        # Create nutrition facts
        nutrition_facts = NutritionFacts(
            recipe_id=recipe_id,
            calories=nutrition_data.calories,
            protein_g=nutrition_data.protein_g,
            carbs_g=nutrition_data.carbs_g,
            fat_g=nutrition_data.fat_g,
            fiber_g=nutrition_data.fiber_g
        )
        db.add(nutrition_facts)
        db.commit()
        db.refresh(nutrition_facts)
        return nutrition_facts
    
    @staticmethod
    def update_nutrition_facts(
        db: Session,
        recipe_id: int,
        nutrition_data: NutritionUpdate,
        user_id: int
    ) -> Optional[NutritionFacts]:
        """
        Update nutrition facts for a recipe.
        Validates user ownership and non-negative values.
        Returns None if validation fails or nutrition facts not found.
        """
        # Verify recipe exists and belongs to user
        recipe = db.query(Recipe).filter(
            Recipe.id == recipe_id,
            Recipe.user_id == user_id
        ).first()
        
        if not recipe:
            return None
        
        # Validate non-negative values
        nutrition_dict = nutrition_data.model_dump(exclude_unset=True)
        if not NutritionTracker.validate_nutrition_values(nutrition_dict):
            return None
        
        # Get existing nutrition facts
        nutrition_facts = db.query(NutritionFacts).filter(
            NutritionFacts.recipe_id == recipe_id
        ).first()
        
        if not nutrition_facts:
            return None
        
        # Update fields
        if nutrition_data.calories is not None:
            nutrition_facts.calories = nutrition_data.calories
        if nutrition_data.protein_g is not None:
            nutrition_facts.protein_g = nutrition_data.protein_g
        if nutrition_data.carbs_g is not None:
            nutrition_facts.carbs_g = nutrition_data.carbs_g
        if nutrition_data.fat_g is not None:
            nutrition_facts.fat_g = nutrition_data.fat_g
        if nutrition_data.fiber_g is not None:
            nutrition_facts.fiber_g = nutrition_data.fiber_g
        
        db.commit()
        db.refresh(nutrition_facts)
        return nutrition_facts
    
    @staticmethod
    def get_nutrition_facts(db: Session, recipe_id: int) -> Optional[NutritionFacts]:
        """
        Get nutrition facts for a recipe.
        Returns None if not found.
        """
        return db.query(NutritionFacts).filter(
            NutritionFacts.recipe_id == recipe_id
        ).first()
    
    @staticmethod
    def calculate_per_serving(
        nutrition: NutritionFacts,
        servings: int
    ) -> Dict[str, Optional[float]]:
        """
        Calculate per-serving nutrition values by dividing total by servings.
        Returns dictionary with per-serving values.
        """
        if servings <= 0:
            servings = 1
        
        return {
            'calories': float(nutrition.calories / servings) if nutrition.calories else None,
            'protein_g': float(nutrition.protein_g / servings) if nutrition.protein_g else None,
            'carbs_g': float(nutrition.carbs_g / servings) if nutrition.carbs_g else None,
            'fat_g': float(nutrition.fat_g / servings) if nutrition.fat_g else None,
            'fiber_g': float(nutrition.fiber_g / servings) if nutrition.fiber_g else None
        }
    
    @staticmethod
    def add_dietary_labels(
        db: Session,
        recipe_id: int,
        labels: List[str],
        user_id: int
    ) -> Optional[List[str]]:
        """
        Add dietary labels to a recipe.
        Validates user ownership and label values.
        Replaces existing labels with new ones.
        Returns list of labels or None if validation fails.
        """
        # Verify recipe exists and belongs to user
        recipe = db.query(Recipe).filter(
            Recipe.id == recipe_id,
            Recipe.user_id == user_id
        ).first()
        
        if not recipe:
            return None
        
        # Validate all labels
        for label in labels:
            if label not in NutritionTracker.VALID_DIETARY_LABELS:
                return None
        
        # Remove existing labels
        db.query(DietaryLabel).filter(
            DietaryLabel.recipe_id == recipe_id
        ).delete()
        
        # Add new labels
        for label in labels:
            dietary_label = DietaryLabel(
                recipe_id=recipe_id,
                label=label
            )
            db.add(dietary_label)
        
        db.commit()
        return labels
    
    @staticmethod
    def add_allergen_warnings(
        db: Session,
        recipe_id: int,
        allergens: List[str],
        user_id: int
    ) -> Optional[List[str]]:
        """
        Add allergen warnings to a recipe.
        Validates user ownership and allergen values.
        Replaces existing allergens with new ones.
        Returns list of allergens or None if validation fails.
        """
        # Verify recipe exists and belongs to user
        recipe = db.query(Recipe).filter(
            Recipe.id == recipe_id,
            Recipe.user_id == user_id
        ).first()
        
        if not recipe:
            return None
        
        # Validate all allergens
        for allergen in allergens:
            if allergen not in NutritionTracker.VALID_ALLERGENS:
                return None
        
        # Remove existing allergens
        db.query(AllergenWarning).filter(
            AllergenWarning.recipe_id == recipe_id
        ).delete()
        
        # Add new allergens
        for allergen in allergens:
            allergen_warning = AllergenWarning(
                recipe_id=recipe_id,
                allergen=allergen
            )
            db.add(allergen_warning)
        
        db.commit()
        return allergens
    
    @staticmethod
    def get_meal_plan_nutrition_summary(
        db: Session,
        user_id: int,
        start_date: date,
        end_date: date
    ) -> Dict:
        """
        Calculate nutrition summary for a meal plan date range.
        Returns daily totals, weekly total, and count of recipes with missing nutrition.
        """
        # Get meal plans for date range
        meal_plans = db.query(MealPlan).filter(
            MealPlan.user_id == user_id,
            MealPlan.meal_date >= start_date,
            MealPlan.meal_date <= end_date
        ).order_by(MealPlan.meal_date).all()
        
        # Group meal plans by date
        daily_meals = {}
        for meal_plan in meal_plans:
            date_str = meal_plan.meal_date.isoformat()
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
                # Get nutrition facts for recipe
                nutrition = NutritionTracker.get_nutrition_facts(db, meal_plan.recipe_id)
                
                if not nutrition:
                    missing_nutrition_count += 1
                    continue
                
                # Add to daily total
                if nutrition.calories:
                    daily_total['calories'] += nutrition.calories
                if nutrition.protein_g:
                    daily_total['protein_g'] += nutrition.protein_g
                if nutrition.carbs_g:
                    daily_total['carbs_g'] += nutrition.carbs_g
                if nutrition.fat_g:
                    daily_total['fat_g'] += nutrition.fat_g
                if nutrition.fiber_g:
                    daily_total['fiber_g'] += nutrition.fiber_g
            
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
