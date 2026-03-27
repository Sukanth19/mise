from fastapi import APIRouter, Depends, HTTPException, status, Header, Query, Body, Response
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Optional
from app.database import get_db
from app.schemas import RecipeCreate, RecipeUpdate, RecipeResponse, BulkDeleteRequest, FavoriteToggleRequest
from app.models import Recipe, User, RecipeRating, DietaryLabel, AllergenWarning
from jose import jwt, JWTError
from app.config import settings
import json

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
    
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"error_code": "INVALID_TOKEN"}
            )
        return int(user_id)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"error_code": "INVALID_TOKEN"}
        )


def recipe_to_response(recipe: Recipe) -> RecipeResponse:
    """Convert Recipe model to RecipeResponse schema."""
    return RecipeResponse(
        id=str(recipe.id),
        user_id=str(recipe.user_id),
        title=recipe.title,
        image_url=recipe.image_url,
        ingredients=json.loads(recipe.ingredients) if recipe.ingredients else [],
        steps=json.loads(recipe.steps) if recipe.steps else [],
        tags=json.loads(recipe.tags) if recipe.tags else [],
        reference_link=recipe.reference_link,
        created_at=recipe.created_at,
        updated_at=recipe.updated_at,
        is_favorite=recipe.is_favorite or False,
        visibility=recipe.visibility or "private",
        servings=recipe.servings or 1,
        source_recipe_id=str(recipe.source_recipe_id) if recipe.source_recipe_id else None,
        source_author_id=str(recipe.source_author_id) if recipe.source_author_id else None
    )


