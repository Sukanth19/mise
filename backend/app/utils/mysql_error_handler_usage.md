# MySQL Error Handler Usage Guide

This guide demonstrates how to integrate the MySQL error handlers into your FastAPI application.

## Overview

The `MySQLErrorHandler` class provides comprehensive error handling for MySQL operations including:
- Connection errors (authentication, database not found, connection refused, timeout)
- Query errors (syntax errors, timeouts, lock wait timeout)
- Constraint violations (foreign key, unique, not null, check)
- Missing record errors (404 responses)
- Transaction errors (deadlock, timeout, rollback)

## Basic Usage

### Method 1: Using the Generic Handler (Recommended)

The simplest way to handle database errors is to use the `handle_database_error` method, which automatically routes to the appropriate specific handler:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.mysql_error_handler import MySQLErrorHandler

router = APIRouter()

@router.post("/recipes")
def create_recipe(recipe_data: dict, db: Session = Depends(get_db)):
    try:
        # Your database operations here
        recipe = Recipe(**recipe_data)
        db.add(recipe)
        db.commit()
        db.refresh(recipe)
        return recipe
    except Exception as e:
        db.rollback()
        raise MySQLErrorHandler.handle_database_error(e)
```

### Method 2: Using Specific Handlers

For more control, you can use specific handlers based on the error type:

```python
from sqlalchemy.exc import IntegrityError, OperationalError
from app.utils.mysql_error_handler import MySQLErrorHandler

@router.post("/recipes")
def create_recipe(recipe_data: dict, db: Session = Depends(get_db)):
    try:
        recipe = Recipe(**recipe_data)
        db.add(recipe)
        db.commit()
        db.refresh(recipe)
        return recipe
    except IntegrityError as e:
        db.rollback()
        raise MySQLErrorHandler.handle_constraint_violation(e)
    except OperationalError as e:
        db.rollback()
        raise MySQLErrorHandler.handle_connection_error(e)
    except Exception as e:
        db.rollback()
        raise MySQLErrorHandler.handle_database_error(e)
```

### Method 3: Using the Decorator (Convenience)

For simple functions, you can use the decorator:

```python
from app.utils.mysql_error_handler import handle_db_operation

@handle_db_operation("create_recipe")
def create_recipe_service(db: Session, recipe_data: dict):
    recipe = Recipe(**recipe_data)
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe
```

## Handling Specific Scenarios

### 1. Connection Errors

```python
from app.utils.mysql_error_handler import MySQLErrorHandler

# At application startup
try:
    engine.connect()
except Exception as e:
    raise MySQLErrorHandler.handle_connection_error(e, connection_string)
```

### 2. Query Errors

```python
@router.get("/recipes/search")
def search_recipes(query: str, db: Session = Depends(get_db)):
    try:
        # Complex query that might timeout or have syntax errors
        results = db.execute(text(query)).fetchall()
        return results
    except Exception as e:
        raise MySQLErrorHandler.handle_query_error(e, query)
```

### 3. Constraint Violations

```python
@router.post("/users/register")
def register_user(user_data: dict, db: Session = Depends(get_db)):
    try:
        user = User(**user_data)
        db.add(user)
        db.commit()
        return user
    except IntegrityError as e:
        db.rollback()
        # Automatically handles:
        # - Duplicate username (unique constraint)
        # - Missing required fields (not null constraint)
        # - Invalid foreign keys
        raise MySQLErrorHandler.handle_constraint_violation(e)
```

### 4. Missing Records (404)

```python
@router.get("/recipes/{recipe_id}")
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise MySQLErrorHandler.handle_not_found("Recipe", recipe_id)
    return recipe
