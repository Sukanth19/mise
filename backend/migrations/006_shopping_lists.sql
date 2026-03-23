-- Migration: Shopping lists and items tables
-- Description: Create tables for managing shopping lists with categorization and sharing

-- Shopping lists table
CREATE TABLE shopping_lists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    share_token VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for shopping_lists
CREATE INDEX idx_shopping_lists_user_id ON shopping_lists(user_id);
CREATE INDEX idx_shopping_lists_share_token ON shopping_lists(share_token);

-- Shopping list items table
CREATE TABLE shopping_list_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shopping_list_id INTEGER NOT NULL REFERENCES shopping_lists(id) ON DELETE CASCADE,
    ingredient_name VARCHAR(255) NOT NULL,
    quantity VARCHAR(100),
    category VARCHAR(50) DEFAULT 'other' CHECK (category IN ('produce', 'dairy', 'meat', 'pantry', 'other')),
    is_checked BOOLEAN DEFAULT FALSE,
    is_custom BOOLEAN DEFAULT FALSE,
    recipe_id INTEGER REFERENCES recipes(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for shopping_list_items
CREATE INDEX idx_shopping_list_items_list_id ON shopping_list_items(shopping_list_id);
