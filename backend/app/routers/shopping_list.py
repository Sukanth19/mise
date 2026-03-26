from fastapi import APIRouter, Depends, HTTPException, status, Header
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from app.database import mongodb
from app.schemas import (
    ShoppingListCreate,
    ShoppingListResponse,
    ShoppingListItemResponse,
    CustomItemCreate,
    ItemUpdateRequest
)
from app.services.shopping_list_service import ShoppingListGenerator
from app.services.auth_service import AuthService
from app.utils.objectid_utils import validate_objectid

router = APIRouter(prefix="/api/shopping-lists", tags=["shopping-lists"])


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


# ============================================================================
# Shopping List CRUD Endpoints (Subtask 13.1)
# ============================================================================

@router.post("", response_model=ShoppingListResponse, status_code=status.HTTP_201_CREATED)
async def create_shopping_list(
    shopping_list_data: ShoppingListCreate,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """
    Create a new shopping list from recipes or meal plan date range.
    Requirements: 18.1, 18.2
    """
    shopping_list = ShoppingListGenerator.create_shopping_list(db, user_id, shopping_list_data)
    
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid shopping list data. Check recipe IDs or meal plan dates.",
            headers={"error_code": "INVALID_SHOPPING_LIST"}
        )
    
    # Get items for response
    items = db.query(ShoppingListItem).filter(
        ShoppingListItem.shopping_list_id == shopping_list.id
    ).all()
    
    items_response = [
        ShoppingListItemResponse(
            id=item.id,
            shopping_list_id=item.shopping_list_id,
            ingredient_name=item.ingredient_name,
            quantity=item.quantity,
            category=item.category,
            is_checked=item.is_checked,
            is_custom=item.is_custom,
            recipe_id=item.recipe_id,
            created_at=item.created_at
        )
        for item in items
    ]
    
    return ShoppingListResponse(
        id=shopping_list.id,
        user_id=shopping_list.user_id,
        name=shopping_list.name,
        share_token=shopping_list.share_token,
        items=items_response,
        created_at=shopping_list.created_at
    )


@router.get("", response_model=List[ShoppingListResponse])
async def get_shopping_lists(
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get all shopping lists for the authenticated user.
    Requirements: 18.1, 18.2
    """
    shopping_lists = ShoppingListGenerator.get_user_shopping_lists(db, user_id)
    
    result = []
    for shopping_list in shopping_lists:
        # Get items for each list
        items = db.query(ShoppingListItem).filter(
            ShoppingListItem.shopping_list_id == shopping_list.id
        ).all()
        
        items_response = [
            ShoppingListItemResponse(
                id=item.id,
                shopping_list_id=item.shopping_list_id,
                ingredient_name=item.ingredient_name,
                quantity=item.quantity,
                category=item.category,
                is_checked=item.is_checked,
                is_custom=item.is_custom,
                recipe_id=item.recipe_id,
                created_at=item.created_at
            )
            for item in items
        ]
        
        result.append(ShoppingListResponse(
            id=shopping_list.id,
            user_id=shopping_list.user_id,
            name=shopping_list.name,
            share_token=shopping_list.share_token,
            items=items_response,
            created_at=shopping_list.created_at
        ))
    
    return result


@router.get("/{list_id}", response_model=ShoppingListResponse)
async def get_shopping_list(
    list_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get a specific shopping list with items.
    Requirements: 18.1, 18.2
    """
    # Validate ObjectId
    validate_objectid(list_id, "list_id")
    shopping_list = ShoppingListGenerator.get_shopping_list_by_id(db, list_id, user_id)
    
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found or access denied",
            headers={"error_code": "SHOPPING_LIST_NOT_FOUND"}
        )
    
    # Get items
    items = db.query(ShoppingListItem).filter(
        ShoppingListItem.shopping_list_id == shopping_list.id
    ).all()
    
    items_response = [
        ShoppingListItemResponse(
            id=item.id,
            shopping_list_id=item.shopping_list_id,
            ingredient_name=item.ingredient_name,
            quantity=item.quantity,
            category=item.category,
            is_checked=item.is_checked,
            is_custom=item.is_custom,
            recipe_id=item.recipe_id,
            created_at=item.created_at
        )
        for item in items
    ]
    
    return ShoppingListResponse(
        id=shopping_list.id,
        user_id=shopping_list.user_id,
        name=shopping_list.name,
        share_token=shopping_list.share_token,
        items=items_response,
        created_at=shopping_list.created_at
    )


