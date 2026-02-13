# Database Schema Specification

**Feature Branch**: `001-fullstack-web-app`
**Created**: 2026-01-14
**Status**: Active Development

## Overview

This specification defines the complete database schema for the Todo application using PostgreSQL with SQLModel ORM. The schema supports multi-user task management with strict data isolation.

## Database Technology

- **Database**: PostgreSQL 14+
- **Hosting**: Neon Serverless PostgreSQL
- **ORM**: SQLModel (combines SQLAlchemy and Pydantic)
- **Migration Tool**: Alembic (optional for Phase II)

## Schema Design Principles

1. **Data Isolation**: Each user's tasks are completely isolated
2. **Referential Integrity**: Foreign keys enforce relationships
3. **Cascade Deletion**: Tasks deleted when user deleted (future feature)
4. **Timestamps**: Track creation and modification times
5. **UUID Primary Keys**: Globally unique identifiers
6. **Indexing**: Optimize common query patterns

---

## Tables

### users

Stores user account information.

**Table Definition**:
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Columns**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique user identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User's email address (normalized to lowercase) |
| hashed_password | VARCHAR(255) | NOT NULL | Bcrypt-hashed password (never plaintext) |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Indexes**:
```sql
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at DESC);
```

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

**Constraints**:
- Email must be unique across all users
- Email is case-insensitive (normalized to lowercase before storage)
- Hashed password must never be null
- Created_at and updated_at automatically set on insert

**Sample Data**:
```sql
INSERT INTO users (id, email, hashed_password, created_at, updated_at)
VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    'alice@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/1jrPK',
    '2026-01-14 10:30:00+00',
    '2026-01-14 10:30:00+00'
);
```

---

### tasks

Stores task information for all users.

**Table Definition**:
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    is_complete BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Columns**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique task identifier |
| user_id | UUID | NOT NULL, FOREIGN KEY → users(id) ON DELETE CASCADE | Owner's user ID |
| title | VARCHAR(200) | NOT NULL | Task title (1-200 characters) |
| description | TEXT | NULL | Task description (optional, max 1000 chars enforced by app) |
| is_complete | BOOLEAN | DEFAULT FALSE, NOT NULL | Completion status |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | Task creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Indexes**:
```sql
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);
CREATE INDEX idx_tasks_is_complete ON tasks(is_complete);
```

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

    # Relationship (optional, for ORM convenience)
    # user: Optional["User"] = Relationship(back_populates="tasks")
```

**Constraints**:
- user_id must reference a valid user (foreign key constraint)
- title cannot be null or empty
- is_complete defaults to false
- ON DELETE CASCADE: When user deleted, all their tasks are deleted
- created_at and updated_at automatically set on insert

**Sample Data**:
```sql
INSERT INTO tasks (id, user_id, title, description, is_complete, created_at, updated_at)
VALUES
(
    '123e4567-e89b-12d3-a456-426614174000',
    '550e8400-e29b-41d4-a716-446655440000',
    'Buy groceries',
    'Milk, eggs, bread, and vegetables',
    FALSE,
    '2026-01-14 10:35:00+00',
    '2026-01-14 10:35:00+00'
),
(
    '223e4567-e89b-12d3-a456-426614174001',
    '550e8400-e29b-41d4-a716-446655440000',
    'Finish project report',
    NULL,
    TRUE,
    '2026-01-13 15:20:00+00',
    '2026-01-14 09:15:00+00'
);
```

---

## Relationships

### users → tasks (One-to-Many)

- One user can have zero or more tasks
- Each task belongs to exactly one user
- Foreign key: `tasks.user_id` → `users.id`
- Cascade delete: When user deleted, all their tasks are deleted

**Relationship Diagram**:
```
┌─────────────────┐         ┌─────────────────┐
│     users       │         │     tasks       │
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

---

## Indexes

### Purpose of Indexes

Indexes optimize query performance for common access patterns:

1. **idx_users_email**: Fast user lookup by email (signin)
2. **idx_users_created_at**: Sort users by registration date
3. **idx_tasks_user_id**: Fast task retrieval by user (most common query)
4. **idx_tasks_created_at**: Sort tasks by creation date
5. **idx_tasks_user_created**: Composite index for user's tasks sorted by date
6. **idx_tasks_is_complete**: Filter tasks by completion status (future feature)

### Index Definitions

