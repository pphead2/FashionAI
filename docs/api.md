# Fashion Finder AI API Documentation

## Base URL

The API base URL is: `http://localhost:8000/api/v1` for local development.

## Authentication

Most endpoints require authentication using JWT tokens. To authenticate, include the token in the Authorization header:

```
Authorization: Bearer <token>
```

### Authentication Endpoints

#### POST /api/v1/auth/register

Register a new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "User Name"
}
```

**Response:**
```json
{
  "id": "user_id",
  "email": "user@example.com",
  "name": "User Name"
}
```

#### POST /api/v1/auth/login

Log in with existing credentials.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "access_token": "jwt_token",
  "token_type": "bearer",
  "user": {
    "id": "user_id",
    "email": "user@example.com",
    "name": "User Name"
  }
}
```

## Image Analysis

### POST /api/v1/images/upload

Upload an image for analysis.

**Request:**
- Multipart form data with an "image" file
- Max file size: 10MB
- Supported formats: JPEG, PNG, WebP
- Min dimensions: 800x800px
- Max dimensions: 4000x4000px

**Response:**
```json
{
  "id": "image_id",
  "url": "image_url",
  "items": [
    {
      "id": "item_id",
      "type": "shirt",
      "box": {
        "x1": 100,
        "y1": 100,
        "x2": 300,
        "y2": 400
      },
      "attributes": {
        "color": "blue",
        "pattern": "solid",
        "style": "casual"
      },
      "confidence": 0.95
    }
  ]
}
```

### GET /api/v1/images/{image_id}

Get information about a previously uploaded image.

**Response:**
```json
{
  "id": "image_id",
  "url": "image_url",
  "uploaded_at": "2023-01-01T12:00:00Z",
  "items": [...]
}
```

## Product Search

### POST /api/v1/products/search

Search for products based on an item in an image.

**Request Body:**
```json
{
  "item_id": "item_id",
  "price_min": 0,
  "price_max": 200,
  "brands": ["brand1", "brand2"]
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "product_id",
      "title": "Product Title",
      "description": "Product description",
      "brand": "Brand Name",
      "price": 59.99,
      "currency": "USD",
      "image_url": "product_image_url",
      "product_url": "retailer_product_url",
      "similarity_score": 0.92
    }
  ],
  "total": 25,
  "page": 1,
  "page_size": 20
}
```

## User Management

### GET /api/v1/users/me

Get the current user's profile.

**Response:**
```json
{
  "id": "user_id",
  "email": "user@example.com",
  "name": "User Name",
  "created_at": "2023-01-01T12:00:00Z"
}
```

### PUT /api/v1/users/me

Update the current user's profile.

**Request Body:**
```json
{
  "name": "New Name"
}
```

**Response:**
```json
{
  "id": "user_id",
  "email": "user@example.com",
  "name": "New Name",
  "updated_at": "2023-01-02T12:00:00Z"
}
```

## Favorites

### GET /api/v1/favorites

Get the current user's favorite items.

**Response:**
```json
{
  "favorites": [
    {
      "id": "favorite_id",
      "product_id": "product_id",
      "title": "Product Title",
      "brand": "Brand Name",
      "price": 59.99,
      "image_url": "product_image_url",
      "saved_at": "2023-01-01T12:00:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "page_size": 20
}
```

### POST /api/v1/favorites

Add a product to favorites.

**Request Body:**
```json
{
  "product_id": "product_id"
}
```

**Response:**
```json
{
  "id": "favorite_id",
  "product_id": "product_id",
  "saved_at": "2023-01-01T12:00:00Z"
}
```

### DELETE /api/v1/favorites/{favorite_id}

Remove a product from favorites.

**Response:**
```json
{
  "success": true
}
``` 