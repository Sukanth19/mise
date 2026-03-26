#!/bin/bash
# Quick API test script

echo "=========================================="
echo "Recipe Saver API Test"
echo "=========================================="
echo ""

# Test 1: Check if backend is running
echo "1. Testing backend connection..."
BACKEND_RESPONSE=$(curl -s http://localhost:8000/)
if echo "$BACKEND_RESPONSE" | grep -q "Recipe Saver API"; then
  echo "   ✓ Backend is running"
else
  echo "   ✗ Backend is not responding"
  echo "   Please start backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
  exit 1
fi
echo ""

# Test 2: Login
echo "2. Testing login..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo1234"}')

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "   ✗ Login failed"
  echo "   Response: $LOGIN_RESPONSE"
  exit 1
fi
echo "   ✓ Login successful"
echo "   Token: ${TOKEN:0:20}..."
echo ""

# Test 3: Fetch recipes
echo "3. Testing recipe fetch..."
RECIPES=$(curl -s -X GET http://localhost:8000/api/recipes \
  -H "Authorization: Bearer $TOKEN")

RECIPE_COUNT=$(echo "$RECIPES" | grep -o '"id":' | wc -l)

if [ "$RECIPE_COUNT" -gt 0 ]; then
  echo "   ✓ Found $RECIPE_COUNT recipes"
  echo ""
  echo "   Sample recipes:"
  echo "$RECIPES" | grep -o '"title":"[^"]*"' | head -5 | sed 's/"title":"//g' | sed 's/"//g' | sed 's/^/     - /'
else
  echo "   ✗ No recipes found"
  echo "   Run: python add_sample_recipes.py"
  exit 1
fi
echo ""

# Test 4: Create recipe
echo "4. Testing recipe creation..."
NEW_RECIPE=$(curl -s -X POST http://localhost:8000/api/recipes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title":"API Test Recipe",
    "ingredients":["Test ingredient 1","Test ingredient 2"],
    "steps":["Test step 1","Test step 2"],
    "tags":["test","api"]
  }')

NEW_RECIPE_ID=$(echo "$NEW_RECIPE" | grep -o '"id":[0-9]*' | cut -d':' -f2)

if [ -n "$NEW_RECIPE_ID" ]; then
  echo "   ✓ Recipe created successfully (ID: $NEW_RECIPE_ID)"
  
  # Clean up - delete test recipe
  curl -s -X DELETE "http://localhost:8000/api/recipes/$NEW_RECIPE_ID" \
    -H "Authorization: Bearer $TOKEN" > /dev/null
  echo "   ✓ Test recipe cleaned up"
else
  echo "   ✗ Recipe creation failed"
  echo "   Response: $NEW_RECIPE"
  exit 1
fi
echo ""

echo "=========================================="
echo "✓ All tests passed!"
echo "=========================================="
echo ""
echo "Your application is working correctly!"
echo ""
echo "To use the web interface:"
echo "  1. Open: http://localhost:3000"
echo "  2. Login with:"
echo "     Username: demo"
echo "     Password: demo1234"
echo "  3. View your recipes and create new ones"
echo ""
echo "=========================================="
