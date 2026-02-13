"""
Task SQLModel definition.

[Task]: T014, T016
[From]: specs/001-fullstack-web-app/data-model.md
"""

from sqlmodel import SQLModel, Field, Index
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional


class Task(SQLModel, table=True):
    """Task entity representing a single todo item."""

    __tablename__ = "tasks"
    __table_args__ = (
        # Composite index for optimal query performance (user's tasks sorted by date)
        Index('idx_tasks_user_created', 'user_id', 'created_at'),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_complete: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread, and vegetables",
                "is_complete": False,
                "created_at": "2026-01-15T10:35:00Z",
                "updated_at": "2026-01-15T10:35:00Z"
            }
        }