```sql
-- Users table indexes
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at DESC);

-- Tasks table indexes
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);
CREATE INDEX idx_tasks_is_complete ON tasks(is_complete);
```

### Query Performance

**Query**: Get all tasks for a user, sorted by creation date
```sql
SELECT * FROM tasks
WHERE user_id = '550e8400-e29b-41d4-a716-446655440000'
ORDER BY created_at DESC;
```
**Index Used**: `idx_tasks_user_created` (composite index)
**Expected Performance**: < 10ms for 1000 tasks

---

## Data Validation

### Application-Level Validation

The following validations are enforced by the application (not database constraints):

**Users**:
- Email format validation (RFC 5322)
- Email normalization (lowercase)
- Password minimum length (8 characters)
- Password maximum length (128 characters)

**Tasks**:
- Title minimum length (1 character after trimming whitespace)
- Title maximum length (200 characters)
- Description maximum length (1000 characters)
- Title cannot be only whitespace

### Database-Level Constraints

The following constraints are enforced by the database:

**Users**:
- Email uniqueness (UNIQUE constraint)
- Email not null (NOT NULL constraint)
- Hashed password not null (NOT NULL constraint)

**Tasks**:
- User ID must reference valid user (FOREIGN KEY constraint)
- Title not null (NOT NULL constraint)
- is_complete not null (NOT NULL constraint)

---

## Database Initialization

### Schema Creation Script

```sql
-- Create users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for users
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at DESC);

-- Create tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    is_complete BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for tasks
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);
CREATE INDEX idx_tasks_is_complete ON tasks(is_complete);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### SQLModel Initialization

```python
from sqlmodel import SQLModel, create_engine
from app.config import settings

# Create database engine
engine = create_engine(settings.DATABASE_URL, echo=True)

# Create all tables
def init_db():
    SQLModel.metadata.create_all(engine)
```

---

## Common Queries

### User Queries

**1. Create User**:
```sql
INSERT INTO users (email, hashed_password)
VALUES ('alice@example.com', '$2b$12$...')
RETURNING id, email, created_at;
```

**2. Find User by Email**:
```sql
SELECT id, email, hashed_password, created_at
FROM users
WHERE email = 'alice@example.com';
```

**3. Get User by ID**:
```sql
SELECT id, email, created_at
FROM users
WHERE id = '550e8400-e29b-41d4-a716-446655440000';
```

### Task Queries

**1. Create Task**:
```sql
INSERT INTO tasks (user_id, title, description)
VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    'Buy groceries',
    'Milk, eggs, bread'
)
RETURNING id, user_id, title, description, is_complete, created_at, updated_at;
```

**2. Get All Tasks for User**:
```sql
SELECT id, user_id, title, description, is_complete, created_at, updated_at
FROM tasks
WHERE user_id = '550e8400-e29b-41d4-a716-446655440000'
ORDER BY created_at DESC;
```

**3. Get Single Task (with ownership check)**:
```sql
SELECT id, user_id, title, description, is_complete, created_at, updated_at
FROM tasks
WHERE id = '123e4567-e89b-12d3-a456-426614174000'
  AND user_id = '550e8400-e29b-41d4-a716-446655440000';
```

**4. Update Task**:
```sql
UPDATE tasks
SET title = 'Buy groceries and cook dinner',
    description = 'Milk, eggs, bread, vegetables, chicken'
WHERE id = '123e4567-e89b-12d3-a456-426614174000'
  AND user_id = '550e8400-e29b-41d4-a716-446655440000'
RETURNING id, user_id, title, description, is_complete, created_at, updated_at;
```

**5. Toggle Task Completion**:
```sql
UPDATE tasks
SET is_complete = NOT is_complete
WHERE id = '123e4567-e89b-12d3-a456-426614174000'
  AND user_id = '550e8400-e29b-41d4-a716-446655440000'
RETURNING id, user_id, title, description, is_complete, created_at, updated_at;
```

**6. Delete Task**:
```sql
DELETE FROM tasks
WHERE id = '123e4567-e89b-12d3-a456-426614174000'
  AND user_id = '550e8400-e29b-41d4-a716-446655440000'