@router.delete("/{list_id}", status_code=status.HTTP_200_OK)
async def delete_shopping_list(
    list_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """
    Delete a shopping list.
    Requirements: 18.1, 18.2
    """
    # Validate ObjectId
    validate_objectid(list_id, "list_id")
    success = ShoppingListGenerator.delete_shopping_list(db, list_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found or access denied",
            headers={"error_code": "SHOPPING_LIST_NOT_FOUND"}
        )
    
    return {"message": "Shopping list deleted successfully"}


# ============================================================================
# Shopping List Item Endpoints (Subtask 13.2)
# ============================================================================

@router.patch("/{list_id}/items/{item_id}", response_model=ShoppingListItemResponse)
async def update_item(
    list_id: str,
    item_id: str,
    update_data: ItemUpdateRequest,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """
    Update a shopping list item (check/uncheck).
    Requirements: 21.1, 21.2
    """
    # Validate ObjectIds
    validate_objectid(list_id, "list_id")
    validate_objectid(item_id, "item_id")
    item = ShoppingListGenerator.update_item_status(db, item_id, update_data.is_checked, user_id)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list item not found or access denied",
            headers={"error_code": "ITEM_NOT_FOUND"}
        )
    
    return ShoppingListItemResponse(
        id=item.id,
        shopping_list_id=item.shopping_list_id,
        ingredient_name=item.ingredient_name,
        quantity=item.quantity,
        category=item.category,
        is_checked=item.is_checked,
        is_custom=item.is_custom,
        recipe_id=item.recipe_id,
        created_at=item.created_at
    )


@router.post("/{list_id}/items", response_model=ShoppingListItemResponse, status_code=status.HTTP_201_CREATED)
async def add_custom_item(
    list_id: str,
    item_data: CustomItemCreate,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """
    Add a custom item to a shopping list.
    Requirements: 22.1, 22.3
    """
    # Validate ObjectId
    validate_objectid(list_id, "list_id")
    item = ShoppingListGenerator.add_custom_item(db, list_id, item_data, user_id)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found or access denied",
            headers={"error_code": "SHOPPING_LIST_NOT_FOUND"}
        )
    
    return ShoppingListItemResponse(
        id=item.id,
        shopping_list_id=item.shopping_list_id,
        ingredient_name=item.ingredient_name,
        quantity=item.quantity,
        category=item.category,
        is_checked=item.is_checked,
        is_custom=item.is_custom,
        recipe_id=item.recipe_id,
        created_at=item.created_at
    )


@router.delete("/{list_id}/items/{item_id}", status_code=status.HTTP_200_OK)
async def delete_item(
    list_id: str,
    item_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """
    Delete a shopping list item.
    Requirements: 22.1, 22.3
    """
    # Validate ObjectIds
    validate_objectid(list_id, "list_id")
    validate_objectid(item_id, "item_id")
    success = ShoppingListGenerator.delete_item(db, item_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list item not found or access denied",
            headers={"error_code": "ITEM_NOT_FOUND"}
        )
    
    return {"message": "Item deleted successfully"}


# ============================================================================
# Shopping List Sharing Endpoints (Subtask 13.3)
# ============================================================================

@router.post("/{list_id}/share")
async def share_shopping_list(
    list_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    user_id: str = Depends(get_current_user_id)
):
    """
    Generate a share link for a shopping list.
    Requirements: 23.1
    """
    # Validate ObjectId
    validate_objectid(list_id, "list_id")
    share_token = ShoppingListGenerator.generate_share_token(db, list_id, user_id)
    
    if not share_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found or access denied",
            headers={"error_code": "SHOPPING_LIST_NOT_FOUND"}
        )
    
    # Generate share URL (in production, this would be the actual domain)
    share_url = f"/api/shopping-lists/shared/{share_token}"
    
    return {
        "share_url": share_url,
        "share_token": share_token
    }


@router.get("/shared/{share_token}", response_model=ShoppingListResponse)
async def get_shared_list(
    share_token: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """
    Access a shared shopping list (no authentication required).
    Requirements: 23.2
    """
    shopping_list = ShoppingListGenerator.get_shared_list(db, share_token)
    
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared shopping list not found",
            headers={"error_code": "SHARED_LIST_NOT_FOUND"}
        )
    
    # Get items
    items = db.query(ShoppingListItem).filter(
        ShoppingListItem.shopping_list_id == shopping_list.id
    ).all()
    
    items_response = [
        ShoppingListItemResponse(
            id=item.id,
            shopping_list_id=item.shopping_list_id,
            ingredient_name=item.ingredient_name,
            quantity=item.quantity,
            category=item.category,
            is_checked=item.is_checked,
            is_custom=item.is_custom,
            recipe_id=item.recipe_id,
            created_at=item.created_at
        )
        for item in items
    ]
    
    return ShoppingListResponse(
        id=shopping_list.id,
        user_id=shopping_list.user_id,
        name=shopping_list.name,
        share_token=shopping_list.share_token,
        items=items_response,
        created_at=shopping_list.created_at
    )


@router.patch("/shared/{share_token}/items/{item_id}", response_model=ShoppingListItemResponse)
async def update_shared_item(
    share_token: str,
    item_id: str,
    update_data: ItemUpdateRequest,
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """
    Update an item in a shared shopping list (no authentication required).
    Requirements: 23.3
    """
    # Validate ObjectId
    validate_objectid(item_id, "item_id")
    item = ShoppingListGenerator.update_shared_item_status(db, share_token, item_id, update_data.is_checked)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared shopping list or item not found",
            headers={"error_code": "SHARED_ITEM_NOT_FOUND"}
        )
    
    return ShoppingListItemResponse(
        id=item.id,
        shopping_list_id=item.shopping_list_id,
        ingredient_name=item.ingredient_name,
        quantity=item.quantity,
        category=item.category,
        is_checked=item.is_checked,
        is_custom=item.is_custom,
        recipe_id=item.recipe_id,
        created_at=item.created_at
    )
