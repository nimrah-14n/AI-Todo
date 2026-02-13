# Data Model: Phase II - Todo Full-Stack Web Application

**Feature Branch**: `001-fullstack-web-app`
**Created**: 2026-01-14
**Status**: Active Development

## Overview

This document defines the complete data model for the Todo application, including entity definitions, relationships, validation rules, and state transitions. The model supports multi-user task management with strict data isolation.

## Entity Definitions

### User Entity

**Purpose**: Represents a registered user account in the system.

**Attributes**:

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL, DEFAULT gen_random_uuid() | Unique identifier for the user |
| email | String(255) | UNIQUE, NOT NULL, INDEX | User's email address (normalized to lowercase) |
| hashed_password | String(255) | NOT NULL | Bcrypt-hashed password (never plaintext) |
| created_at | Timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Account creation timestamp (UTC) |
| updated_at | Timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update timestamp (UTC) |

**Validation Rules**:
- **email**: Must be valid email format (RFC 5322), case-insensitive, max 255 characters
- **email**: Normalized to lowercase before storage
- **email**: Must be unique across all users
- **hashed_password**: Must be bcrypt hash (60 characters), never store plaintext
- **hashed_password**: Minimum password length 8 characters (enforced before hashing)
- **created_at**: Automatically set on insert, immutable
- **updated_at**: Automatically updated on every modification

**Business Rules**:
- Email uniqueness check is case-insensitive (user@example.com === USER@EXAMPLE.COM)
- Password must be hashed with bcrypt (work factor 12) before storage
- User cannot be created without valid email and password
- User deletion cascades to all owned tasks

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True)
    hashed_password: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Example Instance**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "alice@example.com",
  "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/1jrPK",
  "created_at": "2026-01-14T10:30:00Z",
  "updated_at": "2026-01-14T10:30:00Z"
}
```

---

### Task Entity

**Purpose**: Represents a single todo item belonging to a specific user.

**Attributes**:

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL, DEFAULT gen_random_uuid() | Unique identifier for the task |
| user_id | UUID | FOREIGN KEY → users.id, NOT NULL, INDEX | Owner's user ID |
| title | String(200) | NOT NULL | Task title (1-200 characters) |
| description | Text | NULLABLE | Task description (optional, max 1000 characters) |
| is_complete | Boolean | NOT NULL, DEFAULT FALSE | Completion status |
| created_at | Timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP, INDEX | Task creation timestamp (UTC) |
| updated_at | Timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update timestamp (UTC) |

**Validation Rules**:
- **user_id**: Must reference a valid user (foreign key constraint)
- **title**: Required, 1-200 characters, cannot be only whitespace
- **title**: Trimmed of leading/trailing whitespace before validation
- **description**: Optional, max 1000 characters if provided
- **description**: Can be null or empty string
- **is_complete**: Boolean, defaults to false
- **created_at**: Automatically set on insert, immutable
- **updated_at**: Automatically updated on every modification

**Business Rules**:
- Task must belong to exactly one user
- Task cannot exist without a valid user_id
- Title cannot be empty after trimming whitespace
- Description is optional but limited to 1000 characters
- Completion status can be toggled independently of other fields
- Tasks are ordered by created_at DESC by default (newest first)

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_complete: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Example Instance**:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread, and vegetables",
  "is_complete": false,
  "created_at": "2026-01-14T10:35:00Z",
  "updated_at": "2026-01-14T10:35:00Z"
}
```

---

## Entity Relationships

### User → Tasks (One-to-Many)

**Relationship Type**: One-to-Many (1:N)

**Description**: One user can own zero or more tasks. Each task belongs to exactly one user.

**Cardinality**:
- User: 1
- Tasks: 0..N (zero to many)

**Foreign Key**: `tasks.user_id` → `users.id`

**Cascade Rules**:
- **ON DELETE CASCADE**: When a user is deleted, all their tasks are automatically deleted
- **ON UPDATE CASCADE**: When a user's ID changes (rare with UUIDs), task references update

**Referential Integrity**:
- Cannot create task with non-existent user_id (foreign key constraint)
- Cannot delete user without deleting or reassigning their tasks (CASCADE handles this)
- Database enforces referential integrity at all times

