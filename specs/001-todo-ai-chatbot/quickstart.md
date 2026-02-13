# Quick Start Guide: Todo AI Chatbot

**Feature**: Todo AI Chatbot
**Branch**: `001-todo-ai-chatbot`
**Prerequisites**: Phase II completed (authentication, task CRUD, database)

## Overview

This guide walks you through setting up the Todo AI Chatbot development environment, running the MCP server, testing the chat endpoint, and configuring ChatKit for the frontend.

**Architecture Summary**:
- **Frontend**: Next.js 16+ with OpenAI ChatKit
- **Backend**: FastAPI with OpenAI Agents SDK
- **MCP Server**: Official MCP SDK with 5 task management tools
- **Database**: Neon Serverless PostgreSQL (existing from Phase II)
- **Authentication**: Better Auth JWT (existing from Phase II)

---

## Prerequisites

### System Requirements
- **Python**: 3.13 or higher
- **Node.js**: 18.x or higher
- **npm**: 9.x or higher
- **PostgreSQL**: Neon Serverless (existing from Phase II)
- **Git**: For version control

### Required Accounts
- **OpenAI API**: Account with API key (for Agents SDK)
- **Neon**: PostgreSQL database (existing from Phase II)
- **Vercel** (optional): For frontend deployment

---

## Step 1: Clone and Setup Repository

```bash
# Clone repository (if not already done)
git clone <repository-url>
cd ai-cloud-hackathon-2

# Checkout feature branch
git checkout 001-todo-ai-chatbot

# Verify branch
git branch --show-current
# Should output: 001-todo-ai-chatbot
```

---

## Step 2: Backend Setup

### 2.1 Install Python Dependencies

```bash
cd phase-ll/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Phase III specific dependencies
pip install openai-agents mcp sqlmodel asyncpg
```

### 2.2 Configure Environment Variables

Create or update `.env` file in `phase-ll/backend/`:

```bash
# Database (existing from Phase II)
DATABASE_URL=postgresql://user:password@host/database?sslmode=require

# Authentication (existing from Phase II)
BETTER_AUTH_SECRET=your-secret-key-here

# OpenAI API (NEW for Phase III)
OPENAI_API_KEY=sk-proj-...your-key-here

# MCP Server (NEW for Phase III)
MCP_SERVER_PORT=8001

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
```

**Security Note**: Never commit `.env` file to version control. Add to `.gitignore`.

### 2.3 Run Database Migrations

```bash
# Apply Phase III migrations (Conversation and Message tables)
python -m alembic upgrade head

# Verify tables created
python -c "
from sqlmodel import create_engine, Session, select
from src.models.conversation import Conversation
from src.models.message import Message
engine = create_engine('your-database-url')
with Session(engine) as session:
    print('Conversation table:', session.exec(select(Conversation)).first() is not None or 'exists')
    print('Message table:', session.exec(select(Message)).first() is not None or 'exists')
"
```

### 2.4 Start Backend Server

```bash
# Start FastAPI server
uvicorn src.main:app --reload --port 8000

# Server should start at http://localhost:8000
# API docs available at http://localhost:8000/docs
```

---

## Step 3: MCP Server Setup

### 3.1 Start MCP Server

The MCP server runs as a separate process and provides task management tools to the AI agent.

```bash
# In a new terminal, navigate to backend directory
cd phase-ll/backend
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start MCP server
python -m src.mcp.server

# Server should start at http://localhost:8001
# Tool registration logs should appear
```

**Expected Output**:
```
INFO: MCP Server starting on port 8001
INFO: Registered tool: add_task
INFO: Registered tool: list_tasks
INFO: Registered tool: complete_task
INFO: Registered tool: delete_task
INFO: Registered tool: update_task
INFO: MCP Server ready
```

### 3.2 Verify MCP Tools

```bash
# Test tool availability
curl http://localhost:8001/tools

# Expected response: JSON array with 5 tools
# [
#   {"name": "add_task", "description": "..."},
#   {"name": "list_tasks", "description": "..."},
#   ...
# ]
```

---

## Step 4: Frontend Setup

### 4.1 Install Node Dependencies

```bash
cd phase-ll/frontend

# Install dependencies
npm install

# Install Phase III specific dependencies
npm install @openai/chatkit
```

### 4.2 Configure Environment Variables

Create or update `.env.local` file in `phase-ll/frontend/`:

```bash
# API URL (backend)
NEXT_PUBLIC_API_URL=http://localhost:8000

# OpenAI ChatKit (NEW for Phase III)
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key-here

# Authentication (existing from Phase II)
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret
```

