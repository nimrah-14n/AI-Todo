# Phase III Quick Start Guide

Get the Todo AI Chatbot running in 5 minutes!

## Prerequisites Check

```bash
# Check Python version (need 3.13+)
python --version

# Check Node.js version (need 18+)
node --version

# Check if you have a Groq API key
# Get one free at: https://console.groq.com/keys
```

## Step 1: Backend Setup (2 minutes)

```bash
# Navigate to backend
cd phase-3/backend

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env and add your credentials:
# - OPENAI_API_KEY=your_groq_api_key
# - DATABASE_URL=your_postgresql_url
# - BETTER_AUTH_SECRET=any_random_string
# - JWT_SECRET_KEY=any_random_string
```

## Step 2: Database Setup (1 minute)

```bash
# Run migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend should now be running at http://localhost:8000

## Step 3: Frontend Setup (2 minutes)

Open a new terminal:

```bash
# Navigate to frontend
cd phase-3/frontend

# Install dependencies
npm install

# Copy environment file
cp .env.local.example .env.local

# Edit .env.local and add:
# - NEXT_PUBLIC_API_URL=http://localhost:8000
# - NEXTAUTH_SECRET=any_random_string
# - DATABASE_URL=same_as_backend

# Start frontend
npm run dev
```

Frontend should now be running at http://localhost:3000

## Step 4: Test It Out!

1. **Sign Up**: Go to http://localhost:3000/signup
2. **Create Tasks**: Use the dashboard to create some tasks
3. **Try AI Chat**: Click "AI Chat" in the navigation
4. **Chat with AI**: Try these commands:
   - "Show me all my tasks"
   - "Add a task to buy groceries"
   - "Mark the first task as complete"
   - "What tasks do I have left?"

## Troubleshooting

### Backend won't start
- Check if port 8000 is already in use
- Verify DATABASE_URL is correct
- Ensure all environment variables are set

### Frontend won't start
- Check if port 3000 is already in use
- Run `npm install` again
- Clear `.next` folder: `rm -rf .next`

### Chat not working
- Verify Groq API key is valid
- Check backend logs for errors
- Ensure you're signed in

### CORS errors
- Verify CORS_ORIGINS in backend .env includes http://localhost:3000
- Restart backend server after changing .env

## Quick Commands Reference

```bash
# Backend
cd phase-3/backend
.venv\Scripts\activate
uvicorn app.main:app --reload

# Frontend
cd phase-3/frontend
npm run dev

# Run tests
cd phase-3/backend && pytest
cd phase-3/frontend && npm test
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the API docs at http://localhost:8000/docs
- Customize the AI assistant behavior in `backend/app/agents/todo_agent.py`
- Add more MCP tools in `backend/app/mcp/tools/`

## Need Help?

- Check backend logs for detailed error messages
- Verify all environment variables are set correctly
- Ensure PostgreSQL database is accessible
- Make sure both backend and frontend are running

Happy coding! 🚀
