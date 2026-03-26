from fastapi import APIRouter, Depends, HTTPException, status, Header, Body
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from app.database import mongodb
from app.schemas import CollectionCreate, CollectionUpdate, CollectionResponse, RecipeResponse
from app.services.collection_service import CollectionManager
from app.services.auth_service import AuthService
from app.repositories.collection_repository import CollectionRepository
from app.repositories.recipe_repository import RecipeRepository
from app.repositories.user_repository import UserRepository
from app.utils.objectid_utils import validate_objectid, validate_objectid_list

router = APIRouter(prefix="/api/collections", tags=["collections"])


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


@router.post("", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
async def create_collection(
    collection_data: CollectionCreate,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """Create a new collection for the authenticated user."""
    collection_repo = CollectionRepository(db)
    recipe_repo = RecipeRepository(db)
    collection_manager = CollectionManager(collection_repo, recipe_repo)
    
    try:
        collection = await collection_manager.create_collection(user_id, collection_data)
        return collection
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
            headers={"error_code": "VALIDATION_ERROR"}
        )


@router.get("", response_model=dict)
async def get_collections(
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """Get all collections for the authenticated user."""
    collection_repo = CollectionRepository(db)
    recipe_repo = RecipeRepository(db)
    collection_manager = CollectionManager(collection_repo, recipe_repo)
    
    collections = await collection_manager.get_user_collections(user_id)
    return {"collections": collections}


@router.get("/{collection_id}")
async def get_collection(
    collection_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """Get a specific collection by ID with recipes."""
    # Validate ObjectId
    validate_objectid(collection_id, "collection_id")
    
    collection_repo = CollectionRepository(db)
    recipe_repo = RecipeRepository(db)
    collection_manager = CollectionManager(collection_repo, recipe_repo)
    
    collection = await collection_manager.get_collection_by_id(collection_id, user_id)
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
            headers={"error_code": "COLLECTION_NOT_FOUND"}
        )
    
    # Get recipes in this collection (recipe_ids are embedded in collection)
    recipe_ids = collection.get("recipe_ids", [])
    recipes = []
    
    if recipe_ids:
        # Convert ObjectIds to strings for repository query
        recipe_id_strs = [str(rid) for rid in recipe_ids]
        for recipe_id_str in recipe_id_strs:
            recipe = await recipe_repo.find_by_id(recipe_id_str)
            if recipe:
                recipes.append(RecipeResponse.from_orm(recipe))
    
    # Convert collection to dict and add recipes
    collection_dict = {
        "id": str(collection["_id"]),
        "user_id": str(collection["user_id"]),
        "name": collection["name"],
        "description": collection.get("description"),
        "cover_image_url": collection.get("cover_image_url"),
        "parent_collection_id": str(collection["parent_collection_id"]) if collection.get("parent_collection_id") else None,
        "nesting_level": collection.get("nesting_level", 0),
        "share_token": collection.get("share_token"),
        "created_at": collection["created_at"],
        "updated_at": collection["updated_at"],
        "recipes": recipes
    }
    
    return collection_dict


@router.put("/{collection_id}", response_model=CollectionResponse)
async def update_collection(
    collection_id: str,
    collection_data: CollectionUpdate,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """Update a collection with ownership validation."""
    # Validate ObjectId
    validate_objectid(collection_id, "collection_id")
    
    collection_repo = CollectionRepository(db)
    recipe_repo = RecipeRepository(db)
    collection_manager = CollectionManager(collection_repo, recipe_repo)
    
    collection = await collection_manager.update_collection(collection_id, user_id, collection_data)
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found or access denied",
            headers={"error_code": "COLLECTION_NOT_FOUND"}
        )
    
    return collection


@router.delete("/{collection_id}", status_code=status.HTTP_200_OK)
async def delete_collection(
    collection_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """Delete a collection with ownership validation. Cascades to sub-collections."""
    # Validate ObjectId
    validate_objectid(collection_id, "collection_id")
    
    collection_repo = CollectionRepository(db)
    recipe_repo = RecipeRepository(db)
    collection_manager = CollectionManager(collection_repo, recipe_repo)
    
    success = await collection_manager.delete_collection(collection_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found or access denied",
            headers={"error_code": "COLLECTION_NOT_FOUND"}
        )
    
    return {"message": "Collection deleted successfully"}


@router.post("/{collection_id}/recipes")
async def add_recipes_to_collection(
    collection_id: str,
    recipe_ids: List[str] = Body(..., embed=True),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """Add multiple recipes to a collection."""
    # Validate ObjectIds
    validate_objectid(collection_id, "collection_id")
    validate_objectid_list(recipe_ids, "recipe_ids")
    
    collection_repo = CollectionRepository(db)
    recipe_repo = RecipeRepository(db)
    collection_manager = CollectionManager(collection_repo, recipe_repo)
    
    try:
        added_count = await collection_manager.add_recipes_to_collection(
            collection_id, recipe_ids, user_id
        )
        return {"added_count": added_count}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
            headers={"error_code": "VALIDATION_ERROR"}
        )


@router.delete("/{collection_id}/recipes/{recipe_id}", status_code=status.HTTP_200_OK)
async def remove_recipe_from_collection(
    collection_id: str,
    recipe_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """Remove a recipe from a collection."""
    # Validate ObjectIds
    validate_objectid(collection_id, "collection_id")
    validate_objectid(recipe_id, "recipe_id")
    
    collection_repo = CollectionRepository(db)
    recipe_repo = RecipeRepository(db)
    collection_manager = CollectionManager(collection_repo, recipe_repo)
    
    success = await collection_manager.remove_recipe_from_collection(
        collection_id, recipe_id, user_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection or recipe association not found",
            headers={"error_code": "NOT_FOUND"}
        )
    
    return {"message": "Recipe removed from collection"}


@router.post("/{collection_id}/share")
async def generate_share_link(
    collection_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """Generate a share link for a collection."""
    # Validate ObjectId
    validate_objectid(collection_id, "collection_id")
    
    collection_repo = CollectionRepository(db)
    recipe_repo = RecipeRepository(db)
    collection_manager = CollectionManager(collection_repo, recipe_repo)
    
    share_token = await collection_manager.generate_share_token(collection_id, user_id)
    
    if not share_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found or access denied",
            headers={"error_code": "COLLECTION_NOT_FOUND"}
        )
    
    # In production, this would be the actual domain
    share_url = f"/api/collections/shared/{share_token}"
    
    return {"share_url": share_url, "share_token": share_token}


@router.delete("/{collection_id}/share", status_code=status.HTTP_200_OK)
async def revoke_sharing(
    collection_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """Revoke sharing for a collection."""
    # Validate ObjectId
    validate_objectid(collection_id, "collection_id")
    
    collection_repo = CollectionRepository(db)
    recipe_repo = RecipeRepository(db)
    collection_manager = CollectionManager(collection_repo, recipe_repo)
    
    success = await collection_manager.revoke_share_token(collection_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found or access denied",
            headers={"error_code": "COLLECTION_NOT_FOUND"}
        )
    
    return {"message": "Sharing revoked"}


@router.get("/shared/{share_token}")
async def get_shared_collection(
    share_token: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """Access a shared collection (public, no auth required)."""
    collection_repo = CollectionRepository(db)
    recipe_repo = RecipeRepository(db)
    collection_manager = CollectionManager(collection_repo, recipe_repo)
    
    collection = await collection_manager.get_shared_collection(share_token)
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared collection not found",
            headers={"error_code": "COLLECTION_NOT_FOUND"}
        )
    
    # Get recipes in this collection (recipe_ids are embedded in collection)
    recipe_ids = collection.get("recipe_ids", [])
    recipes = []
    
    if recipe_ids:
        # Convert ObjectIds to strings for repository query
        recipe_id_strs = [str(rid) for rid in recipe_ids]
        for recipe_id_str in recipe_id_strs:
            recipe = await recipe_repo.find_by_id(recipe_id_str)
            if recipe:
                recipes.append(RecipeResponse.from_orm(recipe))
    
    # Convert collection to dict and add recipes
    collection_dict = {
        "id": str(collection["_id"]),
        "user_id": str(collection["user_id"]),
        "name": collection["name"],
        "description": collection.get("description"),
        "cover_image_url": collection.get("cover_image_url"),
        "parent_collection_id": str(collection["parent_collection_id"]) if collection.get("parent_collection_id") else None,
        "nesting_level": collection.get("nesting_level", 0),
        "share_token": collection.get("share_token"),
        "created_at": collection["created_at"],
        "updated_at": collection["updated_at"],
        "recipes": recipes
    }
    
    return collection_dict
