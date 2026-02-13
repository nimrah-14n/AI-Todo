# Quickstart Guide: Phase II - Todo Full-Stack Web Application

**Feature Branch**: `001-fullstack-web-app`
**Created**: 2026-01-14
**Status**: Active Development

## Overview

This guide provides step-by-step instructions to set up, develop, test, and deploy the Phase II Todo Full-Stack Web Application. Follow these instructions to get the application running locally and deploy it to production.

## Prerequisites

### Required Software

| Software | Version | Purpose | Installation |
|----------|---------|---------|--------------|
| Node.js | 18+ LTS | Frontend runtime | https://nodejs.org/ |
| Python | 3.13+ | Backend runtime | https://www.python.org/ |
| Git | Latest | Version control | https://git-scm.com/ |
| VS Code | Latest | Code editor (recommended) | https://code.visualstudio.com/ |

### Required Accounts

| Service | Purpose | Sign Up |
|---------|---------|---------|
| Neon | PostgreSQL database | https://neon.tech/ |
| Vercel | Frontend deployment | https://vercel.com/ |
| GitHub | Code hosting | https://github.com/ |

### System Requirements

- **Operating System**: Windows 10+ (with WSL 2), macOS 11+, or Linux
- **RAM**: 8GB minimum, 16GB recommended
- **Disk Space**: 2GB free space
- **Internet**: Stable broadband connection

---

## Project Setup

### 1. Clone Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-cloud-hackathon-2.git
cd ai-cloud-hackathon-2

# Checkout feature branch
git checkout 001-fullstack-web-app
```

### 2. Verify Prerequisites

```bash
# Check Node.js version (should be 18+)
node --version

# Check Python version (should be 3.13+)
python --version

# Check Git version
git --version
```

---

## Backend Setup

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Create Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# On Windows (Command Prompt):
.\venv\Scripts\activate.bat

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

**Expected dependencies** (requirements.txt):
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlmodel==0.0.14
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pydantic==2.5.3
pydantic-settings==2.1.0
pytest==7.4.4
pytest-asyncio==0.23.3
httpx==0.26.0
```

### 4. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your values
```

**Required environment variables** (.env):
```bash
# Database
DATABASE_URL=postgresql://user:password@host/database

# Authentication
BETTER_AUTH_SECRET=your-secure-random-secret-here-min-32-chars

# Application
APP_ENV=development
DEBUG=True
CORS_ORIGINS=http://localhost:3000

# Server
HOST=0.0.0.0
PORT=8000
```

**How to get DATABASE_URL**:
1. Sign up at https://neon.tech/
2. Create a new project
3. Copy the connection string from the dashboard
4. Format: `postgresql://username:password@hostname/database?sslmode=require`

**How to generate BETTER_AUTH_SECRET**:
```bash
# Generate a secure random secret (32+ characters)
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. Initialize Database

```bash
# Run database initialization script
python -m app.database

# Or use the init command if available
python -m app.main init-db
```

This will create the `users` and `tasks` tables with appropriate indexes.

### 6. Run Backend Server

```bash
# Start development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the run script if available
python -m app.main
```

**Expected output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 7. Verify Backend

Open browser and navigate to:
- API docs: http://localhost:8000/docs (Swagger UI)
- Alternative docs: http://localhost:8000/redoc (ReDoc)
- Health check: http://localhost:8000/health (if implemented)

---

## Frontend Setup

### 1. Navigate to Frontend Directory

```bash
# Open new terminal window/tab
cd frontend
```

### 2. Install Dependencies

```bash
# Install Node.js dependencies
npm install

# Or use yarn
yarn install
```

**Expected dependencies** (package.json):
```json
{
  "dependencies": {
    "next": "^16.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "better-auth": "^1.0.0",
    "typescript": "^5.3.3"
  },
  "devDependencies": {
    "@types/node": "^20.10.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0",
    "eslint": "^8.56.0",
    "eslint-config-next": "^16.0.0"
  }
}
```

### 3. Configure Environment Variables

```bash
# Copy example environment file
cp .env.local.example .env.local

# Edit .env.local file with your values
```

**Required environment variables** (.env.local):
```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Authentication (must match backend secret)
BETTER_AUTH_SECRET=your-secure-random-secret-here-min-32-chars

