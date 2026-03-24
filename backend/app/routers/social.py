from fastapi import APIRouter, Depends, HTTPException, status, Header, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from io import BytesIO
from app.database import get_db
from app.schemas import (
    RecipeResponse, 
    PublicRecipeResponse, 
    CommentCreate, 
    CommentResponse,
    UserFollowResponse,
    ShareMetadataResponse,
    VisibilityUpdate
)
from app.services.sharing_service import SharingService
from app.services.auth_service import AuthService
from app.config import settings

router = APIRouter(prefix="/api", tags=["social"])


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
# Subtask 20.1: Visibility and Discovery Endpoints
# ============================================================================

@router.patch("/recipes/{recipe_id}/visibility", response_model=dict)
def set_recipe_visibility(
    recipe_id: int,
    visibility_data: VisibilityUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Set recipe visibility (private, public, unlisted).
    Requirements: 29.1, 29.2
    """
    recipe = SharingService.set_recipe_visibility(
        db, recipe_id, visibility_data.visibility, user_id
    )
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found or you don't have permission to modify it",
            headers={"error_code": "RECIPE_NOT_FOUND"}
        )
    
    return {"id": recipe.id, "visibility": recipe.visibility}


@router.get("/recipes/discover", response_model=dict)
def discover_recipes(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search query"),
    db: Session = Depends(get_db)
):
    """
    Get paginated discovery feed of public recipes.
    Requirements: 30.1, 30.4
    """
    recipes, total = SharingService.get_public_recipes(db, page, limit, search)
    
    return {
        "recipes": [RecipeResponse.from_orm(r) for r in recipes],
        "total": total,
        "page": page,
        "limit": limit
    }


@router.get("/recipes/public/{recipe_id}", response_model=dict)
def get_public_recipe(
    recipe_id: int,
    db: Session = Depends(get_db)
):
    """
    Get public recipe with author info, likes count, and comments.
    Requirements: 30.1, 30.2, 30.3
    """
    result = SharingService.get_public_recipe_by_id(db, recipe_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found or is not public",
            headers={"error_code": "RECIPE_NOT_FOUND"}
        )
    
    return {
        "recipe": RecipeResponse.from_orm(result['recipe']),
        "author": {
            "id": result['author'].id,
            "username": result['author'].username,
            "email": result['author'].email
        },
        "likes_count": result['likes_count'],
        "comments": [CommentResponse.from_orm(c) for c in result['comments']]
    }


# ============================================================================
# Subtask 20.2: Recipe Forking Endpoint
# ============================================================================

@router.post("/recipes/{recipe_id}/fork", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
def fork_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Fork a public or unlisted recipe to user's collection.
    Requirements: 33.1
    """
    forked_recipe = SharingService.fork_recipe(db, recipe_id, user_id)
    
    if not forked_recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found or is not forkable (must be public or unlisted)",
            headers={"error_code": "RECIPE_NOT_FORKABLE"}
        )
    
    return RecipeResponse.from_orm(forked_recipe)


# ============================================================================
# Subtask 20.3: Likes and Comments Endpoints
# ============================================================================

@router.post("/recipes/{recipe_id}/like", response_model=dict)
def like_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Like a recipe.
    Requirements: 32.1, 32.2
    """
    liked, likes_count = SharingService.like_recipe(db, recipe_id, user_id)
    
    if not liked and likes_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
            headers={"error_code": "RECIPE_NOT_FOUND"}
        )
    
    return {"liked": liked, "likes_count": likes_count}


@router.delete("/recipes/{recipe_id}/like", response_model=dict)
def unlike_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Unlike a recipe.
    Requirements: 32.1, 32.2
    """
    liked, likes_count = SharingService.unlike_recipe(db, recipe_id, user_id)
    
    return {"liked": liked, "likes_count": likes_count}


@router.post("/recipes/{recipe_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def add_comment(
    recipe_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Add a comment to a recipe.
    Requirements: 32.3
    """
    comment = SharingService.add_comment(db, recipe_id, user_id, comment_data.comment_text)
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
            headers={"error_code": "RECIPE_NOT_FOUND"}
        )
    
    return CommentResponse.from_orm(comment)


# ============================================================================
# Subtask 20.4: User Following Endpoints
# ============================================================================

@router.post("/users/{user_id}/follow", response_model=dict)
def follow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Follow a user.
    Requirements: 31.1, 31.2
    """
    following, followers_count = SharingService.follow_user(db, current_user_id, user_id)
    
    if not following and followers_count == 0:
        if current_user_id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot follow yourself",
                headers={"error_code": "CANNOT_FOLLOW_SELF"}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
                headers={"error_code": "USER_NOT_FOUND"}
            )
    
    return {"following": following, "followers_count": followers_count}


@router.delete("/users/{user_id}/follow", response_model=dict)
def unfollow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Unfollow a user.
    Requirements: 31.1, 31.2
    """
    following, followers_count = SharingService.unfollow_user(db, current_user_id, user_id)
    
    return {"following": following, "followers_count": followers_count}


@router.get("/users/{user_id}/followers", response_model=dict)
def get_followers(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get list of users following the specified user.
    Requirements: 31.3, 31.4
    """
    followers = SharingService.get_followers(db, user_id)
    
    return {
        "followers": [
            {"id": u.id, "username": u.username, "email": u.email}
            for u in followers
        ],
        "count": len(followers)
    }


@router.get("/users/{user_id}/following", response_model=dict)
def get_following(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get list of users that the specified user is following.
    Requirements: 31.3, 31.4
    """
    following = SharingService.get_following(db, user_id)
    
    return {
        "following": [
            {"id": u.id, "username": u.username, "email": u.email}
            for u in following
        ],
        "count": len(following)
    }


# ============================================================================
# Subtask 20.5: Additional Sharing Endpoints
# ============================================================================

@router.post("/recipes/import-url", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
def import_recipe_from_url(
    url_data: dict,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Import recipe from URL.
    Requirements: 34.1
    """
    url = url_data.get("url")
    if not url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL is required",
            headers={"error_code": "URL_REQUIRED"}
        )
    
    recipe = SharingService.import_recipe_from_url(db, url, user_id)
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to import recipe from URL. The URL may not contain parseable recipe data.",
            headers={"error_code": "IMPORT_FAILED"}
        )
    
    return RecipeResponse.from_orm(recipe)


@router.get("/recipes/{recipe_id}/qrcode")
def get_recipe_qrcode(
    recipe_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate QR code image for recipe.
    Requirements: 36.1
    """
    # Build recipe URL (use public URL if available)
    base_url = getattr(settings, 'base_url', 'http://localhost:3000')
    recipe_url = f"{base_url}/recipes/{recipe_id}"
    
    # Generate QR code
    qr_bytes = SharingService.generate_qr_code(recipe_url)
    
    # Return as PNG image
    return StreamingResponse(
        BytesIO(qr_bytes),
        media_type="image/png",
        headers={"Content-Disposition": f"inline; filename=recipe_{recipe_id}_qr.png"}
    )


@router.get("/recipes/{recipe_id}/share-metadata", response_model=ShareMetadataResponse)
def get_share_metadata(
    recipe_id: int,
    db: Session = Depends(get_db)
):
    """
    Get social media share metadata for recipe.
    Requirements: 35.1
    """
    base_url = getattr(settings, 'base_url', 'http://localhost:3000')
    metadata = SharingService.get_share_metadata(db, recipe_id, base_url)
    
    if not metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
            headers={"error_code": "RECIPE_NOT_FOUND"}
        )
    
    return ShareMetadataResponse(**metadata)
