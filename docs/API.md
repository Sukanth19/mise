# API Documentation

## Base URL

```text
http://localhost:8000
```

## Authentication Endpoints

### Register User

```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "username": "john_doe"
}
```

**Error Codes:**
- `400 Bad Request` - Username already exists or invalid input

### Login

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

**Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Codes:**
- `401 Unauthorized` - Invalid credentials

## Recipe Endpoints

### List Recipes

```http
GET /api/recipes?search=optional
Authorization: Bearer {token}
```

**Response (200 OK):**

```json
{
  "recipes": [
    {
      "id": 1,
      "title": "Chocolate Chip Cookies",
      "is_favorite": true,
      "visibility": "private",
      "servings": 24,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Get Recipe

```http
GET /api/recipes/{id}
Authorization: Bearer {token}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "user_id": 1,
  "title": "Chocolate Chip Cookies",
  "ingredients": "2 cups flour, 1 cup sugar...",
  "steps": "1. Mix dry ingredients...",
  "tags": "dessert,cookies",
  "is_favorite": true,
  "visibility": "private",
  "servings": 24,
  "source_recipe_id": null,
  "source_author_id": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Error Codes:**
- `404 Not Found` - Recipe does not exist
- `403 Forbidden` - Recipe belongs to another user

### Create Recipe

```http
POST /api/recipes
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "string",
  "ingredients": "string",
  "steps": "string",
  "tags": "string (optional)",
  "reference_link": "string (optional)",
  "image_url": "string (optional)",
  "servings": 4
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "title": "Chocolate Chip Cookies",
  "visibility": "private"
}
```

### Update Recipe

```http
PUT /api/recipes/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "string",
  "ingredients": "string",
  "steps": "string",
  "tags": "string (optional)",
  "servings": 4
}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "title": "Updated Recipe Title"
}
```

### Delete Recipe

```http
DELETE /api/recipes/{id}
Authorization: Bearer {token}
```

**Response (200 OK):**

```json
{
  "message": "Recipe deleted successfully"
}
```

### Toggle Favorite

```http
PATCH /api/recipes/{id}/favorite
Authorization: Bearer {token}
Content-Type: application/json

{
  "is_favorite": true
}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "is_favorite": true
}
```

### Duplicate Recipe

```http
POST /api/recipes/{id}/duplicate
Authorization: Bearer {token}
```

**Response (201 Created):**

```json
{
  "id": 2,
  "title": "Chocolate Chip Cookies (Copy)"
}
```

### Bulk Delete Recipes

```http
DELETE /api/recipes/bulk
Authorization: Bearer {token}
Content-Type: application/json

{
  "recipe_ids": [1, 2, 3]
}
```

**Response (200 OK):**

```json
{
  "deleted_count": 3
}
```

**Error Codes:**
- `403 Forbidden` - One or more recipes not owned by user

### Import Recipe from URL

```http
POST /api/recipes/import-url
Authorization: Bearer {token}
Content-Type: application/json

{
  "url": "https://example.com/recipe"
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "title": "Imported Recipe",
  "reference_link": "https://example.com/recipe"
}
```

**Error Codes:**
- `400 Bad Request` - URL does not contain parseable recipe data

### Filter Recipes

```http
GET /api/recipes/filter?favorites=true&min_rating=4&tags=dessert,cookies&dietary_labels=vegan&exclude_allergens=nuts&sort_by=rating&sort_order=desc
Authorization: Bearer {token}
```

**Query Parameters:**
- `favorites` (boolean) - Filter by favorite status
- `min_rating` (integer 1-5) - Minimum rating threshold
- `tags` (comma-separated) - Filter by tags (any match)
- `dietary_labels` (comma-separated) - Filter by dietary labels
- `exclude_allergens` (comma-separated) - Exclude recipes with allergens
- `sort_by` (string) - Sort field: `date`, `rating`, `title`
- `sort_order` (string) - Sort order: `asc`, `desc`

**Response (200 OK):**

```json
{
  "recipes": [...],
  "total": 15
}
```

## Rating Endpoints

