# Mise - Recipe Saver

```text
    __  ____              
   /  |/  (_)_______      
  / /|_/ / / ___/ _ \     
 / /  / / (__  )  __/     
/_/  /_/_/____/\___/      
                          
Your personal recipe collection, beautifully organized.
```

A modern, full-stack web application for saving and managing your favorite recipes with a clean, intuitive interface.

---

## Tech Stack

### Backend

- FastAPI (Python) - High-performance async API framework
- SQLAlchemy ORM - Elegant database interactions
- JWT Authentication - Secure token-based auth
- pytest + hypothesis - Property-based testing

### Frontend

- Next.js 14 (React + TypeScript) - Modern React framework
- Tailwind CSS - Utility-first styling
- Framer Motion - Smooth animations
- Jest + fast-check - Comprehensive testing

### Database

- PostgreSQL - Robust relational database

---

## Project Structure

```text
mise/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── routers/           # API endpoints
│   │   ├── services/          # Business logic
│   │   ├── main.py            # App entry point
│   │   ├── models.py          # Database models
│   │   └── schemas.py         # Request/response schemas
│   ├── tests/                 # Backend tests
│   └── uploads/               # Recipe images (gitignored)
│
├── frontend/                  # Next.js frontend
│   ├── app/                  # Pages (App Router)
│   ├── components/           # React components
│   ├── contexts/             # React contexts
│   ├── lib/                  # Utilities & API client
│   └── __tests__/            # Frontend tests
│
├── database/                 # Database setup
│   └── init.sql              # Schema initialization
│
└── docs/                     # Documentation
    ├── API.md                # API reference
    ├── SETUP.md              # Setup instructions
    ├── TESTING.md            # Testing guide
    └── CONTRIBUTING.md       # Contribution guide
```

---

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

### 1. Database Setup

```bash
createdb recipe_saver
psql -U postgres -d recipe_saver -f database/init.sql
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
uvicorn app.main:app --reload
```

Backend: http://localhost:8000

### 3. Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Frontend: http://localhost:3000

For detailed setup instructions, see [docs/SETUP.md](docs/SETUP.md)

---

## Features

### User Authentication

- Secure registration and login
- JWT token-based sessions
- Protected routes

### Recipe Management

- Create, edit, and delete recipes
- Rich text ingredients and instructions
- Image upload support
- Search by title

### Modern UI/UX

- Responsive design (mobile, tablet, desktop)
- Smooth page transitions
- Interactive animations
- Dark mode support

### Robust Testing

- Property-based testing
- Integration tests
- 80%+ code coverage

---

## Running Tests

### Backend

```bash
cd backend
source venv/bin/activate
pytest                    # Run all tests
pytest --cov=app         # With coverage
```

### Frontend

```bash
cd frontend
npm test                 # Run all tests
npm test -- --coverage  # With coverage
```

For detailed testing information, see [docs/TESTING.md](docs/TESTING.md)

---

## API Documentation

Interactive documentation available when backend is running:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

```text
POST   /api/auth/register      # Create account
POST   /api/auth/login         # Authenticate
GET    /api/recipes            # List recipes (with search)
POST   /api/recipes            # Create recipe
GET    /api/recipes/{id}       # Get recipe
PUT    /api/recipes/{id}       # Update recipe
DELETE /api/recipes/{id}       # Delete recipe
POST   /api/images/upload      # Upload image
```

For detailed API documentation, see [docs/API.md](docs/API.md)

---

## Development

### Ports

- Backend: 8000
- Frontend: 3000
- Database: 5432

### Environment Variables

Backend (.env):

```env
DATABASE_URL=postgresql://user:password@localhost:5432/recipe_saver
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Frontend (.env.local):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## License

MIT License - feel free to use this project for learning or personal use.

---

Made with ❤️ and lots of coffee
