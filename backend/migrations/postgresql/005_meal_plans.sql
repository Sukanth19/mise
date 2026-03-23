-- Migration: Meal plans and templates tables (PostgreSQL)
-- Description: Create tables for calendar-based meal planning and reusable templates

-- Meal plans table
CREATE TABLE meal_plans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    meal_date DATE NOT NULL,
    meal_time VARCHAR(20) NOT NULL CHECK (meal_time IN ('breakfast', 'lunch', 'dinner', 'snack')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for meal_plans
CREATE INDEX idx_meal_plans_user_id ON meal_plans(user_id);
CREATE INDEX idx_meal_plans_date ON meal_plans(meal_date);
CREATE INDEX idx_meal_plans_recipe_id ON meal_plans(recipe_id);

-- Meal plan templates table
CREATE TABLE meal_plan_templates (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for meal_plan_templates
CREATE INDEX idx_meal_plan_templates_user_id ON meal_plan_templates(user_id);

-- Meal plan template items table
CREATE TABLE meal_plan_template_items (
    id SERIAL PRIMARY KEY,
    template_id INTEGER NOT NULL REFERENCES meal_plan_templates(id) ON DELETE CASCADE,
    recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    day_offset INTEGER NOT NULL,
    meal_time VARCHAR(20) NOT NULL CHECK (meal_time IN ('breakfast', 'lunch', 'dinner', 'snack'))
);

-- Create index for meal_plan_template_items
CREATE INDEX idx_template_items_template_id ON meal_plan_template_items(template_id);
