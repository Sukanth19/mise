#!/bin/bash
# Setup script for Recipe Saver application

echo "=== Recipe Saver Setup ==="
echo ""

# Check prerequisites
echo "Checking prerequisites..."
command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required but not installed. Aborting."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "Node.js is required but not installed. Aborting."; exit 1; }

echo "✓ All prerequisites found"
echo ""

# Setup database
echo "Setting up database..."
echo "Database will be initialized automatically on first run."
echo "For MySQL, ensure Docker is running and use: docker-compose up -d"
echo ""

# Setup backend
echo "Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠ Please update backend/.env with your database credentials and secret key"
fi

echo "✓ Backend setup complete"
cd ..
echo ""

# Setup frontend
echo "Setting up frontend..."
cd frontend

echo "Installing Node.js dependencies..."
npm install

if [ ! -f ".env.local" ]; then
    echo "Creating .env.local file..."
    cp .env.example .env.local
fi

echo "✓ Frontend setup complete"
cd ..
echo ""

echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Update backend/.env with your database credentials"
echo "2. Start the backend: cd backend && ./run.sh"
echo "3. Start the frontend: cd frontend && npm run dev"
echo ""
echo "Backend will run on: http://localhost:8000"
echo "Frontend will run on: http://localhost:3000"
