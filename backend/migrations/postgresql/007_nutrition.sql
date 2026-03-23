-- Migration: Nutrition facts, dietary labels, and allergen warnings tables (PostgreSQL)
-- Description: Create tables for tracking nutrition information and dietary restrictions

-- Nutrition facts table
CREATE TABLE nutrition_facts (
    id SERIAL PRIMARY KEY,
    recipe_id INTEGER NOT NULL UNIQUE REFERENCES recipes(id) ON DELETE CASCADE,
    calories DECIMAL(10, 2),
    protein_g DECIMAL(10, 2),
    carbs_g DECIMAL(10, 2),
    fat_g DECIMAL(10, 2),
    fiber_g DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for nutrition_facts
CREATE INDEX idx_nutrition_facts_recipe_id ON nutrition_facts(recipe_id);

-- Dietary labels table
CREATE TABLE dietary_labels (
    id SERIAL PRIMARY KEY,
    recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    label VARCHAR(50) NOT NULL CHECK (label IN ('vegan', 'vegetarian', 'gluten-free', 'dairy-free', 'keto', 'paleo', 'low-carb')),
    UNIQUE(recipe_id, label)
);

-- Create indexes for dietary_labels
CREATE INDEX idx_dietary_labels_recipe_id ON dietary_labels(recipe_id);
CREATE INDEX idx_dietary_labels_label ON dietary_labels(label);

-- Allergen warnings table
CREATE TABLE allergen_warnings (
    id SERIAL PRIMARY KEY,
    recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    allergen VARCHAR(50) NOT NULL CHECK (allergen IN ('nuts', 'dairy', 'eggs', 'soy', 'wheat', 'fish', 'shellfish')),
    UNIQUE(recipe_id, allergen)
);

-- Create indexes for allergen_warnings
CREATE INDEX idx_allergen_warnings_recipe_id ON allergen_warnings(recipe_id);
CREATE INDEX idx_allergen_warnings_allergen ON allergen_warnings(allergen);