**Relationship Diagram**:
```
┌─────────────────┐         ┌─────────────────┐
│     User        │         │     Task        │
├─────────────────┤         ├─────────────────┤
│ id (PK)         │◄────────│ id (PK)         │
│ email           │    1:N  │ user_id (FK)    │
│ hashed_password │         │ title           │
│ created_at      │         │ description     │
│ updated_at      │         │ is_complete     │
└─────────────────┘         │ created_at      │
                            │ updated_at      │
                            └─────────────────┘
```

**Query Patterns**:
```sql
-- Get all tasks for a user
SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC;

-- Get user with task count
SELECT u.*, COUNT(t.id) as task_count
FROM users u
LEFT JOIN tasks t ON u.id = t.user_id
WHERE u.id = ?
GROUP BY u.id;

-- Delete user and cascade to tasks
DELETE FROM users WHERE id = ?;
-- All tasks with user_id = ? are automatically deleted
```

---

## Validation Rules

### User Validation

**Email Validation**:
```python
import re

def validate_email(email: str) -> bool:
    """Validate email format (RFC 5322 simplified)"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def normalize_email(email: str) -> str:
    """Normalize email to lowercase"""
    return email.strip().lower()
```

**Password Validation**:
```python
def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if len(password) > 128:
        return False, "Password must be at most 128 characters"
    return True, ""

def hash_password(password: str) -> str:
    """Hash password with bcrypt"""
    import bcrypt
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    import bcrypt
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
```

### Task Validation

**Title Validation**:
```python
def validate_title(title: str) -> tuple[bool, str]:
    """Validate task title"""
    title = title.strip()

    if not title:
        return False, "Title cannot be empty"

    if len(title) < 1:
        return False, "Title must be at least 1 character"

    if len(title) > 200:
        return False, "Title must be at most 200 characters"

    return True, ""
```

**Description Validation**:
```python
def validate_description(description: Optional[str]) -> tuple[bool, str]:
    """Validate task description"""
    if description is None:
        return True, ""  # Description is optional

    if len(description) > 1000:
        return False, "Description must be at most 1000 characters"

    return True, ""
```

---

## State Transitions

### Task Completion State

**States**:
- **Incomplete**: `is_complete = false` (default)
- **Complete**: `is_complete = true`

**Transitions**:
```
┌─────────────┐
│ Incomplete  │
│ (default)   │
└──────┬──────┘
       │
       │ Mark Complete
       ▼
┌─────────────┐
│  Complete   │
└──────┬──────┘
       │
       │ Mark Incomplete
       ▼
┌─────────────┐
│ Incomplete  │
└─────────────┘
```

**State Transition Rules**:
- Task starts in Incomplete state when created
- User can toggle between Incomplete and Complete at any time
- No restrictions on number of transitions
- State persists across sessions
- State is independent of other task attributes

**State Transition Operations**:
```python
def toggle_completion(task: Task) -> Task:
    """Toggle task completion status"""
    task.is_complete = not task.is_complete
    task.updated_at = datetime.utcnow()
    return task

def mark_complete(task: Task) -> Task:
    """Mark task as complete"""
    task.is_complete = True
    task.updated_at = datetime.utcnow()
    return task

def mark_incomplete(task: Task) -> Task:
    """Mark task as incomplete"""
    task.is_complete = False
    task.updated_at = datetime.utcnow()
    return task
```

---

## Data Integrity Constraints

### Database-Level Constraints

**Primary Keys**:
- `users.id`: UUID, unique, not null
- `tasks.id`: UUID, unique, not null

**Foreign Keys**:
- `tasks.user_id` → `users.id` (ON DELETE CASCADE, ON UPDATE CASCADE)

**Unique Constraints**:
- `users.email`: Unique across all users

**Not Null Constraints**:
- `users.email`: Cannot be null
- `users.hashed_password`: Cannot be null
- `tasks.user_id`: Cannot be null
- `tasks.title`: Cannot be null
- `tasks.is_complete`: Cannot be null

