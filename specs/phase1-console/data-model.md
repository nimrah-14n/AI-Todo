# Data Model: Phase 1 - Todo Console Application

**Feature**: phase1-console
**Date**: 2025-12-29
**Source**: `specs/phase1-console/spec.md`, `specs/phase1-console/research.md`

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────┐
│                      TaskManager                         │
│─────────────────────────────────────────────────────────│
│  _tasks: dict[int, Task]                                │
│  _next_id: int                                          │
│─────────────────────────────────────────────────────────│
│  + add_task(title, description?) -> Task                │
│  + get_task(task_id) -> Task | None                     │
│  + get_all_tasks() -> list[Task]                        │
│  + get_pending_tasks() -> list[Task]                    │
│  + get_completed_tasks() -> list[Task]                  │
│  + update_task(task_id, title?, description?) -> Task   │
│  + delete_task(task_id) -> bool                         │
│  + toggle_complete(task_id) -> Task                     │
│  + task_count() -> int                                  │
└─────────────────────────────────────────────────────────┘
                           │
                           │ manages 0..*
                           ▼
┌─────────────────────────────────────────────────────────┐
│                         Task                             │
│─────────────────────────────────────────────────────────│
│  id: int                    [PK, auto-generated]        │
│  title: str                 [required, 1-200 chars]     │
│  description: str           [optional, max 1000 chars]  │
│  completed: bool            [default: False]            │
│  created_at: datetime       [auto-generated]            │
└─────────────────────────────────────────────────────────┘
```

---

## Entity: Task

### Definition

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Task:
    """
    Represents a single todo item.

    [From]: spec.md §Key Entities
    """
    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert task to dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "created_at": self.created_at.isoformat()
        }
```

### Field Specifications

| Field | Type | Required | Default | Constraints | Notes |
|-------|------|----------|---------|-------------|-------|
| `id` | `int` | Auto | Auto-increment | Positive, unique | Never reused after deletion |
| `title` | `str` | Yes | - | 1-200 chars, non-empty | Whitespace-only rejected |
| `description` | `str` | No | `""` | 0-1000 chars | Empty string if not provided |
| `completed` | `bool` | No | `False` | True/False | Toggleable |
| `created_at` | `datetime` | Auto | `datetime.now()` | Immutable | Set once at creation |

### Validation Rules

```python
# Title validation
def validate_title(title: str) -> str:
    """
    Validate and normalize task title.

    Raises:
        EmptyTitleError: If title is empty or whitespace-only
        TitleTooLongError: If title exceeds 200 characters
    """
    title = title.strip()
    if not title:
        raise EmptyTitleError("Task title cannot be empty")
    if len(title) > 200:
        raise TitleTooLongError("Task title must be 200 characters or less")
    return title

# Description validation
def validate_description(description: str | None) -> str:
    """
    Validate and normalize task description.

    Raises:
        DescriptionTooLongError: If description exceeds 1000 characters
    """
    if description is None:
        return ""
    description = description.strip()
    if len(description) > 1000:
        raise DescriptionTooLongError("Description must be 1000 characters or less")
    return description
```

---

## Entity: TaskManager

### Definition

```python
class TaskManager:
    """
    Manages in-memory collection of tasks.

    Provides CRUD operations and filtering capabilities.

    [From]: spec.md §Key Entities
    """

    def __init__(self):
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1
```

### Method Specifications

#### `add_task(title: str, description: str = "") -> Task`

**Purpose**: Create and store a new task

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `title` | `str` | Yes | Task title (1-200 chars) |
| `description` | `str` | No | Task description (max 1000 chars) |

**Returns**: `Task` - The newly created task

**Raises**:
- `EmptyTitleError` - If title is empty
- `TitleTooLongError` - If title > 200 chars
- `DescriptionTooLongError` - If description > 1000 chars

**Behavior**:
1. Validate title and description
2. Generate unique ID
3. Create Task instance
4. Store in `_tasks` dictionary
5. Return created task

---

#### `get_task(task_id: int) -> Task | None`

**Purpose**: Retrieve a task by its ID

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `task_id` | `int` | Yes | Task identifier |

**Returns**: `Task | None` - The task if found, None otherwise

---

#### `get_all_tasks() -> list[Task]`

**Purpose**: Retrieve all tasks

**Returns**: `list[Task]` - All tasks sorted by ID (ascending)

---

#### `get_pending_tasks() -> list[Task]`

**Purpose**: Retrieve incomplete tasks

**Returns**: `list[Task]` - Tasks where `completed == False`

---

#### `get_completed_tasks() -> list[Task]`

**Purpose**: Retrieve completed tasks

**Returns**: `list[Task]` - Tasks where `completed == True`

---

