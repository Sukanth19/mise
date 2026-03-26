# MySQL Schema Documentation

## Overview

This document describes the MySQL database schema for the Recipe Saver application. The schema consists of 17 tables with foreign key relationships, indexes, and constraints to ensure data integrity and optimal query performance.

**Database Configuration:**
- Character Set: `utf8mb4`
- Collation: `utf8mb4_unicode_ci`
- Storage Engine: InnoDB
- MySQL Version: 8.0+

## Table Definitions

### 1. users

Stores user account information.

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Columns:**
- `id`: Primary key, auto-incremented
- `username`: Unique username for login
- `password_hash`: Hashed password (bcrypt)
- `created_at`: Account creation timestamp

**Indexes:**
- Primary key on `id`
- Unique index on `username` (for login lookups)
- Index on `created_at` (for sorting)

**Relationships:**
- One-to-many with `recipes`
- One-to-many with `collections`
- One-to-many with `meal_plans`
- One-to-many with `shopping_lists`
- Many-to-many with `users` (via `user_follows`)

---

### 2. recipes

Stores recipe information including ingredients and instructions.

```sql
CREATE TABLE recipes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(500) NOT NULL,
    image_url VARCHAR(1000),
    ingredients TEXT NOT NULL,
    steps TEXT NOT NULL,
    tags VARCHAR(1000),
    reference_link VARCHAR(1000),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_favorite BOOLEAN DEFAULT FALSE,
    visibility VARCHAR(20) DEFAULT 'private',
    servings INT,
    source_recipe_id INT,
    source_author_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (source_recipe_id) REFERENCES recipes(id) ON DELETE SET NULL,
    FOREIGN KEY (source_author_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_title (title),
    INDEX idx_created_at (created_at),
    INDEX idx_visibility (visibility),
    INDEX idx_user_created (user_id, created_at),
    FULLTEXT INDEX idx_search (title, ingredients)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Columns:**
- `id`: Primary key, auto-incremented
- `user_id`: Foreign key to `users.id`
- `title`: Recipe name (max 500 characters)
- `image_url`: URL to recipe image
- `ingredients`: JSON array stored as TEXT
- `steps`: JSON array stored as TEXT
- `tags`: Comma-separated tags or JSON array
- `reference_link`: Source URL for imported recipes
- `created_at`: Creation timestamp
- `updated_at`: Last modification timestamp
- `is_favorite`: Boolean flag for user favorites
- `visibility`: `private`, `public`, or `unlisted`
- `servings`: Number of servings
- `source_recipe_id`: Original recipe ID if forked
- `source_author_id`: Original author ID if forked

**Indexes:**
- Primary key on `id`
- Index on `user_id` (for user's recipes queries)
- Index on `title` (for sorting)
- Index on `created_at` (for sorting by date)
- Index on `visibility` (for filtering public recipes)
- Compound index on `(user_id, created_at)` (for user's recent recipes)
- FULLTEXT index on `(title, ingredients)` (for search)

**Foreign Keys:**
- `user_id` → `users.id` (CASCADE on delete)
- `source_recipe_id` → `recipes.id` (SET NULL on delete)
- `source_author_id` → `users.id` (SET NULL on delete)

**Relationships:**
- Many-to-one with `users`
- One-to-one with `nutrition_facts`
- One-to-many with `dietary_labels`
- One-to-many with `allergen_warnings`
- One-to-many with `recipe_ratings`
- One-to-many with `recipe_notes`
- Many-to-many with `collections` (via `collection_recipes`)

---

### 3. nutrition_facts

Stores nutritional information for recipes (one-to-one relationship).

```sql
CREATE TABLE nutrition_facts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recipe_id INT UNIQUE NOT NULL,
    calories FLOAT,
    protein_g FLOAT,
    carbs_g FLOAT,
    fat_g FLOAT,
    fiber_g FLOAT,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    INDEX idx_recipe_id (recipe_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Columns:**
- `id`: Primary key, auto-incremented
- `recipe_id`: Foreign key to `recipes.id` (unique)
- `calories`: Calories per serving
- `protein_g`: Protein in grams
- `carbs_g`: Carbohydrates in grams
- `fat_g`: Fat in grams
- `fiber_g`: Fiber in grams

**Constraints:**
- UNIQUE constraint on `recipe_id` (one-to-one relationship)

**Foreign Keys:**
- `recipe_id` → `recipes.id` (CASCADE on delete)

---

### 4. dietary_labels

Stores dietary labels for recipes (vegan, vegetarian, gluten-free, etc.).

```sql
CREATE TABLE dietary_labels (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recipe_id INT NOT NULL,
    label VARCHAR(100) NOT NULL,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    INDEX idx_recipe_id (recipe_id),
    INDEX idx_label (label)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Columns:**
- `id`: Primary key, auto-incremented
- `recipe_id`: Foreign key to `recipes.id`
- `label`: Dietary label (e.g., "vegan", "gluten-free", "keto")

**Indexes:**
- Index on `recipe_id` (for recipe lookups)
- Index on `label` (for filtering by dietary preference)

**Foreign Keys:**
- `recipe_id` → `recipes.id` (CASCADE on delete)

---

### 5. allergen_warnings

Stores allergen warnings for recipes.

```sql
CREATE TABLE allergen_warnings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recipe_id INT NOT NULL,
    allergen VARCHAR(100) NOT NULL,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    INDEX idx_recipe_id (recipe_id),
    INDEX idx_allergen (allergen)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Columns:**
- `id`: Primary key, auto-incremented
- `recipe_id`: Foreign key to `recipes.id`
- `allergen`: Allergen name (e.g., "nuts", "dairy", "eggs")

**Indexes:**
- Index on `recipe_id` (for recipe lookups)
- Index on `allergen` (for filtering by allergen)

**Foreign Keys:**
- `recipe_id` → `recipes.id` (CASCADE on delete)

---

### 6. recipe_ratings

Stores user ratings for recipes (1-5 stars).

```sql
CREATE TABLE recipe_ratings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recipe_id INT NOT NULL,
    user_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_recipe_rating (recipe_id, user_id),
    INDEX idx_recipe_id (recipe_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Columns:**
- `id`: Primary key, auto-incremented
- `recipe_id`: Foreign key to `recipes.id`
- `user_id`: Foreign key to `users.id`
- `rating`: Rating value (1-5)
- `created_at`: Rating creation timestamp
- `updated_at`: Last update timestamp

**Constraints:**
- CHECK constraint: `rating >= 1 AND rating <= 5`
- UNIQUE constraint on `(recipe_id, user_id)` (one rating per user per recipe)

**Foreign Keys:**
- `recipe_id` → `recipes.id` (CASCADE on delete)
- `user_id` → `users.id` (CASCADE on delete)

---

### 7. recipe_notes

Stores personal notes users add to recipes.

```sql
CREATE TABLE recipe_notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recipe_id INT NOT NULL,
    user_id INT NOT NULL,
    note_text TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_recipe_id (recipe_id),
    INDEX idx_user_id (user_id),
    INDEX idx_recipe_user (recipe_id, user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Columns:**
- `id`: Primary key, auto-incremented
- `recipe_id`: Foreign key to `recipes.id`
- `user_id`: Foreign key to `users.id`
- `note_text`: Note content
- `created_at`: Note creation timestamp
- `updated_at`: Last update timestamp

**Indexes:**
- Compound index on `(recipe_id, user_id)` (for user's notes on recipe)

**Foreign Keys:**
- `recipe_id` → `recipes.id` (CASCADE on delete)
- `user_id` → `users.id` (CASCADE on delete)

---

### 8. collections

Stores recipe collections (folders) with support for nesting.

```sql
CREATE TABLE collections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    cover_image_url VARCHAR(1000),
    parent_collection_id INT,
    nesting_level INT DEFAULT 0,
    share_token VARCHAR(255) UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_collection_id) REFERENCES collections(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_parent_collection_id (parent_collection_id),
    INDEX idx_share_token (share_token),
    INDEX idx_user_created (user_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Columns:**
- `id`: Primary key, auto-incremented
- `user_id`: Foreign key to `users.id`
- `name`: Collection name
- `description`: Collection description
- `cover_image_url`: Cover image URL
- `parent_collection_id`: Parent collection ID (for nesting)
- `nesting_level`: Depth level (0-3)
- `share_token`: Unique token for sharing
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

**Indexes:**
- Index on `user_id` (for user's collections)
- Index on `parent_collection_id` (for nested collections)
- Unique index on `share_token` (for shared collections)
- Compound index on `(user_id, created_at)` (for recent collections)

**Foreign Keys:**
- `user_id` → `users.id` (CASCADE on delete)
- `parent_collection_id` → `collections.id` (CASCADE on delete)

**Relationships:**
- Self-referential (nested collections)
- Many-to-many with `recipes` (via `collection_recipes`)

---

### 9. collection_recipes

Join table for many-to-many relationship between collections and recipes.

```sql
CREATE TABLE collection_recipes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    collection_id INT NOT NULL,
    recipe_id INT NOT NULL,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    UNIQUE KEY unique_collection_recipe (collection_id, recipe_id),
    INDEX idx_collection_id (collection_id),
    INDEX idx_recipe_id (recipe_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Columns:**
- `id`: Primary key, auto-incremented
- `collection_id`: Foreign key to `collections.id`
- `recipe_id`: Foreign key to `recipes.id`
- `added_at`: Timestamp when recipe was added to collection

**Constraints:**
- UNIQUE constraint on `(collection_id, recipe_id)` (no duplicate entries)

**Foreign Keys:**
- `collection_id` → `collections.id` (CASCADE on delete)
- `recipe_id` → `recipes.id` (CASCADE on delete)

---

### 10. meal_plans

Stores meal planning entries (recipes scheduled for specific dates/times).

```sql
CREATE TABLE meal_plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    recipe_id INT NOT NULL,
    meal_date DATE NOT NULL,
    meal_time VARCHAR(20) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_meal_date (meal_date),
    INDEX idx_user_date (user_id, meal_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Columns:**
- `id`: Primary key, auto-incremented
- `user_id`: Foreign key to `users.id`
- `recipe_id`: Foreign key to `recipes.id`
- `meal_date`: Date of the meal
- `meal_time`: Time slot (e.g., "breakfast", "lunch", "dinner", "snack")
- `created_at`: Creation timestamp

**Indexes:**
- Index on `user_id` (for user's meal plans)
- Index on `meal_date` (for date-based queries)
- Compound index on `(user_id, meal_date)` (for user's meals on specific date)

**Foreign Keys:**
- `user_id` → `users.id` (CASCADE on delete)
- `recipe_id` → `recipes.id` (CASCADE on delete)

---

### 11. meal_plan_templates

Stores reusable meal plan templates.

```sql
CREATE TABLE meal_plan_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Columns:**
- `id`: Primary key, auto-incremented
- `user_id`: Foreign key to `users.id`
- `name`: Template name
- `description`: Template description
- `created_at`: Creation timestamp

**Foreign Keys:**
- `user_id` → `users.id` (CASCADE on delete)

---

### 12. meal_plan_template_items

Stores items within meal plan templates.

```sql
CREATE TABLE meal_plan_template_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    template_id INT NOT NULL,
    recipe_id INT NOT NULL,
    day_offset INT NOT NULL,
    meal_time VARCHAR(20) NOT NULL,
    FOREIGN KEY (template_id) REFERENCES meal_plan_templates(id) ON DELETE CASCADE,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    INDEX idx_template_id (template_id),
    INDEX idx_recipe_id (recipe_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Columns:**
- `id`: Primary key, auto-incremented
- `template_id`: Foreign key to `meal_plan_templates.id`
- `recipe_id`: Foreign key to `recipes.id`
- `day_offset`: Day offset from template start (0-6 for weekly)
- `meal_time`: Time slot (e.g., "breakfast", "lunch", "dinner")

**Foreign Keys:**
- `template_id` → `meal_plan_templates.id` (CASCADE on delete)
- `recipe_id` → `recipes.id` (CASCADE on delete)

---

### 13. shopping_lists

Stores shopping lists.

```sql
CREATE TABLE shopping_lists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    share_token VARCHAR(255) UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_share_token (share_token)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Columns:**
- `id`: Primary key, auto-incremented
- `user_id`: Foreign key to `users.id`
- `name`: Shopping list name
- `share_token`: Unique token for sharing
- `created_at`: Creation timestamp

**Foreign Keys:**
- `user_id` → `users.id` (CASCADE on delete)

---

### 14. shopping_list_items

Stores items within shopping lists.

```sql
CREATE TABLE shopping_list_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    shopping_list_id INT NOT NULL,
    ingredient_name VARCHAR(255) NOT NULL,
    quantity VARCHAR(100),
    category VARCHAR(50),
    is_checked BOOLEAN DEFAULT FALSE,
    is_custom BOOLEAN DEFAULT FALSE,
    recipe_id INT,
    FOREIGN KEY (shopping_list_id) REFERENCES shopping_lists(id) ON DELETE CASCADE,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE SET NULL,
    INDEX idx_shopping_list_id (shopping_list_id),
    INDEX idx_recipe_id (recipe_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Columns:**
- `id`: Primary key, auto-incremented
- `shopping_list_id`: Foreign key to `shopping_lists.id`
- `ingredient_name`: Ingredient name
- `quantity`: Quantity (e.g., "2 cups", "500g")
- `category`: Grocery category (e.g., "produce", "dairy", "meat")
- `is_checked`: Whether item is checked off
- `is_custom`: Whether item was manually added
- `recipe_id`: Optional reference to source recipe

**Foreign Keys:**
- `shopping_list_id` → `shopping_lists.id` (CASCADE on delete)
- `recipe_id` → `recipes.id` (SET NULL on delete)

---

### 15. user_follows

Stores user follow relationships (social feature).

```sql
CREATE TABLE user_follows (
    id INT AUTO_INCREMENT PRIMARY KEY,
    follower_id INT NOT NULL,
    following_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (follower_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (following_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_follow (follower_id, following_id),
    INDEX idx_follower_id (follower_id),
    INDEX idx_following_id (following_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Columns:**
- `id`: Primary key, auto-incremented
- `follower_id`: User who is following
- `following_id`: User being followed
- `created_at`: Follow timestamp

**Constraints:**
- UNIQUE constraint on `(follower_id, following_id)` (no duplicate follows)

**Foreign Keys:**
- `follower_id` → `users.id` (CASCADE on delete)
- `following_id` → `users.id` (CASCADE on delete)

---

### 16. recipe_likes

Stores recipe likes (social feature).

```sql
CREATE TABLE recipe_likes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recipe_id INT NOT NULL,
    user_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_like (recipe_id, user_id),
    INDEX idx_recipe_id (recipe_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Columns:**
- `id`: Primary key, auto-incremented
- `recipe_id`: Foreign key to `recipes.id`
- `user_id`: Foreign key to `users.id`
- `created_at`: Like timestamp

**Constraints:**
- UNIQUE constraint on `(recipe_id, user_id)` (one like per user per recipe)

**Foreign Keys:**
- `recipe_id` → `recipes.id` (CASCADE on delete)
- `user_id` → `users.id` (CASCADE on delete)

---

### 17. recipe_comments

Stores comments on recipes (social feature).

```sql
CREATE TABLE recipe_comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recipe_id INT NOT NULL,
    user_id INT NOT NULL,
    comment_text TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_recipe_id (recipe_id),
    INDEX idx_user_id (user_id),
    INDEX idx_recipe_created (recipe_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Columns:**
- `id`: Primary key, auto-incremented
- `recipe_id`: Foreign key to `recipes.id`
- `user_id`: Foreign key to `users.id`
- `comment_text`: Comment content
- `created_at`: Comment creation timestamp
- `updated_at`: Last update timestamp

**Indexes:**
- Compound index on `(recipe_id, created_at)` (for chronological comments)

**Foreign Keys:**
- `recipe_id` → `recipes.id` (CASCADE on delete)
- `user_id` → `users.id` (CASCADE on delete)

---

## Entity Relationship Diagram

```
┌─────────────┐
│    users    │
└──────┬──────┘
       │
       ├─────────────────────────────────────────────────────┐
       │                                                     │
       ▼                                                     ▼
┌─────────────┐                                      ┌──────────────┐
│   recipes   │◄─────────────────────────────────────│ collections  │
└──────┬──────┘                                      └──────┬───────┘
       │                                                     │
       ├──────────┬──────────┬──────────┬──────────┐       │
       │          │          │          │          │       │
       ▼          ▼          ▼          ▼          ▼       ▼
┌──────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────────────┐
│nutrition │ │dietary  │ │allergen │ │ recipe  │ │collection_recipes│
│  _facts  │ │ _labels │ │_warnings│ │ _ratings│ │  (join table)    │
└──────────┘ └─────────┘ └─────────┘ └─────────┘ └──────────────────┘

       ┌──────────────────────────────────────────┐
       │                                          │
       ▼                                          ▼
┌──────────────┐                          ┌──────────────┐
│  meal_plans  │                          │recipe_notes  │
└──────────────┘                          └──────────────┘

       ┌──────────────────────────────────────────┐
       │                                          │
       ▼                                          ▼
┌──────────────────┐                      ┌──────────────┐
│meal_plan         │                      │shopping_lists│
│  _templates      │                      └──────┬───────┘
└────────┬─────────┘                             │
         │                                       ▼
         ▼                                ┌──────────────────┐
┌──────────────────────┐                 │shopping_list     │
│meal_plan_template    │                 │    _items        │
│      _items          │                 └──────────────────┘
└──────────────────────┘

       ┌──────────────────────────────────────────┐
       │                                          │
       ▼                                          ▼
┌──────────────┐                          ┌──────────────┐
│ user_follows │                          │recipe_likes  │
└──────────────┘                          └──────────────┘
                                                 │
                                                 ▼
                                          ┌──────────────┐
                                          │recipe        │
                                          │  _comments   │
                                          └──────────────┘
```

## Index Summary

### Performance-Critical Indexes

1. **User Lookups:**
   - `users.username` (UNIQUE) - Login queries
   - `recipes.user_id` - User's recipes

2. **Recipe Search:**
   - `recipes.title, recipes.ingredients` (FULLTEXT) - Text search
   - `recipes.visibility` - Public recipe filtering

3. **Sorting:**
   - `recipes.created_at` - Recent recipes
   - `recipes.title` - Alphabetical sorting
   - `(recipes.user_id, recipes.created_at)` - User's recent recipes

4. **Meal Planning:**
   - `meal_plans.meal_date` - Date-based queries
   - `(meal_plans.user_id, meal_plans.meal_date)` - User's meals on date

5. **Collections:**
   - `collections.share_token` (UNIQUE) - Shared collection access
   - `collection_recipes.(collection_id, recipe_id)` (UNIQUE) - Join queries

6. **Social Features:**
   - `(recipe_ratings.recipe_id, recipe_ratings.user_id)` (UNIQUE) - User ratings
   - `(recipe_likes.recipe_id, recipe_likes.user_id)` (UNIQUE) - User likes
   - `(user_follows.follower_id, user_follows.following_id)` (UNIQUE) - Follow relationships

## Foreign Key Relationships

### Cascade Behavior

**ON DELETE CASCADE:**
- When a user is deleted, all their recipes, collections, meal plans, ratings, notes, follows, likes, and comments are deleted
- When a recipe is deleted, all its nutrition facts, dietary labels, allergen warnings, ratings, notes, likes, and comments are deleted
- When a collection is deleted, all its collection_recipes entries are deleted
- When a meal plan template is deleted, all its items are deleted
- When a shopping list is deleted, all its items are deleted

**ON DELETE SET NULL:**
- When a recipe is deleted, references in `recipes.source_recipe_id` and `recipes.source_author_id` are set to NULL
- When a recipe is deleted, references in `shopping_list_items.recipe_id` are set to NULL

## Data Types and Constraints

### String Lengths

- `VARCHAR(20)`: Short enums (visibility, meal_time)
- `VARCHAR(50)`: Categories
- `VARCHAR(100)`: Labels, allergens
- `VARCHAR(255)`: Usernames, names, tokens
- `VARCHAR(500)`: Recipe titles
- `VARCHAR(1000)`: URLs, tags
- `TEXT`: Unlimited content (ingredients, steps, notes, descriptions, comments)

### Numeric Types

- `INT`: Primary keys, foreign keys, counts, servings
- `FLOAT`: Nutrition values (calories, protein, carbs, fat, fiber)

### Date/Time Types

- `DATETIME`: Timestamps with time component
- `DATE`: Date-only fields (meal_date)

### Boolean Types

- `BOOLEAN`: Flags (is_favorite, is_checked, is_custom)

## Character Set and Collation

All tables use:
- Character Set: `utf8mb4` (supports full Unicode including emoji)
- Collation: `utf8mb4_unicode_ci` (case-insensitive Unicode collation)

This ensures proper handling of international characters and emoji in recipe titles, ingredients, and user content.

## Storage Engine

All tables use InnoDB storage engine for:
- ACID compliance
- Foreign key constraint support
- Row-level locking
- Crash recovery
- Better performance for read-write workloads
