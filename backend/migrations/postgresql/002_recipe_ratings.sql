-- Migration: Recipe ratings table (PostgreSQL)
-- Description: Create table for storing user ratings of recipes

CREATE TABLE recipe_ratings (
    id SERIAL PRIMARY KEY,
    recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(recipe_id, user_id)
);

-- Create indexes
CREATE INDEX idx_recipe_ratings_recipe_id ON recipe_ratings(recipe_id);
CREATE INDEX idx_recipe_ratings_user_id ON recipe_ratings(user_id);