@router.post("", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
def create_recipe(
    recipe_data: RecipeCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Create a new recipe for the authenticated user."""
    recipe = Recipe(
        user_id=user_id,
        title=recipe_data.title,
        image_url=recipe_data.image_url,
        ingredients=json.dumps(recipe_data.ingredients),
        steps=json.dumps(recipe_data.steps),
        tags=json.dumps(recipe_data.tags) if recipe_data.tags else None,
        reference_link=recipe_data.reference_link,
        is_favorite=recipe_data.is_favorite if hasattr(recipe_data, 'is_favorite') else False,
        visibility=recipe_data.visibility if hasattr(recipe_data, 'visibility') else "private",
        servings=recipe_data.servings if hasattr(recipe_data, 'servings') else 1
    )
    
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    
    return recipe_to_response(recipe)


@router.get("", response_model=List[RecipeResponse])
def get_recipes(
    search: Optional[str] = Query(None, description="Search query for recipe titles"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Get all recipes for the authenticated user, optionally filtered by search query."""
    query = db.query(Recipe).filter(Recipe.user_id == user_id)
    
    if search:
        query = query.filter(Recipe.title.ilike(f"%{search}%"))
    
    recipes = query.order_by(desc(Recipe.created_at)).all()
    return [recipe_to_response(recipe) for recipe in recipes]


@router.delete("/bulk")
def bulk_delete_recipes(
    request: BulkDeleteRequest = Body(...),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Delete multiple recipes atomically."""
    recipe_ids = request.recipe_ids
    
    # Verify all recipes belong to the user
    recipes = db.query(Recipe).filter(
        and_(
            Recipe.id.in_(recipe_ids),
            Recipe.user_id == user_id
        )
    ).all()
    
    found_recipe_ids = {recipe.id for recipe in recipes}
    missing_recipe_ids = [rid for rid in recipe_ids if rid not in found_recipe_ids]
    
    if missing_recipe_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipes with IDs {missing_recipe_ids} not found or you don't have access to them",
            headers={"error_code": "RECIPE_NOT_FOUND"}
        )
    
    deleted_count = db.query(Recipe).filter(
        and_(
            Recipe.id.in_(recipe_ids),
            Recipe.user_id == user_id
        )
    ).delete(synchronize_session=False)
    
    db.commit()
    
    return {"deleted_count": deleted_count}


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
    """Filter and sort recipes with multiple criteria."""
    query = db.query(Recipe).filter(Recipe.user_id == user_id)
    
    # Filter by favorites
    if favorites is not None:
        query = query.filter(Recipe.is_favorite == favorites)
    
    # Filter by tags
    if tags:
        tags_list = [tag.strip() for tag in tags.split(",")]
        tag_filters = []
        for tag in tags_list:
            tag_filters.append(Recipe.tags.like(f'%"{tag}"%'))
        query = query.filter(or_(*tag_filters))
    
    # Filter by dietary labels
    if dietary_labels:
        labels_list = [label.strip() for label in dietary_labels.split(",")]
        query = query.join(DietaryLabel).filter(DietaryLabel.label.in_(labels_list))
    
    # Exclude allergens
    if exclude_allergens:
        allergens_list = [allergen.strip() for allergen in exclude_allergens.split(",")]
        # Subquery to find recipes with excluded allergens
        excluded_recipe_ids = db.query(AllergenWarning.recipe_id).filter(
            AllergenWarning.allergen.in_(allergens_list)
        ).subquery()
        query = query.filter(~Recipe.id.in_(excluded_recipe_ids))
    
    # Filter by minimum rating
    if min_rating is not None:
        # Subquery to calculate average ratings
        avg_ratings = db.query(
            RecipeRating.recipe_id,
            func.avg(RecipeRating.rating).label('avg_rating')
        ).group_by(RecipeRating.recipe_id).subquery()
        
        query = query.join(avg_ratings, Recipe.id == avg_ratings.c.recipe_id).filter(
            avg_ratings.c.avg_rating >= min_rating
        )
    
    # Apply sorting
    if sort_by == "date":
        query = query.order_by(desc(Recipe.created_at) if sort_order == "desc" else asc(Recipe.created_at))
    elif sort_by == "title":
        query = query.order_by(desc(Recipe.title) if sort_order == "desc" else asc(Recipe.title))
    elif sort_by == "rating":
        # Join with average ratings for sorting
        avg_ratings = db.query(
            RecipeRating.recipe_id,
            func.avg(RecipeRating.rating).label('avg_rating')
        ).group_by(RecipeRating.recipe_id).subquery()
        
        query = query.outerjoin(avg_ratings, Recipe.id == avg_ratings.c.recipe_id).order_by(
            desc(avg_ratings.c.avg_rating) if sort_order == "desc" else asc(avg_ratings.c.avg_rating)
        )
    else:
        # Default sort by created_at desc
        query = query.order_by(desc(Recipe.created_at))
    
    recipes = query.all()
    return [recipe_to_response(recipe) for recipe in recipes]


@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Get a specific recipe by ID with ownership check."""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    
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
    
    return recipe_to_response(recipe)


@router.put("/{recipe_id}", response_model=RecipeResponse)
def update_recipe(
    recipe_id: int,
    recipe_data: RecipeUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Update a recipe with ownership validation."""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    
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
    
    # Update fields
    update_data = recipe_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field in ['ingredients', 'steps', 'tags'] and value is not None:
            setattr(recipe, field, json.dumps(value))
        else:
            setattr(recipe, field, value)
    
    db.commit()
    db.refresh(recipe)
    
    return recipe_to_response(recipe)


@router.delete("/{recipe_id}", status_code=status.HTTP_200_OK)
def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Delete a recipe with ownership validation."""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    
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
    
    db.delete(recipe)
    db.commit()
    
    return {"message": "Recipe deleted successfully"}


@router.patch("/{recipe_id}/favorite")
def toggle_favorite(
    recipe_id: int,
    request: FavoriteToggleRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Toggle favorite status for a recipe."""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    
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
    
    recipe.is_favorite = request.is_favorite
    db.commit()
    
    return {"id": str(recipe.id), "is_favorite": recipe.is_favorite}


@router.post("/{recipe_id}/duplicate", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
def duplicate_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Duplicate an existing recipe."""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    
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
    
    # Create duplicate
    duplicated_recipe = Recipe(
        user_id=user_id,
        title=f"{recipe.title} (Copy)",
        image_url=recipe.image_url,
        ingredients=recipe.ingredients,
        steps=recipe.steps,
        tags=recipe.tags,
        reference_link=recipe.reference_link,
        is_favorite=False,
        visibility=recipe.visibility,
        servings=recipe.servings,
        source_recipe_id=recipe.id,
        source_author_id=recipe.user_id
    )
    
    db.add(duplicated_recipe)
    db.commit()
    db.refresh(duplicated_recipe)
    
    return recipe_to_response(duplicated_recipe)


# Rating endpoints
@router.post("/{recipe_id}/rating", status_code=status.HTTP_201_CREATED)
def create_rating(
    recipe_id: int,
    rating_data: dict,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Create a new rating for a recipe."""
    from app.models import RecipeRating
    
    # Validate rating value
    rating_value = rating_data.get("rating")
    if not rating_value or not isinstance(rating_value, int) or rating_value < 1 or rating_value > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5",
            headers={"error_code": "INVALID_RATING"}
        )
    
    # Check if recipe exists
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
            headers={"error_code": "RECIPE_NOT_FOUND"}
        )
    
    # Check if rating already exists
    existing_rating = db.query(RecipeRating).filter(
        RecipeRating.recipe_id == recipe_id,
        RecipeRating.user_id == user_id
    ).first()
    
    if existing_rating:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Rating already exists. Use PUT to update.",
            headers={"error_code": "RATING_EXISTS"}
        )
    
    # Create new rating
    new_rating = RecipeRating(
        recipe_id=recipe_id,
        user_id=user_id,
        rating=rating_value
    )
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    
    return {"rating": new_rating.rating}


@router.put("/{recipe_id}/rating")
def update_rating(
    recipe_id: int,
    rating_data: dict,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Update an existing rating for a recipe."""
    from app.models import RecipeRating
    
    # Validate rating value
    rating_value = rating_data.get("rating")
    if not rating_value or not isinstance(rating_value, int) or rating_value < 1 or rating_value > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5",
            headers={"error_code": "INVALID_RATING"}
        )
    
    # Find existing rating
    existing_rating = db.query(RecipeRating).filter(
        RecipeRating.recipe_id == recipe_id,
        RecipeRating.user_id == user_id
    ).first()
    
    if not existing_rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found. Use POST to create.",
            headers={"error_code": "RATING_NOT_FOUND"}
        )
    
    # Update rating
    existing_rating.rating = rating_value
    db.commit()
    db.refresh(existing_rating)
    
    return {"rating": existing_rating.rating}


@router.get("/{recipe_id}/rating")
def get_rating(
    recipe_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Get the current user's rating for a recipe."""
    from app.models import RecipeRating
    
    rating = db.query(RecipeRating).filter(
        RecipeRating.recipe_id == recipe_id,
        RecipeRating.user_id == user_id
    ).first()
    
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found",
            headers={"error_code": "RATING_NOT_FOUND"}
        )
    
    return {"rating": rating.rating}