**Getting OpenAI Domain Key**:
1. Deploy frontend to get production URL (e.g., Vercel)
2. Add domain to OpenAI allowlist: https://platform.openai.com/settings/organization/security/domain-allowlist
3. Copy domain key from OpenAI dashboard
4. Add to `NEXT_PUBLIC_OPENAI_DOMAIN_KEY`

**Development Note**: For local development, you may need to use `localhost` in the allowlist or deploy to a staging environment.

### 4.3 Start Frontend Server

```bash
# Start Next.js development server
npm run dev

# Server should start at http://localhost:3000
```

---

## Step 5: Testing the Chat Endpoint

### 5.1 Obtain Authentication Token

```bash
# Login to get JWT token (using existing Phase II auth)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "your-password"
  }'

# Response includes access_token
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "user_id": "550e8400-e29b-41d4-a716-446655440000"
# }
```

### 5.2 Send Chat Message

```bash
# Set variables
export TOKEN="your-jwt-token-here"
export USER_ID="your-user-id-here"

# Send message to create a task
curl -X POST http://localhost:8000/api/${USER_ID}/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{
    "message": "Add a task to buy groceries"
  }'

# Expected response:
# {
#   "conversation_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
#   "response": "I've added 'Buy groceries' to your task list.",
#   "tool_calls": [
#     {
#       "tool": "add_task",
#       "args": {
#         "user_id": "550e8400-e29b-41d4-a716-446655440000",
#         "title": "Buy groceries",
#         "description": null
#       }
#     }
#   ]
# }
```

### 5.3 Continue Conversation

```bash
# Use conversation_id from previous response
export CONVERSATION_ID="7c9e6679-7425-40de-944b-e07fc1f90ae7"

# Send follow-up message
curl -X POST http://localhost:8000/api/${USER_ID}/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{
    "message": "Show me my tasks",
    "conversation_id": "'${CONVERSATION_ID}'"
  }'

# Expected response:
# {
#   "conversation_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
#   "response": "You have 1 pending task: 1. Buy groceries",
#   "tool_calls": [
#     {
#       "tool": "list_tasks",
#       "args": {
#         "user_id": "550e8400-e29b-41d4-a716-446655440000",
#         "status": "pending"
#       }
#     }
#   ]
# }
```

---

## Step 6: Frontend Chat Interface

### 6.1 Access Chat Page

1. Open browser to http://localhost:3000
2. Login with existing credentials (Phase II authentication)
3. Navigate to `/chat` page
4. Chat interface should load with ChatKit component

### 6.2 Test Chat Interactions

**Create Task**:
- Type: "Add a task to buy groceries"
- Expected: Task created confirmation message

**View Tasks**:
- Type: "Show me my tasks"
- Expected: List of tasks displayed

**Complete Task**:
- Type: "Mark the groceries task as done"
- Expected: Task marked complete confirmation

**Delete Task**:
- Type: "Delete the groceries task"
- Expected: Task deleted confirmation

**Update Task**:
- Type: "Change the groceries task to include vegetables"
- Expected: Task updated confirmation

---

## Step 7: Running Tests

### 7.1 Backend Tests

```bash
cd phase-ll/backend

# Run all tests
pytest

# Run specific test suites
pytest tests/unit/test_mcp_tools.py          # MCP tool tests
pytest tests/unit/test_agent.py              # Agent tests
pytest tests/integration/test_chat_endpoint.py  # Chat endpoint tests
pytest tests/contract/test_mcp_contracts.py  # Contract tests

# Run with coverage
pytest --cov=src --cov-report=html
```

### 7.2 Frontend Tests

```bash
cd phase-ll/frontend

# Run all tests
npm test

# Run specific test suites
npm test -- ChatInterface.test.tsx  # Chat component tests
npm test -- chat.test.tsx           # Chat flow tests

# Run with coverage
npm test -- --coverage
```

---

## Step 8: Development Workflow

### 8.1 Typical Development Session

```bash
# Terminal 1: Backend server
cd phase-ll/backend
source venv/bin/activate
uvicorn src.main:app --reload --port 8000

# Terminal 2: MCP server
cd phase-ll/backend
source venv/bin/activate
python -m src.mcp.server

# Terminal 3: Frontend server
cd phase-ll/frontend
npm run dev

# Terminal 4: Testing/commands
cd phase-ll/backend
pytest --watch  # or npm test in frontend
```

### 8.2 Hot Reload

- **Backend**: FastAPI auto-reloads on file changes (with `--reload` flag)
- **MCP Server**: Restart manually after changes
- **Frontend**: Next.js auto-reloads on file changes

---

## Troubleshooting

