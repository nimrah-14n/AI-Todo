# API Specification: RESTful Endpoints

**Feature Branch**: `001-fullstack-web-app`
**Created**: 2026-01-14
**Status**: Active Development

## Overview

This specification defines all RESTful API endpoints for the Todo application, including request/response schemas, authentication requirements, error responses, and HTTP status codes.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.yourdomain.com` (to be configured)

## Authentication

All endpoints except authentication endpoints require a valid JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

## Common Response Formats

### Success Response

```json
{
  "data": { ... },
  "message": "Optional success message"
}
```

### Error Response

```json
{
  "error": "Error message",
  "field": "field_name (optional)",
  "details": "Additional details (optional)"
}
```

## HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT, PATCH requests |
| 201 | Created | Successful POST request creating a resource |
| 400 | Bad Request | Validation error, malformed request |
| 401 | Unauthorized | Missing, invalid, or expired token |
| 403 | Forbidden | Valid token but insufficient permissions |
| 404 | Not Found | Resource does not exist |
| 500 | Internal Server Error | Unexpected server error |

---

## Authentication Endpoints

### POST /api/auth/signup

Create a new user account.

**Authentication**: Not required

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Request Schema**:
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| email | string | Yes | Valid email format, max 255 chars |
| password | string | Yes | Min 8 characters, max 128 chars |

**Success Response (201 Created)**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNTUwZTg0MDAtZTI5Yi00MWQ0LWE3MTYtNDQ2NjU1NDQwMDAwIiwiZW1haWwiOiJ1c2VyQGV4YW1wbGUuY29tIiwiaWF0IjoxNzA0MDY3MjAwLCJleHAiOjE3MDQ2NzIwMDB9.signature",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "created_at": "2026-01-14T10:30:00Z"
  }
}
```

**Error Responses**:

**400 Bad Request** - Validation errors:
```json
{
  "error": "Email is required",
  "field": "email"
}
```

```json
{
  "error": "Please enter a valid email address",
  "field": "email"
}
```

```json
{
  "error": "Password is required",
  "field": "password"
}
```

```json
{
  "error": "Password must be at least 8 characters",
  "field": "password"
}
```

```json
{
  "error": "This email is already registered. Please sign in instead.",
  "field": "email"
}
```

**500 Internal Server Error**:
```json
{
  "error": "Service temporarily unavailable. Please try again."
}
```

---

### POST /api/auth/signin

Authenticate an existing user.

**Authentication**: Not required

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Request Schema**:
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| email | string | Yes | Valid email format |
| password | string | Yes | Any length |

