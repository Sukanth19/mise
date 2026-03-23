from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Dict, Optional
from datetime import date
from app.database import get_db
from app.schemas import (
    NutritionCreate, NutritionUpdate, NutritionResponse,
    DietaryLabelsRequest, AllergensRequest, NutritionSummaryResponse
)
from app.services.nutrition_service import NutritionTracker
from app.services.auth_service import AuthService
from app.models import Recipe

router = APIRouter(prefix="/api", tags=["nutrition"])


def get_current_user_id(authorization: str = Header(...)) -> int:
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
def add_nutrition_facts(
    recipe_id: int,
    nutrition_data: NutritionCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Add nutrition facts to a recipe.
    Requirements: 24.1, 24.4, 25.3
    """
    nutrition = NutritionTracker.add_nutrition_facts(db, recipe_id, nutrition_data, user_id)
    
    if not nutrition:
        # Check if recipe exists and belongs to user
        recipe = db.query(Recipe).filter(
            Recipe.id == recipe_id,
            Recipe.user_id == user_id
        ).first()
        
        if not recipe:
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
    
    return nutrition


@router.put("/recipes/{recipe_id}/nutrition", response_model=NutritionResponse)
def update_nutrition_facts(
    recipe_id: int,
    nutrition_data: NutritionUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Update nutrition facts for a recipe.
    Requirements: 24.1, 24.4, 25.3
    """
    nutrition = NutritionTracker.update_nutrition_facts(db, recipe_id, nutrition_data, user_id)
    
    if not nutrition:
        # Check if recipe exists and belongs to user
        recipe = db.query(Recipe).filter(
            Recipe.id == recipe_id,
            Recipe.user_id == user_id
        ).first()
        
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found or you don't have permission",
                headers={"error_code": "RECIPE_NOT_FOUND"}
            )
        
        # Nutrition facts don't exist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nutrition facts not found. Use POST to create.",
            headers={"error_code": "NUTRITION_NOT_FOUND"}
        )
    
    return nutrition


@router.get("/recipes/{recipe_id}/nutrition")
def get_nutrition_facts(
    recipe_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Get nutrition facts for a recipe (total and per-serving).
    Requirements: 24.1, 24.4, 25.3
    """
    # Verify recipe exists and belongs to user
    recipe = db.query(Recipe).filter(
        Recipe.id == recipe_id,
        Recipe.user_id == user_id
    ).first()
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found or you don't have permission",
            headers={"error_code": "RECIPE_NOT_FOUND"}
        )
    
    # Get nutrition facts
    nutrition = NutritionTracker.get_nutrition_facts(db, recipe_id)
    
    if not nutrition:
        return {
            "nutrition_facts": None,
            "per_serving": None
        }
    
    # Calculate per-serving values
    servings = recipe.servings if recipe.servings else 1
    per_serving = NutritionTracker.calculate_per_serving(nutrition, servings)
    
    return {
        "nutrition_facts": nutrition,
        "per_serving": per_serving
    }


# ============================================================================
# Dietary Labels and Allergen Endpoints (Task 16.2)
# ============================================================================

@router.post("/recipes/{recipe_id}/dietary-labels")
def set_dietary_labels(
    recipe_id: int,
    labels_data: DietaryLabelsRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Set dietary labels for a recipe.
    Requirements: 26.1, 27.1
    """
    labels = NutritionTracker.add_dietary_labels(db, recipe_id, labels_data.labels, user_id)
    
    if labels is None:
        # Check if recipe exists and belongs to user
        recipe = db.query(Recipe).filter(
            Recipe.id == recipe_id,
            Recipe.user_id == user_id
        ).first()
        
        if not recipe:
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
def set_allergen_warnings(
    recipe_id: int,
    allergens_data: AllergensRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Set allergen warnings for a recipe.
    Requirements: 26.1, 27.1
    """
    allergens = NutritionTracker.add_allergen_warnings(db, recipe_id, allergens_data.allergens, user_id)
    
    if allergens is None:
        # Check if recipe exists and belongs to user
        recipe = db.query(Recipe).filter(
            Recipe.id == recipe_id,
            Recipe.user_id == user_id
        ).first()
        
        if not recipe:
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
def get_meal_plan_nutrition_summary(
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
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
    
    # Get nutrition summary
    summary = NutritionTracker.get_meal_plan_nutrition_summary(db, user_id, start, end)
    
    return summary
