from fastapi import APIRouter, Depends, HTTPException, status, Header
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Dict, Optional
from datetime import date
from app.database import mongodb
from app.schemas import (
    NutritionCreate, NutritionUpdate, NutritionResponse,
    DietaryLabelsRequest, AllergensRequest, NutritionSummaryResponse
)
from app.services.nutrition_service import NutritionTracker
from app.services.auth_service import AuthService
from app.utils.objectid_utils import validate_objectid
from app.repositories.recipe_repository import RecipeRepository
from app.repositories.meal_plan_repository import MealPlanRepository

router = APIRouter(prefix="/api", tags=["nutrition"])


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
# Nutrition Facts Endpoints (Task 16.1)
# ============================================================================

@router.post("/recipes/{recipe_id}/nutrition", response_model=NutritionResponse, status_code=status.HTTP_201_CREATED)
async def add_nutrition_facts(
    recipe_id: str,
    nutrition_data: NutritionCreate,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """
    Add nutrition facts to a recipe.
    Requirements: 24.1, 24.4, 25.3
    """
    # Validate ObjectId
    validate_objectid(recipe_id, "recipe_id")
    
    # Initialize repositories
    recipe_repository = RecipeRepository(db)
    meal_plan_repository = MealPlanRepository(db)
    nutrition_tracker = NutritionTracker(recipe_repository, meal_plan_repository)
    
    # Add nutrition facts
    recipe = await nutrition_tracker.add_nutrition_facts(recipe_id, nutrition_data, user_id)
    
    if not recipe:
        # Check if recipe exists and belongs to user
        recipe_doc = await recipe_repository.find_by_id(recipe_id)
        
        if not recipe_doc or str(recipe_doc["user_id"]) != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found or you don't have permission",
                headers={"error_code": "RECIPE_NOT_FOUND"}
            )
        
        # Validation failed (negative values)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nutrition values must be non-negative",
            headers={"error_code": "INVALID_NUTRITION_VALUES"}
        )
    
    # Return nutrition facts from the recipe
    return recipe.get("nutrition_facts")


@router.put("/recipes/{recipe_id}/nutrition", response_model=NutritionResponse)
async def update_nutrition_facts(
    recipe_id: str,
    nutrition_data: NutritionUpdate,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """
    Update nutrition facts for a recipe.
    Requirements: 24.1, 24.4, 25.3
    """
    # Validate ObjectId
    validate_objectid(recipe_id, "recipe_id")
    
    # Initialize repositories
    recipe_repository = RecipeRepository(db)
    meal_plan_repository = MealPlanRepository(db)
    nutrition_tracker = NutritionTracker(recipe_repository, meal_plan_repository)
    
    # Update nutrition facts
    recipe = await nutrition_tracker.update_nutrition_facts(recipe_id, nutrition_data, user_id)
    
    if not recipe:
        # Check if recipe exists and belongs to user
        recipe_doc = await recipe_repository.find_by_id(recipe_id)
        
        if not recipe_doc or str(recipe_doc["user_id"]) != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found or you don't have permission",
                headers={"error_code": "RECIPE_NOT_FOUND"}
            )
        
        # Nutrition facts don't exist or validation failed
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nutrition values must be non-negative",
            headers={"error_code": "INVALID_NUTRITION_VALUES"}
        )
    
    return recipe.get("nutrition_facts")


