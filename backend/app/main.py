from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app.routers import auth, recipes, images, ratings, notes, collections
from app.config import settings
import os

# Create database tables
# Note: Commented out for testing with SQLite which doesn't support ARRAY types
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Recipe Saver API")

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
app.include_router(images.router)
app.include_router(ratings.router)
app.include_router(notes.router)
app.include_router(collections.router)


@app.get("/")
def read_root():
    return {"message": "Recipe Saver API"}
