-- Migration: Social features tables (PostgreSQL)
-- Description: Create tables for user follows, recipe likes, and recipe comments

-- User follows table
CREATE TABLE user_follows (
    id SERIAL PRIMARY KEY,
    follower_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    following_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(follower_id, following_id),
    CHECK (follower_id != following_id)
);

-- Create indexes for user_follows
CREATE INDEX idx_user_follows_follower_id ON user_follows(follower_id);
CREATE INDEX idx_user_follows_following_id ON user_follows(following_id);

-- Recipe likes table
CREATE TABLE recipe_likes (
    id SERIAL PRIMARY KEY,
    recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(recipe_id, user_id)
);

-- Create indexes for recipe_likes
CREATE INDEX idx_recipe_likes_recipe_id ON recipe_likes(recipe_id);
CREATE INDEX idx_recipe_likes_user_id ON recipe_likes(user_id);

-- Recipe comments table
CREATE TABLE recipe_comments (
    id SERIAL PRIMARY KEY,
    recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    comment_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for recipe_comments
CREATE INDEX idx_recipe_comments_recipe_id ON recipe_comments(recipe_id);
CREATE INDEX idx_recipe_comments_user_id ON recipe_comments(user_id);