**Success Response (200 OK)**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNTUwZTg0MDAtZTI5Yi00MWQ0LWE3MTYtNDQ2NjU1NDQwMDAwIiwiZW1haWwiOiJ1c2VyQGV4YW1wbGUuY29tIiwiaWF0IjoxNzA0MDY3MjAwLCJleHAiOjE3MDQ2NzIwMDB9.signature",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "created_at": "2026-01-14T10:30:00Z"
  }
}
```

**Error Responses**:

**400 Bad Request** - Validation errors:
```json
{
  "error": "Email is required",
  "field": "email"
}
```

```json
{
  "error": "Password is required",
  "field": "password"
}
```

**401 Unauthorized** - Invalid credentials:
```json
{
  "error": "Invalid email or password"
}
```

**500 Internal Server Error**:
```json
{
  "error": "Service temporarily unavailable. Please try again."
}
```

---

### POST /api/auth/signout

Sign out the current user (informational endpoint).

**Authentication**: Required

**Request Headers**:
```
Authorization: Bearer <jwt_token>
```

**Request Body**: None

**Success Response (200 OK)**:
```json
{
  "message": "Successfully signed out"
}
```

**Error Responses**:

**401 Unauthorized**:
```json
{
  "error": "Authentication required"
}
```

**Note**: This endpoint is primarily informational. The frontend is responsible for removing the token from storage. The backend does not maintain a token blacklist (stateless authentication).

---

## Task Management Endpoints

### GET /api/{user_id}/tasks

Retrieve all tasks for the authenticated user.

**Authentication**: Required

**URL Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| user_id | UUID | User's unique identifier |

**Request Headers**:
```
Authorization: Bearer <jwt_token>
```

**Query Parameters**: None (Phase II does not include filtering or sorting)

**Success Response (200 OK)**:
```json
{
  "tasks": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread, and vegetables",
      "is_complete": false,
      "created_at": "2026-01-14T10:30:00Z",
      "updated_at": "2026-01-14T10:30:00Z"
    },
    {
      "id": "223e4567-e89b-12d3-a456-426614174001",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Finish project report",
      "description": null,
      "is_complete": true,
      "created_at": "2026-01-13T15:20:00Z",
      "updated_at": "2026-01-14T09:15:00Z"
    }
  ]
}
```

**Response Schema**:
| Field | Type | Description |
|-------|------|-------------|
| tasks | array | Array of task objects |
| tasks[].id | UUID | Task unique identifier |
| tasks[].user_id | UUID | Owner's user ID |
| tasks[].title | string | Task title (1-200 chars) |
| tasks[].description | string\|null | Task description (max 1000 chars) |
| tasks[].is_complete | boolean | Completion status |
| tasks[].created_at | ISO 8601 | Creation timestamp |
| tasks[].updated_at | ISO 8601 | Last update timestamp |

**Empty List Response (200 OK)**:
```json
{
  "tasks": []
}
```

**Error Responses**:

**401 Unauthorized** - Missing or invalid token:
```json
{
  "error": "Authentication required"
}
```

**403 Forbidden** - User ID mismatch:
```json
{
  "error": "Access denied"
}
```

**500 Internal Server Error**:
```json
{
  "error": "Service temporarily unavailable. Please try again."
}
```

---

### POST /api/{user_id}/tasks

Create a new task for the authenticated user.

**Authentication**: Required

**URL Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| user_id | UUID | User's unique identifier |

**Request Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread, and vegetables"
}
```

**Request Schema**:
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| title | string | Yes | 1-200 characters, not only whitespace |
| description | string | No | Max 1000 characters |

**Success Response (201 Created)**:
```json
{
  "task": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread, and vegetables",
    "is_complete": false,
    "created_at": "2026-01-14T10:30:00Z",
    "updated_at": "2026-01-14T10:30:00Z"
  }
}
```

**Error Responses**:

**400 Bad Request** - Validation errors:
```json
{
  "error": "Title is required",
  "field": "title"
}
```

```json
{
  "error": "Title cannot be empty",
  "field": "title"
}
```

```json
{
  "error": "Title must be 200 characters or less",
  "field": "title"
}
```

```json
{
  "error": "Description must be 1000 characters or less",
  "field": "description"
}
```

**401 Unauthorized**:
```json
{
  "error": "Authentication required"
}
```

**403 Forbidden** - User ID mismatch:
```json
{
  "error": "Access denied"
}
```

**500 Internal Server Error**:
```json
{
  "error": "Service temporarily unavailable. Please try again."
}
```

---

### GET /api/{user_id}/tasks/{id}

Retrieve a specific task by ID.

**Authentication**: Required

**URL Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| user_id | UUID | User's unique identifier |
| id | UUID | Task's unique identifier |

**Request Headers**:
```
Authorization: Bearer <jwt_token>
```

**Success Response (200 OK)**:
```json
{
  "task": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread, and vegetables",
    "is_complete": false,
    "created_at": "2026-01-14T10:30:00Z",
    "updated_at": "2026-01-14T10:30:00Z"
  }
}
```

**Error Responses**:

**400 Bad Request** - Invalid UUID format:
```json
{
  "error": "Invalid task ID format",
  "field": "id"
}
```

**401 Unauthorized**:
```json
{
  "error": "Authentication required"
}
```

**403 Forbidden** - User ID mismatch:
```json
{
  "error": "Access denied"
}
```

**404 Not Found** - Task doesn't exist or belongs to another user:
```json
{
  "error": "Task not found"
}
```

**500 Internal Server Error**:
```json
{
  "error": "Service temporarily unavailable. Please try again."
}
```

---

### PUT /api/{user_id}/tasks/{id}

Update a task's title and/or description.

**Authentication**: Required

**URL Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| user_id | UUID | User's unique identifier |
| id | UUID | Task's unique identifier |

