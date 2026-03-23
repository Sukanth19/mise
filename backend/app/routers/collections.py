from fastapi import APIRouter, Depends, HTTPException, status, Header, Body
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import CollectionCreate, CollectionUpdate, CollectionResponse, RecipeResponse
from app.services.collection_service import CollectionManager
from app.services.auth_service import AuthService
from app.models import CollectionRecipe, Recipe

router = APIRouter(prefix="/api/collections", tags=["collections"])


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


@router.post("", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
def create_collection(
    collection_data: CollectionCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Create a new collection for the authenticated user."""
    try:
        collection = CollectionManager.create_collection(db, user_id, collection_data)
        return collection
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
            headers={"error_code": "VALIDATION_ERROR"}
        )


@router.get("", response_model=List[CollectionResponse])
def get_collections(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Get all collections for the authenticated user."""
    collections = CollectionManager.get_user_collections(db, user_id)
    return collections


@router.get("/{collection_id}")
def get_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Get a specific collection by ID with recipes."""
    collection = CollectionManager.get_collection_by_id(db, collection_id, user_id)
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
            headers={"error_code": "COLLECTION_NOT_FOUND"}
        )
    
    # Get recipes in this collection
    recipe_associations = db.query(CollectionRecipe).filter(
        CollectionRecipe.collection_id == collection_id
    ).all()
    
    recipe_ids = [assoc.recipe_id for assoc in recipe_associations]
    recipes = []
    
    if recipe_ids:
        recipes = db.query(Recipe).filter(Recipe.id.in_(recipe_ids)).all()
        recipes = [RecipeResponse.from_orm(recipe) for recipe in recipes]
    
    # Convert collection to dict and add recipes
    collection_dict = {
        "id": collection.id,
        "user_id": collection.user_id,
        "name": collection.name,
        "description": collection.description,
        "cover_image_url": collection.cover_image_url,
        "parent_collection_id": collection.parent_collection_id,
        "nesting_level": collection.nesting_level,
        "share_token": collection.share_token,
        "created_at": collection.created_at,
        "updated_at": collection.updated_at,
        "recipes": recipes
    }
    
    return collection_dict


@router.put("/{collection_id}", response_model=CollectionResponse)
def update_collection(
    collection_id: int,
    collection_data: CollectionUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Update a collection with ownership validation."""
    collection = CollectionManager.update_collection(db, collection_id, user_id, collection_data)
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found or access denied",
            headers={"error_code": "COLLECTION_NOT_FOUND"}
        )
    
    return collection


@router.delete("/{collection_id}", status_code=status.HTTP_200_OK)
def delete_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Delete a collection with ownership validation. Cascades to sub-collections."""
    success = CollectionManager.delete_collection(db, collection_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found or access denied",
            headers={"error_code": "COLLECTION_NOT_FOUND"}
        )
    
    return {"message": "Collection deleted successfully"}


@router.post("/{collection_id}/recipes")
def add_recipes_to_collection(
    collection_id: int,
    recipe_ids: List[int] = Body(..., embed=True),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Add multiple recipes to a collection."""
    try:
        added_count = CollectionManager.add_recipes_to_collection(
            db, collection_id, recipe_ids, user_id
        )
        return {"added_count": added_count}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
            headers={"error_code": "VALIDATION_ERROR"}
        )


@router.delete("/{collection_id}/recipes/{recipe_id}", status_code=status.HTTP_200_OK)
def remove_recipe_from_collection(
    collection_id: int,
    recipe_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Remove a recipe from a collection."""
    success = CollectionManager.remove_recipe_from_collection(
        db, collection_id, recipe_id, user_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection or recipe association not found",
            headers={"error_code": "NOT_FOUND"}
        )
    
    return {"message": "Recipe removed from collection"}


@router.post("/{collection_id}/share")
def generate_share_link(
    collection_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Generate a share link for a collection."""
    share_token = CollectionManager.generate_share_token(db, collection_id, user_id)
    
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
def revoke_sharing(
    collection_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Revoke sharing for a collection."""
    success = CollectionManager.revoke_share_token(db, collection_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found or access denied",
            headers={"error_code": "COLLECTION_NOT_FOUND"}
        )
    
    return {"message": "Sharing revoked"}


@router.get("/shared/{share_token}")
def get_shared_collection(
    share_token: str,
    db: Session = Depends(get_db)
):
    """Access a shared collection (public, no auth required)."""
    collection = CollectionManager.get_shared_collection(db, share_token)
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared collection not found",
            headers={"error_code": "COLLECTION_NOT_FOUND"}
        )
    
    # Get recipes in this collection
    recipe_associations = db.query(CollectionRecipe).filter(
        CollectionRecipe.collection_id == collection.id
    ).all()
    
    recipe_ids = [assoc.recipe_id for assoc in recipe_associations]
    recipes = []
    
    if recipe_ids:
        recipes = db.query(Recipe).filter(Recipe.id.in_(recipe_ids)).all()
        recipes = [RecipeResponse.from_orm(recipe) for recipe in recipes]
    
    # Convert collection to dict and add recipes
    collection_dict = {
        "id": collection.id,
        "user_id": collection.user_id,
        "name": collection.name,
        "description": collection.description,
        "cover_image_url": collection.cover_image_url,
        "parent_collection_id": collection.parent_collection_id,
        "nesting_level": collection.nesting_level,
        "share_token": collection.share_token,
        "created_at": collection.created_at,
        "updated_at": collection.updated_at,
        "recipes": recipes
    }
    
    return collection_dict
