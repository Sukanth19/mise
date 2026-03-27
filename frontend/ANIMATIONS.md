# Animation Components Guide

This document describes the animation components available in the application.

## LoginAnimation

A specialized animation component for login/authentication flows.

### Usage

```tsx
import LoginAnimation from '@/components/LoginAnimation';

// Display during login
<LoginAnimation />
```

### Features
- Animated chef hat with rotation
- Sparkle effects
- "LOGGING IN" text with animated dots
- Progress bar animation
- Automatically integrated into `AuthForm` component

## LoadingSpinner

A versatile loading spinner with multiple variants for different contexts.

### Usage

```tsx
import LoadingSpinner from '@/components/LoadingSpinner';

// Default variant (spinning utensils)
<LoadingSpinner size="md" text="Loading..." />

// Recipe-specific variant (cooking pot)
<LoadingSpinner variant="recipe" size="lg" text="Cooking up your recipes..." />

// Collection variant (book/folder)
<LoadingSpinner variant="collection" size="md" text="Loading collections..." />

// Minimal variant (simple spinner)
<LoadingSpinner variant="minimal" size="sm" />
```

### Props

- `size`: `'sm' | 'md' | 'lg'` - Size of the spinner (default: `'md'`)
- `text`: `string` - Optional loading text to display
- `variant`: `'default' | 'recipe' | 'collection' | 'minimal'` - Animation style (default: `'default'`)

### Variants

1. **default**: Spinning fork and spoon with orbiting dots
2. **recipe**: Animated cooking pot with steam bubbles
3. **collection**: Rotating book/folder icon
4. **minimal**: Simple circular spinner

## LoadingSkeleton

Skeleton loading components for different content types (already existing).

### Usage

```tsx
import { 
  RecipeGridSkeleton, 
  RecipeDetailSkeleton,
  CollectionGridSkeleton,
  MealPlanGridSkeleton 
} from '@/components/LoadingSkeleton';

// Recipe grid skeleton
<RecipeGridSkeleton count={8} />

// Recipe detail skeleton
<RecipeDetailSkeleton />

// Collection grid skeleton
<CollectionGridSkeleton count={6} />

// Meal plan grid skeleton
<MealPlanGridSkeleton count={7} />
```

## CSS Animation Classes

Available animation utility classes in `globals.css`:

- `animate-shake` - Shake effect (used for errors)
- `animate-pulse-scale` - Gentle pulsing scale effect
- `animate-slide-up` - Slide up from bottom
- `animate-pop-in` - Pop in with scale effect
- `animate-spin` - Continuous rotation
- `animate-bounce-subtle` - Subtle bounce effect
- `animate-fade-in` - Fade in effect

### Usage

```tsx
<div className="animate-pop-in">
  Content appears with pop effect
</div>

<div className="animate-shake">
  Error message shakes
</div>
```

## Best Practices

1. **Login/Auth**: Use `LoginAnimation` for authentication flows
2. **Recipe Loading**: Use `LoadingSpinner` with `variant="recipe"` or `RecipeGridSkeleton`
3. **Collection Loading**: Use `LoadingSpinner` with `variant="collection"` or `CollectionGridSkeleton`
4. **General Loading**: Use `LoadingSpinner` with `variant="default"` or `variant="minimal"`
5. **Content Placeholders**: Use skeleton components for better perceived performance

## Examples

### In a Recipe Page

```tsx
'use client';

import { useState, useEffect } from 'react';
import LoadingSpinner from '@/components/LoadingSpinner';
import { RecipeGridSkeleton } from '@/components/LoadingSkeleton';

export default function RecipesPage() {
  const [loading, setLoading] = useState(true);
  const [recipes, setRecipes] = useState([]);

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        {/* Option 1: Use spinner */}
        <LoadingSpinner variant="recipe" size="lg" text="Loading recipes..." />
        
        {/* Option 2: Use skeleton (better for grid layouts) */}
        <RecipeGridSkeleton count={8} />
      </div>
    );
  }

  return <div>{/* Recipe content */}</div>;
}
```

### In a Button

```tsx
<button 
  className="comic-button"
  disabled={isSubmitting}
>
  {isSubmitting ? (
    <LoadingSpinner variant="minimal" size="sm" />
  ) : (
    'Submit'
  )}
</button>
```

### Custom Loading State

```tsx
<div className="flex flex-col items-center gap-4 animate-fade-in">
  <LoadingSpinner variant="default" size="lg" />
  <p className="comic-text animate-pulse-scale">
    Preparing your meal plan...
  </p>
</div>
```
