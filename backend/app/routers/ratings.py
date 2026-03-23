from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import RatingCreate, RatingUpdate, RatingResponse
from app.services.rating_service import RatingSystem
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/recipes", tags=["ratings"])


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


@router.post("/{recipe_id}/rating", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
def create_rating(
    recipe_id: int,
    rating_data: RatingCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Create a new rating for a recipe."""
    rating = RatingSystem.add_rating(db, recipe_id, user_id, rating_data.rating)
    
    if not rating:
        # Check if rating already exists
        existing = RatingSystem.get_user_rating(db, recipe_id, user_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Rating already exists for this recipe. Use PUT to update.",
                headers={"error_code": "RATING_EXISTS"}
            )
        
        # Check if validation failed
        if not RatingSystem.validate_rating(rating_data.rating):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 1 and 5",
                headers={"error_code": "INVALID_RATING"}
            )
        
        # Recipe doesn't exist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
            headers={"error_code": "RECIPE_NOT_FOUND"}
        )
    
    return rating


@router.put("/{recipe_id}/rating", response_model=RatingResponse)
def update_rating(
    recipe_id: int,
    rating_data: RatingUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Update an existing rating for a recipe."""
    rating = RatingSystem.update_rating(db, recipe_id, user_id, rating_data.rating)
    
    if not rating:
        # Check if validation failed
        if not RatingSystem.validate_rating(rating_data.rating):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 1 and 5",
                headers={"error_code": "INVALID_RATING"}
            )
        
        # Rating doesn't exist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found. Use POST to create a new rating.",
            headers={"error_code": "RATING_NOT_FOUND"}
        )
    
    return rating


@router.get("/{recipe_id}/rating", response_model=RatingResponse)
def get_rating(
    recipe_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Get the authenticated user's rating for a recipe."""
    rating = RatingSystem.get_user_rating(db, recipe_id, user_id)
    
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found",
            headers={"error_code": "RATING_NOT_FOUND"}
        )
    
    return rating