RETURNING id;
```

---

## Data Integrity Rules

### Referential Integrity

1. **Foreign Key Constraint**:
   - Every task must have a valid user_id
   - Cannot create task with non-existent user_id
   - Database enforces this constraint

2. **Cascade Deletion**:
   - When user is deleted, all their tasks are automatically deleted
   - Prevents orphaned tasks
   - Enforced by `ON DELETE CASCADE`

### Data Consistency

1. **Atomic Operations**:
   - All database operations are atomic (ACID properties)
   - Either entire operation succeeds or entire operation fails
   - No partial updates

2. **Transaction Isolation**:
   - Default isolation level: READ COMMITTED
   - Prevents dirty reads
   - Ensures consistent data view

### Uniqueness Constraints

1. **User Email**:
   - Each email can only be registered once
   - Enforced by UNIQUE constraint
   - Case-insensitive (normalized to lowercase)

2. **Primary Keys**:
   - UUIDs ensure global uniqueness
   - No collisions across distributed systems
   - Generated by database (gen_random_uuid())

---

## Performance Considerations

### Query Optimization

1. **Index Usage**:
   - All common queries use indexes
   - Composite index for user's tasks sorted by date
   - Explain plan shows index scans, not table scans

2. **Connection Pooling**:
   - Reuse database connections
   - Reduce connection overhead
   - Configured in SQLModel engine

3. **Query Limits**:
   - No pagination in Phase II (all tasks returned)
   - Future: Add LIMIT and OFFSET for large task lists

### Scalability

1. **Vertical Scaling**:
   - Neon automatically scales compute resources
   - Handles increased load without manual intervention

2. **Horizontal Scaling**:
   - Read replicas for read-heavy workloads (future)
   - Sharding by user_id (future, if needed)

3. **Capacity Planning**:
   - Support 10,000+ total tasks
   - Support 1,000+ tasks per user
   - Support 100+ concurrent users

---

## Backup and Recovery

### Neon Automatic Backups

- **Point-in-Time Recovery**: Restore to any point in last 7 days
- **Automatic Snapshots**: Daily backups
- **Retention**: 7 days (configurable)

### Manual Backup

```bash
# Export database to SQL file
pg_dump $DATABASE_URL > backup.sql

# Restore from SQL file
psql $DATABASE_URL < backup.sql
```

---

## Security Considerations

### Password Storage

- **Never store plaintext passwords**
- **Always use bcrypt hashing**
- **Salt automatically generated per password**
- **Work factor: 12 rounds (configurable)**

### SQL Injection Prevention

- **Always use parameterized queries**
- **Never concatenate user input into SQL**
- **SQLModel ORM handles parameterization automatically**

### Access Control

- **Database credentials in environment variables**
- **Least privilege principle**
- **Application user has only necessary permissions**

---

## Testing Data

### Seed Data for Development

```sql
-- Insert test users
INSERT INTO users (id, email, hashed_password) VALUES
('550e8400-e29b-41d4-a716-446655440000', 'alice@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/1jrPK'),
('660e8400-e29b-41d4-a716-446655440001', 'bob@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/1jrPK');

-- Insert test tasks for Alice
INSERT INTO tasks (user_id, title, description, is_complete) VALUES
('550e8400-e29b-41d4-a716-446655440000', 'Buy groceries', 'Milk, eggs, bread', FALSE),
('550e8400-e29b-41d4-a716-446655440000', 'Finish report', NULL, TRUE),
('550e8400-e29b-41d4-a716-446655440000', 'Call dentist', 'Schedule appointment', FALSE);

-- Insert test tasks for Bob
INSERT INTO tasks (user_id, title, description, is_complete) VALUES
('660e8400-e29b-41d4-a716-446655440001', 'Review code', 'PR #123', FALSE),
('660e8400-e29b-41d4-a716-446655440001', 'Update documentation', NULL, FALSE);
```

---

## Migration Strategy

### Phase II Approach

- **No migrations**: Create schema from scratch
- **SQLModel.metadata.create_all()**: Generate tables automatically
- **Development**: Drop and recreate tables as needed

### Future Approach (Production)

- **Alembic**: Database migration tool
- **Version control**: Track schema changes
- **Rollback capability**: Revert migrations if needed

---

## References

- **Main Specification**: `specs/001-fullstack-web-app/spec.md`
- **Architecture**: `specs/001-fullstack-web-app/architecture.md`
- **API Endpoints**: `specs/001-fullstack-web-app/api/rest-endpoints.md`
- **Authentication**: `specs/001-fullstack-web-app/features/authentication.md`
- **Task CRUD**: `specs/001-fullstack-web-app/features/task-crud.md`