#### `update_task(task_id: int, title: str | None = None, description: str | None = None) -> Task`

**Purpose**: Update task title and/or description

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `task_id` | `int` | Yes | Task identifier |
| `title` | `str \| None` | No | New title (if provided) |
| `description` | `str \| None` | No | New description (if provided) |

**Returns**: `Task` - The updated task

**Raises**:
- `TaskNotFoundError` - If task doesn't exist
- `EmptyTitleError` - If new title is empty
- `TitleTooLongError` - If new title > 200 chars

**Behavior**:
1. Find task by ID (raise if not found)
2. If title provided, validate and update
3. If description provided, validate and update
4. Return updated task

---

#### `delete_task(task_id: int) -> bool`

**Purpose**: Remove a task from the collection

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `task_id` | `int` | Yes | Task identifier |

**Returns**: `bool` - True if deleted, False if not found

**Raises**:
- `TaskNotFoundError` - If task doesn't exist

---

#### `toggle_complete(task_id: int) -> Task`

**Purpose**: Toggle task completion status

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `task_id` | `int` | Yes | Task identifier |

**Returns**: `Task` - The task with toggled status

**Raises**:
- `TaskNotFoundError` - If task doesn't exist

**Behavior**:
1. Find task by ID (raise if not found)
2. Flip `completed` boolean
3. Return modified task

---

#### `task_count() -> int`

**Purpose**: Get total number of tasks

**Returns**: `int` - Number of tasks in collection

---

## Exception Hierarchy

```python
class TodoError(Exception):
    """Base exception for all todo application errors."""
    pass


class ValidationError(TodoError):
    """Base class for validation errors."""
    pass


class EmptyTitleError(ValidationError):
    """Raised when task title is empty or whitespace-only."""
    def __init__(self, message: str = "Task title cannot be empty"):
        super().__init__(message)


class TitleTooLongError(ValidationError):
    """Raised when task title exceeds 200 characters."""
    def __init__(self, message: str = "Task title must be 200 characters or less"):
        super().__init__(message)


class DescriptionTooLongError(ValidationError):
    """Raised when description exceeds 1000 characters."""
    def __init__(self, message: str = "Description must be 1000 characters or less"):
        super().__init__(message)


class TaskNotFoundError(TodoError):
    """Raised when task with given ID does not exist."""
    def __init__(self, task_id: int):
        super().__init__(f"Task with ID {task_id} not found")
        self.task_id = task_id
```

---

## State Transitions

### Task Completion State

```
┌──────────┐  toggle_complete()  ┌───────────┐
│ PENDING  │ ◄─────────────────► │ COMPLETED │
│completed │                     │ completed │
│ = False  │                     │ = True    │
└──────────┘                     └───────────┘
```

### Task Lifecycle

```
                    add_task()
                        │
                        ▼
┌─────────────────────────────────────┐
│              ACTIVE                  │
│  (exists in TaskManager._tasks)     │
│                                      │
│  Can be:                            │
│  - Viewed (get_task, get_all_tasks) │
│  - Updated (update_task)            │
│  - Toggled (toggle_complete)        │
└─────────────────────────────────────┘
                        │
                        │ delete_task()
                        ▼
┌─────────────────────────────────────┐
│              DELETED                 │
│  (removed from TaskManager._tasks)  │
│  (ID never reused)                  │
└─────────────────────────────────────┘
```

---

## Invariants

1. **ID Uniqueness**: `∀ t1, t2 ∈ tasks: t1 ≠ t2 → t1.id ≠ t2.id`
2. **ID Monotonicity**: `∀ t_new: t_new.id > max(existing_ids)`
3. **Title Non-Empty**: `∀ t ∈ tasks: len(t.title.strip()) > 0`
4. **Title Length**: `∀ t ∈ tasks: len(t.title) ≤ 200`
5. **Description Length**: `∀ t ∈ tasks: len(t.description) ≤ 1000`
6. **Created Immutable**: `t.created_at` never changes after creation

---

## Storage Schema (In-Memory)

```python
# Internal storage structure
_tasks: dict[int, Task] = {
    1: Task(id=1, title="Buy groceries", description="Milk, eggs", completed=False, created_at=datetime(...)),
    2: Task(id=2, title="Call mom", description="", completed=True, created_at=datetime(...)),
    # ...
}

# ID counter (never decrements, even after deletion)
_next_id: int = 3
```

---

## Future Considerations (Phase II+)

| Aspect | Phase 1 | Phase II+ |
|--------|---------|-----------|
| Storage | In-memory dict | PostgreSQL (Neon) |
| ID Type | Sequential int | UUID or auto-increment |
| User Scope | Single user | Multi-user with user_id FK |
| Timestamps | Local datetime | UTC with timezone |
| Persistence | None | Full database persistence |
