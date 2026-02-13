"""
Main entry point for the FastAPI application.

This module loads environment variables from .env file before
importing the FastAPI app, ensuring DATABASE_URL is available.
"""
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Verify critical environment variables are loaded
if not os.getenv("DATABASE_URL"):
    raise ValueError("DATABASE_URL not found in environment variables")

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables")

# Now import the FastAPI app (after env vars are loaded)
from src.api.chat import app
from src.mcp.database import init_db, engine
from sqlmodel import Session
from uuid import UUID
from datetime import datetime

# Initialize database tables immediately
try:
    print("Initializing database tables...")
    init_db()
    print("Database tables initialized!")

    # Create test user if it doesn't exist
    print("Checking for test user...")
    from src.models.user import User

    test_user_id = UUID("00000000-0000-0000-0000-000000000001")

    with Session(engine) as session:
        existing_user = session.get(User, test_user_id)

        if not existing_user:
            test_user = User(
                id=test_user_id,
                email="test@example.com",
                hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7qXqK9OEUK",  # "password123"
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(test_user)
            session.commit()
            print(f"[OK] Created test user: {test_user_id}")
            print(f"     Email: test@example.com")
        else:
            print(f"[OK] Test user already exists: {test_user_id}")
except Exception as e:
    print(f"[WARNING] Database initialization failed: {e}")
    print("[WARNING] Server will start but database operations may fail")

# Export app for uvicorn
__all__ = ["app"]
