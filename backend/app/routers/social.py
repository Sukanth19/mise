from fastapi import APIRouter, Depends, HTTPException, status, Header, Query, Response
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from io import BytesIO
from app.database import mongodb
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
from app.repositories.recipe_repository import RecipeRepository
from app.repositories.user_repository import UserRepository
from app.repositories.recipe_like_repository import RecipeLikeRepository
from app.repositories.recipe_comment_repository import RecipeCommentRepository
from app.repositories.user_follow_repository import UserFollowRepository
from app.config import settings
from app.utils.objectid_utils import validate_objectid

router = APIRouter(prefix="/api", tags=["social"])


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


def get_sharing_service(db: AsyncIOMotorDatabase) -> SharingService:
    """Initialize and return SharingService with all required repositories."""
    recipe_repo = RecipeRepository(db)
    user_repo = UserRepository(db)
    like_repo = RecipeLikeRepository(db)
    comment_repo = RecipeCommentRepository(db)
    follow_repo = UserFollowRepository(db)
    
    return SharingService(recipe_repo, user_repo, like_repo, comment_repo, follow_repo)


# ============================================================================
# Subtask 20.1: Visibility and Discovery Endpoints
# ============================================================================

@router.patch("/recipes/{recipe_id}/visibility", response_model=dict)
async def set_recipe_visibility(
    recipe_id: str,
    visibility_data: VisibilityUpdate,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """
    Set recipe visibility (private, public, unlisted).
    Requirements: 29.1, 29.2
    """
    # Validate ObjectId
    validate_objectid(recipe_id, "recipe_id")
    
    sharing_service = get_sharing_service(db)
    recipe = await sharing_service.set_recipe_visibility(
        recipe_id, visibility_data.visibility, user_id
    )
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found or you don't have permission to modify it",
            headers={"error_code": "RECIPE_NOT_FOUND"}
        )
    
    return {"id": str(recipe['_id']), "visibility": recipe['visibility']}


