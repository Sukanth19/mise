# Fix: Add Recipes to Collection Modal Issue

## Problem
When clicking "ADD RECIPES" button in a collection detail page, the modal was showing collections to select instead of recipes to add. The button showed "ADD TO 0 COLLECTIONS" and was disabled because the wrong modal was being used.

## Root Cause
The collection detail page was using `AddToCollectionModal` which is designed for:
- **Selecting which collections to add a recipe TO**

But what was needed was:
- **Selecting which recipes to add TO a collection**

These are opposite use cases!

## Solution
Created a new modal component `AddRecipesToCollectionModal` specifically for selecting recipes to add to a collection.

### New Component: AddRecipesToCollectionModal
**File**: `frontend/components/AddRecipesToCollectionModal.tsx`

Features:
- Shows a list of available recipes (recipes not already in the collection)
- Allows multi-select with checkboxes
- Includes search functionality to filter recipes
- Shows recipe thumbnails
- Displays recipe tags
- Shows count of selected recipes in the submit button

### Updated Collection Detail Page
**File**: `frontend/app/collections/[id]/page.tsx`

Changed from:
```tsx
<AddToCollectionModal
  isOpen={showAddRecipesModal}
  onClose={() => setShowAddRecipesModal(false)}
  onSubmit={async (recipeIds) => {
    await handleAddRecipes(recipeIds);
  }}
  collections={[collection]}  // WRONG: showing collections
  initialSelectedIds={[collection.id]}
/>
```

To:
```tsx
<AddRecipesToCollectionModal
  isOpen={showAddRecipesModal}
  onClose={() => setShowAddRecipesModal(false)}
  onSubmit={async (recipeIds) => {
    await handleAddRecipes(recipeIds);
  }}
  availableRecipes={availableRecipes}  // CORRECT: showing recipes
  collectionName={collection.name}
/>
```

## Modal Usage Guide

### AddToCollectionModal
Use when you have a recipe and want to add it to one or more collections.

**Example**: Recipe detail page, dashboard bulk actions
```tsx
<AddToCollectionModal
  collections={allCollections}
  onSubmit={(collectionIds) => addRecipeToCollections(recipe.id, collectionIds)}
/>
```

### AddRecipesToCollectionModal
Use when you have a collection and want to add one or more recipes to it.

**Example**: Collection detail page
```tsx
<AddRecipesToCollectionModal
  availableRecipes={recipesNotInCollection}
  onSubmit={(recipeIds) => addRecipesToCollection(collection.id, recipeIds)}
/>
```

## Testing

1. Navigate to a collection (e.g., `/collections/1`)
2. Click "ADD RECIPES" button
3. Modal should show:
   - List of recipes not already in the collection
   - Search bar to filter recipes
   - Checkboxes to select recipes
   - Button showing "ADD X RECIPE(S)"
4. Select one or more recipes
5. Click the add button
6. Recipes should be added to the collection

## Files Changed

1. **Created**: `frontend/components/AddRecipesToCollectionModal.tsx`
   - New modal for selecting recipes to add to a collection

2. **Modified**: `frontend/app/collections/[id]/page.tsx`
   - Changed import from `AddToCollectionModal` to `AddRecipesToCollectionModal`
   - Updated modal props to pass `availableRecipes` instead of `collections`
