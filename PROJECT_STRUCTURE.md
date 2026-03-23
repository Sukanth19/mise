# Project Structure

## Overview

Clean, organized structure for the Recipe Saver application with clear separation of concerns.

## Directory Layout

```
mise/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── routers/           # API endpoints
│   │   │   ├── auth.py        # Authentication routes
│   │   │   ├── recipes.py     # Recipe CRUD routes
│   │   │   └── images.py      # Image upload routes
│   │   ├── services/          # Business logic
│   │   │   ├── auth_service.py
│   │   │   ├── recipe_service.py
│   │   │   ├── image_service.py
│   │   │   └── search_service.py
│   │   ├── config.py          # Environment configuration
│   │   ├── database.py        # Database connection
│   │   ├── main.py            # Application entry point
│   │   ├── models.py          # SQLAlchemy models
│   │   └── schemas.py         # Pydantic schemas
│   ├── tests/                 # Test suite
│   │   ├── conftest.py        # Test fixtures
│   │   ├── test_auth_endpoints.py
│   │   ├── test_auth_properties.py
│   │   ├── test_recipe_endpoints.py
│   │   ├── test_recipe_properties.py
│   │   ├── test_image_endpoints.py
│   │   ├── test_image_properties.py
│   │   └── test_integration.py
│   ├── uploads/               # Recipe images (gitignored)
│   ├── .env.example           # Environment template
│   ├── .gitignore
│   ├── pytest.ini
│   ├── requirements.txt
│   └── run.sh
│
├── frontend/                   # Next.js frontend
│   ├── app/                   # Pages (App Router)
│   │   ├── dashboard/
│   │   │   └── page.tsx       # Dashboard page
│   │   ├── recipes/
│   │   │   ├── [id]/
│   │   │   │   ├── page.tsx   # Recipe detail
│   │   │   │   └── edit/
│   │   │   │       └── page.tsx
│   │   │   └── new/
│   │   │       └── page.tsx   # Create recipe
│   │   ├── register/
│   │   │   └── page.tsx       # Registration page
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx           # Landing page
│   ├── components/            # React components
│   │   ├── AuthForm.tsx
│   │   ├── RecipeCard.tsx
│   │   ├── RecipeDetail.tsx
│   │   ├── RecipeForm.tsx
│   │   ├── RecipeGrid.tsx
│   │   ├── SearchBar.tsx
│   │   ├── ImageUpload.tsx
│   │   ├── Header.tsx
│   │   ├── LoadingSkeleton.tsx
│   │   ├── PageTransition.tsx
│   │   └── Toast.tsx
│   ├── contexts/              # React contexts
│   │   └── ThemeContext.tsx
│   ├── lib/                   # Utilities
│   │   └── api.ts             # API client
│   ├── types/                 # TypeScript types
│   │   └── index.ts
│   ├── __tests__/             # Integration tests
│   ├── .env.example
│   ├── .gitignore
│   ├── jest.config.js
│   ├── next.config.js
│   ├── package.json
│   ├── tailwind.config.ts
│   └── tsconfig.json
│
├── database/                   # Database setup
│   └── init.sql               # Schema initialization
│
├── docs/                       # Documentation
│   ├── API.md                 # API reference
│   ├── SETUP.md               # Setup guide
│   └── TESTING.md             # Testing guide
│
├── .gitignore                 # Root gitignore
├── README.md                  # Main documentation
└── PROJECT_STRUCTURE.md       # This file
```

## Key Components

### Backend Architecture

**Configuration Layer**
- `config.py` - Environment variables and settings
- `database.py` - Database connection and session management

**Data Layer**
- `models.py` - SQLAlchemy ORM models (User, Recipe)
- `schemas.py` - Pydantic validation schemas

**Business Logic Layer**
- `services/auth_service.py` - Authentication logic
- `services/recipe_service.py` - Recipe CRUD operations
- `services/image_service.py` - Image upload handling
- `services/search_service.py` - Search functionality

**API Layer**
- `routers/auth.py` - Authentication endpoints
- `routers/recipes.py` - Recipe endpoints
- `routers/images.py` - Image upload endpoints

**Application Entry**
- `main.py` - FastAPI app initialization, middleware, startup

### Frontend Architecture

**Pages (App Router)**
- Landing page, dashboard, recipe views, authentication

**Components**
- Reusable UI components with TypeScript
- Comprehensive test coverage

**State Management**
- React contexts for theme and auth state
- API client for backend communication

**Styling**
- Tailwind CSS for utility-first styling
- Framer Motion for animations

### Database Schema

**Users Table**
- id, username (unique), password_hash, created_at

**Recipes Table**
- id, user_id (FK), title, image_url, ingredients, steps, tags, reference_link, timestamps
- Indexes on user_id, title for performance

## Technology Stack

### Backend
- FastAPI - Modern async web framework
- SQLAlchemy - ORM for database operations
- PostgreSQL - Primary database
- JWT - Token-based authentication
- pytest + hypothesis - Testing framework

### Frontend
- Next.js 14 - React framework with App Router
- TypeScript - Type safety
- Tailwind CSS - Utility-first styling
- Framer Motion - Animations
- Jest + fast-check - Testing framework

## File Organization Principles

### What's Tracked in Git
- Source code (Python, TypeScript, React)
- Configuration files (.example files)
- Database schema (init.sql)
- Documentation (docs/)
- Test files

### What's Ignored
- Virtual environments (venv/)
- Node modules (node_modules/)
- Build artifacts (.next/, __pycache__/)
- Environment files (.env, .env.local)
- Uploaded images (uploads/)
- Test coverage reports (coverage/, htmlcov/)
- IDE settings (.vscode/, .kiro/)
- Database files (*.db, *.sqlite3)

## Development Workflow

1. Backend runs on port 8000
2. Frontend runs on port 3000
3. PostgreSQL runs on port 5432
4. Images stored in backend/uploads/ (gitignored)
5. Tests run independently for backend and frontend

## Documentation Structure

- `README.md` - Project overview and quick start
- `docs/SETUP.md` - Detailed setup instructions
- `docs/API.md` - API endpoint reference
- `docs/TESTING.md` - Testing guide and strategy
- `PROJECT_STRUCTURE.md` - This file