# Application
NEXT_PUBLIC_APP_NAME=Todo App
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

**Important**: The `BETTER_AUTH_SECRET` must be **identical** to the backend secret.

### 4. Run Frontend Development Server

```bash
# Start Next.js development server
npm run dev

# Or use yarn
yarn dev
```

**Expected output**:
```
   ▲ Next.js 16.0.0
   - Local:        http://localhost:3000
   - Network:      http://192.168.1.100:3000

 ✓ Ready in 2.5s
```

### 5. Verify Frontend

Open browser and navigate to:
- Landing page: http://localhost:3000
- Signup page: http://localhost:3000/signup
- Signin page: http://localhost:3000/signin

---

## Testing

### Backend Tests

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment (if not already active)
source venv/bin/activate  # macOS/Linux
.\venv\Scripts\Activate.ps1  # Windows

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x
```

**Expected output**:
```
======================== test session starts ========================
collected 25 items

tests/test_auth.py ........                                   [ 32%]
tests/test_tasks.py ................                          [100%]

======================== 25 passed in 3.45s ========================
```

### Frontend Tests

```bash
# Navigate to frontend directory
cd frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch

# Run specific test file
npm test -- TaskItem.test.tsx
```

**Expected output**:
```
PASS  tests/components/TaskItem.test.tsx
PASS  tests/components/TaskList.test.tsx
PASS  tests/components/SignupForm.test.tsx

Test Suites: 3 passed, 3 total
Tests:       15 passed, 15 total
Snapshots:   0 total
Time:        4.567 s
```

### Integration Tests

```bash
# Ensure both backend and frontend are running

# Run integration tests (backend)
cd backend
pytest tests/test_integration.py

# Run E2E tests (frontend - if implemented)
cd frontend
npm run test:e2e
```

---

## Development Workflow

### 1. Start Development Environment

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Available for commands
```

### 2. Make Changes

1. **Backend changes**: Edit files in `backend/app/`
   - Server auto-reloads on file changes
   - Check http://localhost:8000/docs for API updates

2. **Frontend changes**: Edit files in `frontend/app/` or `frontend/components/`
   - Browser auto-refreshes on file changes
   - Check browser console for errors

### 3. Test Changes

```bash
# Backend: Run tests
cd backend
pytest

# Frontend: Run tests
cd frontend
npm test
```

### 4. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add task completion toggle

- Implement PATCH /api/{user_id}/tasks/{id}/complete endpoint
- Add toggle button to TaskItem component
- Add tests for completion toggle

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# Push to remote
git push origin 001-fullstack-web-app
```

---

## Deployment

### Backend Deployment (Render/Railway/Fly.io)

#### Option 1: Render

1. **Create Render account**: https://render.com/

2. **Create new Web Service**:
   - Connect GitHub repository
   - Select `backend` directory
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Configure environment variables**:
   - `DATABASE_URL`: Your Neon connection string
   - `BETTER_AUTH_SECRET`: Same secret as frontend
   - `CORS_ORIGINS`: Your Vercel frontend URL

4. **Deploy**: Render automatically deploys on push

#### Option 2: Railway

1. **Create Railway account**: https://railway.app/

2. **Create new project**:
   - Connect GitHub repository
   - Select `backend` directory

3. **Configure**:
   - Railway auto-detects Python
   - Add environment variables
   - Deploy

#### Option 3: Fly.io

1. **Install Fly CLI**: https://fly.io/docs/hands-on/install-flyctl/

2. **Login and create app**:
```bash
cd backend
fly auth login
fly launch
```

3. **Set secrets**:
```bash
fly secrets set DATABASE_URL="your-neon-url"
fly secrets set BETTER_AUTH_SECRET="your-secret"
fly secrets set CORS_ORIGINS="your-vercel-url"
```

4. **Deploy**:
```bash
fly deploy
```

### Frontend Deployment (Vercel)

1. **Create Vercel account**: https://vercel.com/

2. **Import project**:
   - Click "New Project"
   - Import from GitHub
   - Select repository

3. **Configure project**:
   - Framework Preset: Next.js
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`

