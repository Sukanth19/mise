from fastapi import APIRouter, Depends, HTTPException, status, Header, Query, Body, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas import RecipeCreate, RecipeUpdate, RecipeResponse, BulkDeleteRequest, FavoriteToggleRequest, URLImportRequest, ShareMetadataResponse
from app.services.recipe_service import RecipeManager
from app.services.search_service import SearchEngine
from app.services.auth_service import AuthService
from app.services.filter_service import FilterEngine
from app.services.sharing_service import SharingService

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


@router.delete("/bulk")
def bulk_delete_recipes(
    request: BulkDeleteRequest = Body(...),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Delete multiple recipes atomically."""
    try:
        deleted_count = RecipeManager.bulk_delete_recipes(db, request.recipe_ids, user_id)
        return {"deleted_count": deleted_count}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
            headers={"error_code": "RECIPE_NOT_FOUND"}
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
            headers={"error_code": "FORBIDDEN"}
        )


@router.get("/filter", response_model=List[RecipeResponse])
def filter_recipes(
    favorites: Optional[bool] = Query(None, description="Filter by favorite status"),
    min_rating: Optional[float] = Query(None, description="Minimum average rating threshold", ge=1, le=5),
    tags: Optional[str] = Query(None, description="Comma-separated list of tags"),
    dietary_labels: Optional[str] = Query(None, description="Comma-separated list of dietary labels"),
    exclude_allergens: Optional[str] = Query(None, description="Comma-separated list of allergens to exclude"),
    sort_by: Optional[str] = Query(None, description="Sort by field (date, rating, title)"),
    sort_order: Optional[str] = Query("asc", description="Sort order (asc or desc)"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Filter and sort recipes with multiple criteria.
    
    Query parameters:
    - favorites: Filter by favorite status (true/false)
    - min_rating: Minimum average rating (1-5)
    - tags: Comma-separated tags (recipes with any of these tags)
    - dietary_labels: Comma-separated dietary labels (vegan, vegetarian, gluten-free, etc.)
    - exclude_allergens: Comma-separated allergens to exclude (nuts, dairy, eggs, etc.)
    - sort_by: Sort field (date, rating, title)
    - sort_order: Sort order (asc or desc)
    """
    # Parse comma-separated lists
    tags_list = [tag.strip() for tag in tags.split(",")] if tags else None
    dietary_labels_list = [label.strip() for label in dietary_labels.split(",")] if dietary_labels else None
    exclude_allergens_list = [allergen.strip() for allergen in exclude_allergens.split(",")] if exclude_allergens else None
    
    # Validate sort_by parameter
    if sort_by and sort_by not in ["date", "rating", "title"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid sort_by parameter. Must be one of: date, rating, title",
            headers={"error_code": "INVALID_SORT_BY"}
        )
    
    # Validate sort_order parameter
    if sort_order and sort_order.lower() not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid sort_order parameter. Must be 'asc' or 'desc'",
            headers={"error_code": "INVALID_SORT_ORDER"}
        )
    
    # Apply filters and sorting
    recipes = FilterEngine.filter_recipes(
        db=db,
        user_id=user_id,
        favorites=favorites,
        min_rating=min_rating,
        tags=tags_list,
        dietary_labels=dietary_labels_list,
        exclude_allergens=exclude_allergens_list,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
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


@router.patch("/{recipe_id}/favorite")
def toggle_favorite(
    recipe_id: int,
    request: FavoriteToggleRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Toggle favorite status for a recipe."""
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
            detail="You don't have permission to modify this recipe",
            headers={"error_code": "FORBIDDEN"}
        )
    
    # Update favorite status
    recipe.is_favorite = request.is_favorite
    db.commit()
    db.refresh(recipe)
    
    return {"id": recipe.id, "is_favorite": recipe.is_favorite}


@router.post("/{recipe_id}/duplicate", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
def duplicate_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Duplicate an existing recipe."""
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
            detail="You don't have permission to duplicate this recipe",
            headers={"error_code": "FORBIDDEN"}
        )
    
    duplicated_recipe = RecipeManager.duplicate_recipe(db, recipe_id, user_id)
    
    if not duplicated_recipe:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to duplicate recipe"
        )
    
    return RecipeResponse.from_orm(duplicated_recipe)



@router.post("/import-url", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
def import_recipe_from_url(
    request: URLImportRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Import a recipe from a URL by parsing the webpage content.
    Requirements: 34.1, 34.2, 34.3, 34.4
    """
    recipe = SharingService.import_recipe_from_url(db, request.url, user_id)
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to import recipe from URL. The URL may be invalid or the page does not contain parseable recipe data.",
            headers={"error_code": "IMPORT_FAILED"}
        )
    
    return RecipeResponse.from_orm(recipe)


@router.get("/{recipe_id}/qrcode")
def get_recipe_qr_code(
    recipe_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate a QR code for a recipe.
    Returns PNG image bytes.
    Requirements: 36.1, 36.2, 36.3
    """
    # Check if recipe exists
    recipe = RecipeManager.get_recipe_by_id(db, recipe_id)
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
            headers={"error_code": "RECIPE_NOT_FOUND"}
        )
    
    # Generate recipe URL (use public URL if recipe is public/unlisted)
    # For now, use a placeholder base URL - in production this would come from config
    base_url = "http://localhost:3000"
    if recipe.visibility in ['public', 'unlisted']:
        recipe_url = f"{base_url}/recipes/public/{recipe_id}"
    else:
        recipe_url = f"{base_url}/recipes/{recipe_id}"
    
    # Generate QR code
    qr_code_bytes = SharingService.generate_qr_code(recipe_url)
    
    # Return as PNG image
    return Response(content=qr_code_bytes, media_type="image/png")


@router.get("/{recipe_id}/share-metadata", response_model=ShareMetadataResponse)
def get_recipe_share_metadata(
    recipe_id: int,
    db: Session = Depends(get_db)
):
    """
    Get social media share metadata for a recipe.
    Returns metadata formatted for Open Graph and Twitter Cards.
    Requirements: 35.1, 35.2
    """
    # Use placeholder base URL - in production this would come from config
    base_url = "http://localhost:3000"
    
    metadata = SharingService.get_share_metadata(db, recipe_id, base_url)
    
    if not metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
            headers={"error_code": "RECIPE_NOT_FOUND"}
        )
    
    return metadata
