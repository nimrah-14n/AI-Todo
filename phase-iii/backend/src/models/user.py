"""
User model for authenticated users.
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from .conversation import Conversation
    from .message import Message
    from .task import Task


class User(SQLModel, table=True):
    """Authenticated user of the system."""

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True)
    hashed_password: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversations: List["Conversation"] = Relationship(back_populates="user")
    tasks: List["Task"] = Relationship(back_populates="user")
