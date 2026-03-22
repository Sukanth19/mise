# Recipe Saver - Quick Start Guide

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10+**: `python3 --version`
- **Node.js 18+**: `node --version`
- **PostgreSQL 14+**: `psql --version`
- **npm or yarn**: `npm --version`

## Quick Setup (Automated)

Run the automated setup script:

```bash
chmod +x setup.sh
./setup.sh
```

This will:
1. Check prerequisites
2. Initialize the PostgreSQL database
3. Set up Python virtual environment
4. Install backend dependencies
5. Install frontend dependencies
6. Create environment files

## Manual Setup

### 1. Database Setup

Create the database and tables:

```bash
# Option 1: Using psql directly
psql -U postgres -f database/init.sql

# Option 2: Create database first, then run init script
createdb recipe_saver
psql -U postgres -d recipe_saver -f database/init.sql
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

Update `.env` with your database credentials:
```
DATABASE_URL=postgresql://your_user:your_password@localhost:5432/recipe_saver
SECRET_KEY=generate-a-secure-random-key-here
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# No changes needed unless your backend runs on a different port
```

## Running the Application

### Start Backend

```bash
cd backend
source venv/bin/activate  # If not already activated
uvicorn app.main:app --reload
```

Backend will be available at: **http://localhost:8000**

API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Start Frontend

In a new terminal:

```bash
cd frontend
npm run dev
```

Frontend will be available at: **http://localhost:3000**

## Running Tests

### Backend Tests

```bash
cd backend
source venv/bin/activate
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm test
```

Run in watch mode:
```bash
npm run test:watch
```

## Troubleshooting

### Database Connection Issues

If you get database connection errors:

1. Ensure PostgreSQL is running:
   ```bash
   sudo systemctl status postgresql  # Linux
   brew services list  # macOS
   ```

2. Check your database credentials in `backend/.env`

3. Verify the database exists:
   ```bash
   psql -U postgres -l | grep recipe_saver
   ```

### Port Already in Use

If port 8000 or 3000 is already in use:

**Backend:**
```bash
uvicorn app.main:app --reload --port 8001
```

**Frontend:**
```bash
npm run dev -- -p 3001
```

Update `frontend/.env.local` with the new backend port if changed.

### Python Virtual Environment Issues

If you have issues with the virtual environment:

```bash
# Remove existing venv
rm -rf venv

# Create new venv
python3 -m venv venv

# Activate and reinstall
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Node Modules Issues

If you have issues with node_modules:

```bash
# Remove existing modules
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

## Development Workflow

1. **Create a new feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Backend code in `backend/app/`
   - Frontend code in `frontend/`

3. **Run tests**
   ```bash
   # Backend
   cd backend && pytest
   
   # Frontend
   cd frontend && npm test
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin feature/your-feature-name
   ```

## Project Status

✅ **Task 1 Complete**: Project structure and database setup

**Next Tasks:**
- Task 2: Implement authentication service
- Task 4: Implement recipe management service
- Task 5: Implement image upload service
- Task 6: Implement search functionality
- Tasks 8-12: Frontend implementation

## Useful Commands

### Backend

```bash
# Run server
uvicorn app.main:app --reload

# Run tests
pytest

# Run tests with coverage
pytest --cov=app

# Format code
black app/

# Lint code
flake8 app/
```

### Frontend

```bash
# Development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run tests
npm test

# Lint code
npm run lint
```

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [fast-check Documentation](https://fast-check.dev/)
