# Recipe Saver - Project Structure

## Overview
This document describes the complete project structure for the Recipe Saver application.

## Directory Structure

```
recipe-saver/
├── backend/                    # FastAPI backend application
│   ├── app/
│   │   ├── routers/           # API route handlers (to be implemented)
│   │   ├── services/          # Business logic services (to be implemented)
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration and environment variables
│   │   ├── database.py        # Database connection and session management
│   │   ├── main.py            # FastAPI application entry point
│   │   ├── models.py          # SQLAlchemy ORM models (User, Recipe)
│   │   └── schemas.py         # Pydantic request/response models
│   ├── tests/
│   │   ├── __init__.py
│   │   └── conftest.py        # Pytest fixtures and test configuration
│   ├── .env.example           # Example environment variables
│   ├── .gitignore
│   ├── pytest.ini             # Pytest configuration
│   ├── requirements.txt       # Python dependencies
│   └── run.sh                 # Backend startup script
│
├── frontend/                   # Next.js frontend application
│   ├── app/
│   │   ├── globals.css        # Global styles with Tailwind
│   │   ├── layout.tsx         # Root layout component
│   │   └── page.tsx           # Home page
│   ├── components/            # React components (to be implemented)
│   ├── lib/                   # Utility functions (to be implemented)
│   ├── types/
│   │   └── index.ts           # TypeScript type definitions
│   ├── .env.example           # Example environment variables
│   ├── .gitignore
│   ├── jest.config.js         # Jest test configuration
│   ├── jest.setup.js          # Jest setup file
│   ├── next.config.js         # Next.js configuration
│   ├── package.json           # Node.js dependencies and scripts
│   ├── postcss.config.js      # PostCSS configuration for Tailwind
│   ├── tailwind.config.ts     # Tailwind CSS configuration
│   └── tsconfig.json          # TypeScript configuration
│
├── database/
│   └── init.sql               # Database initialization script
│
├── README.md                   # Project documentation
├── PROJECT_STRUCTURE.md        # This file
└── setup.sh                    # Automated setup script
```

## Key Files

### Backend

**app/config.py**
- Manages environment variables using pydantic-settings
- Database URL, JWT secret key, token expiration settings

**app/database.py**
- SQLAlchemy engine and session configuration
- Database connection dependency for FastAPI

**app/models.py**
- User model: id, username, password_hash, created_at
- Recipe model: id, user_id, title, image_url, ingredients, steps, tags, reference_link, timestamps

**app/schemas.py**
- Pydantic models for request/response validation
- RegisterRequest, LoginRequest, TokenResponse
- RecipeCreate, RecipeUpdate, RecipeResponse

**app/main.py**
- FastAPI application instance
- CORS middleware configuration
- Database table creation on startup

**tests/conftest.py**
- Pytest fixtures for database and test client
- Uses SQLite for testing

### Frontend

**types/index.ts**
- TypeScript interfaces for User, Recipe, AuthToken
- Request/response types matching backend schemas

**app/layout.tsx**
- Root layout with metadata
- Global styles import

**app/page.tsx**
- Landing page component

**package.json**
- Dependencies: Next.js 14, React 18, TypeScript
- Dev dependencies: Jest, fast-check, Tailwind CSS
- Scripts: dev, build, start, test

### Database

**database/init.sql**
- Creates recipe_saver database
- Users table with username uniqueness constraint
- Recipes table with foreign key to users
- Indexes on user_id, title, and username for performance

## Dependencies

### Backend (Python)
- fastapi: Web framework
- uvicorn: ASGI server
- sqlalchemy: ORM
- psycopg2-binary: PostgreSQL adapter
- python-jose: JWT token handling
- passlib: Password hashing
- pydantic: Data validation
- pytest: Testing framework
- hypothesis: Property-based testing

### Frontend (Node.js)
- next: React framework
- react & react-dom: UI library
- typescript: Type safety
- tailwindcss: Utility-first CSS
- jest: Testing framework
- fast-check: Property-based testing
- @testing-library/react: Component testing

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/recipe_saver
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24
UPLOAD_DIR=uploads
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Next Steps

After completing Task 1 (project setup), the following tasks will implement:

1. Authentication service (Task 2)
   - User registration and login
   - Password hashing with bcrypt
   - JWT token generation and verification

2. Recipe management service (Task 4)
   - CRUD operations for recipes
   - User ownership validation
   - Database operations

3. Image upload service (Task 5)
   - File validation and storage
   - Image URL generation

4. Search functionality (Task 6)
   - Case-insensitive title search
   - User-scoped results

5. Frontend components (Tasks 8-12)
   - Authentication forms
   - Recipe display components
   - Recipe creation/editing forms
   - Dashboard and detail pages
   - UI animations

## Testing Strategy

- **Unit tests**: Specific examples and edge cases
- **Property-based tests**: Universal properties across all inputs
- Backend: pytest + hypothesis (100+ iterations per property)
- Frontend: Jest + fast-check (100+ iterations per property)
- Target coverage: 80% backend, 70% frontend
