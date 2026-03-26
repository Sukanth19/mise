"""Example integration of MySQL error handlers into FastAPI routers.

This file demonstrates how to integrate the MySQL error handlers into
existing FastAPI routers for comprehensive error handling.

Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.7
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError
from app.database import get_db
from app.models import Recipe, User, RecipeRating
from app.schemas import RecipeCreate, RecipeUpdate, RecipeResponse
from app.utils.mysql_error_handler import MySQLErrorHandler

router = APIRouter(prefix="/api/recipes", tags=["recipes"])


# Example 1: Create Recipe with Constraint Violation Handling
@router.post("", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
def create_recipe(
    recipe_data: RecipeCreate,
    db: Session = Depends(get_db),
    user_id: int = 1  # From auth dependency
):
    """
    Create a new recipe with comprehensive error handling.
    
    Handles:
    - Foreign key violations (invalid user_id)
    - Not null violations (missing required fields)
    - Connection errors
    """
    try:
        recipe = Recipe(
            user_id=user_id,
            title=recipe_data.title,
            ingredients=recipe_data.ingredients,
            steps=recipe_data.steps,
            # ... other fields
        )
        db.add(recipe)
        db.commit()
        db.refresh(recipe)
        return recipe
    except IntegrityError as e:
        db.rollback()
        # Automatically provides user-friendly messages for:
        # - Foreign key violations: "Referenced record does not exist"
        # - Not null violations: "Required field 'title' cannot be empty"
        raise MySQLErrorHandler.handle_constraint_violation(e)
    except OperationalError as e:
        db.rollback()
        # Handles connection errors, timeouts, deadlocks
        raise MySQLErrorHandler.handle_database_error(e)
    except Exception as e:
        db.rollback()
        # Generic error handler for unexpected errors
        raise MySQLErrorHandler.handle_database_error(e)


# Example 2: Get Recipe with 404 Handling
@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    user_id: int = 1  # From auth dependency
):
    """
    Get a recipe by ID with proper 404 handling.
    
    Handles:
    - Missing records (404 Not Found)
    - Query errors
    """
    try:
        recipe = db.query(Recipe).filter(
            Recipe.id == recipe_id,
            Recipe.user_id == user_id
        ).first()
        
        if not recipe:
            # Provides consistent 404 response: "Recipe not found."
            raise MySQLErrorHandler.handle_not_found("Recipe", recipe_id)
        
        return recipe
    except Exception as e:
        # Handle any query errors (syntax, timeout, etc.)
        raise MySQLErrorHandler.handle_query_error(e)


# Example 3: Update Recipe with Constraint Handling
@router.put("/{recipe_id}", response_model=RecipeResponse)
def update_recipe(
    recipe_id: int,
    recipe_data: RecipeUpdate,
    db: Session = Depends(get_db),
    user_id: int = 1  # From auth dependency
):
    """
    Update a recipe with comprehensive error handling.
    
    Handles:
    - Missing records (404)
    - Constraint violations
    - Transaction errors
    """
    try:
        recipe = db.query(Recipe).filter(
            Recipe.id == recipe_id,
            Recipe.user_id == user_id
        ).first()
        
        if not recipe:
            raise MySQLErrorHandler.handle_not_found("Recipe", recipe_id)
        
        # Update fields
        for field, value in recipe_data.dict(exclude_unset=True).items():
            setattr(recipe, field, value)
        
        db.commit()
        db.refresh(recipe)
        return recipe
    except IntegrityError as e:
        db.rollback()
        raise MySQLErrorHandler.handle_constraint_violation(e)
    except Exception as e:
        db.rollback()
        raise MySQLErrorHandler.handle_database_error(e)


# Example 4: Delete Recipe with Foreign Key Handling
@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    user_id: int = 1  # From auth dependency
):
    """
    Delete a recipe with foreign key constraint handling.
    
    Handles:
    - Missing records (404)
    - Foreign key violations (recipe referenced by other records)
    """
    try:
        recipe = db.query(Recipe).filter(
            Recipe.id == recipe_id,
            Recipe.user_id == user_id
        ).first()
        
        if not recipe:
            raise MySQLErrorHandler.handle_not_found("Recipe", recipe_id)
        
        db.delete(recipe)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        # Provides message: "Cannot delete this record because it is referenced by other records."
        raise MySQLErrorHandler.handle_constraint_violation(e)
    except Exception as e:
        db.rollback()
        raise MySQLErrorHandler.handle_database_error(e)


# Example 5: Rate Recipe with Unique Constraint Handling
@router.post("/{recipe_id}/rate", status_code=status.HTTP_201_CREATED)
def rate_recipe(
    recipe_id: int,
    rating: int,
    db: Session = Depends(get_db),
    user_id: int = 1  # From auth dependency
):
    """
    Rate a recipe with unique constraint handling.
    
    Handles:
    - Duplicate ratings (unique constraint on recipe_id + user_id)
    - Check constraint violations (rating must be 1-5)
    - Missing recipe (404)
    """
    try:
        # Check if recipe exists
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if not recipe:
            raise MySQLErrorHandler.handle_not_found("Recipe", recipe_id)
        
        # Create rating
        recipe_rating = RecipeRating(
            recipe_id=recipe_id,
            user_id=user_id,
            rating=rating
        )
        db.add(recipe_rating)
        db.commit()
        db.refresh(recipe_rating)
        return recipe_rating
    except IntegrityError as e:
        db.rollback()
        # Automatically provides appropriate messages:
        # - Unique constraint: "You have already rated this recipe."
        # - Check constraint: "Rating must be between 1 and 5."
        raise MySQLErrorHandler.handle_constraint_violation(e)
    except Exception as e:
        db.rollback()
        raise MySQLErrorHandler.handle_database_error(e)


# Example 6: Transaction with Deadlock Handling
@router.post("/{recipe_id}/like", status_code=status.HTTP_201_CREATED)
def like_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    user_id: int = 1  # From auth dependency
):
    """
    Like a recipe with transaction error handling.
    
    Handles:
    - Deadlocks (concurrent likes)
    - Lock wait timeouts
    - Transaction timeouts
    """
    try:
        # Check if recipe exists
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if not recipe:
            raise MySQLErrorHandler.handle_not_found("Recipe", recipe_id)
        
        # Create like (might cause deadlock with concurrent requests)
        from app.models import RecipeLike
        recipe_like = RecipeLike(recipe_id=recipe_id, user_id=user_id)
        db.add(recipe_like)
        
        # Update like count (might cause deadlock)
        recipe.like_count = db.query(RecipeLike).filter(
            RecipeLike.recipe_id == recipe_id
        ).count()
        
        db.commit()
        return {"message": "Recipe liked successfully"}
    except IntegrityError as e:
        db.rollback()
        # Handles duplicate likes
        raise MySQLErrorHandler.handle_constraint_violation(e)
    except OperationalError as e:
        db.rollback()
        # Provides message: "Database deadlock detected. Please retry your request."
        raise MySQLErrorHandler.handle_transaction_error(e)
    except Exception as e:
        db.rollback()
        raise MySQLErrorHandler.handle_database_error(e)


# Example 7: Using Generic Handler (Simplest Approach)
@router.get("/search", response_model=list[RecipeResponse])
def search_recipes(
    query: str,
    db: Session = Depends(get_db),
    user_id: int = 1  # From auth dependency
):
    """
    Search recipes with generic error handling.
    
    The generic handler automatically routes to the appropriate specific handler.
    """
    try:
        recipes = db.query(Recipe).filter(
            Recipe.user_id == user_id,
            Recipe.title.like(f"%{query}%")
        ).all()
        return recipes
    except Exception as e:
        # Generic handler automatically determines error type and provides
        # appropriate status code and message
        raise MySQLErrorHandler.handle_database_error(e)


# Example 8: Global Exception Handler (Application-Wide)
"""
Add this to your main.py for application-wide error handling:

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
"""
