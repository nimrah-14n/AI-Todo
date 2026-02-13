# Data Model: Todo AI Chatbot

**Feature**: Todo AI Chatbot
**Branch**: 001-todo-ai-chatbot
**Date**: 2026-02-07
**Status**: Complete

## Overview

This document defines the data model for the Todo AI Chatbot feature, extending the existing Phase II schema with conversation and message entities. All entities use UUID primary keys per constitution v1.1.0.

---

## Entity Definitions

### Existing Entities (Phase II)

#### User
Represents an authenticated user of the system.

**Fields**:
- `id` (UUID, PRIMARY KEY): Unique user identifier
- `email` (string, UNIQUE, NOT NULL): User email address (max 255 characters)
- `hashed_password` (string, NOT NULL): Bcrypt hashed password (max 255 characters)
- `created_at` (timestamp, AUTO): Account creation timestamp
- `updated_at` (timestamp, AUTO): Last update timestamp

**Validation Rules**:
- Email must be valid format and unique
- Password must be hashed before storage (never store plaintext)

**Relationships**:
- One user has many tasks
- One user has many conversations

---

#### Task
Represents a todo item belonging to a user.

**Fields**:
- `id` (UUID, PRIMARY KEY): Unique task identifier
- `user_id` (UUID, FOREIGN KEY → users.id, NOT NULL): Owner of the task
- `title` (string, NOT NULL): Task title (1-200 characters)
- `description` (text, NULLABLE): Task description (max 1000 characters)
- `is_complete` (boolean, DEFAULT false): Completion status
- `created_at` (timestamp, AUTO): Task creation timestamp
- `updated_at` (timestamp, AUTO): Last update timestamp

**Validation Rules**:
- Title: Required, 1-200 characters
- Description: Optional, max 1000 characters
- is_complete: Boolean, defaults to false

**Relationships**:
- Many tasks belong to one user
- Tasks can be referenced in conversation messages (implicit)

**Indexes**:
- `idx_task_user_id` on `user_id` (for filtering user's tasks)
- `idx_task_is_complete` on `is_complete` (for status filtering)

---

### New Entities (Phase III)

#### Conversation
Represents a chat session between a user and the AI assistant.

**Fields**:
- `id` (UUID, PRIMARY KEY): Unique conversation identifier
- `user_id` (UUID, FOREIGN KEY → users.id, NOT NULL): Owner of the conversation
- `created_at` (timestamp, AUTO): Conversation start timestamp
- `updated_at` (timestamp, AUTO): Last message timestamp

**Validation Rules**:
- user_id: Required, must reference existing user
- Timestamps: Auto-generated, immutable after creation (except updated_at)

**Relationships**:
- Many conversations belong to one user
- One conversation has many messages

**Indexes**:
- `idx_conversation_user_id` on `user_id` (for loading user's conversations)
- `idx_conversation_updated_at` on `updated_at` (for sorting by recency)

**State Transitions**:
- Created: When user sends first message (no conversation_id provided)
- Active: While messages are being exchanged
- Inactive: No explicit state - conversations remain accessible indefinitely

**Business Rules**:
- Each conversation belongs to exactly one user
- Conversations cannot be shared between users
- Conversations persist indefinitely (no automatic deletion)
- Most recent conversation can be loaded on chat interface open

---

#### Message
Represents a single message in a conversation (from user or assistant).

**Fields**:
- `id` (UUID, PRIMARY KEY): Unique message identifier
- `conversation_id` (UUID, FOREIGN KEY → conversation.id, NOT NULL): Parent conversation
- `user_id` (UUID, FOREIGN KEY → users.id, NOT NULL): Owner of the conversation
- `role` (enum, NOT NULL): Message sender ('user' or 'assistant')
- `content` (text, NOT NULL): Message text content
- `created_at` (timestamp, AUTO): Message timestamp

**Validation Rules**:
- conversation_id: Required, must reference existing conversation
- user_id: Required, must match conversation owner
- role: Required, must be 'user' or 'assistant'
- content: Required, non-empty text
- created_at: Auto-generated, immutable

**Relationships**:
- Many messages belong to one conversation
- Many messages belong to one user (indirectly through conversation)

**Indexes**:
- `idx_message_conversation_id` on `conversation_id` (for loading conversation history)
- `idx_message_created_at` on `created_at` (for chronological ordering)

**Business Rules**:
- Messages are immutable once created (no updates or deletes)
- Messages must alternate between 'user' and 'assistant' roles (enforced by application logic)
- Message content is stored as-is (no sanitization in database, handled at application layer)
- Messages are ordered chronologically by created_at

---

## Entity Relationships Diagram

```
┌─────────────────┐
│      User       │
│  (Phase II)     │
│─────────────────│
│ id (UUID) PK    │
│ email           │
│ hashed_password │
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │
         │ 1:N
         │
    ┌────┴─────────────────────────┐
    │                              │
    │                              │
┌───▼──────────┐          ┌────────▼────────┐
│     Task     │          │  Conversation   │
│  (Phase II)  │          │   (Phase III)   │
│──────────────│          │─────────────────│
│ id (UUID) PK │          │ id (UUID) PK    │
│ user_id FK   │          │ user_id FK      │
│ title        │          │ created_at      │
│ description  │          │ updated_at      │
│ is_complete  │          └────────┬────────┘
│ created_at   │                   │
│ updated_at   │                   │ 1:N
└──────────────┘                   │
                            ┌──────▼─────────┐
                            │    Message     │
                            │  (Phase III)   │
                            │────────────────│
                            │ id (UUID) PK   │
                            │ conversation_id│
                            │ user_id FK     │
                            │ role (enum)    │
                            │ content        │
                            │ created_at     │
                            └────────────────┘
```

---

## Database Schema (SQL)

### Conversation Table

```sql
CREATE TABLE conversation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversation_user_id ON conversation(user_id);
CREATE INDEX idx_conversation_updated_at ON conversation(updated_at DESC);

COMMENT ON TABLE conversation IS 'Chat sessions between users and AI assistant';
COMMENT ON COLUMN conversation.user_id IS 'Owner of the conversation';
COMMENT ON COLUMN conversation.updated_at IS 'Timestamp of last message in conversation';
```

### Message Table

```sql
CREATE TABLE message (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL CHECK (length(content) > 0),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_message_conversation_id ON message(conversation_id);
CREATE INDEX idx_message_created_at ON message(created_at);

COMMENT ON TABLE message IS 'Individual messages in conversations';
COMMENT ON COLUMN message.role IS 'Message sender: user or assistant';
COMMENT ON COLUMN message.content IS 'Message text content';
```

---

## SQLModel Definitions (Python)

### Conversation Model

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4

class Conversation(SQLModel, table=True):
    """Chat session between user and AI assistant."""

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")
    user: "User" = Relationship(back_populates="conversations")
```

### Message Model

```python
class Message(SQLModel, table=True):
    """Individual message in a conversation."""

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversation.id", index=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    role: str = Field(max_length=20)  # 'user' or 'assistant'
    content: str = Field(sa_column_kwargs={"type_": "TEXT"})
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
    user: "User" = Relationship(back_populates="messages")

    # Validation
    @validator('role')
    def validate_role(cls, v):
        if v not in ['user', 'assistant']:
            raise ValueError("Role must be 'user' or 'assistant'")
        return v

    @validator('content')
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        return v
```

---

## Data Access Patterns

### Create Conversation

```python
def create_conversation(user_id: UUID, session: Session) -> Conversation:
    """Create a new conversation for a user."""
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation
```

### Load Conversation History

```python
def load_conversation_history(
    conversation_id: UUID,
    session: Session,
    max_messages: int = 50
) -> List[dict]:
    """Load recent messages from a conversation."""
    messages = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(max_messages)
    ).all()

    # Reverse to chronological order
    return [
        {"role": msg.role, "content": msg.content}
        for msg in reversed(messages)
    ]
```

### Store Message

```python
def store_message(
    conversation_id: UUID,
    user_id: UUID,
    role: str,
    content: str,
    session: Session
) -> Message:
    """Store a new message in a conversation."""
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content=content
    )
    session.add(message)

    # Update conversation timestamp
    conversation = session.get(Conversation, conversation_id)
    conversation.updated_at = datetime.utcnow()

    session.commit()
    session.refresh(message)
    return message