@router.get("/recipes/discover", response_model=dict)
async def discover_recipes(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search query"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """
    Get paginated discovery feed of public recipes.
    Requirements: 30.1, 30.4
    """
    sharing_service = get_sharing_service(db)
    recipes, total = await sharing_service.get_public_recipes(page, limit, search)
    
    return {
        "recipes": [RecipeResponse.from_orm(r) for r in recipes],
        "total": total,
        "page": page,
        "limit": limit
    }


@router.get("/recipes/public/{recipe_id}", response_model=dict)
async def get_public_recipe(
    recipe_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """
    Get public recipe with author info, likes count, and comments.
    Requirements: 30.1, 30.2, 30.3
    """
    # Validate ObjectId
    validate_objectid(recipe_id, "recipe_id")
    
    sharing_service = get_sharing_service(db)
    result = await sharing_service.get_public_recipe_by_id(recipe_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found or is not public",
            headers={"error_code": "RECIPE_NOT_FOUND"}
        )
    
    return {
        "recipe": RecipeResponse.from_orm(result['recipe']),
        "author": {
            "id": str(result['author']['_id']),
            "username": result['author']['username'],
            "email": result['author'].get('email', '')
        },
        "likes_count": result['likes_count'],
        "comments": [CommentResponse.from_orm(c) for c in result['comments']]
    }


# ============================================================================
# Subtask 20.2: Recipe Forking Endpoint
# ============================================================================

@router.post("/recipes/{recipe_id}/fork", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
async def fork_recipe(
    recipe_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """
    Fork a public or unlisted recipe to user's collection.
    Requirements: 33.1
    """
    # Validate ObjectId
    validate_objectid(recipe_id, "recipe_id")
    
    sharing_service = get_sharing_service(db)
    forked_recipe = await sharing_service.fork_recipe(recipe_id, user_id)
    
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
async def like_recipe(
    recipe_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """
    Like a recipe.
    Requirements: 32.1, 32.2
    """
    # Validate ObjectId
    validate_objectid(recipe_id, "recipe_id")
    
    sharing_service = get_sharing_service(db)
    liked, likes_count = await sharing_service.like_recipe(recipe_id, user_id)
    
    if not liked and likes_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
            headers={"error_code": "RECIPE_NOT_FOUND"}
        )
    
    return {"liked": liked, "likes_count": likes_count}


@router.delete("/recipes/{recipe_id}/like", response_model=dict)
async def unlike_recipe(
    recipe_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """
    Unlike a recipe.
    Requirements: 32.1, 32.2
    """
    # Validate ObjectId
    validate_objectid(recipe_id, "recipe_id")
    
    sharing_service = get_sharing_service(db)
    liked, likes_count = await sharing_service.unlike_recipe(recipe_id, user_id)
    
    return {"liked": liked, "likes_count": likes_count}


@router.post("/recipes/{recipe_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def add_comment(
    recipe_id: str,
    comment_data: CommentCreate,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """
    Add a comment to a recipe.
    Requirements: 32.3
    """
    # Validate ObjectId
    validate_objectid(recipe_id, "recipe_id")
    
    sharing_service = get_sharing_service(db)
    comment = await sharing_service.add_comment(recipe_id, user_id, comment_data.comment_text)
    
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
async def follow_user(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Follow a user.
    Requirements: 31.1, 31.2
    """
    # Validate ObjectId
    validate_objectid(user_id, "user_id")
    
    sharing_service = get_sharing_service(db)
    following, followers_count = await sharing_service.follow_user(current_user_id, user_id)
    
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
async def unfollow_user(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Unfollow a user.
    Requirements: 31.1, 31.2
    """
    # Validate ObjectId
    validate_objectid(user_id, "user_id")
    
    sharing_service = get_sharing_service(db)
    following, followers_count = await sharing_service.unfollow_user(current_user_id, user_id)
    
    return {"following": following, "followers_count": followers_count}


@router.get("/users/{user_id}/followers", response_model=dict)
async def get_followers(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """
    Get list of users following the specified user.
    Requirements: 31.3, 31.4
    """
    # Validate ObjectId
    validate_objectid(user_id, "user_id")
    
    sharing_service = get_sharing_service(db)
    followers = await sharing_service.get_followers(user_id)
    
    return {
        "followers": [
            {"id": str(u['_id']), "username": u['username'], "email": u.get('email', '')}
            for u in followers
        ],
        "count": len(followers)
    }


@router.get("/users/{user_id}/following", response_model=dict)
async def get_following(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """
    Get list of users that the specified user is following.
    Requirements: 31.3, 31.4
    """
    # Validate ObjectId
    validate_objectid(user_id, "user_id")
    
    sharing_service = get_sharing_service(db)
    following = await sharing_service.get_following(user_id)
    
    return {
        "following": [
            {"id": str(u['_id']), "username": u['username'], "email": u.get('email', '')}
            for u in following
        ],
        "count": len(following)
    }


# ============================================================================
# Subtask 20.5: Additional Sharing Endpoints
# ============================================================================

@router.post("/recipes/import-url", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
async def import_recipe_from_url(
    url_data: dict,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
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
    
    sharing_service = get_sharing_service(db)
    recipe = await sharing_service.import_recipe_from_url(url, user_id)
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to import recipe from URL. The URL may not contain parseable recipe data.",
            headers={"error_code": "IMPORT_FAILED"}
        )
    
    return RecipeResponse.from_orm(recipe)


@router.get("/recipes/{recipe_id}/qrcode")
async def get_recipe_qrcode(
    recipe_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """
    Generate QR code image for recipe.
    Requirements: 36.1
    """
    # Validate ObjectId
    validate_objectid(recipe_id, "recipe_id")
    # Build recipe URL (use public URL if available)
    base_url = getattr(settings, 'base_url', 'http://localhost:3000')
    recipe_url = f"{base_url}/recipes/{recipe_id}"
    
    # Generate QR code
    sharing_service = get_sharing_service(db)
    qr_bytes = sharing_service.generate_qr_code(recipe_url)
    
    # Return as PNG image
    return StreamingResponse(
        BytesIO(qr_bytes),
        media_type="image/png",
        headers={"Content-Disposition": f"inline; filename=recipe_{recipe_id}_qr.png"}
    )


@router.get("/recipes/{recipe_id}/share-metadata", response_model=ShareMetadataResponse)
async def get_share_metadata(
    recipe_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """
    Get social media share metadata for recipe.
    Requirements: 35.1
    """
    # Validate ObjectId
    validate_objectid(recipe_id, "recipe_id")
    base_url = getattr(settings, 'base_url', 'http://localhost:3000')
    
    sharing_service = get_sharing_service(db)
    metadata = await sharing_service.get_share_metadata(recipe_id, base_url)
    
    if not metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
            headers={"error_code": "RECIPE_NOT_FOUND"}
        )
    
    return ShareMetadataResponse(**metadata)
