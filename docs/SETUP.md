# Setup Guide

## Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

## New Dependencies

The Recipe Saver Enhancements add several new Python libraries:

- **icalendar** - For meal plan calendar export
- **beautifulsoup4** - For recipe URL import
- **qrcode** - For recipe QR code generation
- **hypothesis** - For property-based testing

These are included in `backend/requirements.txt` and will be installed automatically.

## Quick Setup

### 1. Database Setup

```bash
# Create database
createdb recipe_saver

# Initialize schema
psql -U postgres -d recipe_saver -f database/init.sql
```

**Database Migrations:**

The enhancements add many new tables and columns. If you have an existing database, run the migration scripts:

```bash
# Run all migrations in order
psql -U postgres -d recipe_saver -f database/migrations/001_add_recipe_extensions.sql
psql -U postgres -d recipe_saver -f database/migrations/002_add_ratings.sql
psql -U postgres -d recipe_saver -f database/migrations/003_add_notes.sql
psql -U postgres -d recipe_saver -f database/migrations/004_add_collections.sql
psql -U postgres -d recipe_saver -f database/migrations/005_add_meal_plans.sql
psql -U postgres -d recipe_saver -f database/migrations/006_add_shopping_lists.sql
psql -U postgres -d recipe_saver -f database/migrations/007_add_nutrition.sql
psql -U postgres -d recipe_saver -f database/migrations/008_add_social.sql
```

**New Tables:**
- `recipe_ratings` - 5-star recipe ratings
- `recipe_notes` - Personal recipe notes
- `collections` - Recipe collections/folders
- `collection_recipes` - Many-to-many recipe-collection relationships
- `meal_plans` - Calendar-based meal planning
- `meal_plan_templates` - Reusable meal plan templates
- `meal_plan_template_items` - Template items
- `shopping_lists` - Shopping lists
- `shopping_list_items` - Shopping list items
- `nutrition_facts` - Recipe nutrition information
- `dietary_labels` - Dietary labels (vegan, gluten-free, etc.)
- `allergen_warnings` - Allergen warnings
- `user_follows` - User following relationships
- `recipe_likes` - Recipe likes
- `recipe_comments` - Recipe comments

**Extended Tables:**
- `recipes` - Added `is_favorite`, `visibility`, `servings`, `source_recipe_id`, `source_author_id` columns

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
# Edit .env with your database credentials
```

**Environment Variables:**

Edit `backend/.env` with the following settings:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/recipe_saver

# Authentication
SECRET_KEY=your-secret-key-here-use-a-long-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE=5242880  # 5MB in bytes

# Application
DEBUG=True
CORS_ORIGINS=http://localhost:3000

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
```

**Environment Variables:**

Edit `frontend/.env.local` with the following settings:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Feature Flags (optional)
NEXT_PUBLIC_ENABLE_SOCIAL=true
NEXT_PUBLIC_ENABLE_MEAL_PLANNING=true

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