**Default Values**:
- `users.id`: gen_random_uuid()
- `users.created_at`: CURRENT_TIMESTAMP
- `users.updated_at`: CURRENT_TIMESTAMP
- `tasks.id`: gen_random_uuid()
- `tasks.is_complete`: FALSE
- `tasks.created_at`: CURRENT_TIMESTAMP
- `tasks.updated_at`: CURRENT_TIMESTAMP

### Application-Level Constraints

**Business Logic Constraints**:
- Email must be valid format before storage
- Email must be normalized to lowercase
- Password must be hashed before storage
- Title must not be only whitespace
- Description length validated before storage
- User ID in JWT must match user_id in URL

**Data Isolation Constraints**:
- Users can only access their own tasks
- All task queries must filter by authenticated user_id
- Task ownership verified before any modification
- Cross-user data access returns 403 Forbidden

---

## Indexes

### Performance Indexes

**users table**:
```sql
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at DESC);
```

**tasks table**:
```sql
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);
CREATE INDEX idx_tasks_is_complete ON tasks(is_complete);
```

**Index Usage**:
- `idx_users_email`: Fast user lookup by email (signin)
- `idx_users_created_at`: Sort users by registration date
- `idx_tasks_user_id`: Fast task retrieval by user (most common query)
- `idx_tasks_created_at`: Sort tasks by creation date
- `idx_tasks_user_created`: Composite index for user's tasks sorted by date (optimal for main query)
- `idx_tasks_is_complete`: Filter tasks by completion status (future feature)

---

## Data Access Patterns

### Common Queries

**User Operations**:
```sql
-- Create user
INSERT INTO users (email, hashed_password)
VALUES (?, ?)
RETURNING id, email, created_at;

-- Find user by email (signin)
SELECT id, email, hashed_password, created_at
FROM users
WHERE email = ?;

-- Get user by ID
SELECT id, email, created_at
FROM users
WHERE id = ?;
```

**Task Operations**:
```sql
-- Create task
INSERT INTO tasks (user_id, title, description)
VALUES (?, ?, ?)
RETURNING id, user_id, title, description, is_complete, created_at, updated_at;

-- Get all tasks for user (with ownership check)
SELECT id, user_id, title, description, is_complete, created_at, updated_at
FROM tasks
WHERE user_id = ?
ORDER BY created_at DESC;

-- Get single task (with ownership check)
SELECT id, user_id, title, description, is_complete, created_at, updated_at
FROM tasks
WHERE id = ? AND user_id = ?;

-- Update task (with ownership check)
UPDATE tasks
SET title = ?, description = ?, updated_at = CURRENT_TIMESTAMP
WHERE id = ? AND user_id = ?
RETURNING id, user_id, title, description, is_complete, created_at, updated_at;

-- Toggle completion (with ownership check)
UPDATE tasks
SET is_complete = NOT is_complete, updated_at = CURRENT_TIMESTAMP
WHERE id = ? AND user_id = ?
RETURNING id, user_id, title, description, is_complete, created_at, updated_at;

-- Delete task (with ownership check)
DELETE FROM tasks
WHERE id = ? AND user_id = ?
RETURNING id;
```

---

## Data Migration Strategy

### Initial Schema Creation

**Phase II Approach**:
- Use SQLModel's `create_all()` to generate schema from models
- No migration tool required for initial development
- Drop and recreate tables during development

**Schema Creation Code**:
```python
from sqlmodel import SQLModel, create_engine
from app.config import settings

engine = create_engine(settings.DATABASE_URL, echo=True)

def init_db():
    """Initialize database schema"""
    SQLModel.metadata.create_all(engine)
```

### Future Migration Strategy (Phase III+)

**Alembic Integration**:
- Use Alembic for schema versioning
- Generate migrations from model changes
- Support rollback and forward migration
- Track migration history in database

---

## References

- **Main Specification**: `specs/001-fullstack-web-app/spec.md`
- **Database Schema**: `specs/001-fullstack-web-app/database/schema.md`
- **API Endpoints**: `specs/001-fullstack-web-app/api/rest-endpoints.md`
- **Architecture**: `specs/001-fullstack-web-app/architecture.md`