### Issue: MCP Server Connection Failed

**Symptoms**: Chat endpoint returns 503 Service Unavailable

**Solutions**:
1. Verify MCP server is running: `curl http://localhost:8001/tools`
2. Check MCP server logs for errors
3. Verify `MCP_SERVER_PORT` in `.env` matches server port
4. Restart MCP server

### Issue: OpenAI API Rate Limit

**Symptoms**: Chat endpoint returns 429 Too Many Requests

**Solutions**:
1. Check OpenAI API usage: https://platform.openai.com/usage
2. Upgrade OpenAI plan if needed
3. Implement request throttling in development
4. Use `gpt-4o-mini` model for lower costs

### Issue: ChatKit Domain Not Allowed

**Symptoms**: Frontend shows "Domain not allowed" error

**Solutions**:
1. Add domain to OpenAI allowlist: https://platform.openai.com/settings/organization/security/domain-allowlist
2. For local development, add `localhost:3000` to allowlist
3. Verify `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` is set correctly
4. Clear browser cache and reload

### Issue: Database Connection Failed

**Symptoms**: Backend fails to start with database connection error

**Solutions**:
1. Verify `DATABASE_URL` in `.env` is correct
2. Check Neon database is running and accessible
3. Verify SSL mode is set: `?sslmode=require`
4. Test connection: `psql $DATABASE_URL`

### Issue: Authentication Failed

**Symptoms**: Chat endpoint returns 401 Unauthorized

**Solutions**:
1. Verify JWT token is valid and not expired
2. Check `Authorization: Bearer <token>` header is set
3. Verify `BETTER_AUTH_SECRET` matches between login and chat endpoints
4. Re-login to get fresh token

---

## Next Steps

### Development Tasks
1. Implement MCP tools in `backend/src/mcp/tools.py`
2. Implement agent configuration in `backend/src/agents/todo_agent.py`
3. Implement chat endpoint in `backend/src/api/chat.py`
4. Implement ChatKit integration in `frontend/src/components/ChatInterface.tsx`
5. Write tests for all components

### Testing Tasks
1. Unit test MCP tools with various inputs
2. Integration test chat endpoint with agent
3. Contract test MCP tool schemas
4. End-to-end test complete user workflows

### Deployment Tasks
1. Deploy backend to production server
2. Deploy frontend to Vercel
3. Configure OpenAI domain allowlist with production URL
4. Set up monitoring and logging
5. Configure CI/CD pipeline

---

## Useful Commands

### Database
```bash
# Connect to database
psql $DATABASE_URL

# View conversations
SELECT * FROM conversation ORDER BY updated_at DESC LIMIT 10;

# View messages
SELECT * FROM message WHERE conversation_id = 'your-id' ORDER BY created_at;

# View tasks
SELECT * FROM task WHERE user_id = 'your-id';
```

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# List conversations
curl http://localhost:8000/api/${USER_ID}/conversations \
  -H "Authorization: Bearer ${TOKEN}"

# Get conversation history
curl http://localhost:8000/api/${USER_ID}/conversations/${CONVERSATION_ID} \
  -H "Authorization: Bearer ${TOKEN}"
```

### Logs
```bash
# Backend logs
tail -f logs/backend.log

# MCP server logs
tail -f logs/mcp-server.log

# Frontend logs (browser console)
# Open DevTools > Console
```

---

## Resources

### Documentation
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-sdk)
- [Official MCP SDK](https://github.com/modelcontextprotocol/python-sdk)
- [OpenAI ChatKit](https://github.com/openai/chatkit)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Next.js](https://nextjs.org/docs)
- [SQLModel](https://sqlmodel.tiangolo.com/)

### Specifications
- [Feature Spec](./spec.md) - Requirements and user stories
- [Implementation Plan](./plan.md) - Architecture and design decisions
- [Data Model](./data-model.md) - Database schema and entities
- [Chat API Contract](./contracts/chat-api.yaml) - OpenAPI specification
- [MCP Tools Contract](./contracts/mcp-tools.yaml) - MCP tool definitions

### Support
- GitHub Issues: Report bugs and request features
- Team Chat: Ask questions and get help
- Code Reviews: Submit PRs for review

---

## Summary

You should now have:
- ✅ Backend server running on http://localhost:8000
- ✅ MCP server running on http://localhost:8001
- ✅ Frontend server running on http://localhost:3000
- ✅ Database migrations applied
- ✅ Environment variables configured
- ✅ Chat endpoint tested and working
- ✅ ChatKit interface accessible

**Ready to start development!** 🚀

Next: Run `/sp.tasks` to generate implementation tasks.