### Add Rating

```http
POST /api/recipes/{id}/rating
Authorization: Bearer {token}
Content-Type: application/json

{
  "rating": 5
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "recipe_id": 1,
  "user_id": 1,
  "rating": 5
}
```

**Error Codes:**
- `400 Bad Request` - Rating outside 1-5 range

### Update Rating

```http
PUT /api/recipes/{id}/rating
Authorization: Bearer {token}
Content-Type: application/json

{
  "rating": 4
}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "rating": 4
}
```

### Get User Rating

```http
GET /api/recipes/{id}/rating
Authorization: Bearer {token}
```

**Response (200 OK):**

```json
{
  "rating": 5
}
```

## Recipe Notes Endpoints

### Add Note

```http
POST /api/recipes/{id}/notes
Authorization: Bearer {token}
Content-Type: application/json

{
  "note_text": "Added extra vanilla - delicious!"
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "recipe_id": 1,
  "note_text": "Added extra vanilla - delicious!",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Get Notes

```http
GET /api/recipes/{id}/notes
Authorization: Bearer {token}
```

**Response (200 OK):**

```json
{
  "notes": [
    {
      "id": 1,
      "note_text": "Added extra vanilla - delicious!",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Delete Note

```http
DELETE /api/recipes/{recipe_id}/notes/{note_id}
Authorization: Bearer {token}
```

**Response (200 OK):**

```json
{
  "message": "Note deleted successfully"
}
```

## Collection Endpoints

### Create Collection

```http
POST /api/collections
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Holiday Recipes",
  "description": "Recipes for special occasions",
  "parent_collection_id": null
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "name": "Holiday Recipes",
  "nesting_level": 0
}
```

**Error Codes:**
- `400 Bad Request` - Empty name or nesting level exceeds 3

### List Collections

```http
GET /api/collections
Authorization: Bearer {token}
```

**Response (200 OK):**

```json
{
  "collections": [
    {
      "id": 1,
      "name": "Holiday Recipes",
      "recipe_count": 12
    }
  ]
}
```

### Get Collection

```http
GET /api/collections/{id}
Authorization: Bearer {token}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "name": "Holiday Recipes",
  "recipes": [...],
  "sub_collections": [...]
}
```

### Update Collection

```http
PUT /api/collections/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Updated Name",
  "description": "Updated description"
}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "name": "Updated Name"
}
```

### Delete Collection

```http
DELETE /api/collections/{id}
Authorization: Bearer {token}
```

**Response (200 OK):**

```json
{
  "message": "Collection deleted successfully"
}
```

### Add Recipes to Collection

```http
POST /api/collections/{id}/recipes
Authorization: Bearer {token}
Content-Type: application/json

{
  "recipe_ids": [1, 2, 3]
}
```

**Response (200 OK):**

```json
{
  "added_count": 3
}
```

### Remove Recipe from Collection

```http
DELETE /api/collections/{collection_id}/recipes/{recipe_id}
Authorization: Bearer {token}
```

**Response (200 OK):**

```json
{
  "message": "Recipe removed from collection"
}
```

### Generate Share Link

```http
POST /api/collections/{id}/share
Authorization: Bearer {token}
```

**Response (200 OK):**

```json
{
  "share_url": "http://localhost:3000/collections/shared/abc123",
  "share_token": "abc123"
}
```

### Revoke Sharing

```http
DELETE /api/collections/{id}/share
Authorization: Bearer {token}
```

**Response (200 OK):**

```json
{
  "message": "Sharing revoked"
}
```

### Access Shared Collection

```http
GET /api/collections/shared/{share_token}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "name": "Holiday Recipes",
  "recipes": [...]
}
```

**Error Codes:**
- `404 Not Found` - Invalid share token

## Meal Planning Endpoints

### Create Meal Plan

```http
POST /api/meal-plans
Authorization: Bearer {token}
Content-Type: application/json

{
  "recipe_id": 1,
  "meal_date": "2024-01-20",
  "meal_time": "dinner"
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "recipe_id": 1,
  "meal_date": "2024-01-20",
  "meal_time": "dinner"
}
```

**Error Codes:**
- `400 Bad Request` - Invalid meal_time (must be breakfast, lunch, dinner, or snack)

### Get Meal Plans

```http
GET /api/meal-plans?start_date=2024-01-15&end_date=2024-01-21
Authorization: Bearer {token}
```

**Response (200 OK):**

```json
{
  "meal_plans": [
    {
      "id": 1,
      "recipe_id": 1,
      "recipe_title": "Spaghetti Carbonara",
      "meal_date": "2024-01-20",
      "meal_time": "dinner"
    }
  ]
}
```

### Update Meal Plan

```http
PUT /api/meal-plans/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "meal_date": "2024-01-21",
  "meal_time": "lunch"
}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "meal_date": "2024-01-21",
  "meal_time": "lunch"
}
```

### Delete Meal Plan

```http
DELETE /api/meal-plans/{id}
Authorization: Bearer {token}
```

**Response (200 OK):**

```json
{
  "message": "Meal plan deleted successfully"
}
```

### Create Meal Plan Template

```http
POST /api/meal-plan-templates
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Weekly Meal Plan",
  "description": "My standard week",
  "items": [
    {
      "recipe_id": 1,
      "day_offset": 0,
      "meal_time": "dinner"
    },
    {
      "recipe_id": 2,
      "day_offset": 1,
      "meal_time": "dinner"
    }
  ]
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "name": "Weekly Meal Plan"
}
```

### List Templates

```http
GET /api/meal-plan-templates
Authorization: Bearer {token}
```

**Response (200 OK):**

```json
{
  "templates": [
    {
      "id": 1,
      "name": "Weekly Meal Plan",
      "item_count": 7
    }
  ]
}
```

### Apply Template

```http
POST /api/meal-plan-templates/{id}/apply
Authorization: Bearer {token}
Content-Type: application/json

{
  "start_date": "2024-01-15"
}
```

**Response (200 OK):**

```json
{
  "created_count": 7
}
```

### Delete Template

```http
DELETE /api/meal-plan-templates/{id}
Authorization: Bearer {token}
```

**Response (200 OK):**

```json
{
  "message": "Template deleted successfully"
}
```

### Export to iCal

```http
GET /api/meal-plans/export?start_date=2024-01-15&end_date=2024-01-21
Authorization: Bearer {token}
```

**Response (200 OK):**

Returns an iCal file download with `Content-Type: text/calendar`

## Shopping List Endpoints

### Create Shopping List

```http
POST /api/shopping-lists
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Weekly Groceries",
  "recipe_ids": [1, 2, 3]
}
```

Or from meal plan:

```json
{
  "name": "Weekly Groceries",
  "meal_plan_start_date": "2024-01-15",
  "meal_plan_end_date": "2024-01-21"
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "name": "Weekly Groceries",
  "items": [
    {
      "id": 1,
      "ingredient_name": "flour",
      "quantity": "2 cups",
      "category": "pantry",
      "is_checked": false
    }
  ]
}
```

### List Shopping Lists

```http
GET /api/shopping-lists
Authorization: Bearer {token}
```

**Response (200 OK):**

```json
{
  "shopping_lists": [
    {
      "id": 1,
      "name": "Weekly Groceries",
      "item_count": 15,
      "checked_count": 5
    }
  ]
}
```

### Get Shopping List

```http
GET /api/shopping-lists/{id}
Authorization: Bearer {token}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "name": "Weekly Groceries",
  "items": [
    {
      "id": 1,
      "ingredient_name": "flour",
      "quantity": "2 cups",
      "category": "pantry",
      "is_checked": false,
      "is_custom": false
    }
  ]
}
```

### Delete Shopping List

```http
DELETE /api/shopping-lists/{id}
Authorization: Bearer {token}
```

**Response (200 OK):**

```json
{
  "message": "Shopping list deleted successfully"
}
```

### Update Item Status

```http
PATCH /api/shopping-lists/{list_id}/items/{item_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "is_checked": true
}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "is_checked": true
}
```

### Add Custom Item

```http
POST /api/shopping-lists/{id}/items
Authorization: Bearer {token}
Content-Type: application/json

{
  "ingredient_name": "paper towels",
  "quantity": "1 roll",
  "category": "other"
}
```

**Response (201 Created):**

```json
{
  "id": 10,
  "ingredient_name": "paper towels",
  "is_custom": true
}
```

### Delete Item

```http
DELETE /api/shopping-lists/{list_id}/items/{item_id}
Authorization: Bearer {token}
```

**Response (200 OK):**

```json
{
  "message": "Item deleted successfully"
}
```

### Generate Share Link

```http
POST /api/shopping-lists/{id}/share
Authorization: Bearer {token}
```

**Response (200 OK):**

```json
{
  "share_url": "http://localhost:3000/shopping-lists/shared/xyz789",
  "share_token": "xyz789"
}
```

### Access Shared Shopping List

```http
GET /api/shopping-lists/shared/{share_token}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "name": "Weekly Groceries",
  "items": [...]
}
```

### Update Shared Item Status

```http
PATCH /api/shopping-lists/shared/{share_token}/items/{item_id}
Content-Type: application/json

{
  "is_checked": true
}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "is_checked": true
}
```

## Nutrition Endpoints

### Add Nutrition Facts

```http
POST /api/recipes/{id}/nutrition
Authorization: Bearer {token}
Content-Type: application/json

{
  "calories": 350,
  "protein_g": 12,
  "carbs_g": 45,
  "fat_g": 15,
  "fiber_g": 3
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "recipe_id": 1,
  "calories": 350,
  "protein_g": 12
}
```

**Error Codes:**
- `400 Bad Request` - Negative nutrition values

### Update Nutrition Facts

```http
PUT /api/recipes/{id}/nutrition
Authorization: Bearer {token}
Content-Type: application/json

{
  "calories": 320,
  "protein_g": 10
}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "calories": 320
}
```

### Get Nutrition Facts

```http
GET /api/recipes/{id}/nutrition
Authorization: Bearer {token}
```

**Response (200 OK):**

```json
{
  "nutrition_facts": {
    "calories": 350,
    "protein_g": 12,
    "carbs_g": 45,
    "fat_g": 15,
    "fiber_g": 3
  },
  "per_serving": {
    "calories": 87.5,
    "protein_g": 3,
    "carbs_g": 11.25,
    "fat_g": 3.75,
    "fiber_g": 0.75
  }
}
```

### Set Dietary Labels

```http
POST /api/recipes/{id}/dietary-labels
Authorization: Bearer {token}
Content-Type: application/json

{
  "labels": ["vegan", "gluten-free"]
}
```

**Response (200 OK):**

```json
{
  "labels": ["vegan", "gluten-free"]
}
```

**Valid Labels:** `vegan`, `vegetarian`, `gluten-free`, `dairy-free`, `keto`, `paleo`, `low-carb`

### Set Allergen Warnings

```http
POST /api/recipes/{id}/allergens
Authorization: Bearer {token}
Content-Type: application/json

{
  "allergens": ["nuts", "dairy"]
}
```

**Response (200 OK):**

```json
{
  "allergens": ["nuts", "dairy"]
}
```

**Valid Allergens:** `nuts`, `dairy`, `eggs`, `soy`, `wheat`, `fish`, `shellfish`

### Get Meal Plan Nutrition Summary

```http
GET /api/meal-plans/nutrition-summary?start_date=2024-01-15&end_date=2024-01-21
Authorization: Bearer {token}
```

**Response (200 OK):**

```json
{
  "daily_totals": [
    {
      "date": "2024-01-15",
      "calories": 2100,
      "protein_g": 85,
      "carbs_g": 250,
      "fat_g": 70
    }
  ],
  "weekly_total": {
    "calories": 14700,
    "protein_g": 595,
    "carbs_g": 1750,
    "fat_g": 490
  },
  "missing_nutrition_count": 2
}
```

## Social and Sharing Endpoints

### Set Recipe Visibility

```http
PATCH /api/recipes/{id}/visibility
Authorization: Bearer {token}
Content-Type: application/json

{
  "visibility": "public"
}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "visibility": "public"
}
```

**Valid Values:** `private`, `public`, `unlisted`

### Discovery Feed

```http
GET /api/recipes/discover?page=1&limit=20&search=pasta
```

**Response (200 OK):**

```json
{
  "recipes": [
    {
      "id": 1,
      "title": "Spaghetti Carbonara",
      "author": {
        "id": 2,
        "username": "chef_mario"
      },
      "likes_count": 45,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 150,
  "page": 1
}
```

### Get Public Recipe

```http
GET /api/recipes/public/{id}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "title": "Spaghetti Carbonara",
  "author": {
    "id": 2,
    "username": "chef_mario"
  },
  "likes_count": 45,
  "comments": [...]
}
```

### Fork Recipe

```http
POST /api/recipes/{id}/fork
Authorization: Bearer {token}
```

**Response (201 Created):**

```json
{
  "id": 10,
  "title": "Spaghetti Carbonara",
  "source_recipe_id": 1,
  "source_author_id": 2
}
```

**Error Codes:**
- `403 Forbidden` - Recipe is private

### Like Recipe

```http
POST /api/recipes/{id}/like
Authorization: Bearer {token}
```

**Response (200 OK):**

```json
{
  "liked": true,
  "likes_count": 46
}
```

### Unlike Recipe

```http
DELETE /api/recipes/{id}/like
Authorization: Bearer {token}
```

**Response (200 OK):**

```json
{
  "liked": false,
  "likes_count": 45
}
```

### Add Comment

```http
POST /api/recipes/{id}/comments
Authorization: Bearer {token}
Content-Type: application/json

{
  "comment_text": "This recipe is amazing!"
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "user": {
    "id": 1,
    "username": "john_doe"
  },
  "comment_text": "This recipe is amazing!",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Follow User

```http
POST /api/users/{id}/follow
Authorization: Bearer {token}
```

**Response (200 OK):**

```json
{
  "following": true,
  "followers_count": 120
}
```

**Error Codes:**
- `400 Bad Request` - Cannot follow yourself

### Unfollow User

```http
DELETE /api/users/{id}/follow
Authorization: Bearer {token}
```

**Response (200 OK):**

```json
{
  "following": false,
  "followers_count": 119
}
```

### Get Followers

```http
GET /api/users/{id}/followers
```

**Response (200 OK):**

```json
{
  "followers": [
    {
      "id": 1,
      "username": "john_doe"
    }
  ],
  "count": 119
}
```

### Get Following

```http
GET /api/users/{id}/following
```

**Response (200 OK):**

```json
{
  "following": [
    {
      "id": 2,
      "username": "chef_mario"
    }
  ],
  "count": 25
}
```

### Generate QR Code

```http
GET /api/recipes/{id}/qrcode
```

**Response (200 OK):**

Returns a PNG image with `Content-Type: image/png`

### Get Share Metadata

```http
GET /api/recipes/{id}/share-metadata
```

**Response (200 OK):**

```json
{
  "title": "Spaghetti Carbonara",
  "description": "A classic Italian pasta dish...",
  "image_url": "http://localhost:8000/uploads/recipe1.jpg",
  "url": "http://localhost:3000/recipes/1/public"
}
```

## Image Endpoints

### Upload Image

```http
POST /api/images/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: <image file>
```

**Response (200 OK):**

```json
{
  "image_url": "/uploads/abc123.jpg"
}
```

**Error Codes:**
- `400 Bad Request` - Invalid file type or size

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Human-readable error message",
  "error_code": "SPECIFIC_ERROR_CODE"
}
```

**Common Error Codes:**
- `400 Bad Request` - Invalid input or validation error
- `401 Unauthorized` - Missing or invalid authentication token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource does not exist
- `409 Conflict` - Resource conflict (e.g., duplicate like)

## Interactive Documentation

When the backend is running, visit:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>