4. **Configure environment variables**:
   - `NEXT_PUBLIC_API_URL`: Your backend URL (e.g., https://your-app.onrender.com)
   - `BETTER_AUTH_SECRET`: Same secret as backend

5. **Deploy**:
   - Click "Deploy"
   - Vercel automatically builds and deploys
   - Get deployment URL (e.g., https://your-app.vercel.app)

6. **Update backend CORS**:
   - Add Vercel URL to backend `CORS_ORIGINS` environment variable
   - Redeploy backend

### Database Setup (Neon)

1. **Create Neon project**: https://neon.tech/

2. **Get connection string**:
   - Navigate to project dashboard
   - Copy connection string
   - Format: `postgresql://user:pass@host/db?sslmode=require`

3. **Initialize database**:
```bash
# Run locally with production DATABASE_URL
DATABASE_URL="your-neon-url" python -m app.database
```

4. **Verify**:
   - Check Neon dashboard for tables
   - Should see `users` and `tasks` tables

---

## Troubleshooting

### Backend Issues

**Issue**: `ModuleNotFoundError: No module named 'app'`
```bash
# Solution: Ensure you're in backend directory and venv is activated
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**Issue**: `sqlalchemy.exc.OperationalError: could not connect to server`
```bash
# Solution: Check DATABASE_URL in .env
# Verify Neon database is running
# Check network connectivity
```

**Issue**: `CORS error in browser console`
```bash
# Solution: Add frontend URL to CORS_ORIGINS in backend .env
CORS_ORIGINS=http://localhost:3000,https://your-app.vercel.app
```

### Frontend Issues

**Issue**: `Error: Cannot find module 'next'`
```bash
# Solution: Install dependencies
cd frontend
npm install
```

**Issue**: `API calls failing with 401 Unauthorized`
```bash
# Solution: Check BETTER_AUTH_SECRET matches between frontend and backend
# Verify token is being sent in Authorization header
# Check browser console for errors
```

**Issue**: `Module not found: Can't resolve '@/components/...'`
```bash
# Solution: Check tsconfig.json has correct path aliases
# Restart Next.js dev server
```

### Database Issues

**Issue**: `relation "users" does not exist`
```bash
# Solution: Initialize database
cd backend
python -m app.database
```

**Issue**: `password authentication failed`
```bash
# Solution: Verify DATABASE_URL credentials
# Check Neon dashboard for correct username/password
```

---

## Useful Commands

### Backend

```bash
# Start server
uvicorn app.main:app --reload

# Run tests
pytest

# Run tests with coverage
pytest --cov=app

# Format code
black app/

# Lint code
flake8 app/

# Type check
mypy app/
```

### Frontend

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run tests
npm test

# Lint code
npm run lint

# Format code
npm run format
```

### Database

```bash
# Initialize database
python -m app.database

# Create migration (if using Alembic)
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

---

## Next Steps

After completing this quickstart:

1. ✅ **Verify Setup**: Ensure both frontend and backend are running
2. ✅ **Test Functionality**: Create account, add tasks, test all features
3. ✅ **Run Tests**: Ensure all tests pass
4. ✅ **Deploy**: Deploy to Vercel (frontend) and cloud provider (backend)
5. ✅ **Create Demo Video**: Record < 90 second demo
6. ✅ **Submit**: Submit GitHub repo and deployment URLs

---

## Additional Resources

### Documentation

- **Next.js**: https://nextjs.org/docs
- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLModel**: https://sqlmodel.tiangolo.com/
- **Neon**: https://neon.tech/docs
- **Better Auth**: https://better-auth.com/docs

### Tutorials

- **Next.js App Router**: https://nextjs.org/docs/app
- **FastAPI Tutorial**: https://fastapi.tiangolo.com/tutorial/
- **PostgreSQL Tutorial**: https://www.postgresql.org/docs/

### Community

- **Next.js Discord**: https://nextjs.org/discord
- **FastAPI Discord**: https://discord.gg/fastapi
- **GitHub Discussions**: Repository discussions tab

---

## Support

For issues or questions:

1. Check this quickstart guide
2. Review specification files in `specs/001-fullstack-web-app/`
3. Check GitHub Issues
4. Ask in project Discord/Slack

---

**Last Updated**: 2026-01-14
**Version**: 1.0.0
