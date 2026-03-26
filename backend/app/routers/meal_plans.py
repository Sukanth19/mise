from fastapi import APIRouter, Depends, HTTPException, status, Header, Query, Response
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from datetime import datetime, date
from app.database import mongodb
from app.schemas import (
    MealPlanCreate, 
    MealPlanUpdate, 
    MealPlanResponse,
    TemplateCreate,
    TemplateResponse,
    TemplateItemResponse
)
from app.services.meal_plan_service import MealPlanner
from app.services.auth_service import AuthService
from app.utils.objectid_utils import validate_objectid

router = APIRouter(prefix="/api/meal-plans", tags=["meal-plans"])
template_router = APIRouter(prefix="/api/meal-plan-templates", tags=["meal-plan-templates"])


async def get_mongodb() -> AsyncIOMotorDatabase:
    """Get MongoDB database instance."""
    return await mongodb.get_database()


async def get_current_user_id(authorization: str = Header(...)) -> str:
    """Extract and verify user ID from JWT token."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"error_code": "INVALID_AUTH_HEADER"}
        )
    
    token = authorization.replace("Bearer ", "")
    user_id = AuthService.verify_token(token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"error_code": "INVALID_TOKEN"}
        )
    
    return user_id


# ============================================================================
# Meal Plan CRUD Endpoints (Subtask 11.1)
# ============================================================================

@router.post("", response_model=MealPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_meal_plan(
    meal_plan_data: MealPlanCreate,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """Create a new meal plan entry."""
    meal_plan = MealPlanner.create_meal_plan(db, user_id, meal_plan_data)
    
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid meal plan data. Check meal_time, meal_date format, and recipe ownership.",
            headers={"error_code": "INVALID_MEAL_PLAN"}
        )
    
    # Convert meal_date to string for response
    return MealPlanResponse(
        id=meal_plan.id,
        user_id=meal_plan.user_id,
        recipe_id=meal_plan.recipe_id,
        meal_date=meal_plan.meal_date.strftime('%Y-%m-%d'),
        meal_time=meal_plan.meal_time,
        created_at=meal_plan.created_at
    )


@router.get("", response_model=List[MealPlanResponse])
async def get_meal_plans(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """Get meal plans for a date range."""
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD.",
            headers={"error_code": "INVALID_DATE_FORMAT"}
        )
    
    meal_plans = MealPlanner.get_meal_plans(db, user_id, start, end)
    
    # Convert meal_date to string for response
    return [
        MealPlanResponse(
            id=mp.id,
            user_id=mp.user_id,
            recipe_id=mp.recipe_id,
            meal_date=mp.meal_date.strftime('%Y-%m-%d'),
            meal_time=mp.meal_time,
            created_at=mp.created_at
        )
        for mp in meal_plans
    ]


@router.put("/{meal_plan_id}", response_model=MealPlanResponse)
async def update_meal_plan(
    meal_plan_id: str,
    meal_plan_data: MealPlanUpdate,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """Update an existing meal plan (for drag-and-drop)."""
    # Validate ObjectId
    validate_objectid(meal_plan_id, "meal_plan_id")
    meal_plan = MealPlanner.update_meal_plan(db, meal_plan_id, user_id, meal_plan_data)
    
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found or access denied",
            headers={"error_code": "MEAL_PLAN_NOT_FOUND"}
        )
    
    # Convert meal_date to string for response
    return MealPlanResponse(
        id=meal_plan.id,
        user_id=meal_plan.user_id,
        recipe_id=meal_plan.recipe_id,
        meal_date=meal_plan.meal_date.strftime('%Y-%m-%d'),
        meal_time=meal_plan.meal_time,
        created_at=meal_plan.created_at
    )


@router.delete("/{meal_plan_id}", status_code=status.HTTP_200_OK)
async def delete_meal_plan(
    meal_plan_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """Delete a meal plan entry."""
    # Validate ObjectId
    validate_objectid(meal_plan_id, "meal_plan_id")
    success = MealPlanner.delete_meal_plan(db, meal_plan_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found or access denied",
            headers={"error_code": "MEAL_PLAN_NOT_FOUND"}
        )
    
    return {"message": "Meal plan deleted successfully"}


# ============================================================================
# Meal Plan Template Endpoints (Subtask 11.2)
# ============================================================================

@template_router.post("", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TemplateCreate,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """Create a new meal plan template."""
    template = MealPlanner.create_template(db, user_id, template_data)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid template data. Check meal_time values and recipe ownership.",
            headers={"error_code": "INVALID_TEMPLATE"}
        )
    
    # Get template items
    template_items = db.query(MealPlanTemplateItem).filter(
        MealPlanTemplateItem.template_id == template.id
    ).all()
    
    items_response = [
        TemplateItemResponse(
            id=item.id,
            template_id=item.template_id,
            recipe_id=item.recipe_id,
            day_offset=item.day_offset,
            meal_time=item.meal_time
        )
        for item in template_items
    ]
    
    return TemplateResponse(
        id=template.id,
        user_id=template.user_id,
        name=template.name,
        description=template.description,
        items=items_response,
        created_at=template.created_at
    )


@template_router.get("", response_model=List[TemplateResponse])
async def get_templates(
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """Get all meal plan templates for the authenticated user."""
    templates = MealPlanner.get_user_templates(db, user_id)
    
    result = []
    for template in templates:
        # Get template items
        template_items = db.query(MealPlanTemplateItem).filter(
            MealPlanTemplateItem.template_id == template.id
        ).all()
        
        items_response = [
            TemplateItemResponse(
                id=item.id,
                template_id=item.template_id,
                recipe_id=item.recipe_id,
                day_offset=item.day_offset,
                meal_time=item.meal_time
            )
            for item in template_items
        ]
        
        result.append(TemplateResponse(
            id=template.id,
            user_id=template.user_id,
            name=template.name,
            description=template.description,
            items=items_response,
            created_at=template.created_at
        ))
    
    return result


@template_router.post("/{template_id}/apply")
async def apply_template(
    template_id: str,
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """Apply a meal plan template to a date range."""
    # Validate ObjectId
    validate_objectid(template_id, "template_id")
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD.",
            headers={"error_code": "INVALID_DATE_FORMAT"}
        )
    
    created_count = MealPlanner.apply_template(db, template_id, user_id, start)
    
    if created_count is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found or access denied",
            headers={"error_code": "TEMPLATE_NOT_FOUND"}
        )
    
    return {"created_count": created_count}


@template_router.delete("/{template_id}", status_code=status.HTTP_200_OK)
async def delete_template(
    template_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """Delete a meal plan template."""
    # Validate ObjectId
    validate_objectid(template_id, "template_id")
    success = MealPlanner.delete_template(db, template_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found or access denied",
            headers={"error_code": "TEMPLATE_NOT_FOUND"}
        )
    
    return {"message": "Template deleted successfully"}


# ============================================================================
# iCal Export Endpoint (Subtask 11.3)
# ============================================================================

@router.get("/export")
async def export_meal_plans(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """Export meal plans to iCal format."""
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD.",
            headers={"error_code": "INVALID_DATE_FORMAT"}
        )
    
    try:
        ical_content = MealPlanner.export_to_ical(db, user_id, start, end)
    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
            headers={"error_code": "ICALENDAR_NOT_INSTALLED"}
        )
    
    # Generate filename with date range
    filename = f"meal_plan_{start_date}_to_{end_date}.ics"
    
    return Response(
        content=ical_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
