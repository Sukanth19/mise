# Deployment Guide - Recipe Saver Enhancements

This guide covers deploying the Recipe Saver application with all enhancements.

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 12+ (for production) or SQLite (for development)
- Node.js 16+ (for frontend)
- Git

## Backend Deployment

### 1. Install Dependencies

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the `backend` directory:

```bash
# For development (SQLite)
DATABASE_URL=sqlite:///./recipe_saver.db

# For production (PostgreSQL)
# DATABASE_URL=postgresql://username:password@localhost:5432/recipe_saver

SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24
UPLOAD_DIR=uploads
```

**Important:** Generate a secure SECRET_KEY for production:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Initialize Database

For a **new deployment** (clean database):

```bash
# Create all tables with the full schema
python init_db.py
```

For **upgrading an existing database**:

```bash
# Run migrations to add enhancement tables and columns
python run_migrations.py
```

### 4. (Optional) Add Sample Data

For testing or demonstration purposes:

```bash
python seed_data.py
```

This creates:
- 3 sample users (demo_user, chef_alice, baker_bob - all with password: demo123)
- 6 sample recipes (some public for discovery feed)
- Sample collections, meal plans, and shopping lists
- Sample ratings, notes, likes, and comments

### 5. Run the Server

**Development:**
```bash
./run.sh
# Or: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production:**
```bash
# Use gunicorn with uvicorn workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Database Migration Details

### Migration Files

The `migrations/` directory contains SQL migration files:

1. `001_recipe_extensions.sql` - Adds favorite, visibility, servings, source tracking
2. `002_recipe_ratings.sql` - Creates recipe ratings table
3. `003_recipe_notes.sql` - Creates recipe notes table
4. `004_collections.sql` - Creates collections and collection_recipes tables
5. `005_meal_plans.sql` - Creates meal planning tables
6. `006_shopping_lists.sql` - Creates shopping list tables
7. `007_nutrition.sql` - Creates nutrition tracking tables
8. `008_social.sql` - Creates social feature tables

### Migration Runner

The `run_migrations.py` script:
- Automatically detects database type (SQLite or PostgreSQL)
- Tracks applied migrations in `applied_migrations` table
- Applies pending migrations in order
- Commits each statement separately for SQLite compatibility

### Testing Migrations

Use the `test_migrations.py` script to verify migrations:

```bash
python test_migrations.py
```

This tests:
- Clean database initialization
- Migrations on existing database with data
- Verification of all tables and indexes

## Dependencies

All required dependencies are in `requirements.txt`:

### Core Dependencies
- `fastapi>=0.104.1` - Web framework
- `uvicorn[standard]>=0.24.0` - ASGI server
- `sqlalchemy>=2.0.23` - ORM
- `python-jose[cryptography]>=3.3.0` - JWT tokens
- `passlib[bcrypt]>=1.7.4` - Password hashing
- `python-multipart>=0.0.6` - File uploads
- `pydantic>=2.5.0` - Data validation
- `pydantic-settings>=2.1.0` - Settings management

### Enhancement Dependencies
- `icalendar>=5.0.0` - iCal export for meal plans
- `beautifulsoup4>=4.12.0` - Recipe URL import
- `qrcode>=7.4.0` - QR code generation
- `pillow>=10.0.0` - Image processing

### Testing Dependencies
- `pytest>=7.4.3` - Test framework
- `pytest-asyncio>=0.21.1` - Async test support
- `hypothesis>=6.92.1` - Property-based testing
- `httpx>=0.25.2` - HTTP client for tests

## Production Considerations

### Database

**PostgreSQL Setup:**
```sql
CREATE DATABASE recipe_saver;
CREATE USER recipe_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE recipe_saver TO recipe_user;
```

Update `.env`:
```
DATABASE_URL=postgresql://recipe_user:secure_password@localhost:5432/recipe_saver
```

### Security

1. **Change SECRET_KEY** - Use a cryptographically secure random key
2. **Use HTTPS** - Always use HTTPS in production
3. **Set CORS** - Configure allowed origins in `app/main.py`
4. **Database credentials** - Use strong passwords and restrict access
5. **File uploads** - Validate file types and sizes

### Performance

1. **Use PostgreSQL** - Better performance than SQLite for production
2. **Add indexes** - All migrations include necessary indexes
3. **Use gunicorn** - Multiple worker processes for better concurrency
4. **Static files** - Serve uploads through nginx or CDN
5. **Database connection pooling** - Configure in `app/database.py`

### Monitoring

1. **Logging** - Configure logging in `app/main.py`
2. **Error tracking** - Consider Sentry or similar
3. **Performance monitoring** - Use APM tools
4. **Database backups** - Regular automated backups

## Troubleshooting

### Migration Issues

**Problem:** Migration fails with "duplicate column" error
**Solution:** The column already exists. Either:
- Skip that migration (mark as applied manually)
- Or use `init_db.py` for clean database

**Problem:** Migration fails with "no such table" error
**Solution:** Run `init_db.py` first to create base tables

### Database Issues

**Problem:** "database is locked" error (SQLite)
**Solution:** 
- Close other connections to the database
- Use PostgreSQL for production (better concurrency)

**Problem:** Connection pool exhausted
**Solution:** Increase pool size in `app/database.py`

### Dependency Issues

**Problem:** bcrypt installation fails
**Solution:** Install build tools:
```bash
# Ubuntu/Debian
sudo apt-get install build-essential python3-dev

# macOS
xcode-select --install
```

## Rollback Procedure

If you need to rollback a deployment:

1. **Restore database backup:**
```bash
# PostgreSQL
pg_restore -d recipe_saver backup_file.dump

# SQLite
cp backup_file.db recipe_saver.db
```

2. **Revert code:**
```bash
git checkout previous_version_tag
pip install -r requirements.txt
```

3. **Restart server**

## Health Checks

The API provides health check endpoints:

- `GET /` - Basic health check
- `GET /api/health` - Detailed health status (if implemented)

## Support

For issues or questions:
- Check the main README.md
- Review API documentation in docs/API.md
- Check test files for usage examples