**Request Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "title": "Buy groceries and cook dinner",
  "description": "Milk, eggs, bread, vegetables, and chicken"
}
```

**Request Schema**:
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| title | string | Yes | 1-200 characters, not only whitespace |
| description | string | No | Max 1000 characters, can be null |

**Success Response (200 OK)**:
```json
{
  "task": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries and cook dinner",
    "description": "Milk, eggs, bread, vegetables, and chicken",
    "is_complete": false,
    "created_at": "2026-01-14T10:30:00Z",
    "updated_at": "2026-01-14T11:45:00Z"
  }
}
```

**Error Responses**:

**400 Bad Request** - Validation errors:
```json
{
  "error": "Title is required",
  "field": "title"
}
```

```json
{
  "error": "Title cannot be empty",
  "field": "title"
}
```

```json
{
  "error": "Title must be 200 characters or less",
  "field": "title"
}
```

```json
{
  "error": "Description must be 1000 characters or less",
  "field": "description"
}
```

```json
{
  "error": "Invalid task ID format",
  "field": "id"
}
```

**401 Unauthorized**:
```json
{
  "error": "Authentication required"
}
```

**403 Forbidden** - User ID mismatch or task ownership violation:
```json
{
  "error": "You do not have permission to access this task"
}
```

**404 Not Found**:
```json
{
  "error": "Task not found"
}
```

**500 Internal Server Error**:
```json
{
  "error": "Service temporarily unavailable. Please try again."
}
```

---

### DELETE /api/{user_id}/tasks/{id}

Delete a task permanently.

**Authentication**: Required

**URL Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| user_id | UUID | User's unique identifier |
| id | UUID | Task's unique identifier |

**Request Headers**:
```
Authorization: Bearer <jwt_token>
```

**Success Response (200 OK)**:
```json
{
  "message": "Task deleted successfully"
}
```

**Error Responses**:

**400 Bad Request** - Invalid UUID format:
```json
{
  "error": "Invalid task ID format",
  "field": "id"
}
```

**401 Unauthorized**:
```json
{
  "error": "Authentication required"
}
```

**403 Forbidden** - User ID mismatch or task ownership violation:
```json
{
  "error": "You do not have permission to access this task"
}
```

**404 Not Found**:
```json
{
  "error": "Task not found"
}
```

**500 Internal Server Error**:
```json
{
  "error": "Service temporarily unavailable. Please try again."
}
```

---

### PATCH /api/{user_id}/tasks/{id}/complete

Toggle a task's completion status.

**Authentication**: Required

**URL Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| user_id | UUID | User's unique identifier |
| id | UUID | Task's unique identifier |

**Request Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "is_complete": true
}
```

**Request Schema**:
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| is_complete | boolean | Yes | true or false |

**Success Response (200 OK)**:
```json
{
  "task": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread, and vegetables",
    "is_complete": true,
    "created_at": "2026-01-14T10:30:00Z",
    "updated_at": "2026-01-14T12:00:00Z"
  }
}
```

**Error Responses**:

**400 Bad Request** - Validation errors:
```json
{
  "error": "is_complete field is required",
  "field": "is_complete"
}
```

```json
{
  "error": "is_complete must be a boolean",
  "field": "is_complete"
}
```

```json
{
  "error": "Invalid task ID format",
  "field": "id"
}
```

**401 Unauthorized**:
```json
{
  "error": "Authentication required"
}
```

**403 Forbidden** - User ID mismatch or task ownership violation:
```json
{
  "error": "You do not have permission to access this task"
}
```

**404 Not Found**:
```json
{
  "error": "Task not found"
}
```

**500 Internal Server Error**:
```json
{
  "error": "Service temporarily unavailable. Please try again."
}
```

---

## CORS Configuration

The backend API must be configured to accept requests from the frontend origin.

