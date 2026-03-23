-- Migration: Recipe table extensions (PostgreSQL)
-- Description: Add new columns to recipes table for favorites, visibility, servings, and source tracking

-- Add is_favorite column
ALTER TABLE recipes ADD COLUMN is_favorite BOOLEAN DEFAULT FALSE;

-- Add visibility column
ALTER TABLE recipes ADD COLUMN visibility VARCHAR(20) DEFAULT 'private' CHECK (visibility IN ('private', 'public', 'unlisted'));

-- Add servings column
ALTER TABLE recipes ADD COLUMN servings INTEGER DEFAULT 1;

-- Add source tracking columns
ALTER TABLE recipes ADD COLUMN source_recipe_id INTEGER REFERENCES recipes(id) ON DELETE SET NULL;
ALTER TABLE recipes ADD COLUMN source_author_id INTEGER REFERENCES users(id) ON DELETE SET NULL;

-- Create indexes for new columns
CREATE INDEX idx_recipes_is_favorite ON recipes(is_favorite);
CREATE INDEX idx_recipes_visibility ON recipes(visibility);
CREATE INDEX idx_recipes_source_recipe_id ON recipes(source_recipe_id);
