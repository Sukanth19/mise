# Troubleshooting Guide - Recipe Creation Issue

## Issue: "Create Recipe Not Working" / "No Recipes Yet"

### Root Cause
You need to be logged in to see and create recipes. The demo recipes were added to the database, but you need to authenticate first.

---

## Solution: Log In with Demo Account

### Step 1: Open the Application
Navigate to: http://localhost:3000

### Step 2: Log In
Use these credentials:
- **Username:** `demo`
- **Password:** `demo1234`

### Step 3: View Your Recipes
After logging in, you'll be redirected to the dashboard where you'll see 10 sample recipes:
- Classic Margherita Pizza
- Chicken Tikka Masala
- Avocado Toast with Poached Egg
- Beef Tacos
- Caesar Salad
- Chocolate Chip Cookies
- Greek Salad
- Pad Thai
- Banana Bread
- Caprese Salad

---

## How to Create a New Recipe

1. Click the **"CREATE RECIPE"** button (orange button in top right)
2. Fill in the form:
   - **Title** (required)
   - **Ingredients** (at least one required)
   - **Steps** (at least one required)
   - **Tags** (optional, comma-separated)
   - **Reference Link** (optional)
   - **Image** (optional)
3. Click **"SAVE RECIPE"**
4. You'll be redirected to the recipe detail page

---

## Verification Steps

### Check if Backend is Running
```bash
curl http://localhost:8000/
# Should return: {"message":"Recipe Saver API"}
```

### Check if Frontend is Running
```bash
curl http://localhost:3000/
# Should return HTML content
```

### Test API Authentication
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo1234"}'
# Should return: {"access_token":"...","token_type":"bearer"}
```

### Test Recipe Fetch (with auth)
```bash
# First get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo1234"}' | \
  grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

# Then fetch recipes
curl -X GET http://localhost:8000/api/recipes \
  -H "Authorization: Bearer $TOKEN"
# Should return array of 10+ recipes
```

---

## Common Issues

### Issue 1: "No recipes showing after login"
**Cause:** Browser cache or localStorage issue

**Solution:**
1. Open browser DevTools (F12)
2. Go to Application tab → Local Storage
3. Check if `auth_token` exists
4. If not, log out and log in again
5. Clear browser cache if needed

### Issue 2: "Create recipe button does nothing"
**Cause:** Not logged in or token expired

**Solution:**
1. Check browser console (F12) for errors
2. Log out and log in again
3. Token expires after 24 hours

### Issue 3: "401 Unauthorized error"
**Cause:** Invalid or expired token

**Solution:**
1. Log out (click SIGN OUT button)
2. Log in again with demo credentials
3. Token will be refreshed

### Issue 4: "CORS error in console"
**Cause:** Backend CORS configuration

**Solution:**
Backend is configured to allow `http://localhost:3000`. If you're using a different port, update `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:YOUR_PORT"],
    ...
)
```

---

## Quick Test Script

Run this to verify everything works:

```bash
cd backend
source venv/bin/activate

# Test login
echo "Testing login..."
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo1234"}' | \
  grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ Login failed"
  exit 1
fi
echo "✓ Login successful"

# Test recipe fetch
echo "Testing recipe fetch..."
RECIPES=$(curl -s -X GET http://localhost:8000/api/recipes \
  -H "Authorization: Bearer $TOKEN")

if echo "$RECIPES" | grep -q "Classic Margherita Pizza"; then
  echo "✓ Recipes found"
  echo "✓ Recipe count: $(echo $RECIPES | grep -o '"id":' | wc -l)"
else
  echo "❌ No recipes found"
  exit 1
fi

# Test recipe creation
echo "Testing recipe creation..."
NEW_RECIPE=$(curl -s -X POST http://localhost:8000/api/recipes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"Test Recipe","ingredients":["test"],"steps":["test"]}')

if echo "$NEW_RECIPE" | grep -q '"title":"Test Recipe"'; then
  echo "✓ Recipe creation works"
else
  echo "❌ Recipe creation failed"
  exit 1
fi

echo ""
echo "✓ All tests passed!"
echo "✓ You can now use the application at http://localhost:3000"
echo "✓ Login with username: demo, password: demo1234"
```

---

## Still Having Issues?

1. **Restart both servers:**
   ```bash
   # Terminal 1 - Backend
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload
   
   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

2. **Check browser console** (F12) for JavaScript errors

3. **Check backend logs** in the terminal running uvicorn

4. **Verify database has recipes:**
   ```bash
   cd backend
   source venv/bin/activate
   python -c "from app.database import SessionLocal; from app.models import Recipe; db = SessionLocal(); print(f'Total recipes: {db.query(Recipe).count()}'); db.close()"
   ```

---

## Creating Additional Users

If you want to create your own account instead of using demo:

1. Go to http://localhost:3000
2. Click "REGISTER HERE"
3. Enter username and password (min 8 characters)
4. You'll be logged in automatically
5. Start creating your own recipes!

---

## Summary

**The application is working correctly!** You just need to:
1. ✅ Open http://localhost:3000
2. ✅ Log in with username: `demo`, password: `demo1234`
3. ✅ See your 10 sample recipes
4. ✅ Click "CREATE RECIPE" to add new ones

The backend API is functioning properly, and recipe creation works as expected.
