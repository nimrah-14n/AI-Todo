# Todo AI Chatbot API Documentation

## Overview

The Todo AI Chatbot API provides endpoints for natural language task management through conversational AI. Built with FastAPI, it integrates Groq's Llama 3.3 70B model with the Model Context Protocol (MCP) for tool execution.

**Base URL:** `http://localhost:8000`

**Authentication:** Bearer JWT tokens (from Phase II Better Auth)

---

## Authentication

All endpoints require authentication via JWT token in the Authorization header:

```
Authorization: Bearer <jwt-token>
```

**Getting a Token:**

Use the Phase II authentication endpoints to obtain a JWT token:

```bash
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password"
}
```

---

## Endpoints

### 1. Send Chat Message

Send a message to the AI assistant for task management.

**Endpoint:** `POST /api/{user_id}/chat`

**Path Parameters:**
- `user_id` (string, required): UUID of the authenticated user

**Request Body:**
```json
{
  "message": "string (required, min 1 character)",
  "conversation_id": "string (optional, UUID)"
}
```

**Response:** `200 OK`
```json
{
  "response": "string",
  "conversation_id": "string (UUID)"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/123e4567-e89b-12d3-a456-426614174000/chat \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task to buy groceries",
    "conversation_id": null
  }'
```

**Example Response:**
```json
{
  "response": "I've created a task to buy groceries for you. Is there anything else you'd like me to help with?",
  "conversation_id": "987fcdeb-51a2-43f1-b456-789012345678"
}
```

**Error Responses:**

- `400 Bad Request`: Invalid user_id or conversation_id format
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: User attempting to access another user's conversation
- `404 Not Found`: Conversation not found
- `422 Unprocessable Entity`: Invalid request body
- `500 Internal Server Error`: Server error

---

### 2. List Conversations

Get all conversations for the authenticated user.

**Endpoint:** `GET /api/{user_id}/conversations`

**Path Parameters:**
- `user_id` (string, required): UUID of the authenticated user

**Response:** `200 OK`
```json
{
  "conversations": [
    {
      "id": "string (UUID)",
      "created_at": "string (ISO 8601)",
      "updated_at": "string (ISO 8601)"
    }
  ]
}
```

**Example Request:**
```bash
curl -X GET http://localhost:8000/api/123e4567-e89b-12d3-a456-426614174000/conversations \
  -H "Authorization: Bearer <token>"
```

**Example Response:**
```json
{
  "conversations": [
    {
      "id": "987fcdeb-51a2-43f1-b456-789012345678",
      "created_at": "2026-02-08T10:00:00Z",
      "updated_at": "2026-02-08T10:15:00Z"
    },
    {
      "id": "123fcdeb-51a2-43f1-b456-789012345678",
      "created_at": "2026-02-07T14:30:00Z",
      "updated_at": "2026-02-07T15:00:00Z"
    }
  ]
}
```

**Notes:**
- Conversations are ordered by `updated_at` descending (most recent first)
- Empty array returned if user has no conversations

---

### 3. Get Conversation History

Retrieve message history for a specific conversation.

**Endpoint:** `GET /api/{user_id}/conversations/{conversation_id}`

**Path Parameters:**
- `user_id` (string, required): UUID of the authenticated user
- `conversation_id` (string, required): UUID of the conversation

**Response:** `200 OK`
```json
{
  "id": "string (UUID)",
  "created_at": "string (ISO 8601)",
  "updated_at": "string (ISO 8601)",
  "messages": [
    {
      "role": "string (user|assistant)",
      "content": "string"
    }
  ]
}
```

**Example Request:**
```bash
curl -X GET http://localhost:8000/api/123e4567-e89b-12d3-a456-426614174000/conversations/987fcdeb-51a2-43f1-b456-789012345678 \
  -H "Authorization: Bearer <token>"
```

**Example Response:**
```json
{
  "id": "987fcdeb-51a2-43f1-b456-789012345678",
  "created_at": "2026-02-08T10:00:00Z",
  "updated_at": "2026-02-08T10:15:00Z",
  "messages": [
    {
      "role": "user",
      "content": "Add a task to buy groceries"
    },
    {
      "role": "assistant",
      "content": "I've created a task to buy groceries for you."
    },
    {
      "role": "user",
      "content": "Show me all my tasks"
    },
    {
      "role": "assistant",
      "content": "Here are your tasks:\n1. Buy groceries (incomplete)\n2. Call mom (complete)"
    }
  ]
}
```

**Notes:**
- Messages are ordered chronologically (oldest first)
- Limited to 50 most recent messages
- Messages include both user and assistant messages

**Error Responses:**
- `400 Bad Request`: Invalid UUID format
- `403 Forbidden`: User attempting to access another user's conversation
- `404 Not Found`: Conversation not found

---

### 4. Health Check

Check if the API is running.

**Endpoint:** `GET /health`

**Response:** `200 OK`
```json
{
  "status": "healthy"
}
```

---

## MCP Tools

The AI agent has access to 5 MCP tools for task management:

### 1. add_task

Create a new todo task.

**Parameters:**
- `user_id` (string, required): UUID of the user
- `title` (string, required): Task title (1-200 characters)
- `description` (string, optional): Task description (max 1000 characters)

**Returns:**
```json
{
  "task_id": "string (UUID)",
  "title": "string",
  "message": "string"
}
```

### 2. list_tasks

List all tasks for the user.

