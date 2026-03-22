from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas import RecipeCreate, RecipeUpdate, RecipeResponse
from app.services.recipe_service import RecipeManager
from app.services.search_service import SearchEngine
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/recipes", tags=["recipes"])


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


@router.post("", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
def create_recipe(
    recipe_data: RecipeCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Create a new recipe for the authenticated user."""
    recipe = RecipeManager.create_recipe(db, user_id, recipe_data)
    return RecipeResponse.from_orm(recipe)


@router.get("", response_model=List[RecipeResponse])
def get_recipes(
    search: Optional[str] = Query(None, description="Search query for recipe titles"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Get all recipes for the authenticated user, optionally filtered by search query."""
    if search:
        # Use SearchEngine when search query is provided
        recipes = SearchEngine.search_recipes(db, user_id, search)
    else:
        # Return all user recipes when no search query
        recipes = RecipeManager.get_user_recipes(db, user_id)
    return [RecipeResponse.from_orm(recipe) for recipe in recipes]


@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Get a specific recipe by ID with ownership check."""
    recipe = RecipeManager.get_recipe_by_id(db, recipe_id)
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
            headers={"error_code": "RECIPE_NOT_FOUND"}
        )
    
    # Verify ownership
    if recipe.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this recipe",
            headers={"error_code": "FORBIDDEN"}
        )
    
    return RecipeResponse.from_orm(recipe)


@router.put("/{recipe_id}", response_model=RecipeResponse)
def update_recipe(
    recipe_id: int,
    recipe_data: RecipeUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Update a recipe with ownership validation."""
    recipe = RecipeManager.get_recipe_by_id(db, recipe_id)
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
            headers={"error_code": "RECIPE_NOT_FOUND"}
        )
    
    # Verify ownership
    if recipe.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this recipe",
            headers={"error_code": "FORBIDDEN"}
        )
    
    updated_recipe = RecipeManager.update_recipe(db, recipe_id, user_id, recipe_data)
    
    if not updated_recipe:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update recipe"
        )
    
    return RecipeResponse.from_orm(updated_recipe)


@router.delete("/{recipe_id}", status_code=status.HTTP_200_OK)
def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Delete a recipe with ownership validation."""
    recipe = RecipeManager.get_recipe_by_id(db, recipe_id)
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
            headers={"error_code": "RECIPE_NOT_FOUND"}
        )
    
    # Verify ownership
    if recipe.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this recipe",
            headers={"error_code": "FORBIDDEN"}
        )
    
    success = RecipeManager.delete_recipe(db, recipe_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete recipe"
        )
    
    return {"message": "Recipe deleted successfully"}
