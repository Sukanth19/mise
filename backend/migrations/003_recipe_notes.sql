-- Migration: Recipe notes table
-- Description: Create table for storing user notes on recipes

CREATE TABLE recipe_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    note_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_recipe_notes_recipe_id ON recipe_notes(recipe_id);
CREATE INDEX idx_recipe_notes_user_id ON recipe_notes(user_id);
