# Fix: Recipe Count Not Updating in Collections

## Problem
Collections were showing "0 RECIPES" even after adding recipes to them. The recipe count was not being displayed or updated.

## Root Cause
The `CollectionResponse` schema in the backend was missing the `recipe_count` field, even though the backend code was calculating it and trying to include it in responses.

## Solution

### 1. Added recipe_count to CollectionResponse Schema
**File**: `backend/app/schemas.py`

```python
class CollectionResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    cover_image_url: Optional[str]
    parent_collection_id: Optional[int]
    nesting_level: int
    share_token: Optional[str]
    recipe_count: int = 0  # ADDED THIS FIELD
    created_at: datetime
    updated_at: datetime
```

### 2. Fixed ID Type Consistency
The backend was converting IDs to strings in some places but the schema expected integers. Fixed all response functions to use integers consistently.

**File**: `backend/app/routers/collections.py`

Changed from:
```python
id=str(collection.id)
user_id=str(collection.user_id)
```

To:
```python
id=collection.id
user_id=collection.user_id
```

### 3. Updated Frontend Types
**File**: `frontend/types/index.ts`

Changed Collection interface from:
```typescript
id: number | string;
user_id: number | string;
```

To:
```typescript
id: number;
user_id: number;
```

This ensures type consistency between frontend and backend.

### 4. Added Missing Recipe Fields
**File**: `backend/app/schemas.py`

Added missing fields to RecipeResponse:
```python
source_recipe_id: Optional[int] = None
source_author_id: Optional[int] = None
```

## Files Modified

### Backend
1. `backend/app/schemas.py`
   - Added `recipe_count` field to `CollectionResponse`
   - Added `source_recipe_id` and `source_author_id` to `RecipeResponse`

2. `backend/app/routers/collections.py`
   - Fixed `collection_to_response()` to use integer IDs
   - Fixed `recipe_to_response()` to use integer IDs
   - Fixed `get_collection()` to include `recipe_count` and use integer IDs

### Frontend
1. `frontend/types/index.ts`
   - Changed Collection IDs from `number | string` to `number`

2. `frontend/components/AddToCollectionModal.tsx`
   - Updated types to use `number` instead of `number | string`

## How Recipe Count Works

The backend calculates recipe count in multiple places:

1. **GET /api/collections** (list all collections)
   ```python
   recipe_count = db.query(CollectionRecipe).filter(
       CollectionRecipe.collection_id == collection.id
   ).count()
   ```

2. **GET /api/collections/{id}** (get single collection)
   ```python
   recipe_count = len(recipes)  # Count of recipes in the collection
   ```

3. **PUT /api/collections/{id}** (update collection)
   ```python
   recipe_count = db.query(CollectionRecipe).filter(
       CollectionRecipe.collection_id == collection.id
   ).count()
   ```

4. **POST /api/collections** (create collection)
   ```python
   recipe_count = 0  # New collections start with 0 recipes
   ```

## Testing

1. **Restart the backend server**:
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Test recipe count display**:
   - Go to `/collections` page
   - Collections should show the correct number of recipes
   - Add a recipe to a collection
   - The count should update immediately

3. **Verify in different views**:
   - Collections list page: Shows "X RECIPES"
   - Collection detail page: Shows recipe count
   - Collection cards: Display recipe count

## Expected Behavior

- New collections show "0 RECIPES"
- After adding recipes, count updates to "1 RECIPE", "2 RECIPES", etc.
- Count updates immediately after adding/removing recipes
- Count is consistent across all views

## Common Issues

### Count still shows 0 after adding recipes
- Make sure you restarted the backend server
- Clear browser cache and refresh
- Check browser console for errors

### Type errors in frontend
- Make sure you restarted the frontend dev server
- TypeScript should now recognize `recipe_count` as a number

## Related Fixes

This fix is part of a series of collection-related fixes:
- `COLLECTION_RECIPE_FIX.md` - Backend API type handling
- `ADD_RECIPES_TO_COLLECTION_FIX.md` - Modal component fix
- `RECIPE_COUNT_FIX.md` - This fix (recipe count display)
