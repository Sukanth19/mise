# API Documentation

## Base URL
```
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

### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

## Recipe Endpoints

### List Recipes
```http
GET /api/recipes?search=optional
Authorization: Bearer {token}
```

### Get Recipe
```http
GET /api/recipes/{id}
Authorization: Bearer {token}
```

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
  "image_url": "string (optional)"
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
  "reference_link": "string (optional)",
  "image_url": "string (optional)"
}
```

### Delete Recipe
```http
DELETE /api/recipes/{id}
Authorization: Bearer {token}
```

## Image Endpoints

### Upload Image
```http
POST /api/images/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: <image file>
```

## Interactive Documentation

When the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
