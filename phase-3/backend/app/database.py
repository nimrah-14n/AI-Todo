"""
Database connection module with SQLModel engine and session management.

[Task]: T005, T015
[From]: specs/001-fullstack-web-app/data-model.md, plan.md
"""

from sqlmodel import SQLModel, create_engine, Session
from app.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)


def init_db():
    """
    Initialize database schema by creating all tables.

    [Task]: T015
    """
    # Import models to register them with SQLModel metadata
    from app.models import User, Task

    # Create all tables
    SQLModel.metadata.create_all(engine)
    print("✓ Database tables created successfully")


def get_session():
    """
    Dependency function to get database session.
    Yields a session and ensures it's closed after use.
    """
    with Session(engine) as session:
        yield session


if __name__ == "__main__":
    """Run database initialization when executed as script."""
    print("Initializing database...")
    init_db()
