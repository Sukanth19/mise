# Fix: Filter Button Borders Disappearing on Hover

## Problem
When hovering over filter buttons (tags, dietary labels, allergens), the comic-style borders would disappear, making the buttons look inconsistent and less polished.

## Root Cause
The unselected button state was using `border-2 border-border` which conflicted with the `comic-border` class. When hovering, the background would change but the border styling was inconsistent.

**Before**:
```tsx
className={`... ${
  selected
    ? 'bg-primary text-primary-foreground comic-border shadow-md'
    : 'bg-muted text-muted-foreground border-2 border-border hover:bg-muted/80'
}`}
```

## Solution
Always apply the `comic-border` class to maintain consistent borders, and only change the background color on hover.

**After**:
```tsx
className={`... comic-border ${
  selected
    ? 'bg-primary text-primary-foreground shadow-md'
    : 'bg-muted text-muted-foreground hover:bg-primary/10'
}`}
```

## Changes Made

### Tags Buttons
- Always use `comic-border` class
- Unselected: `bg-muted` with `hover:bg-primary/10` (subtle orange tint on hover)
- Selected: `bg-primary` with shadow

### Dietary Labels Buttons
- Always use `comic-border` class
- Unselected: `bg-muted` with `hover:bg-success/10` (subtle green tint on hover)
- Selected: `bg-success` with shadow

### Allergen Buttons
- Always use `comic-border` class
- Unselected: `bg-muted` with `hover:bg-destructive/10` (subtle red tint on hover)
- Selected: `bg-destructive` with shadow

## Visual Improvements

### Before
- Borders would disappear on hover
- Inconsistent visual feedback
- Looked broken/buggy

### After
- Borders always visible and consistent
- Smooth color transitions on hover
- Subtle color tint matches the category (orange/green/red)
- Professional, polished appearance

## Comic Border Styling

The `comic-border` class provides:
```css
.comic-border {
  border: 4px solid hsl(var(--border));
  background: hsl(var(--card) / 0.7);
  backdrop-filter: blur(12px);
  box-shadow: 
    3px 3px 0 hsl(var(--border)),
    5px 5px 0 rgba(255, 255, 255, 0.08);
}
```

This creates:
- 4px solid border
- Semi-transparent background with blur
- Offset shadow for depth
- Comic book aesthetic

## Hover Effects

Each category now has a themed hover color:

- **Tags**: `hover:bg-primary/10` - Subtle orange (10% opacity)
- **Dietary**: `hover:bg-success/10` - Subtle green (10% opacity)
- **Allergens**: `hover:bg-destructive/10` - Subtle red (10% opacity)

The `/10` suffix means 10% opacity, creating a very subtle tint that:
- Provides visual feedback
- Doesn't overwhelm the design
- Matches the selected state color
- Maintains readability

## Testing

1. **Hover Test**:
   - Hover over any unselected filter button
   - Border should remain visible
   - Background should show subtle color tint
   - Transition should be smooth

2. **Selection Test**:
   - Click a filter button
   - Should change to full color with shadow
   - Border should remain consistent
   - Hover should still work on selected buttons

3. **Animation Test**:
   - Expand filters
   - Buttons should animate in with borders intact
   - Scale animation should work smoothly

## Files Modified

- `frontend/components/FilterPanel.tsx` - Fixed all three button types (tags, dietary, allergens)

## Related Classes

- `.comic-border` - Main border styling (always applied)
- `.comic-panel` - Panel container styling
- `.comic-button` - Button styling (used elsewhere)

## Browser Compatibility

- Works in all modern browsers
- Backdrop filter has fallback
- Box shadows are widely supported
- Transitions are smooth across browsers
