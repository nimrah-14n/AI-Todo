"""
Message model for individual messages in conversations.
"""
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import Text
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

if TYPE_CHECKING:
    from .conversation import Conversation
    from .user import User


class MessageRole(str, Enum):
    """Enum for message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(SQLModel, table=True):
    """Individual message in a conversation."""

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversation.id", index=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    role: str = Field(max_length=20)  # 'user', 'assistant', or 'system'
    content: str = Field(sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")
