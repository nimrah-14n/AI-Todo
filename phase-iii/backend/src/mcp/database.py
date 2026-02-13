"""
Database session management for MCP tools.

This module provides database connection and session management
for MCP tools to interact with the PostgreSQL database.
"""
from sqlmodel import Session, create_engine
from typing import Generator
import os
import logging

logger = logging.getLogger(__name__)

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,
    max_overflow=10
)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency for database sessions in FastAPI.

    Yields:
        SQLModel Session instance

    Example:
        @app.get("/items")
        def get_items(session: Session = Depends(get_session)):
            # Use session here
            pass
    """
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()


def init_db():
    """
    Initialize database tables.

    This creates all tables defined in SQLModel models.
    Should be called on application startup.
    """
    from sqlmodel import SQLModel
    from ..models.task import Task
    from ..models.conversation import Conversation
    from ..models.message import Message

    logger.info("Initializing database tables...")
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables initialized successfully")


def close_db():
    """
    Close database connections.

    Should be called on application shutdown.
    """
    logger.info("Closing database connections...")
    engine.dispose()
    logger.info("Database connections closed")
