#!/bin/bash

# Test script to verify image upload endpoint is working

echo "Testing image upload endpoint..."
echo ""

# Test 1: Check if endpoint exists
echo "1. Testing if endpoint exists (should get 401 Unauthorized):"
curl -X POST http://localhost:8000/api/images/upload \
  -H "Authorization: Bearer invalid_token" \
  -w "\nHTTP Status: %{http_code}\n" \
  2>/dev/null
echo ""

# Test 2: Check CORS headers
echo "2. Testing CORS headers:"
curl -X OPTIONS http://localhost:8000/api/images/upload \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -v 2>&1 | grep -i "access-control"
echo ""

# Test 3: List all available routes
echo "3. Checking if /api/images is in the routes:"
curl -s http://localhost:8000/openapi.json | grep -o '"/api/images[^"]*"' | head -5
echo ""

echo "Test complete!"
