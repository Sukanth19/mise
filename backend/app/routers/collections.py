from fastapi import APIRouter, Depends, HTTPException, status, Header, Body
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc
from typing import List
from app.database import get_db
from app.schemas import CollectionCreate, CollectionUpdate, CollectionResponse, RecipeResponse
from app.models import Collection, CollectionRecipe, Recipe
from jose import jwt, JWTError
from app.config import settings
import json
import secrets

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


def collection_to_response(collection: Collection, recipe_count: int = 0) -> CollectionResponse:
    """Convert Collection model to CollectionResponse schema."""
    return CollectionResponse(
        id=collection.id,
        user_id=collection.user_id,
        name=collection.name,
        description=collection.description,
        cover_image_url=collection.cover_image_url,
        parent_collection_id=collection.parent_collection_id,
        nesting_level=collection.nesting_level or 0,
        share_token=collection.share_token,
        created_at=collection.created_at,
        updated_at=collection.updated_at,
        recipe_count=recipe_count
    )


def recipe_to_response(recipe: Recipe) -> RecipeResponse:
    """Convert Recipe model to RecipeResponse schema."""
    return RecipeResponse(
        id=recipe.id,
        user_id=recipe.user_id,
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
        source_recipe_id=recipe.source_recipe_id,
        source_author_id=recipe.source_author_id
    )


@router.post("", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
def create_collection(
    collection_data: CollectionCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Create a new collection for the authenticated user."""
    # Validate parent collection if specified
    nesting_level = 0
    if collection_data.parent_collection_id:
        parent_id = int(collection_data.parent_collection_id)
        parent = db.query(Collection).filter(
            and_(
                Collection.id == parent_id,
                Collection.user_id == user_id
            )
        ).first()
        
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent collection not found or access denied",
                headers={"error_code": "VALIDATION_ERROR"}
            )
        
        nesting_level = parent.nesting_level + 1
        if nesting_level > 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum nesting level (3) exceeded",
                headers={"error_code": "VALIDATION_ERROR"}
            )
    
    collection = Collection(
        user_id=user_id,
        name=collection_data.name,
        description=collection_data.description,
        cover_image_url=collection_data.cover_image_url,
        parent_collection_id=int(collection_data.parent_collection_id) if collection_data.parent_collection_id else None,
        nesting_level=nesting_level
    )
    
    db.add(collection)
    db.commit()
    db.refresh(collection)
    
    return collection_to_response(collection, 0)


@router.get("", response_model=dict)
def get_collections(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Get all collections for the authenticated user."""
    collections = db.query(Collection).filter(
        Collection.user_id == user_id
    ).order_by(desc(Collection.created_at)).all()
    
    # Get recipe counts for each collection
    collection_responses = []
    for collection in collections:
        recipe_count = db.query(CollectionRecipe).filter(
            CollectionRecipe.collection_id == collection.id
        ).count()
        collection_responses.append(collection_to_response(collection, recipe_count))
    
    return {"collections": collection_responses}


@router.get("/{collection_id}")
def get_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Get a specific collection by ID with recipes."""
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
            headers={"error_code": "COLLECTION_NOT_FOUND"}
        )
    
    # Verify ownership
    if collection.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this collection",
            headers={"error_code": "FORBIDDEN"}
        )
    
    # Get recipes in this collection
    collection_recipes = db.query(CollectionRecipe).filter(
        CollectionRecipe.collection_id == collection_id
    ).all()
    
    recipes = []
    for cr in collection_recipes:
        recipe = db.query(Recipe).filter(Recipe.id == cr.recipe_id).first()
        if recipe:
            recipes.append(recipe_to_response(recipe))
    
    return {
        "id": collection.id,
        "user_id": collection.user_id,
        "name": collection.name,
        "description": collection.description,
        "cover_image_url": collection.cover_image_url,
        "parent_collection_id": collection.parent_collection_id,
        "nesting_level": collection.nesting_level or 0,
        "share_token": collection.share_token,
        "recipe_count": len(recipes),
        "created_at": collection.created_at,
        "updated_at": collection.updated_at,
        "recipes": recipes
    }


@router.put("/{collection_id}", response_model=CollectionResponse)
def update_collection(
    collection_id: int,
    collection_data: CollectionUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Update a collection with ownership validation."""
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
            headers={"error_code": "COLLECTION_NOT_FOUND"}
        )
    
    # Verify ownership
    if collection.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this collection",
            headers={"error_code": "FORBIDDEN"}
        )
    
    # Update fields
    update_data = collection_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "parent_collection_id" and value is not None:
            # Validate parent collection
            parent_id = int(value)
            parent = db.query(Collection).filter(
                and_(
                    Collection.id == parent_id,
                    Collection.user_id == user_id
                )
            ).first()
            
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent collection not found or access denied",
                    headers={"error_code": "VALIDATION_ERROR"}
                )
            
            collection.nesting_level = parent.nesting_level + 1
            if collection.nesting_level > 3:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Maximum nesting level (3) exceeded",
                    headers={"error_code": "VALIDATION_ERROR"}
                )
            setattr(collection, field, parent_id)
        else:
            setattr(collection, field, value)
    
    db.commit()
    db.refresh(collection)
    
    recipe_count = db.query(CollectionRecipe).filter(
        CollectionRecipe.collection_id == collection.id
    ).count()
    
    return collection_to_response(collection, recipe_count)


