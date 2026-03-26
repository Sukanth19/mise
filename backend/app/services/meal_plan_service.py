from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from bson import ObjectId
from app.repositories.meal_plan_repository import MealPlanRepository
from app.repositories.meal_plan_template_repository import MealPlanTemplateRepository
from app.repositories.recipe_repository import RecipeRepository
from app.schemas import MealPlanCreate, MealPlanUpdate, TemplateCreate


class MealPlanner:
    """Service for managing meal plans and templates."""
    
    # Valid meal time values
    VALID_MEAL_TIMES = {'breakfast', 'lunch', 'dinner', 'snack'}
    
    def __init__(
        self,
        meal_plan_repository: MealPlanRepository,
        template_repository: MealPlanTemplateRepository,
        recipe_repository: RecipeRepository
    ):
        """
        Initialize meal planner with repositories.
        
        Args:
            meal_plan_repository: MealPlanRepository instance for data access
            template_repository: MealPlanTemplateRepository instance for template data access
            recipe_repository: RecipeRepository instance for recipe validation
        """
        self.meal_plan_repository = meal_plan_repository
        self.template_repository = template_repository
        self.recipe_repository = recipe_repository
    
    @staticmethod
    def validate_meal_time(meal_time: str) -> bool:
        """Validate that meal_time is one of the allowed values."""
        return meal_time in MealPlanner.VALID_MEAL_TIMES
    
    async def create_meal_plan(self, user_id: str, meal_plan_data: MealPlanCreate) -> Optional[Dict[str, Any]]:
        """
        Create a new meal plan entry.
        Validates meal_time and recipe existence.
        
        Args:
            user_id: User's ObjectId as string
            meal_plan_data: Meal plan creation data
            
        Returns:
            Meal plan document if successful, None if validation fails
        """
        # Validate meal_time
        if not MealPlanner.validate_meal_time(meal_plan_data.meal_time):
            return None
        
        # Verify recipe exists and belongs to user
        recipe = await self.recipe_repository.find_by_id(meal_plan_data.recipe_id)
        
        if not recipe or str(recipe["user_id"]) != user_id:
            return None
        
        # Parse meal_date string to date object
        try:
            meal_date = datetime.strptime(meal_plan_data.meal_date, '%Y-%m-%d').date()
        except ValueError:
            return None
        
        # Create meal plan
        meal_plan_doc = {
            "user_id": ObjectId(user_id),
            "recipe_id": ObjectId(meal_plan_data.recipe_id),
            "meal_date": meal_date,
            "meal_time": meal_plan_data.meal_time,
            "created_at": datetime.utcnow()
        }
        meal_plan_id = await self.meal_plan_repository.create(meal_plan_doc)
        return await self.meal_plan_repository.find_by_id(meal_plan_id)
    
    async def get_meal_plans(self, user_id: str, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """
        Get all meal plans for a user within a date range.
        Returns meal plans ordered by date and meal time.
        
        Args:
            user_id: User's ObjectId as string
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            List of meal plan documents
        """
        return await self.meal_plan_repository.find_by_user_and_date_range(user_id, start_date, end_date)
    
    async def update_meal_plan(
        self, 
        meal_plan_id: str, 
        user_id: str, 
        meal_plan_data: MealPlanUpdate
    ) -> Optional[Dict[str, Any]]:
        """
        Update an existing meal plan.
        Validates user ownership and meal_time if provided.
        
        Args:
            meal_plan_id: Meal plan's ObjectId as string
            user_id: User's ObjectId as string
            meal_plan_data: Meal plan update data
            
        Returns:
            Updated meal plan document if successful, None if not found or validation fails
        """
        # Find meal plan and verify ownership
        meal_plan = await self.meal_plan_repository.find_by_id(meal_plan_id)
        
        if not meal_plan or str(meal_plan["user_id"]) != user_id:
            return None
        
        # Build update document
        update_doc = {}
        
        # Update meal_date if provided
        if meal_plan_data.meal_date is not None:
            try:
                meal_date = datetime.strptime(meal_plan_data.meal_date, '%Y-%m-%d').date()
                update_doc["meal_date"] = meal_date
            except ValueError:
                return None
        
        # Update meal_time if provided
        if meal_plan_data.meal_time is not None:
            if not MealPlanner.validate_meal_time(meal_plan_data.meal_time):
                return None
            update_doc["meal_time"] = meal_plan_data.meal_time
        
        if update_doc:
            await self.meal_plan_repository.update(meal_plan_id, update_doc)
        
        return await self.meal_plan_repository.find_by_id(meal_plan_id)
    
    async def delete_meal_plan(self, meal_plan_id: str, user_id: str) -> bool:
        """
        Delete a meal plan.
        Validates user ownership.
        
        Args:
            meal_plan_id: Meal plan's ObjectId as string
            user_id: User's ObjectId as string
            
        Returns:
            True if deleted, False if not found
        """
        meal_plan = await self.meal_plan_repository.find_by_id(meal_plan_id)
        
        if not meal_plan or str(meal_plan["user_id"]) != user_id:
            return False
        
        return await self.meal_plan_repository.delete(meal_plan_id)
    
    async def create_template(self, user_id: str, template_data: TemplateCreate) -> Optional[Dict[str, Any]]:
        """
        Create a new meal plan template with embedded items.
        Validates all template items before creation.
        
        Args:
            user_id: User's ObjectId as string
            template_data: Template creation data with items
            
        Returns:
            Template document if successful, None if validation fails
        """
        # Validate all template items
        items = []
        for item in template_data.items:
            # Validate meal_time
            if not MealPlanner.validate_meal_time(item.meal_time):
                return None
            
            # Verify recipe exists and belongs to user
            recipe = await self.recipe_repository.find_by_id(item.recipe_id)
            
            if not recipe or str(recipe["user_id"]) != user_id:
                return None
            
            items.append({
                "recipe_id": ObjectId(item.recipe_id),
                "day_offset": item.day_offset,
                "meal_time": item.meal_time
            })
        
        # Create template with embedded items
        template_doc = {
            "user_id": ObjectId(user_id),
            "name": template_data.name,
            "description": template_data.description,
            "items": items,
            "created_at": datetime.utcnow()
        }
        template_id = await self.template_repository.create(template_doc)
        return await self.template_repository.find_by_id(template_id)
    
    async def get_user_templates(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all meal plan templates for a user.
        
        Args:
            user_id: User's ObjectId as string
            
        Returns:
            List of template documents
        """
        return await self.template_repository.find_by_user(user_id)
    
    async def apply_template(
        self, 
        template_id: str, 
        user_id: str, 
        start_date: date
    ) -> Optional[int]:
        """
        Apply a meal plan template starting from a specific date.
        Creates meal plan entries for all template items with date offset.
        
        Args:
            template_id: Template's ObjectId as string
            user_id: User's ObjectId as string
            start_date: Starting date for the meal plan
            
        Returns:
            Count of meal plans created, or None if template not found
        """
        # Verify template exists and belongs to user
        template = await self.template_repository.find_by_id(template_id)
        
        if not template or str(template["user_id"]) != user_id:
            return None
        
        # Get template items (embedded in the template document)
        template_items = template.get("items", [])
        
        created_count = 0
        
        # Create meal plans from template items
        for item in template_items:
            meal_date = start_date + timedelta(days=item["day_offset"])
            
            meal_plan_doc = {
                "user_id": ObjectId(user_id),
                "recipe_id": item["recipe_id"],
                "meal_date": meal_date,
                "meal_time": item["meal_time"],
                "created_at": datetime.utcnow()
            }
            await self.meal_plan_repository.create(meal_plan_doc)
            created_count += 1
        
        return created_count
    
    async def delete_template(self, template_id: str, user_id: str) -> bool:
        """
        Delete a meal plan template.
        Validates user ownership.
        
        Args:
            template_id: Template's ObjectId as string
            user_id: User's ObjectId as string
            
        Returns:
            True if deleted, False if not found
        """
        template = await self.template_repository.find_by_id(template_id)
        
        if not template or str(template["user_id"]) != user_id:
            return False
        
        return await self.template_repository.delete(template_id)
    
    async def export_to_ical(self, user_id: str, start_date: date, end_date: date) -> bytes:
        """
        Export meal plans to iCal format.
        Generates calendar events for each meal plan with 1-hour duration.
        
        Args:
            user_id: User's ObjectId as string
            start_date: Start date for export
            end_date: End date for export
            
        Returns:
            iCal file content as bytes
            
        Raises:
            ImportError: If icalendar library is not installed
        """
        try:
            from icalendar import Calendar, Event
        except ImportError:
            raise ImportError("icalendar library is required for iCal export. Install with: pip install icalendar")
        
        # Get meal plans for date range
        meal_plans = await self.get_meal_plans(user_id, start_date, end_date)
        
        # Create calendar
        cal = Calendar()
        cal.add('prodid', '-//Recipe Saver Meal Planner//EN')
        cal.add('version', '2.0')
        
        # Meal time to hour mapping
        meal_time_hours = {
            'breakfast': 8,
            'lunch': 12,
            'dinner': 18,
            'snack': 15
        }
        
        # Create events for each meal plan
        for meal_plan in meal_plans:
            # Get recipe details
            recipe = await self.recipe_repository.find_by_id(str(meal_plan["recipe_id"]))
            
            if not recipe:
                continue
            
            event = Event()
            event.add('summary', f"{meal_plan['meal_time'].capitalize()}: {recipe['title']}")
            event.add('description', f"Meal: {meal_plan['meal_time']}")
            
            # Set event time based on meal_time
            hour = meal_time_hours.get(meal_plan['meal_time'], 12)
            start_datetime = datetime.combine(meal_plan['meal_date'], datetime.min.time().replace(hour=hour))
            end_datetime = start_datetime + timedelta(hours=1)
            
            event.add('dtstart', start_datetime)
            event.add('dtend', end_datetime)
            event.add('dtstamp', datetime.now())
            
            cal.add_component(event)
        
        return cal.to_ical()