```

### 5. Transaction Errors

```python
@router.post("/recipes/{recipe_id}/rate")
def rate_recipe(recipe_id: int, rating_data: dict, db: Session = Depends(get_db)):
    try:
        # Start transaction
        rating = RecipeRating(recipe_id=recipe_id, **rating_data)
        db.add(rating)
        
        # Update recipe average rating
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        recipe.avg_rating = calculate_avg_rating(db, recipe_id)
        
        db.commit()
        return rating
    except Exception as e:
        db.rollback()
        # Automatically handles:
        # - Deadlocks (retries recommended)
        # - Lock wait timeouts
        # - Transaction timeouts
        raise MySQLErrorHandler.handle_transaction_error(e)
```

## Integration with FastAPI Exception Handlers

You can also set up global exception handlers in your FastAPI application:

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError
from app.utils.mysql_error_handler import MySQLErrorHandler

app = FastAPI()

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    http_exc = MySQLErrorHandler.handle_constraint_violation(exc)
    return JSONResponse(
        status_code=http_exc.status_code,
        content={"detail": http_exc.detail}
    )

@app.exception_handler(OperationalError)
async def operational_error_handler(request: Request, exc: OperationalError):
    http_exc = MySQLErrorHandler.handle_database_error(exc)
    return JSONResponse(
        status_code=http_exc.status_code,
        content={"detail": http_exc.detail}
    )
```

## Error Messages

The error handler provides user-friendly messages for common scenarios:

### Connection Errors
- "Database authentication failed. Please check credentials."
- "Database not found. Please verify database configuration."
- "Database server is not accessible. Please try again later."
- "Database connection timeout. Please try again later."

### Query Errors
- "Query timeout. The operation took too long to complete."
- "Invalid query syntax. Please check your request parameters."
- "Database is busy. Please try again in a moment."

### Constraint Violations
- "Username already exists. Please choose a different username."
- "Referenced record does not exist. Please verify the related data."
- "Cannot delete this record because it is referenced by other records."
- "Required field 'title' cannot be empty."
- "Rating must be between 1 and 5."

### Transaction Errors
- "Database deadlock detected. Please retry your request."
- "Database is busy. Please try again in a moment."
- "Transaction timeout. Please try again."

## Best Practices

1. **Always rollback on error**: When catching database exceptions, always call `db.rollback()` before raising the HTTP exception.

2. **Use the generic handler**: Unless you need specific behavior, use `handle_database_error()` which routes to the appropriate handler.

3. **Log errors**: The error handlers automatically log errors with appropriate severity levels.

4. **Don't expose internal details**: The error handlers provide user-friendly messages that don't expose database internals.

5. **Handle 404s explicitly**: Use `handle_not_found()` for missing records to provide consistent 404 responses.

6. **Test error scenarios**: Write tests that trigger different error conditions to ensure proper handling.

## Testing Error Handlers

Example test for constraint violation:

```python
def test_duplicate_username_error(client, db):
    # Create first user
    user1 = {"username": "john_doe", "password": "password123"}
    response1 = client.post("/api/auth/register", json=user1)
    assert response1.status_code == 201
    
    # Try to create duplicate user
    response2 = client.post("/api/auth/register", json=user1)
    assert response2.status_code == 409
    assert "username already exists" in response2.json()["detail"].lower()
```

## Logging

The error handlers log errors at appropriate levels:

- **ERROR**: Connection failures, query errors, constraint violations
- **WARNING**: Missing records (404s)
- **CRITICAL**: Rollback failures

Configure logging in your application:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Set DEBUG level for development
if settings.environment == "development":
    logging.getLogger("app.utils.mysql_error_handler").setLevel(logging.DEBUG)
```

## Requirements Validation

This error handling implementation validates the following requirements:

- **Requirement 10.1**: Connection error handling with descriptive messages
- **Requirement 10.2**: Query error handling (syntax errors, timeouts)
- **Requirement 10.3**: Constraint violation error handling (foreign key, unique, not null, check)
- **Requirement 10.4**: Missing record error handling (404 responses)
- **Requirement 10.7**: Transaction error handling (deadlock, timeout, rollback)