@router.delete("/{collection_id}", status_code=status.HTTP_200_OK)
def delete_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Delete a collection with ownership validation. Cascades to sub-collections."""
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
            headers={"error_code": "COLLECTION_NOT_FOUND"}
        )
    
    # Verify ownership
    if collection.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this collection",
            headers={"error_code": "FORBIDDEN"}
        )
    
    # Delete collection (cascade will handle sub-collections and collection_recipes)
    db.delete(collection)
    db.commit()
    
    return {"message": "Collection deleted successfully"}


@router.post("/{collection_id}/recipes")
def add_recipes_to_collection(
    collection_id: int,
    recipe_ids: List[int] = Body(..., embed=True),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Add multiple recipes to a collection."""
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
            headers={"error_code": "COLLECTION_NOT_FOUND"}
        )
    
    # Verify ownership
    if collection.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to modify this collection",
            headers={"error_code": "FORBIDDEN"}
        )
    
    # Verify all recipes exist and belong to the user
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
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Recipes with IDs {missing_recipe_ids} not found or you don't have access to them",
            headers={"error_code": "VALIDATION_ERROR"}
        )
    
    # Add recipes to collection (skip duplicates)
    added_count = 0
    for recipe_id in recipe_ids:
        existing = db.query(CollectionRecipe).filter(
            and_(
                CollectionRecipe.collection_id == collection_id,
                CollectionRecipe.recipe_id == recipe_id
            )
        ).first()
        
        if not existing:
            collection_recipe = CollectionRecipe(
                collection_id=collection_id,
                recipe_id=recipe_id
            )
            db.add(collection_recipe)
            added_count += 1
    
    db.commit()
    
    return {"added_count": added_count}


@router.delete("/{collection_id}/recipes/{recipe_id}", status_code=status.HTTP_200_OK)
def remove_recipe_from_collection(
    collection_id: int,
    recipe_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Remove a recipe from a collection."""
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
            headers={"error_code": "COLLECTION_NOT_FOUND"}
        )
    
    # Verify ownership
    if collection.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to modify this collection",
            headers={"error_code": "FORBIDDEN"}
        )
    
    # Remove recipe from collection
    collection_recipe = db.query(CollectionRecipe).filter(
        and_(
            CollectionRecipe.collection_id == collection_id,
            CollectionRecipe.recipe_id == recipe_id
        )
    ).first()
    
    if not collection_recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found in collection",
            headers={"error_code": "NOT_FOUND"}
        )
    
    db.delete(collection_recipe)
    db.commit()
    
    return {"message": "Recipe removed from collection"}


@router.post("/{collection_id}/share")
def generate_share_link(
    collection_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Generate a share link for a collection."""
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
            headers={"error_code": "COLLECTION_NOT_FOUND"}
        )
    
    # Verify ownership
    if collection.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to share this collection",
            headers={"error_code": "FORBIDDEN"}
        )
    
    # Generate share token if not exists
    if not collection.share_token:
        collection.share_token = secrets.token_urlsafe(32)
        db.commit()
    
    share_url = f"/api/collections/shared/{collection.share_token}"
    
    return {"share_url": share_url, "share_token": collection.share_token}


@router.delete("/{collection_id}/share", status_code=status.HTTP_200_OK)
def revoke_sharing(
    collection_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Revoke sharing for a collection."""
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
            headers={"error_code": "COLLECTION_NOT_FOUND"}
        )
    
    # Verify ownership
    if collection.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to modify this collection",
            headers={"error_code": "FORBIDDEN"}
        )
    
    collection.share_token = None
    db.commit()
    
    return {"message": "Sharing revoked"}


@router.get("/shared/{share_token}")
def get_shared_collection(
    share_token: str,
    db: Session = Depends(get_db)
):
    """Access a shared collection (public, no auth required)."""
    collection = db.query(Collection).filter(Collection.share_token == share_token).first()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared collection not found",
            headers={"error_code": "COLLECTION_NOT_FOUND"}
        )
    
    # Get recipes in this collection
    collection_recipes = db.query(CollectionRecipe).filter(
        CollectionRecipe.collection_id == collection.id
    ).all()
    
    recipes = []
    for cr in collection_recipes:
        recipe = db.query(Recipe).filter(Recipe.id == cr.recipe_id).first()
        if recipe:
            recipes.append(recipe_to_response(recipe))
    
    return {
        "id": str(collection.id),
        "user_id": str(collection.user_id),
        "name": collection.name,
        "description": collection.description,
        "cover_image_url": collection.cover_image_url,
        "parent_collection_id": str(collection.parent_collection_id) if collection.parent_collection_id else None,
        "nesting_level": collection.nesting_level or 0,
        "share_token": collection.share_token,
        "created_at": collection.created_at,
        "updated_at": collection.updated_at,
        "recipes": recipes
    }