**Development**:
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Allow-Credentials: true
```

**Production**:
```
Access-Control-Allow-Origin: https://yourdomain.vercel.app
Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Allow-Credentials: true
```

---

## Rate Limiting

Phase II does not include rate limiting. Production systems should implement:

- **Authentication endpoints**: 5 requests per minute per IP
- **Task endpoints**: 100 requests per minute per user
- **Response header**: `X-RateLimit-Remaining: 95`

---

## API Versioning

Phase II uses implicit versioning (no version in URL). Future versions may use:

- URL versioning: `/api/v2/tasks`
- Header versioning: `Accept: application/vnd.api+json; version=2`

---

## Request/Response Examples

### Example 1: Complete User Flow

**1. Signup**:
```bash
POST /api/auth/signup
Content-Type: application/json

{
  "email": "alice@example.com",
  "password": "securepass123"
}

Response (201):
{
  "token": "eyJhbGc...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "alice@example.com",
    "created_at": "2026-01-14T10:30:00Z"
  }
}
```

**2. Create Task**:
```bash
POST /api/550e8400-e29b-41d4-a716-446655440000/tasks
Authorization: Bearer eyJhbGc...
Content-Type: application/json

{
  "title": "Write documentation",
  "description": "Complete API specification"
}

Response (201):
{
  "task": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Write documentation",
    "description": "Complete API specification",
    "is_complete": false,
    "created_at": "2026-01-14T10:35:00Z",
    "updated_at": "2026-01-14T10:35:00Z"
  }
}
```

**3. Get All Tasks**:
```bash
GET /api/550e8400-e29b-41d4-a716-446655440000/tasks
Authorization: Bearer eyJhbGc...

Response (200):
{
  "tasks": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Write documentation",
      "description": "Complete API specification",
      "is_complete": false,
      "created_at": "2026-01-14T10:35:00Z",
      "updated_at": "2026-01-14T10:35:00Z"
    }
  ]
}
```

**4. Mark Complete**:
```bash
PATCH /api/550e8400-e29b-41d4-a716-446655440000/tasks/123e4567-e89b-12d3-a456-426614174000/complete
Authorization: Bearer eyJhbGc...
Content-Type: application/json

{
  "is_complete": true
}

Response (200):
{
  "task": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Write documentation",
    "description": "Complete API specification",
    "is_complete": true,
    "created_at": "2026-01-14T10:35:00Z",
    "updated_at": "2026-01-14T10:40:00Z"
  }
}
```

---

## Testing Checklist

### Authentication Endpoints

- [ ] POST /api/auth/signup with valid data returns 201
- [ ] POST /api/auth/signup with duplicate email returns 400
- [ ] POST /api/auth/signup with invalid email returns 400
- [ ] POST /api/auth/signup with short password returns 400
- [ ] POST /api/auth/signin with valid credentials returns 200
- [ ] POST /api/auth/signin with invalid credentials returns 401
- [ ] POST /api/auth/signout with valid token returns 200
- [ ] POST /api/auth/signout without token returns 401

### Task Endpoints

- [ ] GET /api/{user_id}/tasks with valid token returns 200
- [ ] GET /api/{user_id}/tasks without token returns 401
- [ ] GET /api/{user_id}/tasks with mismatched user_id returns 403
- [ ] POST /api/{user_id}/tasks with valid data returns 201
- [ ] POST /api/{user_id}/tasks with empty title returns 400
- [ ] POST /api/{user_id}/tasks with long title returns 400
- [ ] GET /api/{user_id}/tasks/{id} with valid ID returns 200
- [ ] GET /api/{user_id}/tasks/{id} with invalid ID returns 404
- [ ] PUT /api/{user_id}/tasks/{id} with valid data returns 200
- [ ] PUT /api/{user_id}/tasks/{id} for another user's task returns 403
- [ ] DELETE /api/{user_id}/tasks/{id} with valid ID returns 200
- [ ] DELETE /api/{user_id}/tasks/{id} for another user's task returns 403
- [ ] PATCH /api/{user_id}/tasks/{id}/complete with valid data returns 200
- [ ] PATCH /api/{user_id}/tasks/{id}/complete for another user's task returns 403

---

## References

- **Main Specification**: `specs/001-fullstack-web-app/spec.md`
- **Architecture**: `specs/001-fullstack-web-app/architecture.md`
- **Database Schema**: `specs/001-fullstack-web-app/database/schema.md`
- **Authentication**: `specs/001-fullstack-web-app/features/authentication.md`
- **Task CRUD**: `specs/001-fullstack-web-app/features/task-crud.md`
