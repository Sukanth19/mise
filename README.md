# Mise - Recipe Saver

```
    __  ____              
   /  |/  (_)_______      
  / /|_/ / / ___/ _ \     
 / /  / / (__  )  __/     
/_/  /_/_/____/\___/      
                          
Your personal recipe collection, beautifully organized.
```

A modern, full-stack web application for saving and managing your favorite recipes with a clean, intuitive interface.

---

## (>) Tech Stack

**Backend**
- FastAPI (Python) - High-performance async API framework
- SQLAlchemy ORM - Elegant database interactions
- JWT Authentication - Secure token-based auth
- pytest + hypothesis - Property-based testing

**Frontend**
- Next.js 14 (React + TypeScript) - Modern React framework
- Tailwind CSS - Utility-first styling
- Framer Motion - Smooth animations
- Jest + fast-check - Comprehensive testing

**Database**
- PostgreSQL - Robust relational database

---

## (~) Project Structure

```
mise/
│
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── main.py         # API entry point
│   │   ├── config.py       # Environment configuration
│   │   ├── database.py     # Database connection & session
│   │   ├── models.py       # SQLAlchemy data models
│   │   ├── schemas.py      # Pydantic validation schemas
│   │   ├── routers/        # API route handlers
│   │   └── services/       # Business logic layer
│   ├── tests/              # Backend test suite
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment template
│
├── frontend/               # Next.js frontend application
│   ├── app/               # Next.js app router pages
│   ├── components/        # Reusable React components
│   ├── contexts/          # React context providers
│   ├── lib/               # Utility functions & API client
│   ├── types/             # TypeScript type definitions
│   ├── __tests__/         # Frontend test suite
│   └── .env.example       # Environment template
│
└── database/              # Database initialization
    └── init.sql           # Schema creation script
```

---

## (+) Quick Start

### Prerequisites

```
[x] Python 3.10 or higher
[x] Node.js 18 or higher
[x] PostgreSQL 14 or higher
```

### (1) Database Setup

Create and initialize the database:

```bash
# Create database
createdb recipe_saver

# Run initialization script
psql -U postgres -d recipe_saver -f database/init.sql
```

### (2) Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Start server
uvicorn app.main:app --reload
```

**Backend running at:** `http://localhost:8000`

### (3) Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local

# Start development server
npm run dev
```

**Frontend running at:** `http://localhost:3000`

---

## (*) Features

```
[✓] User Authentication
    - Secure registration and login
    - JWT token-based sessions
    - Protected routes

[✓] Recipe Management
    - Create, edit, and delete recipes
    - Rich text ingredients and instructions
    - Image upload support
    - Search by title

[✓] Modern UI/UX
    - Responsive design (mobile, tablet, desktop)
    - Smooth page transitions
    - Interactive animations
    - Dark mode support

[✓] Robust Testing
    - Property-based testing
    - Integration tests
    - >80% code coverage
```

---

## (!) Running Tests

### Backend Tests

```bash
cd backend
source venv/bin/activate
pytest                          # Run all tests
pytest --cov=app               # With coverage report
pytest -v                      # Verbose output
```

### Frontend Tests

```bash
cd frontend
npm test                       # Run all tests
npm test -- --coverage        # With coverage report
npm test -- --watch           # Watch mode
```

---

## (?) API Documentation

Interactive API documentation available when backend is running:

```
Swagger UI:  http://localhost:8000/docs
ReDoc:       http://localhost:8000/redoc
```

### Key Endpoints

```
POST   /api/auth/register      # Create new user account
POST   /api/auth/login         # Authenticate user
GET    /api/recipes            # List all recipes (with search)
POST   /api/recipes            # Create new recipe
GET    /api/recipes/{id}       # Get recipe details
PUT    /api/recipes/{id}       # Update recipe
DELETE /api/recipes/{id}       # Delete recipe
POST   /api/images/upload      # Upload recipe image
```

---

## (=) Development

### Port Configuration

```
Backend:   8000
Frontend:  3000
Database:  5432
```

### Environment Variables

**Backend (.env)**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/recipe_saver
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Frontend (.env.local)**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## (#) License

MIT License - feel free to use this project for learning or personal use.

---

```
Made with <3 and lots of coffee
```