```

### Get User's Latest Conversation

```python
def get_latest_conversation(user_id: UUID, session: Session) -> Optional[Conversation]:
    """Get user's most recent conversation."""
    return session.exec(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .limit(1)
    ).first()
```

---

## Migration Strategy

### Phase II → Phase III Migration

1. **Add new tables** (conversation, message)
2. **No changes to existing tables** (user, task remain unchanged)
3. **Backward compatible** (Phase II functionality unaffected)

### Migration Script

```sql
-- Migration: Add conversation and message tables for Phase III
-- Date: 2026-02-07
-- Feature: 001-todo-ai-chatbot

BEGIN;

-- Create conversation table
CREATE TABLE conversation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversation_user_id ON conversation(user_id);
CREATE INDEX idx_conversation_updated_at ON conversation(updated_at DESC);

-- Create message table
CREATE TABLE message (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL CHECK (length(content) > 0),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_message_conversation_id ON message(conversation_id);
CREATE INDEX idx_message_created_at ON message(created_at);

COMMIT;
```

---

## Performance Considerations

### Query Optimization

1. **Conversation History Loading**: Index on `conversation_id` and `created_at` enables efficient chronological retrieval
2. **User's Conversations**: Index on `user_id` and `updated_at` enables efficient "recent conversations" queries
3. **Message Pruning**: Limit query to last N messages to prevent token limit issues

### Storage Estimates

Assuming 100 users, average 10 conversations per user, 50 messages per conversation:
- Conversations: 1,000 rows × ~100 bytes = ~100 KB
- Messages: 50,000 rows × ~500 bytes = ~25 MB

**Conclusion**: Storage requirements are minimal for Phase III scale.

---

## Summary

**New Entities**: 2 (Conversation, Message)
**New Relationships**: 3 (User→Conversation, Conversation→Message, User→Message)
**Database Changes**: 2 new tables, 4 new indexes
**Migration Impact**: Additive only, no changes to existing schema
**Backward Compatibility**: Full (Phase II functionality unaffected)

**Next**: Generate API contracts (chat-api.yaml, mcp-tools.yaml)
