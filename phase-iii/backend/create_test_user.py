"""
Create a test user for Phase III testing.
"""
from dotenv import load_dotenv
load_dotenv()

from sqlmodel import Session, create_engine
from uuid import UUID
from datetime import datetime
import os

# Import the actual User model
from src.models.user import User

# Connect to database
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# Create test user
test_user_id = UUID("00000000-0000-0000-0000-000000000001")

with Session(engine) as session:
    # Check if user exists
    existing_user = session.get(User, test_user_id)

    if not existing_user:
        # Create test user with hashed password
        # Using a simple hash for testing (in production, use proper bcrypt)
        test_user = User(
            id=test_user_id,
            email="test@example.com",
            hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7qXqK9OEUK",  # "password123"
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(test_user)
        session.commit()
        print(f"✓ Created test user: {test_user_id}")
        print(f"  Email: test@example.com")
        print(f"  Password: password123")
    else:
        print(f"✓ Test user already exists: {test_user_id}")
        print(f"  Email: {existing_user.email}")
