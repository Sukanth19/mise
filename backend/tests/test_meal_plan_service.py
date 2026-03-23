import pytest
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models import User, Recipe, MealPlan, MealPlanTemplate, MealPlanTemplateItem
from app.schemas import MealPlanCreate, MealPlanUpdate, TemplateCreate, TemplateItemCreate
from app.services.meal_plan_service import MealPlanner


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
        steps=json.dumps(["step1", "step2"])
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


class TestMealPlannerBasics:
    """Test basic meal plan CRUD operations."""
    
    def test_validate_meal_time(self):
        """Test meal time validation."""
        assert MealPlanner.validate_meal_time('breakfast') is True
        assert MealPlanner.validate_meal_time('lunch') is True
        assert MealPlanner.validate_meal_time('dinner') is True
        assert MealPlanner.validate_meal_time('snack') is True
        assert MealPlanner.validate_meal_time('invalid') is False
        assert MealPlanner.validate_meal_time('BREAKFAST') is False
    
    def test_create_meal_plan_success(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test successful meal plan creation."""
        meal_plan_data = MealPlanCreate(
            recipe_id=test_recipe.id,
            meal_date="2024-01-15",
            meal_time="breakfast"
        )
        
        meal_plan = MealPlanner.create_meal_plan(db, test_user.id, meal_plan_data)
        
        assert meal_plan is not None
        assert meal_plan.user_id == test_user.id
        assert meal_plan.recipe_id == test_recipe.id
        assert meal_plan.meal_date == date(2024, 1, 15)
        assert meal_plan.meal_time == "breakfast"
    
    def test_create_meal_plan_invalid_meal_time(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test meal plan creation with invalid meal time."""
        meal_plan_data = MealPlanCreate(
            recipe_id=test_recipe.id,
            meal_date="2024-01-15",
            meal_time="invalid"
        )
        
        meal_plan = MealPlanner.create_meal_plan(db, test_user.id, meal_plan_data)
        
        assert meal_plan is None
    
    def test_create_meal_plan_invalid_date(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test meal plan creation with invalid date format."""
        meal_plan_data = MealPlanCreate(
            recipe_id=test_recipe.id,
            meal_date="invalid-date",
            meal_time="breakfast"
        )
        
        meal_plan = MealPlanner.create_meal_plan(db, test_user.id, meal_plan_data)
        
        assert meal_plan is None
    
    def test_create_meal_plan_nonexistent_recipe(self, db: Session, test_user: User):
        """Test meal plan creation with non-existent recipe."""
        meal_plan_data = MealPlanCreate(
            recipe_id=99999,
            meal_date="2024-01-15",
            meal_time="breakfast"
        )
        
        meal_plan = MealPlanner.create_meal_plan(db, test_user.id, meal_plan_data)
        
        assert meal_plan is None
    
    def test_get_meal_plans_by_date_range(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test retrieving meal plans by date range."""
        # Create multiple meal plans
        dates = ["2024-01-15", "2024-01-16", "2024-01-20"]
        for meal_date in dates:
            meal_plan_data = MealPlanCreate(
                recipe_id=test_recipe.id,
                meal_date=meal_date,
                meal_time="lunch"
            )
            MealPlanner.create_meal_plan(db, test_user.id, meal_plan_data)
        
        # Query date range
        start_date = date(2024, 1, 15)
        end_date = date(2024, 1, 18)
        
        meal_plans = MealPlanner.get_meal_plans(db, test_user.id, start_date, end_date)
        
        assert len(meal_plans) == 2
        assert all(start_date <= mp.meal_date <= end_date for mp in meal_plans)
    
    def test_update_meal_plan_success(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test successful meal plan update."""
        # Create meal plan
        meal_plan_data = MealPlanCreate(
            recipe_id=test_recipe.id,
            meal_date="2024-01-15",
            meal_time="breakfast"
        )
        meal_plan = MealPlanner.create_meal_plan(db, test_user.id, meal_plan_data)
        
        # Update meal plan
        update_data = MealPlanUpdate(
            meal_date="2024-01-16",
            meal_time="dinner"
        )
        updated_meal_plan = MealPlanner.update_meal_plan(db, meal_plan.id, test_user.id, update_data)
        
        assert updated_meal_plan is not None
        assert updated_meal_plan.meal_date == date(2024, 1, 16)
        assert updated_meal_plan.meal_time == "dinner"
    
    def test_update_meal_plan_invalid_meal_time(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test meal plan update with invalid meal time."""
        # Create meal plan
        meal_plan_data = MealPlanCreate(
            recipe_id=test_recipe.id,
            meal_date="2024-01-15",
            meal_time="breakfast"
        )
        meal_plan = MealPlanner.create_meal_plan(db, test_user.id, meal_plan_data)
        
        # Try to update with invalid meal time
        update_data = MealPlanUpdate(meal_time="invalid")
        updated_meal_plan = MealPlanner.update_meal_plan(db, meal_plan.id, test_user.id, update_data)
        
        assert updated_meal_plan is None
    
    def test_delete_meal_plan_success(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test successful meal plan deletion."""
        # Create meal plan
        meal_plan_data = MealPlanCreate(
            recipe_id=test_recipe.id,
            meal_date="2024-01-15",
            meal_time="breakfast"
        )
        meal_plan = MealPlanner.create_meal_plan(db, test_user.id, meal_plan_data)
        
        # Delete meal plan
        result = MealPlanner.delete_meal_plan(db, meal_plan.id, test_user.id)
        
        assert result is True
        
        # Verify deletion
        deleted_meal_plan = db.query(MealPlan).filter(MealPlan.id == meal_plan.id).first()
        assert deleted_meal_plan is None
    
    def test_delete_meal_plan_not_found(self, db: Session, test_user: User):
        """Test deleting non-existent meal plan."""
        result = MealPlanner.delete_meal_plan(db, 99999, test_user.id)
        
        assert result is False


class TestMealPlanTemplates:
    """Test meal plan template functionality."""
    
    def test_create_template_success(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test successful template creation."""
        template_data = TemplateCreate(
            name="Weekly Plan",
            description="My weekly meal plan",
            items=[
                TemplateItemCreate(recipe_id=test_recipe.id, day_offset=0, meal_time="breakfast"),
                TemplateItemCreate(recipe_id=test_recipe.id, day_offset=1, meal_time="lunch"),
                TemplateItemCreate(recipe_id=test_recipe.id, day_offset=2, meal_time="dinner")
            ]
        )
        
        template = MealPlanner.create_template(db, test_user.id, template_data)
        
        assert template is not None
        assert template.name == "Weekly Plan"
        assert template.description == "My weekly meal plan"
        
        # Verify template items were created
        items = db.query(MealPlanTemplateItem).filter(
            MealPlanTemplateItem.template_id == template.id
        ).all()
        assert len(items) == 3
    
    def test_create_template_invalid_meal_time(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test template creation with invalid meal time."""
        template_data = TemplateCreate(
            name="Invalid Template",
            items=[
                TemplateItemCreate(recipe_id=test_recipe.id, day_offset=0, meal_time="invalid")
            ]
        )
        
        template = MealPlanner.create_template(db, test_user.id, template_data)
        
        assert template is None
    
    def test_create_template_nonexistent_recipe(self, db: Session, test_user: User):
        """Test template creation with non-existent recipe."""
        template_data = TemplateCreate(
            name="Invalid Template",
            items=[
                TemplateItemCreate(recipe_id=99999, day_offset=0, meal_time="breakfast")
            ]
        )
        
        template = MealPlanner.create_template(db, test_user.id, template_data)
        
        assert template is None
    
    def test_get_user_templates(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test retrieving user templates."""
        # Create multiple templates
        for i in range(3):
            template_data = TemplateCreate(
                name=f"Template {i}",
                items=[
                    TemplateItemCreate(recipe_id=test_recipe.id, day_offset=0, meal_time="breakfast")
                ]
            )
            MealPlanner.create_template(db, test_user.id, template_data)
        
        templates = MealPlanner.get_user_templates(db, test_user.id)
        
        assert len(templates) == 3
    
    def test_apply_template_success(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test successful template application."""
        # Create template
        template_data = TemplateCreate(
            name="3-Day Plan",
            items=[
                TemplateItemCreate(recipe_id=test_recipe.id, day_offset=0, meal_time="breakfast"),
                TemplateItemCreate(recipe_id=test_recipe.id, day_offset=1, meal_time="lunch"),
                TemplateItemCreate(recipe_id=test_recipe.id, day_offset=2, meal_time="dinner")
            ]
        )
        template = MealPlanner.create_template(db, test_user.id, template_data)
        
        # Apply template
        start_date = date(2024, 1, 15)
        created_count = MealPlanner.apply_template(db, template.id, test_user.id, start_date)
        
        assert created_count == 3
        
        # Verify meal plans were created
        meal_plans = MealPlanner.get_meal_plans(
            db, test_user.id, start_date, start_date + timedelta(days=2)
        )
        assert len(meal_plans) == 3
        assert meal_plans[0].meal_date == start_date
        assert meal_plans[1].meal_date == start_date + timedelta(days=1)
        assert meal_plans[2].meal_date == start_date + timedelta(days=2)
    
    def test_apply_template_not_found(self, db: Session, test_user: User):
        """Test applying non-existent template."""
        start_date = date(2024, 1, 15)
        created_count = MealPlanner.apply_template(db, 99999, test_user.id, start_date)
        
        assert created_count is None
    
    def test_delete_template_success(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test successful template deletion."""
        # Create template
        template_data = TemplateCreate(
            name="Template to Delete",
            items=[
                TemplateItemCreate(recipe_id=test_recipe.id, day_offset=0, meal_time="breakfast")
            ]
        )
        template = MealPlanner.create_template(db, test_user.id, template_data)
        
        # Delete template
        result = MealPlanner.delete_template(db, template.id, test_user.id)
        
        assert result is True
        
        # Verify deletion
        deleted_template = db.query(MealPlanTemplate).filter(
            MealPlanTemplate.id == template.id
        ).first()
        assert deleted_template is None
    
    def test_delete_template_not_found(self, db: Session, test_user: User):
        """Test deleting non-existent template."""
        result = MealPlanner.delete_template(db, 99999, test_user.id)
        
        assert result is False


class TestICalExport:
    """Test iCal export functionality."""
    
    def test_export_to_ical_success(self, db: Session, test_user: User, test_recipe: Recipe):
        """Test successful iCal export."""
        # Create meal plans
        meal_plan_data1 = MealPlanCreate(
            recipe_id=test_recipe.id,
            meal_date="2024-01-15",
            meal_time="breakfast"
        )
        meal_plan_data2 = MealPlanCreate(
            recipe_id=test_recipe.id,
            meal_date="2024-01-15",
            meal_time="dinner"
        )
        MealPlanner.create_meal_plan(db, test_user.id, meal_plan_data1)
        MealPlanner.create_meal_plan(db, test_user.id, meal_plan_data2)
        
        # Export to iCal
        start_date = date(2024, 1, 15)
        end_date = date(2024, 1, 15)
        
        try:
            ical_data = MealPlanner.export_to_ical(db, test_user.id, start_date, end_date)
            
            assert ical_data is not None
            assert isinstance(ical_data, bytes)
            assert b'BEGIN:VCALENDAR' in ical_data
            assert b'BEGIN:VEVENT' in ical_data
            assert b'Test Recipe' in ical_data
        except ImportError as e:
            pytest.skip(f"icalendar library not installed: {e}")
    
    def test_export_to_ical_empty_range(self, db: Session, test_user: User):
        """Test iCal export with no meal plans."""
        start_date = date(2024, 1, 15)
        end_date = date(2024, 1, 15)
        
        try:
            ical_data = MealPlanner.export_to_ical(db, test_user.id, start_date, end_date)
            
            assert ical_data is not None
            assert isinstance(ical_data, bytes)
            assert b'BEGIN:VCALENDAR' in ical_data
        except ImportError as e:
            pytest.skip(f"icalendar library not installed: {e}")
