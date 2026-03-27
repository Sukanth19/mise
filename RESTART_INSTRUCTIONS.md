# How to Apply the Fix

## Quick Start

1. **Restart the Backend Server**:
   ```bash
   cd backend
   # If the server is running, stop it (Ctrl+C)
   # Then start it again:
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Restart the Frontend** (if needed):
   ```bash
   cd frontend
   # If the dev server is running, stop it (Ctrl+C)
   # Then start it again:
   npm run dev
   ```

3. **Test the Fix**:
   - Log in to your account
   - Navigate to a recipe (e.g., "JOLLOF RICE")
   - Click "ADD TO COLLECTION" button
   - Select a collection (e.g., "AFRICAN")
   - Click "ADD TO 1 COLLECTION"
   - The recipe should be added successfully!

## What Was Fixed

The issue was caused by:
1. Type mismatch in the backend API (expecting strings but should accept integers)
2. Poor error messages that didn't specify which recipes were missing
3. Frontend displaying "[object Object]" instead of proper error messages

All three issues have been fixed.

## If You Still See Errors

If you still get "Recipes with IDs [X] not found or you don't have access to them":

1. **Check Recipe Ownership**: Make sure the recipe belongs to your account
   - The recipe must have been created by you
   - You cannot add other users' recipes to your collections

2. **Check Collection Ownership**: Make sure the collection belongs to your account
   - The collection must have been created by you

3. **Verify Recipe Exists**: Make sure the recipe hasn't been deleted
   - Try viewing the recipe first to confirm it exists

4. **Check Authentication**: Make sure you're logged in
   - If your session expired, log out and log back in

## Database Check (Optional)

To verify your recipes and collections in the database:

```bash
# Check your recipes
sqlite3 test.db "SELECT id, user_id, title FROM recipes WHERE user_id = YOUR_USER_ID;"

# Check your collections
sqlite3 test.db "SELECT id, user_id, name FROM collections WHERE user_id = YOUR_USER_ID;"

# Check collection_recipes relationships
sqlite3 test.db "SELECT * FROM collection_recipes;"
```

Replace `YOUR_USER_ID` with your actual user ID (usually 1 for the first user).