@router.get("/recipes/{recipe_id}/nutrition")
async def get_nutrition_facts(
    recipe_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get nutrition facts for a recipe (total and per-serving).
    Requirements: 24.1, 24.4, 25.3
    """
    # Validate ObjectId
    validate_objectid(recipe_id, "recipe_id")
    
    # Initialize repositories
    recipe_repository = RecipeRepository(db)
    meal_plan_repository = MealPlanRepository(db)
    nutrition_tracker = NutritionTracker(recipe_repository, meal_plan_repository)
    
    # Verify recipe exists and belongs to user
    recipe = await recipe_repository.find_by_id(recipe_id)
    
    if not recipe or str(recipe["user_id"]) != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found or you don't have permission",
            headers={"error_code": "RECIPE_NOT_FOUND"}
        )
    
    # Get nutrition facts
    nutrition = await nutrition_tracker.get_nutrition_facts(recipe_id)
    
    if not nutrition:
        return {
            "nutrition_facts": None,
            "per_serving": None
        }
    
    # Calculate per-serving values
    servings = recipe.get("servings", 1) or 1
    per_serving = nutrition_tracker.calculate_per_serving(nutrition, servings)
    
    return {
        "nutrition_facts": nutrition,
        "per_serving": per_serving
    }


# ============================================================================
# Dietary Labels and Allergen Endpoints (Task 16.2)
# ============================================================================

@router.post("/recipes/{recipe_id}/dietary-labels")
async def set_dietary_labels(
    recipe_id: str,
    labels_data: DietaryLabelsRequest,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """
    Set dietary labels for a recipe.
    Requirements: 26.1, 27.1
    """
    # Validate ObjectId
    validate_objectid(recipe_id, "recipe_id")
    
    # Initialize repositories
    recipe_repository = RecipeRepository(db)
    meal_plan_repository = MealPlanRepository(db)
    nutrition_tracker = NutritionTracker(recipe_repository, meal_plan_repository)
    
    # Add dietary labels
    labels = await nutrition_tracker.add_dietary_labels(recipe_id, labels_data.labels, user_id)
    
    if labels is None:
        # Check if recipe exists and belongs to user
        recipe = await recipe_repository.find_by_id(recipe_id)
        
        if not recipe or str(recipe["user_id"]) != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found or you don't have permission",
                headers={"error_code": "RECIPE_NOT_FOUND"}
            )
        
        # Invalid label
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid dietary label. Valid labels: {', '.join(NutritionTracker.VALID_DIETARY_LABELS)}",
            headers={"error_code": "INVALID_DIETARY_LABEL"}
        )
    
    return {"labels": labels}


@router.post("/recipes/{recipe_id}/allergens")
async def set_allergen_warnings(
    recipe_id: str,
    allergens_data: AllergensRequest,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """
    Set allergen warnings for a recipe.
    Requirements: 26.1, 27.1
    """
    # Validate ObjectId
    validate_objectid(recipe_id, "recipe_id")
    
    # Initialize repositories
    recipe_repository = RecipeRepository(db)
    meal_plan_repository = MealPlanRepository(db)
    nutrition_tracker = NutritionTracker(recipe_repository, meal_plan_repository)
    
    # Add allergen warnings
    allergens = await nutrition_tracker.add_allergen_warnings(recipe_id, allergens_data.allergens, user_id)
    
    if allergens is None:
        # Check if recipe exists and belongs to user
        recipe = await recipe_repository.find_by_id(recipe_id)
        
        if not recipe or str(recipe["user_id"]) != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found or you don't have permission",
                headers={"error_code": "RECIPE_NOT_FOUND"}
            )
        
        # Invalid allergen
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid allergen. Valid allergens: {', '.join(NutritionTracker.VALID_ALLERGENS)}",
            headers={"error_code": "INVALID_ALLERGEN"}
        )
    
    return {"allergens": allergens}


# ============================================================================
# Meal Plan Nutrition Summary Endpoint (Task 16.3)
# ============================================================================

@router.get("/meal-plans/nutrition-summary")
async def get_meal_plan_nutrition_summary(
    start_date: str,
    end_date: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get nutrition summary for a meal plan date range.
    Requirements: 28.1, 28.2, 28.3, 28.4
    """
    # Parse dates
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD",
            headers={"error_code": "INVALID_DATE_FORMAT"}
        )
    
    # Validate date range
    if start > end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be before or equal to end_date",
            headers={"error_code": "INVALID_DATE_RANGE"}
        )
    
    # Initialize repositories
    recipe_repository = RecipeRepository(db)
    meal_plan_repository = MealPlanRepository(db)
    nutrition_tracker = NutritionTracker(recipe_repository, meal_plan_repository)
    
    # Get nutrition summary
    summary = await nutrition_tracker.get_meal_plan_nutrition_summary(user_id, start, end)
    
    return summary
