#!/bin/bash
# Script to open the Recipe Saver application

echo "=========================================="
echo "Opening Mise Recipe Saver..."
echo "=========================================="
echo ""

# Check if backend is running
echo "Checking backend..."
if curl -s http://localhost:8000/ | grep -q "Recipe Saver API"; then
  echo "✓ Backend is running on http://localhost:8000"
else
  echo "✗ Backend is not running!"
  echo ""
  echo "Please start the backend first:"
  echo "  cd backend"
  echo "  source venv/bin/activate"
  echo "  uvicorn app.main:app --reload"
  echo ""
  exit 1
fi

# Check if frontend is running
echo "Checking frontend..."
if curl -s http://localhost:3000/ | grep -q "html"; then
  echo "✓ Frontend is running on http://localhost:3000"
else
  echo "✗ Frontend is not running!"
  echo ""
  echo "Please start the frontend first:"
  echo "  cd frontend"
  echo "  npm run dev"
  echo ""
  exit 1
fi

echo ""
echo "=========================================="
echo "✓ Application is ready!"
echo "=========================================="
echo ""
echo "Login credentials:"
echo "  Username: demo"
echo "  Password: demo1234"
echo ""
echo "Opening browser..."
echo ""

# Try to open browser (works on most Linux systems)
if command -v xdg-open > /dev/null; then
  xdg-open http://localhost:3000
elif command -v gnome-open > /dev/null; then
  gnome-open http://localhost:3000
elif command -v kde-open > /dev/null; then
  kde-open http://localhost:3000
else
  echo "Could not auto-open browser."
  echo "Please manually open: http://localhost:3000"
fi

echo "=========================================="
