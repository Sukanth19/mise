import pytest
from datetime import date
from sqlalchemy.orm import Session
from app.models import User, Recipe, NutritionFacts, DietaryLabel, AllergenWarning, MealPlan
from app.schemas import NutritionCreate, NutritionUpdate
from app.services.nutrition_service import NutritionTracker


@pytest.fixture
def test_user(db: Session):
    """Create a test user."""
    user = User(username="testuser", password_hash="hashed_password")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_recipe(db: Session, test_user: User):
    """Create a test recipe."""
    import json
    recipe = Recipe(
        user_id=test_user.id,
        title="Test Recipe",
        ingredients=json.dumps(["ingredient1", "ingredient2"]),
        steps=json.dumps(["step1", "step2"]),
        servings=4
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


class TestNutritionFactsBasics:
    """Test basic nutrition facts operations."""
    
    def test_validate_nutrition_values_positive(self):
        """Test validation with positive values."""
        data = {'calories': 100, 'protein_g': 10, 'carbs_g': 20, 'fat_g': 5, 'fiber_g': 3}
        assert NutritionTracker.validate_nutrition_values(data) is True
    
    def test_validate_nutrition_values_zero(self):
        """Test validation with zero values."""
        data = {'calories': 0, 'protein_g': 0}
        assert NutritionTracker.validate_nutrition_values(data) is True
    
    def test_validate_nutrition_values_negative(self):
        """Test validation with negative values."""
        data = {'calories': -100}
        assert NutritionTracker.validate_nutrition_values(data) is False
    
    def test_validate_nutrition_values_none(self):
        """Test validation with None values."""
        data = {'calories': None, 'protein_g': 10}
        assert NutritionTracker.validate_nutrition_values(data) is True
    
    def test_add_nutrition_facts_success(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test successful nutrition facts creation."""
        nutrition_data = NutritionCreate(
            calories=500.0,
            protein_g=25.0,
            carbs_g=60.0,
            fat_g=15.0,
            fiber_g=8.0
        )
        
        nutrition = NutritionTracker.add_nutrition_facts(db, test_recipe.id, nutrition_data, test_user.id)
        
        assert nutrition is not None
        assert nutrition.recipe_id == test_recipe.id
        assert float(nutrition.calories) == 500.0
        assert float(nutrition.protein_g) == 25.0
        assert float(nutrition.carbs_g) == 60.0
        assert float(nutrition.fat_g) == 15.0
        assert float(nutrition.fiber_g) == 8.0
    
    def test_add_nutrition_facts_negative_value(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test nutrition facts creation with negative value."""
        from pydantic import ValidationError
        
        # Pydantic should reject negative values at schema level
        with pytest.raises(ValidationError):
            nutrition_data = NutritionCreate(
                calories=-100.0,
                protein_g=25.0
            )
    
    def test_add_nutrition_facts_nonexistent_recipe(self, db: Session, test_user: User):
        """Test nutrition facts creation with non-existent recipe."""
        nutrition_data = NutritionCreate(calories=500.0)
        
        nutrition = NutritionTracker.add_nutrition_facts(db, 99999, nutrition_data, test_user.id)
        
        assert nutrition is None
    
    def test_add_nutrition_facts_updates_existing(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test that adding nutrition facts when they exist updates instead."""
        # Add initial nutrition facts
        nutrition_data1 = NutritionCreate(calories=500.0, protein_g=25.0)
        nutrition1 = NutritionTracker.add_nutrition_facts(db, test_recipe.id, nutrition_data1, test_user.id)
        
        # Add again with different values
        nutrition_data2 = NutritionCreate(calories=600.0, protein_g=30.0)
        nutrition2 = NutritionTracker.add_nutrition_facts(db, test_recipe.id, nutrition_data2, test_user.id)
        
        assert nutrition2 is not None
        assert float(nutrition2.calories) == 600.0
        assert float(nutrition2.protein_g) == 30.0
        
        # Verify only one nutrition facts record exists
        all_nutrition = db.query(NutritionFacts).filter(
            NutritionFacts.recipe_id == test_recipe.id
        ).all()
        assert len(all_nutrition) == 1
    
    def test_update_nutrition_facts_success(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test successful nutrition facts update."""
        # Create initial nutrition facts
        nutrition_data = NutritionCreate(calories=500.0, protein_g=25.0)
        NutritionTracker.add_nutrition_facts(db, test_recipe.id, nutrition_data, test_user.id)
        
        # Update nutrition facts
        update_data = NutritionUpdate(calories=600.0, carbs_g=70.0)
        updated_nutrition = NutritionTracker.update_nutrition_facts(db, test_recipe.id, update_data, test_user.id)
        
        assert updated_nutrition is not None
        assert float(updated_nutrition.calories) == 600.0
        assert float(updated_nutrition.protein_g) == 25.0  # Unchanged
        assert float(updated_nutrition.carbs_g) == 70.0
    
    def test_update_nutrition_facts_not_found(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test updating non-existent nutrition facts."""
        update_data = NutritionUpdate(calories=600.0)
        updated_nutrition = NutritionTracker.update_nutrition_facts(db, test_recipe.id, update_data, test_user.id)
        
        assert updated_nutrition is None
    
    def test_update_nutrition_facts_negative_value(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test updating nutrition facts with negative value."""
        from pydantic import ValidationError
        
        # Create initial nutrition facts
        nutrition_data = NutritionCreate(calories=500.0)
        NutritionTracker.add_nutrition_facts(db, test_recipe.id, nutrition_data, test_user.id)
        
        # Pydantic should reject negative values at schema level
        with pytest.raises(ValidationError):
            update_data = NutritionUpdate(calories=-100.0)
    
    def test_get_nutrition_facts_success(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test retrieving nutrition facts."""
        # Create nutrition facts
        nutrition_data = NutritionCreate(calories=500.0, protein_g=25.0)
        NutritionTracker.add_nutrition_facts(db, test_recipe.id, nutrition_data, test_user.id)
        
        # Retrieve nutrition facts
        nutrition = NutritionTracker.get_nutrition_facts(db, test_recipe.id)
        
        assert nutrition is not None
        assert float(nutrition.calories) == 500.0
        assert float(nutrition.protein_g) == 25.0
    
    def test_get_nutrition_facts_not_found(self, db: Session, test_recipe: Recipe):
        """Test retrieving non-existent nutrition facts."""
        nutrition = NutritionTracker.get_nutrition_facts(db, test_recipe.id)
        
        assert nutrition is None


class TestPerServingCalculation:
    """Test per-serving nutrition calculation."""
    
    def test_calculate_per_serving_normal(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test per-serving calculation with normal values."""
        # Create nutrition facts
        nutrition_data = NutritionCreate(
            calories=800.0,
            protein_g=40.0,
            carbs_g=100.0,
            fat_g=20.0,
            fiber_g=12.0
        )
        nutrition = NutritionTracker.add_nutrition_facts(db, test_recipe.id, nutrition_data, test_user.id)
        
        # Calculate per serving (recipe has 4 servings)
        per_serving = NutritionTracker.calculate_per_serving(nutrition, 4)
        
        assert per_serving['calories'] == 200.0
        assert per_serving['protein_g'] == 10.0
        assert per_serving['carbs_g'] == 25.0
        assert per_serving['fat_g'] == 5.0
        assert per_serving['fiber_g'] == 3.0
    
    def test_calculate_per_serving_one_serving(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test per-serving calculation with 1 serving."""
        nutrition_data = NutritionCreate(calories=500.0, protein_g=25.0)
        nutrition = NutritionTracker.add_nutrition_facts(db, test_recipe.id, nutrition_data, test_user.id)
        
        per_serving = NutritionTracker.calculate_per_serving(nutrition, 1)
        
        assert per_serving['calories'] == 500.0
        assert per_serving['protein_g'] == 25.0
    
    def test_calculate_per_serving_zero_servings(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test per-serving calculation with 0 servings (defaults to 1)."""
        nutrition_data = NutritionCreate(calories=500.0)
        nutrition = NutritionTracker.add_nutrition_facts(db, test_recipe.id, nutrition_data, test_user.id)
        
        per_serving = NutritionTracker.calculate_per_serving(nutrition, 0)
        
        assert per_serving['calories'] == 500.0
    
    def test_calculate_per_serving_none_values(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test per-serving calculation with None values."""
        nutrition_data = NutritionCreate(calories=800.0, protein_g=None)
        nutrition = NutritionTracker.add_nutrition_facts(db, test_recipe.id, nutrition_data, test_user.id)
        
        per_serving = NutritionTracker.calculate_per_serving(nutrition, 4)
        
        assert per_serving['calories'] == 200.0
        assert per_serving['protein_g'] is None


class TestDietaryLabels:
    """Test dietary labels functionality."""
    
    def test_add_dietary_labels_success(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test successful dietary labels addition."""
        labels = ['vegan', 'gluten-free', 'low-carb']
        
        result = NutritionTracker.add_dietary_labels(db, test_recipe.id, labels, test_user.id)
        
        assert result == labels
        
        # Verify labels were created
        db_labels = db.query(DietaryLabel).filter(
            DietaryLabel.recipe_id == test_recipe.id
        ).all()
        assert len(db_labels) == 3
        assert set([l.label for l in db_labels]) == set(labels)
    
    def test_add_dietary_labels_invalid_label(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test dietary labels addition with invalid label."""
        labels = ['vegan', 'invalid-label']
        
        result = NutritionTracker.add_dietary_labels(db, test_recipe.id, labels, test_user.id)
        
        assert result is None
    
    def test_add_dietary_labels_replaces_existing(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test that adding dietary labels replaces existing ones."""
        # Add initial labels
        labels1 = ['vegan', 'gluten-free']
        NutritionTracker.add_dietary_labels(db, test_recipe.id, labels1, test_user.id)
        
        # Add new labels
        labels2 = ['vegetarian', 'dairy-free']
        result = NutritionTracker.add_dietary_labels(db, test_recipe.id, labels2, test_user.id)
        
        assert result == labels2
        
        # Verify only new labels exist
        db_labels = db.query(DietaryLabel).filter(
            DietaryLabel.recipe_id == test_recipe.id
        ).all()
        assert len(db_labels) == 2
        assert set([l.label for l in db_labels]) == set(labels2)
    
    def test_add_dietary_labels_nonexistent_recipe(self, db: Session, test_user: User):
        """Test dietary labels addition with non-existent recipe."""
        labels = ['vegan']
        
        result = NutritionTracker.add_dietary_labels(db, 99999, labels, test_user.id)
        
        assert result is None


class TestAllergenWarnings:
    """Test allergen warnings functionality."""
    
    def test_add_allergen_warnings_success(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test successful allergen warnings addition."""
        allergens = ['nuts', 'dairy', 'eggs']
        
        result = NutritionTracker.add_allergen_warnings(db, test_recipe.id, allergens, test_user.id)
        
        assert result == allergens
        
        # Verify allergens were created
        db_allergens = db.query(AllergenWarning).filter(
            AllergenWarning.recipe_id == test_recipe.id
        ).all()
        assert len(db_allergens) == 3
        assert set([a.allergen for a in db_allergens]) == set(allergens)
    
    def test_add_allergen_warnings_invalid_allergen(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test allergen warnings addition with invalid allergen."""
        allergens = ['nuts', 'invalid-allergen']
        
        result = NutritionTracker.add_allergen_warnings(db, test_recipe.id, allergens, test_user.id)
        
        assert result is None
    
    def test_add_allergen_warnings_replaces_existing(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test that adding allergen warnings replaces existing ones."""
        # Add initial allergens
        allergens1 = ['nuts', 'dairy']
        NutritionTracker.add_allergen_warnings(db, test_recipe.id, allergens1, test_user.id)
        
        # Add new allergens
        allergens2 = ['soy', 'wheat']
        result = NutritionTracker.add_allergen_warnings(db, test_recipe.id, allergens2, test_user.id)
        
        assert result == allergens2
        
        # Verify only new allergens exist
        db_allergens = db.query(AllergenWarning).filter(
            AllergenWarning.recipe_id == test_recipe.id
        ).all()
        assert len(db_allergens) == 2
        assert set([a.allergen for a in db_allergens]) == set(allergens2)
    
    def test_add_allergen_warnings_nonexistent_recipe(self, db: Session, test_user: User):
        """Test allergen warnings addition with non-existent recipe."""
        allergens = ['nuts']
        
        result = NutritionTracker.add_allergen_warnings(db, 99999, allergens, test_user.id)
        
        assert result is None


class TestMealPlanNutritionSummary:
    """Test meal plan nutrition summary functionality."""
    
    def test_get_meal_plan_nutrition_summary_success(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test successful nutrition summary calculation."""
        # Add nutrition facts to recipe
        nutrition_data = NutritionCreate(
            calories=800.0,
            protein_g=40.0,
            carbs_g=100.0,
            fat_g=20.0,
            fiber_g=12.0
        )
        NutritionTracker.add_nutrition_facts(db, test_recipe.id, nutrition_data, test_user.id)
        
        # Create meal plans
        meal_plan1 = MealPlan(
            user_id=test_user.id,
            recipe_id=test_recipe.id,
            meal_date=date(2024, 1, 15),
            meal_time='breakfast'
        )
        meal_plan2 = MealPlan(
            user_id=test_user.id,
            recipe_id=test_recipe.id,
            meal_date=date(2024, 1, 15),
            meal_time='dinner'
        )
        meal_plan3 = MealPlan(
            user_id=test_user.id,
            recipe_id=test_recipe.id,
            meal_date=date(2024, 1, 16),
            meal_time='lunch'
        )
        db.add_all([meal_plan1, meal_plan2, meal_plan3])
        db.commit()
        
        # Get nutrition summary
        summary = NutritionTracker.get_meal_plan_nutrition_summary(
            db, test_user.id, date(2024, 1, 15), date(2024, 1, 16)
        )
        
        assert len(summary['daily_totals']) == 2
        
        # Check day 1 (2 meals)
        day1 = summary['daily_totals'][0]
        assert day1['date'] == '2024-01-15'
        assert day1['calories'] == 1600.0
        assert day1['protein_g'] == 80.0
        
        # Check day 2 (1 meal)
        day2 = summary['daily_totals'][1]
        assert day2['date'] == '2024-01-16'
        assert day2['calories'] == 800.0
        assert day2['protein_g'] == 40.0
        
        # Check weekly total
        assert summary['weekly_total']['calories'] == 2400.0
        assert summary['weekly_total']['protein_g'] == 120.0
        assert summary['missing_nutrition_count'] == 0
    
    def test_get_meal_plan_nutrition_summary_missing_nutrition(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test nutrition summary with recipes missing nutrition facts."""
        # Create recipe without nutrition facts
        import json
        recipe2 = Recipe(
            user_id=test_user.id,
            title="Recipe Without Nutrition",
            ingredients=json.dumps(["ingredient1"]),
            steps=json.dumps(["step1"])
        )
        db.add(recipe2)
        db.commit()
        db.refresh(recipe2)
        
        # Add nutrition to first recipe
        nutrition_data = NutritionCreate(calories=500.0, protein_g=25.0)
        NutritionTracker.add_nutrition_facts(db, test_recipe.id, nutrition_data, test_user.id)
        
        # Create meal plans
        meal_plan1 = MealPlan(
            user_id=test_user.id,
            recipe_id=test_recipe.id,
            meal_date=date(2024, 1, 15),
            meal_time='breakfast'
        )
        meal_plan2 = MealPlan(
            user_id=test_user.id,
            recipe_id=recipe2.id,
            meal_date=date(2024, 1, 15),
            meal_time='lunch'
        )
        db.add_all([meal_plan1, meal_plan2])
        db.commit()
        
        # Get nutrition summary
        summary = NutritionTracker.get_meal_plan_nutrition_summary(
            db, test_user.id, date(2024, 1, 15), date(2024, 1, 15)
        )
        
        # Only first recipe's nutrition should be counted
        assert summary['daily_totals'][0]['calories'] == 500.0
        assert summary['weekly_total']['calories'] == 500.0
        assert summary['missing_nutrition_count'] == 1
    
    def test_get_meal_plan_nutrition_summary_empty_range(self, db: Session, test_user: User):
        """Test nutrition summary with no meal plans."""
        summary = NutritionTracker.get_meal_plan_nutrition_summary(
            db, test_user.id, date(2024, 1, 15), date(2024, 1, 16)
        )
        
        assert len(summary['daily_totals']) == 0
        assert summary['weekly_total']['calories'] == 0.0
        assert summary['missing_nutrition_count'] == 0
