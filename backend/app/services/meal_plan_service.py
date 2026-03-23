from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from datetime import date, datetime, timedelta
from app.models import MealPlan, MealPlanTemplate, MealPlanTemplateItem, Recipe
from app.schemas import MealPlanCreate, MealPlanUpdate, TemplateCreate


class MealPlanner:
    """Service for managing meal plans and templates."""
    
    # Valid meal time values
    VALID_MEAL_TIMES = {'breakfast', 'lunch', 'dinner', 'snack'}
    
    @staticmethod
    def validate_meal_time(meal_time: str) -> bool:
        """Validate that meal_time is one of the allowed values."""
        return meal_time in MealPlanner.VALID_MEAL_TIMES
    
    @staticmethod
    def create_meal_plan(db: Session, user_id: int, meal_plan_data: MealPlanCreate) -> Optional[MealPlan]:
        """
        Create a new meal plan entry.
        Validates meal_time and recipe existence.
        Returns None if validation fails.
        """
        # Validate meal_time
        if not MealPlanner.validate_meal_time(meal_plan_data.meal_time):
            return None
        
        # Verify recipe exists and belongs to user
        recipe = db.query(Recipe).filter(
            Recipe.id == meal_plan_data.recipe_id,
            Recipe.user_id == user_id
        ).first()
        
        if not recipe:
            return None
        
        # Parse meal_date string to date object
        try:
            meal_date = datetime.strptime(meal_plan_data.meal_date, '%Y-%m-%d').date()
        except ValueError:
            return None
        
        # Create meal plan
        meal_plan = MealPlan(
            user_id=user_id,
            recipe_id=meal_plan_data.recipe_id,
            meal_date=meal_date,
            meal_time=meal_plan_data.meal_time
        )
        db.add(meal_plan)
        db.commit()
        db.refresh(meal_plan)
        return meal_plan
    
    @staticmethod
    def get_meal_plans(db: Session, user_id: int, start_date: date, end_date: date) -> List[MealPlan]:
        """
        Get all meal plans for a user within a date range.
        Returns meal plans ordered by date and meal time.
        """
        return db.query(MealPlan).filter(
            MealPlan.user_id == user_id,
            MealPlan.meal_date >= start_date,
            MealPlan.meal_date <= end_date
        ).order_by(MealPlan.meal_date, MealPlan.meal_time).all()
    
    @staticmethod
    def update_meal_plan(
        db: Session, 
        meal_plan_id: int, 
        user_id: int, 
        meal_plan_data: MealPlanUpdate
    ) -> Optional[MealPlan]:
        """
        Update an existing meal plan.
        Validates user ownership and meal_time if provided.
        Returns None if meal plan doesn't exist or validation fails.
        """
        # Find meal plan and verify ownership
        meal_plan = db.query(MealPlan).filter(
            MealPlan.id == meal_plan_id,
            MealPlan.user_id == user_id
        ).first()
        
        if not meal_plan:
            return None
        
        # Update meal_date if provided
        if meal_plan_data.meal_date is not None:
            try:
                meal_date = datetime.strptime(meal_plan_data.meal_date, '%Y-%m-%d').date()
                meal_plan.meal_date = meal_date
            except ValueError:
                return None
        
        # Update meal_time if provided
        if meal_plan_data.meal_time is not None:
            if not MealPlanner.validate_meal_time(meal_plan_data.meal_time):
                return None
            meal_plan.meal_time = meal_plan_data.meal_time
        
        db.commit()
        db.refresh(meal_plan)
        return meal_plan
    
    @staticmethod
    def delete_meal_plan(db: Session, meal_plan_id: int, user_id: int) -> bool:
        """
        Delete a meal plan.
        Validates user ownership.
        Returns True if deleted, False if not found.
        """
        meal_plan = db.query(MealPlan).filter(
            MealPlan.id == meal_plan_id,
            MealPlan.user_id == user_id
        ).first()
        
        if not meal_plan:
            return False
        
        db.delete(meal_plan)
        db.commit()
        return True
    
    @staticmethod
    def create_template(db: Session, user_id: int, template_data: TemplateCreate) -> Optional[MealPlanTemplate]:
        """
        Create a new meal plan template with items.
        Validates all template items before creation.
        Returns None if validation fails.
        """
        # Validate all template items
        for item in template_data.items:
            # Validate meal_time
            if not MealPlanner.validate_meal_time(item.meal_time):
                return None
            
            # Verify recipe exists and belongs to user
            recipe = db.query(Recipe).filter(
                Recipe.id == item.recipe_id,
                Recipe.user_id == user_id
            ).first()
            
            if not recipe:
                return None
        
        # Create template
        template = MealPlanTemplate(
            user_id=user_id,
            name=template_data.name,
            description=template_data.description
        )
        db.add(template)
        db.flush()  # Get template ID without committing
        
        # Create template items
        for item in template_data.items:
            template_item = MealPlanTemplateItem(
                template_id=template.id,
                recipe_id=item.recipe_id,
                day_offset=item.day_offset,
                meal_time=item.meal_time
            )
            db.add(template_item)
        
        db.commit()
        db.refresh(template)
        return template
    
    @staticmethod
    def get_user_templates(db: Session, user_id: int) -> List[MealPlanTemplate]:
        """Get all meal plan templates for a user."""
        return db.query(MealPlanTemplate).filter(
            MealPlanTemplate.user_id == user_id
        ).all()
    
    @staticmethod
    def apply_template(
        db: Session, 
        template_id: int, 
        user_id: int, 
        start_date: date
    ) -> Optional[int]:
        """
        Apply a meal plan template starting from a specific date.
        Creates meal plan entries for all template items with date offset.
        Returns count of meal plans created, or None if template not found.
        """
        # Verify template exists and belongs to user
        template = db.query(MealPlanTemplate).filter(
            MealPlanTemplate.id == template_id,
            MealPlanTemplate.user_id == user_id
        ).first()
        
        if not template:
            return None
        
        # Get template items
        template_items = db.query(MealPlanTemplateItem).filter(
            MealPlanTemplateItem.template_id == template_id
        ).all()
        
        created_count = 0
        
        # Create meal plans from template items
        for item in template_items:
            meal_date = start_date + timedelta(days=item.day_offset)
            
            meal_plan = MealPlan(
                user_id=user_id,
                recipe_id=item.recipe_id,
                meal_date=meal_date,
                meal_time=item.meal_time
            )
            db.add(meal_plan)
            created_count += 1
        
        db.commit()
        return created_count
    
    @staticmethod
    def delete_template(db: Session, template_id: int, user_id: int) -> bool:
        """
        Delete a meal plan template.
        Validates user ownership.
        Cascading delete will remove template items.
        Returns True if deleted, False if not found.
        """
        template = db.query(MealPlanTemplate).filter(
            MealPlanTemplate.id == template_id,
            MealPlanTemplate.user_id == user_id
        ).first()
        
        if not template:
            return False
        
        db.delete(template)
        db.commit()
        return True
    
    @staticmethod
    def export_to_ical(db: Session, user_id: int, start_date: date, end_date: date) -> bytes:
        """
        Export meal plans to iCal format.
        Generates calendar events for each meal plan with 1-hour duration.
        Returns iCal file content as bytes.
        """
        try:
            from icalendar import Calendar, Event
        except ImportError:
            raise ImportError("icalendar library is required for iCal export. Install with: pip install icalendar")
        
        # Get meal plans for date range
        meal_plans = MealPlanner.get_meal_plans(db, user_id, start_date, end_date)
        
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
            recipe = db.query(Recipe).filter(Recipe.id == meal_plan.recipe_id).first()
            
            if not recipe:
                continue
            
            event = Event()
            event.add('summary', f"{meal_plan.meal_time.capitalize()}: {recipe.title}")
            event.add('description', f"Meal: {meal_plan.meal_time}")
            
            # Set event time based on meal_time
            hour = meal_time_hours.get(meal_plan.meal_time, 12)
            start_datetime = datetime.combine(meal_plan.meal_date, datetime.min.time().replace(hour=hour))
            end_datetime = start_datetime + timedelta(hours=1)
            
            event.add('dtstart', start_datetime)
            event.add('dtend', end_datetime)
            event.add('dtstamp', datetime.now())
            
            cal.add_component(event)
        
        return cal.to_ical()
