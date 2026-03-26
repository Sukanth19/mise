# Recipe Saver - Quick Start Guide

## Prerequisites

- Python 3.10+
- Node.js 18+
- Docker (optional, for MySQL)

## Current Status

⚠️ **Note**: The application is currently being migrated from MongoDB to SQLAlchemy. 
- ✅ Authentication (register/login) is working
- 🚧 Other features (recipes, ratings, etc.) are being converted

## Quick Start

### Backend Setup

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the backend
./run.sh
# Or manually: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will run on: http://localhost:8000
API docs: http://localhost:8000/docs

### Frontend Setup

```bash
cd frontend

# Install dependencies (if needed)
npm install

# Run the frontend
npm run dev
```

Frontend will run on: http://localhost:3000

## Test the API

Visit http://localhost:8000/docs to see the interactive API documentation.

Currently available endpoints:
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /health` - Check API health

## Configuration

The backend is configured in `backend/.env`:
```env
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///./recipe_saver.db
SECRET_KEY=your-secret-key-here-change-in-production
```

## Using MySQL Instead of SQLite

### Start MySQL

```bash
# Start MySQL with Docker
docker-compose up -d

# Verify MySQL is running
docker ps | grep mysql
```

### Update Backend Configuration

Edit `backend/.env`:
```env
DATABASE_TYPE=mysql
DATABASE_URL=mysql+pymysql://recipe_user:recipe_password@localhost:3306/recipe_saver
```

Then restart the backend.

## Troubleshooting

### Backend won't start
- Check if port 8000 is already in use: `lsof -i :8000`
- Make sure virtual environment is activated
- Check `backend/.env` file exists

### Frontend won't start
- Check if port 3000 is already in use: `lsof -i :3000`
- Try deleting `node_modules` and running `npm install` again

### Database errors
- For SQLite: The database file will be created automatically
- For MySQL: Make sure Docker container is running with `docker ps`

## Next Steps

The remaining routers (recipes, ratings, notes, etc.) need to be converted from MongoDB to SQLAlchemy. They are currently commented out in `backend/app/main.py`.
