# Fix: Recipe Rating Not Showing on Recipe Cards

## Problem
Recipe cards on the dashboard were showing empty star outlines even though the recipes had been rated. The rating was visible on the recipe detail page but not on the recipe cards in the grid view.

## Root Cause
The `RecipeCard` component had a placeholder `fetchAverageRating` function that always set the rating to 0:

```typescript
const fetchAverageRating = async () => {
  try {
    setIsLoadingRating(true);
    // This would need a backend endpoint to get average rating
    // For now, we'll just set it to 0
    setAverageRating(0);
  } catch (err) {
    setAverageRating(0);
  } finally {
    setIsLoadingRating(false);
  }
};
```

The comment indicated that a backend endpoint was needed, but the endpoint already existed at `GET /api/recipes/{recipe_id}/rating`.

## Solution

### Updated RecipeCard Component
**File**: `frontend/components/RecipeCard.tsx`

Changed the `fetchAverageRating` function to actually fetch the user's rating:

```typescript
const fetchAverageRating = async () => {
  try {
    setIsLoadingRating(true);
    const response = await apiClient<{ rating: number }>(`/api/recipes/${recipe.id}/rating`);
    setAverageRating(response.rating);
  } catch (err) {
    // No rating found for this recipe by the current user
    setAverageRating(0);
  } finally {
    setIsLoadingRating(false);
  }
};
```

Also updated the display text to be clearer:

```typescript
<span className="text-xs text-muted-foreground font-bold">
  {averageRating > 0 ? 'YOUR RATING' : 'NOT RATED'}
</span>
```

## Backend Endpoint

The existing endpoint that provides the rating:

**Endpoint**: `GET /api/recipes/{recipe_id}/rating`

**Response**:
```json
{
  "rating": 5
}
```

**Error**: Returns 404 if the user hasn't rated the recipe yet.

## How It Works

1. When a recipe card is rendered, it calls `fetchAverageRating()`
2. The function makes a GET request to `/api/recipes/{recipe_id}/rating`
3. If the user has rated the recipe, it returns the rating (1-5)
4. If the user hasn't rated it, the endpoint returns 404 and the rating is set to 0
5. The stars are displayed based on the rating value
6. Text shows "YOUR RATING" if rated, "NOT RATED" if not

## Display Behavior

- **Rated recipes**: Shows filled stars (1-5) with "YOUR RATING" text
- **Unrated recipes**: Shows empty stars with "NOT RATED" text
- **Loading**: Shows animated placeholder boxes while fetching

## Testing

1. **Restart the frontend** (backend doesn't need changes):
   ```bash
   cd frontend
   npm run dev
   ```

2. **Test rated recipe**:
   - Go to dashboard
   - Find a recipe you've rated
   - Should show filled stars matching your rating
   - Should show "YOUR RATING" text

3. **Test unrated recipe**:
   - Find a recipe you haven't rated
   - Should show empty stars
   - Should show "NOT RATED" text

4. **Test rating update**:
   - Rate a recipe from the detail page
   - Go back to dashboard
   - Rating should now appear on the card

## Notes

- This shows the **user's own rating**, not an average of all ratings
- Each user sees their own rating on recipe cards
- The rating is fetched individually for each recipe card
- If you want to show average ratings instead, you'd need a different backend endpoint

## Files Modified

- `frontend/components/RecipeCard.tsx` - Fixed rating fetch and display

## Related Components

- `RecipeDetail.tsx` - Shows and allows editing the user's rating
- `RatingStars.tsx` - Displays the star rating UI
- `backend/app/routers/recipes.py` - Provides the rating endpoint
