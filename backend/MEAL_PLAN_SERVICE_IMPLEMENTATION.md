# Meal Plan Service Implementation Summary

## Task 10: Implement meal planning service

### Completed Sub-tasks

#### 10.1 Create MealPlanner service class ✓
**File:** `backend/app/services/meal_plan_service.py`

**Implemented Methods:**
- `validate_meal_time(meal_time: str) -> bool` - Validates meal_time values (breakfast, lunch, dinner, snack)
- `create_meal_plan(db, user_id, meal_plan_data) -> Optional[MealPlan]` - Creates new meal plan with validation
- `get_meal_plans(db, user_id, start_date, end_date) -> List[MealPlan]` - Retrieves meal plans by date range
- `update_meal_plan(db, meal_plan_id, user_id, meal_plan_data) -> Optional[MealPlan]` - Updates existing meal plan
- `delete_meal_plan(db, meal_plan_id, user_id) -> bool` - Deletes meal plan with ownership validation

**Validation:**
- Meal time must be one of: breakfast, lunch, dinner, snack
- Date format must be YYYY-MM-DD
- Recipe must exist and belong to user
- User ownership verified for all operations

**Requirements Satisfied:** 14.2, 14.3, 14.4

#### 10.2 Implement meal plan template methods ✓
**File:** `backend/app/services/meal_plan_service.py`

**Implemented Methods:**
- `create_template(db, user_id, template_data) -> Optional[MealPlanTemplate]` - Creates template with items
- `get_user_templates(db, user_id) -> List[MealPlanTemplate]` - Retrieves user's templates
- `apply_template(db, template_id, user_id, start_date) -> Optional[int]` - Applies template to create meal plans
- `delete_template(db, template_id, user_id) -> bool` - Deletes template with cascading

**Features:**
- Templates store multiple meal plan items with day offsets
- Template application creates meal plans starting from specified date
- Day offset allows flexible template patterns (e.g., 7-day weekly plan)
- All template items validated before creation

**Requirements Satisfied:** 16.1, 16.2, 16.4

#### 10.3 Implement iCal export functionality ✓
**File:** `backend/app/services/meal_plan_service.py`

**Implemented Methods:**
- `export_to_ical(db, user_id, start_date, end_date) -> bytes` - Exports meal plans to iCal format

**Features:**
- Generates RFC 5545 compliant iCalendar format
- Creates events with recipe titles and meal times
- Sets 1-hour duration for each meal event
- Maps meal times to appropriate hours:
  - breakfast: 8:00 AM
  - lunch: 12:00 PM
  - snack: 3:00 PM
  - dinner: 6:00 PM
- Returns iCal data as bytes for download

**Dependencies:**
- Added `icalendar>=5.0.0` to `backend/requirements.txt`
- Library provides Calendar and Event classes for iCal generation

**Requirements Satisfied:** 17.1, 17.2, 17.3

### Testing

**Test File:** `backend/tests/test_meal_plan_service.py`

**Test Coverage:**
1. **TestMealPlannerBasics** - 11 tests
   - Meal time validation
   - Create meal plan (success, invalid meal time, invalid date, nonexistent recipe)
   - Get meal plans by date range
   - Update meal plan (success, invalid meal time)
   - Delete meal plan (success, not found)

2. **TestMealPlanTemplates** - 8 tests
   - Create template (success, invalid meal time, nonexistent recipe)
   - Get user templates
   - Apply template (success, not found)
   - Delete template (success, not found)

3. **TestICalExport** - 2 tests
   - Export to iCal (success, empty range)
   - Validates iCal format and content

**Total:** 21 unit tests covering all service methods

### Code Quality

- ✓ No syntax errors (verified with getDiagnostics)
- ✓ Follows existing service patterns (similar to CollectionManager, RatingSystem)
- ✓ Proper error handling with Optional return types
- ✓ User ownership validation on all operations
- ✓ Input validation for meal times and dates
- ✓ Type hints for all methods
- ✓ Comprehensive docstrings

### Integration Points

**Models Used:**
- `MealPlan` - Main meal plan entries
- `MealPlanTemplate` - Template definitions
- `MealPlanTemplateItem` - Template items with day offsets
- `Recipe` - Recipe references
- `User` - User ownership

**Schemas Used:**
- `MealPlanCreate` - Create meal plan request
- `MealPlanUpdate` - Update meal plan request
- `TemplateCreate` - Create template request
- `TemplateItemCreate` - Template item definition

### Next Steps

To complete the meal planning feature, the following tasks remain:

1. **Task 11.1** - Create meal plan CRUD API endpoints
2. **Task 11.2** - Create meal plan template API endpoints
3. **Task 11.3** - Create iCal export API endpoint
4. **Task 11.4** - Write property tests for meal planning

### Installation Instructions

To use the iCal export functionality, ensure icalendar is installed:

```bash
cd backend
pip install icalendar>=5.0.0
```

Or install all requirements:

```bash
cd backend
pip install -r requirements.txt
```

### Usage Example

```python
from app.services.meal_plan_service import MealPlanner
from app.schemas import MealPlanCreate
from datetime import date

# Create meal plan
meal_plan_data = MealPlanCreate(
    recipe_id=1,
    meal_date="2024-01-15",
    meal_time="breakfast"
)
meal_plan = MealPlanner.create_meal_plan(db, user_id=1, meal_plan_data=meal_plan_data)

# Get meal plans for a week
start_date = date(2024, 1, 15)
end_date = date(2024, 1, 21)
meal_plans = MealPlanner.get_meal_plans(db, user_id=1, start_date=start_date, end_date=end_date)

# Export to iCal
ical_data = MealPlanner.export_to_ical(db, user_id=1, start_date=start_date, end_date=end_date)
with open('meal_plan.ics', 'wb') as f:
    f.write(ical_data)
```