**Parameters:**
- `user_id` (string, required): UUID of the user
- `is_complete` (boolean, optional): Filter by completion status

**Returns:**
```json
{
  "tasks": [
    {
      "task_id": "string (UUID)",
      "title": "string",
      "description": "string|null",
      "is_complete": "boolean",
      "created_at": "string (ISO 8601)"
    }
  ],
  "count": "number"
}
```

### 3. complete_task

Mark a task as complete.

**Parameters:**
- `user_id` (string, required): UUID of the user
- `task_id` (string, required): UUID of the task

**Returns:**
```json
{
  "task_id": "string (UUID)",
  "title": "string",
  "message": "string"
}
```

### 4. delete_task

Delete a task.

**Parameters:**
- `user_id` (string, required): UUID of the user
- `task_id` (string, required): UUID of the task

**Returns:**
```json
{
  "task_id": "string (UUID)",
  "message": "string"
}
```

### 5. update_task

Update a task's title or description.

**Parameters:**
- `user_id` (string, required): UUID of the user
- `task_id` (string, required): UUID of the task
- `title` (string, optional): New title (1-200 characters)
- `description` (string, optional): New description (max 1000 characters)

**Returns:**
```json
{
  "task_id": "string (UUID)",
  "title": "string",
  "description": "string|null",
  "message": "string"
}
```

---

## Natural Language Examples

The AI agent understands various natural language patterns:

### Creating Tasks

- "Add a task to buy groceries"
- "Create a reminder to call mom"
- "I need to finish the report by Friday"
- "Remember to water the plants"

### Viewing Tasks

- "Show me all my tasks"
- "List my incomplete tasks"
- "What do I need to do?"
- "Show completed tasks"

### Completing Tasks

- "Mark 'buy groceries' as complete"
- "I finished the report"
- "Done with calling mom"
- "Complete the first task"

### Deleting Tasks

- "Delete the groceries task"
- "Remove the reminder about mom"
- "Cancel the meeting task"

### Updating Tasks

- "Change 'buy groceries' to 'buy groceries and snacks'"
- "Update the report task description to include deadline"
- "Rename the task to 'Call mom tonight'"

---

## Error Handling

### Validation Errors

**Status:** `422 Unprocessable Entity`

```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Authentication Errors

**Status:** `401 Unauthorized`

```json
{
  "detail": "Invalid token"
}
```

### Authorization Errors

**Status:** `403 Forbidden`

```json
{
  "detail": "Access denied: Cannot access other users' data"
}
```

### Not Found Errors

**Status:** `404 Not Found`

```json
{
  "detail": "Conversation not found"
}
```

### Server Errors

**Status:** `500 Internal Server Error`

```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

**Current:** No rate limiting implemented

**Recommended for Production:**
- 100 requests per minute per user
- 1000 requests per hour per user

---

## Data Models

### Conversation

```typescript
{
  id: UUID;
  user_id: UUID;
  created_at: DateTime;
  updated_at: DateTime;
}
```

### Message

```typescript
{
  id: UUID;
  conversation_id: UUID;
  user_id: UUID;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: DateTime;
}
```

### Task

```typescript
{
  id: UUID;
  user_id: UUID;
  title: string; // 1-200 characters
  description: string | null; // max 1000 characters
  is_complete: boolean;
  created_at: DateTime;
  updated_at: DateTime;
}
```

---

## Best Practices

### 1. Conversation Management

- Store `conversation_id` from first response
- Pass `conversation_id` in subsequent messages for context
- Load conversation history on page mount for continuity

### 2. Error Handling

- Implement retry logic for network errors
- Show user-friendly error messages
- Log errors for debugging

### 3. Optimistic Updates

- Display user messages immediately
- Rollback on error
- Show loading indicators for assistant responses

### 4. Security

- Never expose JWT tokens in URLs
- Store tokens securely (httpOnly cookies or secure storage)
- Validate user_id matches authenticated user

### 5. Performance

- Limit conversation history to 50 messages
- Implement pagination for task lists
- Cache conversation metadata

---

## Testing

### Using cURL

```bash
# Set variables
export API_URL="http://localhost:8000"
export USER_ID="123e4567-e89b-12d3-a456-426614174000"
export TOKEN="your-jwt-token"

# Send chat message
curl -X POST "$API_URL/api/$USER_ID/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to buy groceries"}'

# List conversations
curl -X GET "$API_URL/api/$USER_ID/conversations" \
  -H "Authorization: Bearer $TOKEN"

# Get conversation history
curl -X GET "$API_URL/api/$USER_ID/conversations/<conversation-id>" \
  -H "Authorization: Bearer $TOKEN"
```

### Using Python

```python
import requests

API_URL = "http://localhost:8000"
USER_ID = "123e4567-e89b-12d3-a456-426614174000"
TOKEN = "your-jwt-token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Send chat message
response = requests.post(
    f"{API_URL}/api/{USER_ID}/chat",
    headers=headers,
    json={"message": "Add a task to buy groceries"}
)

print(response.json())
```

---

## Changelog

### Version 1.0.0 (2026-02-08)

- Initial release
- Chat endpoint with conversation management
- 5 MCP tools for task management
- Conversation persistence
- Message history retrieval

---

## Support

For issues or questions:
- GitHub Issues: [repository-url]
- Documentation: `README.md`
- Specification: `specs/001-todo-ai-chatbot/spec.md`
