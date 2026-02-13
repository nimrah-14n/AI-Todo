# Phase III: Todo AI Chatbot Integration

This phase integrates the AI chatbot functionality from phase-iii into the full-stack Todo application from phase-2 (phase-ll).

## Features

### From Phase II (Base Application)
- ✅ User authentication with Better Auth
- ✅ Task CRUD operations
- ✅ PostgreSQL database (Neon)
- ✅ Modern UI with dark mode
- ✅ Protected routes

### New in Phase III (AI Chatbot)
- 🤖 AI-powered todo assistant using Groq LLaMA
- 💬 Natural language task management
- 📝 Conversation history
- 🔧 MCP (Model Context Protocol) tools for task operations
- 🎯 Context-aware responses

## Architecture

```
phase-3/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   │   ├── auth.py          # Authentication endpoints
│   │   │   ├── tasks.py         # Task CRUD endpoints
│   │   │   └── chat.py          # NEW: Chat endpoint
│   │   ├── agents/              # NEW: AI agent logic
│   │   ├── mcp/                 # NEW: MCP server & tools
│   │   ├── services-chatbot/    # NEW: Conversation service
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── task.py
│   │   │   ├── conversation.py  # NEW
│   │   │   └── message.py       # NEW
│   │   └── utils/               # NEW: Sanitizer, metrics
│   └── requirements.txt
└── frontend/
    ├── app/
    │   ├── dashboard/           # Task management UI
    │   └── chat/                # NEW: Chat interface
    └── components/
        └── ChatInterface.tsx    # NEW: Chat component

```

## Setup Instructions

### Prerequisites
- Python 3.13+
- Node.js 18+
- PostgreSQL database (Neon recommended)
- Groq API key (free at https://console.groq.com/keys)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd phase-3/backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and fill in:
   - `OPENAI_API_KEY`: Your Groq API key
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `BETTER_AUTH_SECRET`: Secret for authentication
   - `JWT_SECRET_KEY`: Secret for JWT tokens

5. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

6. **Start the backend server:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd phase-3/frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.local.example .env.local
   ```
   
   Edit `.env.local` and fill in:
   - `NEXT_PUBLIC_API_URL`: Backend URL (default: http://localhost:8000)
   - `NEXTAUTH_SECRET`: Secret for NextAuth
   - `DATABASE_URL`: Same PostgreSQL URL as backend

4. **Start the development server:**
   ```bash
   npm run dev
   ```

5. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Usage

### Task Management (Dashboard)
1. Sign up or sign in at http://localhost:3000
2. Navigate to the dashboard
3. Create, update, complete, or delete tasks

### AI Chatbot
1. Navigate to http://localhost:3000/chat
2. Chat with the AI assistant using natural language:
   - "Add a task to buy groceries"
   - "Show me all my tasks"
   - "Mark the first task as complete"
   - "Delete all completed tasks"

## API Endpoints

### Authentication
- `POST /auth/signup` - Create new user
- `POST /auth/signin` - Sign in user
- `POST /auth/signout` - Sign out user

### Tasks
- `GET /tasks` - List all tasks
- `POST /tasks` - Create task
- `PATCH /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task

### Chat (NEW)
- `POST /api/{user_id}/chat` - Send message to AI assistant

## Database Schema

### New Tables
- `conversations` - Chat conversation sessions
- `messages` - Individual chat messages

### Existing Tables
- `users` - User accounts
- `tasks` - Todo tasks

## Technology Stack

### Backend
- FastAPI - Web framework
- SQLModel - ORM
- PostgreSQL - Database
- Groq LLaMA - AI model
- MCP - Model Context Protocol

### Frontend
- Next.js 14 - React framework
- TypeScript - Type safety
- Tailwind CSS - Styling
- Better Auth - Authentication

## Troubleshooting

### CORS Errors
- Ensure `CORS_ORIGINS` in backend `.env` includes your frontend URL
- Check that backend is running on port 8000

### Database Connection Issues
- Verify `DATABASE_URL` is correct in both backend and frontend
- Ensure PostgreSQL is accessible
- Run migrations: `alembic upgrade head`

### Chat Not Working
- Verify Groq API key is valid
- Check backend logs for errors
- Ensure user is authenticated

## Development

### Running Tests
```bash
# Backend
cd phase-3/backend
pytest

# Frontend
cd phase-3/frontend
npm test
```

### Code Quality
```bash
# Backend linting
ruff check .

# Frontend linting
npm run lint
```

## Deployment

See individual deployment guides:
- Backend: Deploy to Railway, Render, or similar
- Frontend: Deploy to Vercel, Netlify, or similar
- Database: Use Neon, Supabase, or managed PostgreSQL

## License

MIT
