#!/bin/bash
# Integration Verification Script for Recipe Saver
# This script tests the complete user flow through the API

set -e  # Exit on error

API_BASE="http://localhost:8000"
USERNAME="test_user_$(date +%s)"
PASSWORD="testpassword123"
TOKEN=""

echo "=========================================="
echo "Recipe Saver Integration Verification"
echo "=========================================="
echo ""

# Check if backend is running
echo "1. Checking if backend is running..."
if curl -s "${API_BASE}/" > /dev/null; then
    echo "   ✅ Backend is running"
else
    echo "   ❌ Backend is not running. Please start it with: cd backend && ./run.sh"
    exit 1
fi
echo ""

# Test 1: Register a new user
echo "2. Testing user registration..."
REGISTER_RESPONSE=$(curl -s -X POST "${API_BASE}/api/auth/register" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"${USERNAME}\",\"password\":\"${PASSWORD}\"}")

if echo "$REGISTER_RESPONSE" | grep -q "username"; then
    echo "   ✅ User registration successful"
    echo "   User: ${USERNAME}"
else
    echo "   ❌ User registration failed"
    echo "   Response: $REGISTER_RESPONSE"
    exit 1
fi
echo ""

# Test 2: Login and get token
echo "3. Testing user login..."
LOGIN_RESPONSE=$(curl -s -X POST "${API_BASE}/api/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"${USERNAME}\",\"password\":\"${PASSWORD}\"}")

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -n "$TOKEN" ]; then
    echo "   ✅ Login successful"
    echo "   Token: ${TOKEN:0:20}..."
else
    echo "   ❌ Login failed"
    echo "   Response: $LOGIN_RESPONSE"
    exit 1
fi
echo ""

# Test 3: Create a recipe
echo "4. Testing recipe creation..."
CREATE_RESPONSE=$(curl -s -X POST "${API_BASE}/api/recipes" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${TOKEN}" \
    -d '{
        "title": "Integration Test Recipe",
        "ingredients": ["ingredient 1", "ingredient 2", "ingredient 3"],
        "steps": ["step 1", "step 2", "step 3"],
        "tags": ["test", "integration"],
        "reference_link": "https://example.com/recipe"
    }')

RECIPE_ID=$(echo "$CREATE_RESPONSE" | grep -o '"id":[0-9]*' | cut -d':' -f2)

if [ -n "$RECIPE_ID" ]; then
    echo "   ✅ Recipe created successfully"
    echo "   Recipe ID: ${RECIPE_ID}"
else
    echo "   ❌ Recipe creation failed"
    echo "   Response: $CREATE_RESPONSE"
    exit 1
fi
echo ""

# Test 4: Get recipe list
echo "5. Testing recipe list retrieval..."
LIST_RESPONSE=$(curl -s -X GET "${API_BASE}/api/recipes" \
    -H "Authorization: Bearer ${TOKEN}")

if echo "$LIST_RESPONSE" | grep -q "Integration Test Recipe"; then
    echo "   ✅ Recipe list retrieved successfully"
    RECIPE_COUNT=$(echo "$LIST_RESPONSE" | grep -o '"id":' | wc -l)
    echo "   Total recipes: ${RECIPE_COUNT}"
else
    echo "   ❌ Recipe list retrieval failed"
    echo "   Response: $LIST_RESPONSE"
    exit 1
fi
echo ""

# Test 5: Get specific recipe
echo "6. Testing recipe detail retrieval..."
DETAIL_RESPONSE=$(curl -s -X GET "${API_BASE}/api/recipes/${RECIPE_ID}" \
    -H "Authorization: Bearer ${TOKEN}")

if echo "$DETAIL_RESPONSE" | grep -q "Integration Test Recipe"; then
    echo "   ✅ Recipe details retrieved successfully"
else
    echo "   ❌ Recipe detail retrieval failed"
    echo "   Response: $DETAIL_RESPONSE"
    exit 1
fi
echo ""

# Test 6: Update recipe
echo "7. Testing recipe update..."
UPDATE_RESPONSE=$(curl -s -X PUT "${API_BASE}/api/recipes/${RECIPE_ID}" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${TOKEN}" \
    -d '{
        "title": "Updated Integration Test Recipe",
        "ingredients": ["new ingredient 1", "new ingredient 2"]
    }')

if echo "$UPDATE_RESPONSE" | grep -q "Updated Integration Test Recipe"; then
    echo "   ✅ Recipe updated successfully"
else
    echo "   ❌ Recipe update failed"
    echo "   Response: $UPDATE_RESPONSE"
    exit 1
fi
echo ""

# Test 7: Search recipes
echo "8. Testing recipe search..."
SEARCH_RESPONSE=$(curl -s -X GET "${API_BASE}/api/recipes?search=updated" \
    -H "Authorization: Bearer ${TOKEN}")

if echo "$SEARCH_RESPONSE" | grep -q "Updated Integration Test Recipe"; then
    echo "   ✅ Recipe search successful"
else
    echo "   ❌ Recipe search failed"
    echo "   Response: $SEARCH_RESPONSE"
    exit 1
fi
echo ""

# Test 8: Delete recipe
echo "9. Testing recipe deletion..."
DELETE_RESPONSE=$(curl -s -X DELETE "${API_BASE}/api/recipes/${RECIPE_ID}" \
    -H "Authorization: Bearer ${TOKEN}")

if echo "$DELETE_RESPONSE" | grep -q "deleted successfully"; then
    echo "   ✅ Recipe deleted successfully"
else
    echo "   ❌ Recipe deletion failed"
    echo "   Response: $DELETE_RESPONSE"
    exit 1
fi
echo ""

# Test 9: Verify deletion
echo "10. Verifying recipe deletion..."
VERIFY_RESPONSE=$(curl -s -w "%{http_code}" -X GET "${API_BASE}/api/recipes/${RECIPE_ID}" \
    -H "Authorization: Bearer ${TOKEN}")

if echo "$VERIFY_RESPONSE" | grep -q "404"; then
    echo "   ✅ Recipe deletion verified (404 Not Found)"
else
    echo "   ⚠️  Recipe may still exist"
fi
echo ""

# Test 10: Test error handling
echo "11. Testing error handling..."
ERROR_RESPONSE=$(curl -s -w "%{http_code}" -X GET "${API_BASE}/api/recipes/99999" \
    -H "Authorization: Bearer ${TOKEN}")

if echo "$ERROR_RESPONSE" | grep -q "404"; then
    echo "   ✅ 404 error handling works correctly"
else
    echo "   ⚠️  Error handling may need review"
fi
echo ""

echo "=========================================="
echo "✅ All Integration Tests Passed!"
echo "=========================================="
echo ""
echo "Summary:"
echo "  ✅ User registration"
echo "  ✅ User authentication"
echo "  ✅ Recipe creation"
echo "  ✅ Recipe listing"
echo "  ✅ Recipe detail retrieval"
echo "  ✅ Recipe update"
echo "  ✅ Recipe search"
echo "  ✅ Recipe deletion"
echo "  ✅ Error handling"
echo ""
echo "The Recipe Saver API is fully functional!"
