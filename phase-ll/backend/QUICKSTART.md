# Phase II Backend - Quick Reference

## 🚀 Quick Start Commands

### Using UV (Recommended - Fast!)

```bash
# First time setup
uv sync                          # Install all dependencies
cp .env.example .env            # Create environment file
# Edit .env with your DATABASE_URL and BETTER_AUTH_SECRET
uv run python -m app.database   # Initialize database
uv run python -m app.main       # Start server

# Daily development
uv run python -m app.main       # Start server
uv run pytest                   # Run tests
uv run pytest --cov=app         # Run tests with coverage

# Add new dependency
uv add package-name             # Add to dependencies
uv add --dev package-name       # Add to dev dependencies

# Update dependencies
uv sync                         # Sync with pyproject.toml
```

### Using pip (Traditional)

```bash
# First time setup
python -m venv venv             # Create virtual environment
venv\Scripts\activate           # Activate (Windows)
# source venv/bin/activate      # Activate (macOS/Linux)
pip install -r requirements.txt # Install dependencies
cp .env.example .env            # Create environment file
# Edit .env with your DATABASE_URL and BETTER_AUTH_SECRET
python -m app.database          # Initialize database
python -m app.main              # Start server

# Daily development
venv\Scripts\activate           # Activate environment
python -m app.main              # Start server
pytest                          # Run tests
pytest --cov=app                # Run tests with coverage

# Add new dependency
pip install package-name        # Install package
pip freeze > requirements.txt   # Update requirements.txt
```

## 📝 Environment Variables

Required in `.env`:

```env
DATABASE_URL=postgresql://user:pass@host/database
BETTER_AUTH_SECRET=your-32-char-secret-here
APP_ENV=development
DEBUG=True
CORS_ORIGINS=http://localhost:3000
HOST=0.0.0.0
PORT=8000
```

## 🧪 Testing Commands

### UV
```bash
uv run pytest                              # All tests
uv run pytest tests/test_auth.py          # Auth tests only
uv run pytest tests/test_tasks.py         # Task tests only
uv run pytest tests/test_integration.py   # Integration tests
uv run pytest --cov=app --cov-report=html # Coverage report
```

### pip
```bash
pytest                              # All tests
pytest tests/test_auth.py          # Auth tests only
pytest tests/test_tasks.py         # Task tests only
pytest tests/test_integration.py   # Integration tests
pytest --cov=app --cov-report=html # Coverage report
```

## 🔧 Common Tasks

### Database Operations
```bash
# UV
uv run python -m app.database      # Initialize/reset database

# pip
python -m app.database             # Initialize/reset database
```

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Troubleshooting

**UV not found?**
```bash
# Install UV
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows
curl -LsSf https://astral.sh/uv/install.sh | sh             # macOS/Linux
```

**Database connection error?**
- Check DATABASE_URL in `.env`
- Verify Neon database is accessible
- Test connection: `psql $DATABASE_URL`

**Import errors?**
```bash
# UV
uv sync                    # Re-sync dependencies

# pip
pip install -r requirements.txt  # Reinstall dependencies
```

## 📦 Project Structure

```
backend/
├── app/
│   ├── models/          # Database models (User, Task)
│   ├── routes/          # API endpoints (auth, tasks)
│   ├── services/        # Business logic
│   ├── schemas/         # Request/response schemas
│   ├── dependencies/    # FastAPI dependencies
│   ├── middleware/      # Error handlers
│   ├── config.py        # Configuration
│   ├── database.py      # Database connection
│   └── main.py          # FastAPI application
├── tests/               # Test files
├── .env.example         # Environment template
├── .python-version      # Python version for UV
├── pyproject.toml       # Project config (UV)
├── requirements.txt     # Dependencies (pip)
└── Dockerfile           # Docker configuration
```

## 🎯 Why UV?

- **10-100x faster** than pip
- **Automatic virtual environment** management
- **Deterministic installs** with lockfile
- **Better dependency resolution**
- **Compatible with pip** (uses pyproject.toml + requirements.txt)
- **Modern Python tooling** standard

Both UV and pip work perfectly - choose what you prefer!
