-- Migration: Collections and collection_recipes tables (PostgreSQL)
-- Description: Create tables for organizing recipes into collections with nesting support

-- Collections table
CREATE TABLE collections (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    cover_image_url VARCHAR(500),
    parent_collection_id INTEGER REFERENCES collections(id) ON DELETE CASCADE,
    nesting_level INTEGER DEFAULT 0 CHECK (nesting_level <= 3),
    share_token VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for collections
CREATE INDEX idx_collections_user_id ON collections(user_id);
CREATE INDEX idx_collections_parent_id ON collections(parent_collection_id);
CREATE INDEX idx_collections_share_token ON collections(share_token);

-- Collection recipes junction table (many-to-many)
CREATE TABLE collection_recipes (
    id SERIAL PRIMARY KEY,
    collection_id INTEGER NOT NULL REFERENCES collections(id) ON DELETE CASCADE,
    recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(collection_id, recipe_id)
);

-- Create indexes for collection_recipes
CREATE INDEX idx_collection_recipes_collection_id ON collection_recipes(collection_id);
CREATE INDEX idx_collection_recipes_recipe_id ON collection_recipes(recipe_id);
