# Fix: Unable to Add Recipes to Collections

## Problem
Users were unable to add recipes to collections, receiving two types of errors:
1. "Bad Request: One or more recipes not found or access denied"
2. "Validation Error: [object Object]"

## Root Causes

### 1. Type Mismatch in Backend API
The backend endpoint was expecting `recipe_ids: List[str]` but then converting them to integers. This was unnecessary since the frontend already sends numbers, and it could cause issues with type validation.

**File**: `backend/app/routers/collections.py`

**Before**:
```python
recipe_ids: List[str] = Body(..., embed=True)
# Convert recipe IDs to integers
recipe_id_ints = [int(rid) for rid in recipe_ids]
```

**After**:
```python
recipe_ids: List[int] = Body(..., embed=True)
# No conversion needed - use recipe_ids directly
```

### 2. Poor Error Messages
When recipes weren't found, the error message was generic and didn't specify which recipe IDs were missing.

**Before**:
```python
if len(recipes) != len(recipe_id_ints):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="One or more recipes not found or access denied"
    )
```

**After**:
```python
found_recipe_ids = {recipe.id for recipe in recipes}
missing_recipe_ids = [rid for rid in recipe_ids if rid not in found_recipe_ids]

if missing_recipe_ids:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Recipes with IDs {missing_recipe_ids} not found or you don't have access to them"
    )
```

### 3. Frontend Error Display Issue
The API client wasn't handling cases where the error detail might be an object instead of a string, resulting in "[object Object]" being displayed.

**File**: `frontend/lib/api.ts`

**Before**:
```typescript
const errorMessage = error.detail || `HTTP ${response.status}`;
```

**After**:
```typescript
let errorMessage: string;
if (typeof error.detail === 'string') {
  errorMessage = error.detail;
} else if (typeof error.detail === 'object' && error.detail !== null) {
  errorMessage = JSON.stringify(error.detail);
} else {
  errorMessage = `HTTP ${response.status}`;
}
```

## Changes Made

1. **backend/app/routers/collections.py**:
   - Changed `recipe_ids` parameter type from `List[str]` to `List[int]`
   - Removed unnecessary string-to-int conversion
   - Added detailed error messages showing which recipe IDs are missing
   - Used set operations for more efficient validation

2. **backend/app/routers/recipes.py**:
   - Removed unnecessary string-to-int conversion in bulk delete endpoint
   - Added detailed error messages showing which recipe IDs are missing
   - Used set operations for more efficient validation

3. **frontend/lib/api.ts**:
   - Added proper handling for error details that are objects
   - Improved error message formatting

## Testing

To test the fix:

1. Start the backend server:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. Start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. Try adding a recipe to a collection:
   - Create a recipe
   - Create a collection
   - Try to add the recipe to the collection
   - The operation should succeed

4. Test error cases:
   - Try to add a non-existent recipe ID (should show specific error)
   - Try to add someone else's recipe (should show access denied)

## Additional Notes

The most common cause of this error is:
- **Recipe doesn't belong to the logged-in user**: The backend validates that all recipes being added belong to the authenticated user
- **Recipe ID doesn't exist**: The recipe may have been deleted or the ID is incorrect
- **Authentication issues**: Make sure the user is properly logged in

If you continue to see errors after this fix, check:
1. The recipe exists in the database
2. The recipe's `user_id` matches the authenticated user's ID
3. The collection's `user_id` matches the authenticated user's ID
