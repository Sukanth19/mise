# Setup Guide

## Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

## Quick Setup

### 1. Database Setup

```bash
# Create database
createdb recipe_saver

# Initialize schema
psql -U postgres -d recipe_saver -f database/init.sql
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials:
# DATABASE_URL=postgresql://user:password@localhost:5432/recipe_saver
# SECRET_KEY=your-secret-key-here

# Start server
uvicorn app.main:app --reload
```

Backend: http://localhost:8000
API Docs: http://localhost:8000/docs

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Default settings should work if backend is on port 8000

# Start development server
npm run dev
```

Frontend: http://localhost:3000

## Running Tests

### Backend

```bash
cd backend
source venv/bin/activate
pytest                    # Run all tests
pytest --cov=app         # With coverage
pytest -v                # Verbose
```

### Frontend

```bash
cd frontend
npm test                 # Run all tests
npm test -- --coverage  # With coverage
npm test -- --watch     # Watch mode
```

## Troubleshooting

### Database Connection Issues

1. Verify PostgreSQL is running:
```bash
sudo systemctl status postgresql  # Linux
brew services list               # macOS
```

2. Check credentials in `backend/.env`

3. Verify database exists:
```bash
psql -U postgres -l | grep recipe_saver
```

### Port Conflicts

Backend (change port):
```bash
uvicorn app.main:app --port 8001
```

Frontend (change port):
```bash
npm run dev -- -p 3001
```

Update `frontend/.env.local` if backend port changes.

### Virtual Environment Issues

```bash
# Remove and recreate
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Node Modules Issues

```bash
# Clean reinstall
rm -rf node_modules package-lock.json
npm install
```

## Development Workflow

1. Create feature branch:
```bash
git checkout -b feature/your-feature
```

2. Make changes and test:
```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm test
```

3. Commit and push:
```bash
git add .
git commit -m "feat: your feature description"
git push origin feature/your-feature
```

## Useful Commands

### Backend

```bash
uvicorn app.main:app --reload    # Dev server
pytest                           # Run tests
pytest --cov=app                # With coverage
black app/                      # Format code
```

### Frontend

```bash
npm run dev      # Dev server
npm run build    # Production build
npm start        # Production server
npm test         # Run tests
npm run lint     # Lint code
```

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [pytest Documentation](https://docs.pytest.org/)
- [Jest Documentation](https://jestjs.io/)
