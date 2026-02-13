# Phase III: Todo AI Chatbot - Setup Instructions

## Overview

Phase III adds an AI-powered chat interface to the Todo application, allowing users to manage tasks through natural language conversation using Groq's Llama 3.3 70B model and the Model Context Protocol (MCP).

## Architecture

- **Backend**: FastAPI with OpenAI-compatible SDK and MCP Server
- **Frontend**: Next.js 14 with React and TypeScript
- **Database**: PostgreSQL (Neon Serverless)
- **AI Model**: Llama 3.3 70B via Groq API (OpenAI-compatible)
- **Authentication**: JWT tokens (Better Auth from Phase II)

## Prerequisites

- Python 3.13+
- Node.js 18+
- PostgreSQL database (from Phase II)
- Groq API key (https://console.groq.com/keys)
- Phase II application running

## Backend Setup

### 1. Install Dependencies

```bash
cd phase-iii/backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create `.env` file in `phase-iii/backend/`:

```env
# Groq API Configuration
OPENAI_API_KEY=your_groq_api_key_here
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_MODEL=llama-3.3-70b-versatile

# MCP Server Configuration
MCP_SERVER_PORT=8001

# Database Configuration (from Phase II)
DATABASE_URL=postgresql://user:password@host/database?sslmode=require

# Authentication (from Phase II)
BETTER_AUTH_SECRET=your-secret-key-here
```

### 3. Run Database Migrations

The Phase III models (Conversation, Message) will be created automatically on first run via SQLModel.

Alternatively, run the migration SQL manually:

```sql
-- Create conversation table
CREATE TABLE conversation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversation_user_id ON conversation(user_id);
CREATE INDEX idx_conversation_updated_at ON conversation(updated_at DESC);

-- Create message table
CREATE TABLE message (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL CHECK (length(content) > 0),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_message_conversation_id ON message(conversation_id);
CREATE INDEX idx_message_created_at ON message(created_at);
```

### 4. Start the Backend Server

```bash
# Start FastAPI server
cd phase-iii/backend
uvicorn src.api.chat:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Start the MCP Server (Optional)

The MCP server runs as part of the agent execution. For standalone testing:

```bash
cd phase-iii/backend
python -m src.mcp
```

## Frontend Setup

### 1. Install Dependencies

```bash
cd phase-iii/frontend
npm install
```

### 2. Configure Environment Variables

Create `.env.local` file in `phase-iii/frontend/`:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# OpenAI Configuration (if using ChatKit)
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-openai-domain-key-here

# Authentication
NEXTAUTH_URL=http://localhost:3000
```

### 3. Start the Frontend Server

```bash
cd phase-iii/frontend
npm run dev
```

The application will be available at `http://localhost:3000`.

## Testing

### Backend Tests

```bash
cd phase-iii/backend

# Run all tests
pytest

# Run specific test suites
pytest tests/unit/
pytest tests/integration/
pytest tests/contract/

# Run with coverage
pytest --cov=src --cov-report=html
```

### Frontend Tests

```bash
cd phase-iii/frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch
```

## Usage

### 1. Login

Navigate to `http://localhost:3000/login` and authenticate with your Phase II credentials.

### 2. Access Chat Interface

Click "AI Chat" in the navigation or go to `http://localhost:3000/chat`.

### 3. Interact with the AI

Try these example commands:

**Create Tasks:**
- "Add a task to buy groceries"
- "Create a reminder to call mom"
- "I need to finish the report by Friday"

**View Tasks:**
- "Show me all my tasks"
- "List my incomplete tasks"
- "What do I need to do?"

**Complete Tasks:**
- "Mark 'buy groceries' as complete"
- "I finished the report"
- "Done with calling mom"

**Delete Tasks:**
- "Delete the groceries task"
- "Remove the reminder about mom"

**Update Tasks:**
- "Change 'buy groceries' to 'buy groceries and snacks'"
- "Update the report task description"

## API Endpoints

### Chat Endpoint

**POST** `/api/{user_id}/chat`

Send a message to the AI assistant.

**Request:**
```json
{
  "message": "Add a task to buy groceries",
  "conversation_id": "optional-conversation-uuid"
}
```

**Response:**
```json
{
  "response": "I've created a task to buy groceries for you.",
  "conversation_id": "conversation-uuid"
}
```

### List Conversations

**GET** `/api/{user_id}/conversations`

Get all conversations for a user.

**Response:**
```json
{
  "conversations": [
    {
      "id": "conversation-uuid",
      "created_at": "2026-02-08T10:00:00Z",
      "updated_at": "2026-02-08T10:05:00Z"
    }
  ]
}
```

### Get Conversation History

**GET** `/api/{user_id}/conversations/{conversation_id}`

Get messages from a specific conversation.

**Response:**
```json
{
  "id": "conversation-uuid",
  "created_at": "2026-02-08T10:00:00Z",
  "updated_at": "2026-02-08T10:05:00Z",
  "messages": [
    {
      "role": "user",
      "content": "Add a task to buy groceries"
    },
    {
      "role": "assistant",
      "content": "Task created successfully"
    }
  ]
}
```

## Troubleshooting

### OpenAI API Errors

**Error:** `Invalid API key`
- Verify your `OPENAI_API_KEY` in `.env`
- Ensure the key starts with `sk-proj-`

**Error:** `Rate limit exceeded`
- You've exceeded your OpenAI API quota
- Wait or upgrade your OpenAI plan

### Database Connection Errors

**Error:** `Connection refused`
- Verify `DATABASE_URL` is correct
- Ensure PostgreSQL is running
- Check network connectivity to database

### MCP Tool Errors

**Error:** `Task not found`
- The task may have been deleted
- Try listing tasks first to get valid task IDs

### Frontend Errors

**Error:** `Failed to send message`
- Check backend server is running on port 8000
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`
- Check browser console for detailed errors

## Architecture Details

### MCP Tools

The system provides 5 MCP tools for task management:

1. **add_task**: Create new tasks
2. **list_tasks**: View all tasks with optional filtering
3. **complete_task**: Mark tasks as complete
4. **delete_task**: Remove tasks
5. **update_task**: Modify task details

### Agent Instructions

The AI agent is configured with comprehensive instructions for:
- Natural language understanding
- Task reference resolution
- Error handling
- Confirmation messages

### Conversation Persistence

- Conversations are stored in the database
- Message history is limited to 50 messages per conversation
- Users can resume conversations after closing the browser

## Performance Considerations

- **Message Limit**: Conversations are limited to 50 messages to prevent token limit issues
- **Database Indexes**: Optimized for conversation and message queries
- **Caching**: Consider adding Redis for conversation history caching in production

## Security

- **Authentication**: All endpoints require JWT authentication
- **Authorization**: Users can only access their own conversations and tasks
- **Input Validation**: All user inputs are validated before processing
- **SQL Injection**: Protected by SQLModel ORM parameterized queries

## Next Steps

1. Deploy to production (see deployment guide)
2. Set up monitoring and logging
3. Configure rate limiting
4. Add analytics tracking
5. Implement conversation export feature

## Support

For issues or questions:
- Check the troubleshooting section above
- Review the API documentation in `docs/api.md`
- Check the specification in `specs/001-todo-ai-chatbot/spec.md`
