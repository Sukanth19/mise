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
- pytest + Hypothesis - Property-based testing
- icalendar - Meal plan calendar export
- BeautifulSoup4 - Recipe URL import
- qrcode - QR code generation

### Frontend

- Next.js 14 (React + TypeScript) - Modern React framework
- Tailwind CSS - Utility-first styling
- Framer Motion - Smooth animations
- Jest + fast-check - Comprehensive testing
- HTML5 Drag and Drop - Meal planning interactions

### Database

- PostgreSQL - Robust relational database

---

## Project Structure

```text
mise/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── routers/           # API endpoints
│   │   │   ├── auth.py
│   │   │   ├── recipes.py
│   │   │   ├── collections.py
│   │   │   ├── meal_plans.py
│   │   │   ├── shopping_lists.py
│   │   │   ├── nutrition.py
│   │   │   ├── social.py
│   │   │   └── images.py
│   │   ├── services/          # Business logic
│   │   │   ├── collection_manager.py
│   │   │   ├── meal_planner.py
│   │   │   ├── shopping_list_generator.py
│   │   │   ├── nutrition_tracker.py
│   │   │   ├── sharing_service.py
│   │   │   ├── filter_engine.py
│   │   │   └── rating_system.py
│   │   ├── main.py            # App entry point
│   │   ├── models.py          # Database models
│   │   └── schemas.py         # Request/response schemas
│   ├── tests/                 # Backend tests
│   │   ├── test_*_endpoints.py
│   │   ├── test_*_properties.py
│   │   └── test_integration.py
│   └── uploads/               # Recipe images (gitignored)
│
├── frontend/                  # Next.js frontend
│   ├── app/                  # Pages (App Router)
│   │   ├── dashboard/
│   │   ├── collections/
│   │   ├── meal-planner/
│   │   ├── shopping-lists/
│   │   ├── discover/
│   │   └── users/
│   ├── components/           # React components
│   │   ├── collections/
│   │   ├── meal-planning/
│   │   ├── shopping-lists/
│   │   ├── nutrition/
│   │   ├── social/
│   │   └── ui/
│   ├── contexts/             # React contexts
│   │   └── ThemeContext.tsx
│   ├── lib/                  # Utilities & API client
│   └── __tests__/            # Frontend tests
│
├── database/                 # Database setup
│   ├── init.sql              # Schema initialization
│   └── migrations/           # Database migrations
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

### Core Features

#### User Authentication

- Secure registration and login
- JWT token-based sessions
- Protected routes

#### Recipe Management

- Create, edit, and delete recipes
- Rich text ingredients and instructions
- Image upload support
- Search by title
- Mark recipes as favorites
- 5-star rating system
- Personal recipe notes
- Recipe duplication
- Bulk operations (delete, move to collection)
- Import recipes from URLs

### Organization Features

#### Collections

- Create custom collections to organize recipes
- Nested collections (up to 3 levels)
- Add recipes to multiple collections
- Share collections with unique links
- Cover images for collections

### Meal Planning

#### Calendar-Based Planning

- Weekly and monthly calendar views
- Drag-and-drop recipes onto calendar
- Breakfast, lunch, dinner, and snack meal times
- Meal plan templates for recurring patterns
- Export meal plans to iCal format

#### Shopping Lists

- Generate shopping lists from recipes or meal plans
- Automatic ingredient consolidation
- Categorized by grocery sections (produce, dairy, meat, pantry)
- Check off items as you shop
- Add custom items
- Share shopping lists with others
- Real-time synchronization for shared lists

### Nutrition Tracking

- Add nutrition facts to recipes (calories, protein, carbs, fat, fiber)
- Per-serving nutrition calculations
- Dietary labels (vegan, vegetarian, gluten-free, dairy-free, keto, paleo, low-carb)
- Allergen warnings (nuts, dairy, eggs, soy, wheat, fish, shellfish)
- Meal plan nutrition summaries (daily and weekly totals)
- Filter recipes by dietary preferences and allergens

### Social Features

#### Recipe Sharing

- Make recipes public, private, or unlisted
- Discovery feed to browse public recipes
- Like and comment on recipes
- Fork recipes to your collection
- Follow other users
- QR code generation for easy sharing
- Social media sharing (Twitter, Facebook, Pinterest)

### Testing

- Property-based testing with Hypothesis (backend) and fast-check (frontend)
- 57 correctness properties validated
- Integration tests for complete workflows
- 80%+ backend coverage, 70%+ frontend coverage

### UI/UX Enhancements

- Dark mode and light mode themes
- Advanced filtering (favorites, ratings, tags, dietary labels, allergens)
- Multiple sorting options (date, rating, title)
- Recipe preview modal
- Print-friendly recipe view
- Keyboard shortcuts (Ctrl+N, Ctrl+K, Ctrl+T)
- Toast notifications
- Loading skeletons
- Improved empty states
- Responsive design (mobile, tablet, desktop)
- Smooth page transitions
- Interactive animations

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
# Authentication
POST   /api/auth/register         # Create account
POST   /api/auth/login            # Authenticate

# Recipes
GET    /api/recipes               # List recipes (with search)
POST   /api/recipes               # Create recipe
GET    /api/recipes/{id}          # Get recipe
PUT    /api/recipes/{id}          # Update recipe
DELETE /api/recipes/{id}          # Delete recipe
PATCH  /api/recipes/{id}/favorite # Toggle favorite
POST   /api/recipes/{id}/duplicate # Duplicate recipe
DELETE /api/recipes/bulk          # Bulk delete
POST   /api/recipes/import-url    # Import from URL
GET    /api/recipes/filter        # Advanced filtering

# Ratings & Notes
POST   /api/recipes/{id}/rating   # Add/update rating
GET    /api/recipes/{id}/rating   # Get user rating
POST   /api/recipes/{id}/notes    # Add note
GET    /api/recipes/{id}/notes    # Get notes

# Collections
POST   /api/collections           # Create collection
GET    /api/collections           # List collections
GET    /api/collections/{id}      # Get collection
POST   /api/collections/{id}/recipes # Add recipes
POST   /api/collections/{id}/share   # Generate share link

# Meal Planning
POST   /api/meal-plans            # Create meal plan
GET    /api/meal-plans            # Get meal plans (date range)
POST   /api/meal-plan-templates   # Create template
POST   /api/meal-plan-templates/{id}/apply # Apply template
GET    /api/meal-plans/export     # Export to iCal

# Shopping Lists
POST   /api/shopping-lists        # Create shopping list
GET    /api/shopping-lists        # List shopping lists
PATCH  /api/shopping-lists/{list_id}/items/{item_id} # Check/uncheck
POST   /api/shopping-lists/{id}/items # Add custom item
POST   /api/shopping-lists/{id}/share # Generate share link

# Nutrition
POST   /api/recipes/{id}/nutrition # Add nutrition facts
GET    /api/recipes/{id}/nutrition # Get nutrition facts
POST   /api/recipes/{id}/dietary-labels # Set dietary labels
POST   /api/recipes/{id}/allergens # Set allergen warnings
GET    /api/meal-plans/nutrition-summary # Meal plan nutrition

# Social Features
PATCH  /api/recipes/{id}/visibility # Set visibility
GET    /api/recipes/discover      # Discovery feed
POST   /api/recipes/{id}/fork     # Fork recipe
POST   /api/recipes/{id}/like     # Like recipe
POST   /api/recipes/{id}/comments # Add comment
POST   /api/users/{id}/follow     # Follow user
GET    /api/recipes/{id}/qrcode   # Generate QR code

# Images
POST   /api/images/upload         # Upload image
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
