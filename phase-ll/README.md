# Phase II - Todo Full-Stack Web Application

A modern, full-stack todo application built with Next.js, FastAPI, and PostgreSQL.

## 🚀 Features

- **User Authentication**: Secure signup/signin with JWT tokens (7-day expiration)
- **Task Management**: Create, view, update, delete, and mark tasks as complete
- **Data Isolation**: Each user can only access their own tasks
- **Responsive UI**: Works on desktop and mobile devices
- **Real-time Updates**: Optimistic UI updates for instant feedback

## 🛠️ Technology Stack

### Frontend
- **Next.js 16+** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **Better Auth** for authentication

### Backend
- **FastAPI** for RESTful API
- **SQLModel** for ORM
- **PostgreSQL** (Neon) for database
- **JWT** for authentication tokens
- **Bcrypt** for password hashing

## 📋 Prerequisites

- **Python 3.13+**
- **UV** (recommended) or pip - [Install UV](https://docs.astral.sh/uv/getting-started/installation/)
- **Node.js 18+** and npm
- **PostgreSQL database** (Neon recommended)

### Installing UV (Recommended)

UV is a fast Python package manager that's 10-100x faster than pip:

```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

## 🔧 Setup Instructions

### 1. Clone the Repository

```bash
cd ai-cloud-hackathon-2/phase-2
```

### 2. Backend Setup

**Option A: Using UV (Recommended - 10-100x faster)**

```bash
cd backend

# UV automatically creates virtual environment and installs dependencies
uv sync

# Create .env file
cp .env.example .env

# Edit .env and add your configuration:
# - DATABASE_URL: Your Neon PostgreSQL connection string
# - BETTER_AUTH_SECRET: A secure random string (min 32 characters)
# - CORS_ORIGINS: http://localhost:3000

# Initialize database
uv run python -m app.database

# Run the server
uv run python -m app.main
```

**Option B: Using pip (Traditional method)**

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your configuration:
# - DATABASE_URL: Your Neon PostgreSQL connection string
# - BETTER_AUTH_SECRET: A secure random string (min 32 characters)
# - CORS_ORIGINS: http://localhost:3000

# Initialize database
python -m app.database

# Run the server
python -m app.main
```

The backend API will be available at `http://localhost:8000`

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.local.example .env.local

# Edit .env.local and add:
# - NEXT_PUBLIC_API_URL=http://localhost:8000
# - BETTER_AUTH_SECRET=<same secret as backend>

# Run the development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Authentication Endpoints

- `POST /api/auth/signup` - Create new account
- `POST /api/auth/signin` - Sign in to existing account
- `POST /api/auth/signout` - Sign out (informational)

### Task Endpoints

All task endpoints require JWT authentication via `Authorization: Bearer <token>` header.

- `GET /api/{user_id}/tasks` - List all user's tasks
- `POST /api/{user_id}/tasks` - Create new task
- `GET /api/{user_id}/tasks/{id}` - Get single task
- `PUT /api/{user_id}/tasks/{id}` - Update task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle completion
- `DELETE /api/{user_id}/tasks/{id}` - Delete task

## 🧪 Testing

### Backend Tests

The backend includes comprehensive test coverage:
- **Authentication Tests**: Signup, signin, JWT validation, password hashing
- **Task CRUD Tests**: Create, read, update, delete, completion toggle
- **Integration Tests**: Complete user flows, data isolation
- **Total**: 30+ test cases

**Using UV (Recommended):**

```bash
cd backend

# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=app --cov-report=html

# Run specific test file
uv run pytest tests/test_auth.py
uv run pytest tests/test_tasks.py
uv run pytest tests/test_integration.py

# View coverage report
# Open htmlcov/index.html in browser
```

**Using pip (Traditional):**

```bash
cd backend

# Activate virtual environment first
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py
pytest tests/test_tasks.py
pytest tests/test_integration.py

# View coverage report
# Open htmlcov/index.html in browser
```

**Test Coverage**:
- Authentication: 100%
- Task CRUD: 100%
- Data isolation: 100%
- Error handling: 100%

### Frontend Tests

The frontend includes component and integration tests:
- **Auth Components**: SignupForm, SigninForm validation
- **Task Components**: TaskList, TaskItem, CreateTaskForm, EmptyState
- **Total**: 20+ test cases

```bash
cd frontend

# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# View coverage report
# Open coverage/lcov-report/index.html in browser
```

**Test Coverage**:
- Auth forms: 100%
- Task components: 100%
- Form validation: 100%

## 🏗️ Project Structure

```
phase-2/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLModel database models
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── dependencies/    # FastAPI dependencies
│   │   ├── config.py        # Configuration
│   │   ├── database.py      # Database connection
│   │   └── main.py          # FastAPI application
│   ├── tests/               # Backend tests
│   └── requirements.txt     # Python dependencies
│
└── frontend/
    ├── app/                 # Next.js App Router pages
    ├── components/          # React components
    │   ├── auth/           # Authentication components
    │   └── tasks/          # Task management components
    ├── contexts/           # React contexts
    ├── hooks/              # Custom React hooks
    ├── lib/                # Utility functions
    └── package.json        # Node dependencies
```

## 🔐 Security Features

- **Password Hashing**: Bcrypt with salt
- **JWT Tokens**: 7-day expiration, signed with secret
- **Data Isolation**: Users can only access their own tasks
- **Input Validation**: Server-side validation for all inputs
- **CORS Protection**: Configured allowed origins

## 📝 Environment Variables

### Backend (.env)

```env
DATABASE_URL=postgresql://user:password@host/database
BETTER_AUTH_SECRET=your-secure-random-secret-min-32-chars
APP_ENV=development
DEBUG=True
CORS_ORIGINS=http://localhost:3000
HOST=0.0.0.0
PORT=8000
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=same-as-backend-secret
NEXT_PUBLIC_APP_NAME=Todo App
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

## 🚢 Deployment

### Backend Deployment

The backend can be deployed to:
- **Render**: Python web service
- **Railway**: Python deployment
- **Fly.io**: Docker deployment

### Frontend Deployment

The frontend is optimized for **Vercel**:

```bash
cd frontend
vercel deploy
```

## 📖 User Guide

### Getting Started

1. **Sign Up**: Create an account with your email and password (min 8 characters)
2. **Sign In**: Log in with your credentials
3. **Create Tasks**: Add tasks with a title and optional description
4. **Manage Tasks**: Mark complete, edit, or delete tasks as needed
5. **Sign Out**: Securely log out when done

### Task Management

- **Create**: Click "Add Task" button, enter title and description
- **Complete**: Click the checkbox to mark a task as done
- **Edit**: Click the edit icon to modify title or description
- **Delete**: Click the delete icon and confirm deletion

## 🤝 Contributing

This project follows Spec-Driven Development (SDD) methodology. All changes must:
1. Be specified in `specs/001-fullstack-web-app/`
2. Follow the implementation plan
3. Include tests
4. Update documentation

## 📄 License

This project is part of the AI Cloud Hackathon II.

## 🆘 Troubleshooting

### Backend won't start
- Check DATABASE_URL is correct
- Ensure PostgreSQL is running
- Verify all dependencies are installed

### Frontend won't connect to backend
- Check NEXT_PUBLIC_API_URL matches backend URL
- Verify CORS_ORIGINS includes frontend URL
- Ensure backend is running

### Authentication issues
- Verify BETTER_AUTH_SECRET matches between frontend and backend
- Check JWT token hasn't expired (7-day limit)
- Clear browser localStorage and sign in again

## 📞 Support

For issues and questions:
- Check the [specification](../../specs/001-fullstack-web-app/spec.md)
- Review the [implementation plan](../../specs/001-fullstack-web-app/plan.md)
- See [tasks breakdown](../../specs/001-fullstack-web-app/tasks.md)

---

**Built with ❤️ using Spec-Driven Development**
