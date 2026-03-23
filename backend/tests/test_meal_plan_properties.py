"""Property-based tests for meal planning system."""
import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"

from hypothesis import given, strategies as st, settings as hyp_settings, HealthCheck
from datetime import timedelta, date, datetime
import pytest
import uuid


# Feature: recipe-saver-enhancements, Property 27: Meal plan creation and retrieval
@given(
    meal_date_offset=st.integers(min_value=0, max_value=30),
    meal_time=st.sampled_from(['breakfast', 'lunch', 'dinner', 'snack'])
)
@hyp_settings(max_examples=100, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_meal_plan_creation_and_retrieval_property(db, meal_date_offset, meal_time):
    """
    Property 27: Meal plan creation and retrieval
    
    For any recipe, date, and meal time, creating a meal plan should store
    the entry and make it retrievable by date range.
    
    **Validates: Requirements 14.2**
    """
    from app.services.meal_plan_service import MealPlanner
    from app.services.recipe_service import RecipeManager
    from app.services.auth_service import AuthService
    from app.schemas import MealPlanCreate, RecipeCreate
    
    # Create a test user
    unique_username = f"mealuser_{uuid.uuid4().hex[:8]}"
    user = AuthService.create_user(db, unique_username, "password123")
    
    # Create a recipe
    recipe_data = RecipeCreate(
        title="Test Recipe",
        ingredients=["ingredient1"],
        steps=["step1"]
    )
    recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
    
    # Calculate meal date
    meal_date = date.today() + timedelta(days=meal_date_offset)
    meal_date_str = meal_date.strftime('%Y-%m-%d')
    
    # Create meal plan
    meal_plan_data = MealPlanCreate(
        recipe_id=recipe.id,
        meal_date=meal_date_str,
        meal_time=meal_time
    )
    
    meal_plan = MealPlanner.create_meal_plan(db, user.id, meal_plan_data)
    
    assert meal_plan is not None, "Meal plan should be created successfully"
    assert meal_plan.recipe_id == recipe.id, "Meal plan should reference the correct recipe"
    assert meal_plan.meal_date == meal_date, "Meal plan should have the correct date"
    assert meal_plan.meal_time == meal_time, "Meal plan should have the correct meal time"
    assert meal_plan.user_id == user.id, "Meal plan should belong to the user"
    
    # Retrieve meal plans by date range
    start_date = meal_date - timedelta(days=1)
    end_date = meal_date + timedelta(days=1)
    
    retrieved_plans = MealPlanner.get_meal_plans(db, user.id, start_date, end_date)
    
    assert len(retrieved_plans) > 0, "Should retrieve at least one meal plan"
    assert any(mp.id == meal_plan.id for mp in retrieved_plans), \
        "Retrieved meal plans should include the created meal plan"


# Feature: recipe-saver-enhancements, Property 28: Meal time validation
@given(
    valid_meal_time=st.sampled_from(['breakfast', 'lunch', 'dinner', 'snack']),
    invalid_meal_time=st.text(min_size=1, max_size=20).filter(
        lambda x: x not in ['breakfast', 'lunch', 'dinner', 'snack']
    )
)
@hyp_settings(max_examples=100, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_meal_time_validation_property(db, valid_meal_time, invalid_meal_time):
    """
    Property 28: Meal time validation
    
    Meal plans should only accept valid meal times: breakfast, lunch, dinner, or snack.
    Invalid meal times should be rejected.
    
    **Validates: Requirements 14.3**
    """
    from app.services.meal_plan_service import MealPlanner
    from app.services.recipe_service import RecipeManager
    from app.services.auth_service import AuthService
    from app.schemas import MealPlanCreate, RecipeCreate
    
    # Create a test user
    unique_username = f"validuser_{uuid.uuid4().hex[:8]}"
    user = AuthService.create_user(db, unique_username, "password123")
    
    # Create a recipe
    recipe_data = RecipeCreate(
        title="Test Recipe",
        ingredients=["ingredient1"],
        steps=["step1"]
    )
    recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
    
    meal_date_str = date.today().strftime('%Y-%m-%d')
    
    # Test valid meal time - should succeed
    valid_meal_plan_data = MealPlanCreate(
        recipe_id=recipe.id,
        meal_date=meal_date_str,
        meal_time=valid_meal_time
    )
    
    valid_meal_plan = MealPlanner.create_meal_plan(db, user.id, valid_meal_plan_data)
    assert valid_meal_plan is not None, f"Valid meal time '{valid_meal_time}' should be accepted"
    assert valid_meal_plan.meal_time == valid_meal_time, "Meal time should match input"
    
    # Test validation function directly
    assert MealPlanner.validate_meal_time(valid_meal_time) is True, \
        f"Valid meal time '{valid_meal_time}' should pass validation"
    assert MealPlanner.validate_meal_time(invalid_meal_time) is False, \
        f"Invalid meal time '{invalid_meal_time}' should fail validation"


# Feature: recipe-saver-enhancements, Property 29: Meal plan template application
@given(
    num_items=st.integers(min_value=1, max_value=5),
    start_date_offset=st.integers(min_value=0, max_value=30)
)
@hyp_settings(max_examples=50, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_meal_plan_template_application_property(db, num_items, start_date_offset):
    """
    Property 29: Meal plan template application
    
    Applying a meal plan template to a start date should create meal plan entries
    for all template items with dates offset from the start date.
    
    **Validates: Requirements 16.2**
    """
    from app.services.meal_plan_service import MealPlanner
    from app.services.recipe_service import RecipeManager
    from app.services.auth_service import AuthService
    from app.schemas import TemplateCreate, TemplateItemCreate, RecipeCreate
    
    # Create a test user
    unique_username = f"tempuser_{uuid.uuid4().hex[:8]}"
    user = AuthService.create_user(db, unique_username, "password123")
    
    # Create recipes for template items
    recipes = []
    for i in range(num_items):
        recipe_data = RecipeCreate(
            title=f"Recipe {i}",
            ingredients=[f"ingredient{i}"],
            steps=[f"step{i}"]
        )
        recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
        recipes.append(recipe)
    
    # Create template items with different day offsets
    template_items = []
    meal_times = ['breakfast', 'lunch', 'dinner', 'snack']
    for i, recipe in enumerate(recipes):
        item = TemplateItemCreate(
            recipe_id=recipe.id,
            day_offset=i,  # Each item on a different day
            meal_time=meal_times[i % len(meal_times)]
        )
        template_items.append(item)
    
    # Create template
    template_data = TemplateCreate(
        name="Test Template",
        description="Test template description",
        items=template_items
    )
    
    template = MealPlanner.create_template(db, user.id, template_data)
    assert template is not None, "Template should be created successfully"
    
    # Apply template to a start date
    start_date = date.today() + timedelta(days=start_date_offset)
    created_count = MealPlanner.apply_template(db, template.id, user.id, start_date)
    
    assert created_count == num_items, \
        f"Should create {num_items} meal plans from template"
    
    # Verify meal plans were created with correct dates
    end_date = start_date + timedelta(days=num_items)
    meal_plans = MealPlanner.get_meal_plans(db, user.id, start_date, end_date)
    
    assert len(meal_plans) >= num_items, \
        f"Should retrieve at least {num_items} meal plans"
    
    # Verify each template item resulted in a meal plan with correct offset
    for i, item in enumerate(template_items):
        expected_date = start_date + timedelta(days=item.day_offset)
        matching_plans = [
            mp for mp in meal_plans
            if mp.recipe_id == item.recipe_id and
               mp.meal_date == expected_date and
               mp.meal_time == item.meal_time
        ]
        assert len(matching_plans) > 0, \
            f"Should find meal plan for template item {i} on day offset {item.day_offset}"


# Feature: recipe-saver-enhancements, Property 30: iCal export format correctness
@given(
    num_meal_plans=st.integers(min_value=1, max_value=5),
    date_range_days=st.integers(min_value=1, max_value=7)
)
@hyp_settings(max_examples=50, deadline=timedelta(milliseconds=5000), suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_ical_export_format_correctness_property(db, num_meal_plans, date_range_days):
    """
    Property 30: iCal export format correctness
    
    Exporting meal plans to iCal should produce a valid iCal file containing
    events with recipe titles, meal times, and 1-hour durations.
    
    **Validates: Requirements 17.1, 17.2, 17.3**
    """
    from app.services.meal_plan_service import MealPlanner
    from app.services.recipe_service import RecipeManager
    from app.services.auth_service import AuthService
    from app.schemas import MealPlanCreate, RecipeCreate
    
    # Create a test user
    unique_username = f"icaluser_{uuid.uuid4().hex[:8]}"
    user = AuthService.create_user(db, unique_username, "password123")
    
    # Create recipes and meal plans
    start_date = date.today()
    meal_times = ['breakfast', 'lunch', 'dinner', 'snack']
    created_plans = []
    
    for i in range(num_meal_plans):
        # Create a recipe
        recipe_data = RecipeCreate(
            title=f"Recipe {i}",
            ingredients=[f"ingredient{i}"],
            steps=[f"step{i}"]
        )
        recipe = RecipeManager.create_recipe(db, user.id, recipe_data)
        
        # Create meal plan
        meal_date = start_date + timedelta(days=i % date_range_days)
        meal_plan_data = MealPlanCreate(
            recipe_id=recipe.id,
            meal_date=meal_date.strftime('%Y-%m-%d'),
            meal_time=meal_times[i % len(meal_times)]
        )
        
        meal_plan = MealPlanner.create_meal_plan(db, user.id, meal_plan_data)
        created_plans.append((meal_plan, recipe))
    
    # Export to iCal
    end_date = start_date + timedelta(days=date_range_days)
    
    try:
        ical_content = MealPlanner.export_to_ical(db, user.id, start_date, end_date)
    except ImportError:
        pytest.skip("icalendar library not installed")
    
    assert ical_content is not None, "iCal content should be generated"
    assert isinstance(ical_content, bytes), "iCal content should be bytes"
    assert len(ical_content) > 0, "iCal content should not be empty"
    
    # Parse the iCal content to verify format
    from icalendar import Calendar
    
    cal = Calendar.from_ical(ical_content)
    
    # Verify calendar properties
    assert cal.get('prodid') is not None, "Calendar should have PRODID"
    assert cal.get('version') == '2.0', "Calendar should be version 2.0"
    
    # Count events
    events = [component for component in cal.walk() if component.name == "VEVENT"]
    assert len(events) == num_meal_plans, \
        f"Should have {num_meal_plans} events in calendar"
    
    # Verify each event has required properties
    for event in events:
        assert event.get('summary') is not None, "Event should have summary"
        assert event.get('dtstart') is not None, "Event should have start time"
        assert event.get('dtend') is not None, "Event should have end time"
        
        # Verify 1-hour duration
        dtstart = event.get('dtstart').dt
        dtend = event.get('dtend').dt
        duration = dtend - dtstart
        assert duration == timedelta(hours=1), "Event should have 1-hour duration"
        
        # Verify summary contains meal time
        summary = str(event.get('summary'))
        assert any(meal_time.capitalize() in summary for meal_time in meal_times), \
            "Event summary should contain meal time"
