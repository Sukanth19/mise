# Favicon Cache Fix

The favicon has been updated to the orange "MISE" logo, but your browser is showing the old purple one due to aggressive caching.

## Quick Fix - Clear Browser Cache

### Chrome/Edge:
1. Open DevTools (F12)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

OR

1. Go to `chrome://settings/clearBrowserData`
2. Select "Cached images and files"
3. Click "Clear data"

### Firefox:
1. Press `Ctrl+Shift+Delete` (Windows/Linux) or `Cmd+Shift+Delete` (Mac)
2. Select "Cache"
3. Click "Clear Now"

### Safari:
1. Go to Safari > Preferences > Advanced
2. Enable "Show Develop menu"
3. Develop > Empty Caches

## Alternative: Force Refresh

Visit these URLs directly in your browser to force reload:
- http://localhost:3000/favicon.svg?v=2
- http://localhost:3000/favicon.ico?v=2

Then refresh your main page.

## Verify the Fix

After clearing cache:
1. Refresh the page (Ctrl+F5 or Cmd+Shift+R)
2. Check the browser tab - you should see the orange logo
3. The favicon should now match the login/register page logos

## Technical Details

The favicon.svg file in `frontend/public/` is already updated with the orange color (#FF8C00).
The issue is purely browser caching. The `?v=2` parameter in the layout.tsx file helps with cache busting.
