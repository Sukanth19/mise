from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base, health_check
from app.routers import auth, recipes, collections, images
# TODO: Update these routers to use SQLAlchemy instead of MongoDB
# from app.routers import ratings, notes, meal_plans, shopping_list, nutrition, social
from app.config import settings
import os
import logging

logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Recipe Saver API")


@app.on_event("startup")
async def startup_event():
    """
    Startup event handler - establish MySQL connection and verify connectivity.
    
    Logs connection events for MySQL operations.
    
    Validates: Requirements 1.4, 10.1
    """
    logger.info("Starting Recipe Saver API...")
    
    # Log MySQL connection attempt if using MySQL
    if settings.database_url.startswith("mysql"):
        from app.utils.mysql_logger import log_connection_event
        log_connection_event("startup", "Attempting to connect to MySQL database", "info")
    
    # Verify database connectivity
    try:
        if health_check():
            logger.info("Successfully connected to database")
            
            # Log successful MySQL connection
            if settings.database_url.startswith("mysql"):
                from app.utils.mysql_logger import log_connection_event
                log_connection_event("startup_success", "MySQL database connection verified", "info")
        else:
            logger.error("Database health check failed")
            
            # Log MySQL connection failure
            if settings.database_url.startswith("mysql"):
                from app.utils.mysql_logger import log_connection_event
                log_connection_event("startup_failed", "MySQL database health check failed", "error")
            
            raise RuntimeError("Failed to connect to database")
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        
        # Log MySQL connection error
        if settings.database_url.startswith("mysql"):
            from app.utils.mysql_logger import log_error
            log_error("connection", str(e), "startup")
        
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler - close all MySQL connections gracefully.
    
    Logs disconnection events for MySQL operations.
    
    Validates: Requirements 1.5, 10.1
    """
    logger.info("Shutting down Recipe Saver API...")
    
    # Log MySQL disconnection attempt if using MySQL
    if settings.database_url.startswith("mysql"):
        from app.utils.mysql_logger import log_connection_event
        log_connection_event("shutdown", "Closing MySQL database connections", "info")
    
    # Close database connections
    try:
        engine.dispose()
        logger.info("Database connections closed successfully")
        
        # Log successful MySQL disconnection
        if settings.database_url.startswith("mysql"):
            from app.utils.mysql_logger import log_connection_event
            log_connection_event("shutdown_success", "MySQL connections closed successfully", "info")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")
        
        # Log MySQL disconnection error
        if settings.database_url.startswith("mysql"):
            from app.utils.mysql_logger import log_error
            log_error("disconnection", str(e), "shutdown")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
os.makedirs(settings.upload_dir, exist_ok=True)

# Mount static files for serving uploaded images
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# Include routers
app.include_router(auth.router)
app.include_router(recipes.router)
app.include_router(collections.router)
app.include_router(images.router)
# TODO: Re-enable these routers after converting them to SQLAlchemy
# app.include_router(social.router)
# app.include_router(ratings.router)
# app.include_router(notes.router)
# app.include_router(meal_plans.router)
# app.include_router(meal_plans.template_router)
# app.include_router(shopping_list.router)
# app.include_router(nutrition.router)


@app.get("/")
def read_root():
    return {"message": "Recipe Saver API"}


@app.get("/health")
def health_check_endpoint():
    """
    Health check endpoint for MySQL connectivity.
    
    Returns:
        dict: Health status with database connectivity information
        
    Validates: Requirements 1.4
    """
    db_healthy = health_check()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected"
    }
