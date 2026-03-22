# Recipe Saver

A full-stack web application for saving and managing personal recipes.

## Tech Stack

- **Backend**: FastAPI (Python) with SQLAlchemy ORM
- **Frontend**: Next.js (React + TypeScript) with Tailwind CSS
- **Database**: PostgreSQL
- **Authentication**: JWT tokens
- **Testing**: pytest + hypothesis (backend), Jest + fast-check (frontend)

## Project Structure

```
.
├── backend/           # FastAPI backend application
│   ├── app/          # Application code
│   │   ├── __init__.py
│   │   ├── main.py   # FastAPI app entry point
│   │   ├── config.py # Configuration settings
│   │   ├── database.py # Database connection
│   │   └── models.py # SQLAlchemy models
│   ├── tests/        # Backend tests
│   ├── requirements.txt
│   └── .env.example
├── frontend/         # Next.js frontend application
│   ├── app/         # Next.js app directory
│   ├── components/  # React components
│   ├── types/       # TypeScript type definitions
│   ├── package.json
│   └── .env.example
└── database/        # Database initialization scripts
    └── init.sql
```

## Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

### Database Setup

1. Install PostgreSQL
2. Create database and tables:
```bash
psql -U postgres -f database/init.sql
```

Or manually:
```bash
createdb recipe_saver
psql -U postgres -d recipe_saver -f database/init.sql
```

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file from example:
```bash
cp .env.example .env
```

5. Update `.env` with your database credentials and secret key

6. Run the development server:
```bash
uvicorn app.main:app --reload
```

Backend will be available at http://localhost:8000

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env.local` file:
```bash
cp .env.example .env.local
```

4. Run the development server:
```bash
npm run dev
```

Frontend will be available at http://localhost:3000

## Running Tests

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Features

- User registration and authentication
- Create, read, update, and delete recipes
- Upload recipe images
- Search recipes by title
- Responsive design for mobile, tablet, and desktop
- Smooth UI animations

## Development

- Backend API runs on port 8000
- Frontend runs on port 3000
- Database runs on port 5432 (default PostgreSQL)
