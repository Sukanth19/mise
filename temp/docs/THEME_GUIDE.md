# Theme System Guide

This application features a Vesper-inspired theme system with dark and light modes.

## Features

- **Dark Theme**: Vesper-inspired dark theme with deep blacks and purple/pink accents
- **Light Theme**: Clean light version of Vesper with subtle grays
- **Theme Persistence**: User's theme preference is saved to localStorage
- **System Preference Detection**: Automatically detects user's OS theme preference on first visit
- **Smooth Transitions**: All theme changes are smooth and instant

## Theme Colors

### Dark Theme (Vesper Dark)
- Background: Deep dark gray (#101010)
- Foreground: Light gray text
- Primary: Purple (#8B5CF6)
- Secondary: Pink (#EC4899)
- Accent: Subtle dark gray for hover states

### Light Theme (Vesper Light)
- Background: Off-white (#FAFAFA)
- Foreground: Dark gray text
- Primary: Purple (#8B5CF6)
- Secondary: Pink (#EC4899)
- Accent: Light gray for hover states

## Usage

### Using Theme Colors in Components

All theme colors are available as Tailwind CSS classes:

```tsx
// Background and text
<div className="bg-background text-foreground">

// Primary button
<button className="bg-primary text-primary-foreground">

// Card
<div className="bg-card border border-border">

// Muted text
<p className="text-muted-foreground">

// Destructive/error
<div className="text-destructive">
```

### Accessing Theme Context

```tsx
import { useTheme } from '@/contexts/ThemeContext';

function MyComponent() {
  const { theme, toggleTheme } = useTheme();
  
  return (
    <button onClick={toggleTheme}>
      Current theme: {theme}
    </button>
  );
}
```

## Components

- **Header**: Contains the theme toggle button and sign-out functionality
- **ThemeProvider**: Wraps the entire app and manages theme state
- **Favicon**: Custom gradient icon matching the theme colors

## Customization

To customize theme colors, edit `frontend/app/globals.css`:

```css
:root {
  --primary: 262 83% 58%; /* HSL values */
  /* ... other colors */
}

[data-theme="dark"] {
  --primary: 262 83% 58%;
  /* ... other colors */
}
```

All colors use HSL format for better manipulation and consistency.
