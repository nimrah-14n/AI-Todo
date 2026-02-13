# Data Models Specification: Phase 1 - Todo Console Application

**Related Spec**: `specs/phase1-console/spec.md`
**Created**: 2025-12-29
**Status**: Draft

---

## Entity Definitions

### Task Entity

The core entity representing a todo item.

```
Task
├── id: int              # Unique identifier (auto-generated, sequential)
├── title: str           # Task title (required, 1-200 chars)
├── description: str     # Task description (optional, max 1000 chars)
├── completed: bool      # Completion status (default: False)
└── created_at: datetime # Creation timestamp (auto-generated)
```

#### Field Specifications

| Field | Type | Required | Default | Constraints |
|-------|------|----------|---------|-------------|
| `id` | `int` | Auto | Auto-increment | Positive integer, unique |
| `title` | `str` | Yes | - | 1-200 characters, non-empty |
| `description` | `str` | No | `""` | 0-1000 characters |
| `completed` | `bool` | No | `False` | True/False |
| `created_at` | `datetime` | Auto | `datetime.now()` | ISO 8601 format |

#### Validation Rules

1. **Title Validation**:
   - Must not be empty or whitespace only
   - Must be between 1 and 200 characters after trimming
   - Must be a string type

2. **Description Validation**:
   - Optional (can be empty string or None)
   - If provided, must not exceed 1000 characters
   - Must be a string type if provided

3. **ID Validation**:
   - Must be a positive integer
   - Must be unique within the task collection
   - Auto-generated, not user-modifiable

---

### TaskManager Entity

Manages the collection of tasks and provides CRUD operations.

```
TaskManager
├── _tasks: dict[int, Task]    # Internal task storage (id -> Task)
├── _next_id: int              # Next available ID (starts at 1)
│
├── add_task(title, description?) -> Task
├── get_task(id) -> Task | None
├── get_all_tasks() -> list[Task]
├── get_pending_tasks() -> list[Task]
├── get_completed_tasks() -> list[Task]
├── update_task(id, title?, description?) -> Task | None
├── delete_task(id) -> bool
├── toggle_complete(id) -> Task | None
└── task_count() -> int
```

#### Method Specifications

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `add_task` | `title: str`, `description: str = ""` | `Task` | Creates and stores a new task |
| `get_task` | `task_id: int` | `Task \| None` | Retrieves task by ID |
| `get_all_tasks` | - | `list[Task]` | Returns all tasks |
| `get_pending_tasks` | - | `list[Task]` | Returns incomplete tasks |
| `get_completed_tasks` | - | `list[Task]` | Returns completed tasks |
| `update_task` | `task_id: int`, `title: str = None`, `description: str = None` | `Task \| None` | Updates task fields |
| `delete_task` | `task_id: int` | `bool` | Removes task, returns success |
| `toggle_complete` | `task_id: int` | `Task \| None` | Toggles completion status |
| `task_count` | - | `int` | Returns total task count |

---

## Data Flow Diagrams

### Add Task Flow

```
User Input                TaskManager              Task
    │                         │                     │
    │  add "Buy milk"         │                     │
    ├────────────────────────>│                     │
    │                         │  validate title     │
    │                         ├──────────┐          │
    │                         │<─────────┘          │
    │                         │                     │
    │                         │  create Task        │
    │                         ├────────────────────>│
    │                         │                     │
    │                         │  store in _tasks    │
    │                         ├──────────┐          │
    │                         │<─────────┘          │
    │                         │                     │
    │  Task(id=1, ...)        │                     │
    │<────────────────────────┤                     │
```

### View Tasks Flow

```
User Input                TaskManager              Output
    │                         │                     │
    │  list --all             │                     │
    ├────────────────────────>│                     │
    │                         │                     │
    │                         │  get_all_tasks()    │
    │                         ├──────────┐          │
    │                         │<─────────┘          │
    │                         │                     │
    │  [Task1, Task2, ...]    │                     │
    │<────────────────────────┤                     │
    │                         │                     │
    │  format_output()        │                     │
    ├────────────────────────────────────────────>│
    │                         │    Display List     │
```

### Complete Task Flow

```
User Input                TaskManager              Task
    │                         │                     │
    │  complete 1             │                     │
    ├────────────────────────>│                     │
    │                         │                     │
    │                         │  get_task(1)        │
    │                         ├────────────────────>│
    │                         │<────────────────────┤
    │                         │                     │
    │                         │  toggle completed   │
    │                         ├────────────────────>│
    │                         │<────────────────────┤
    │                         │                     │
    │  Task(completed=True)   │                     │
    │<────────────────────────┤                     │
```

---

## Error Handling

### Custom Exceptions

| Exception | Trigger | Message Template |
|-----------|---------|------------------|
| `TaskNotFoundError` | Task ID doesn't exist | "Task with ID {id} not found" |
| `ValidationError` | Invalid input data | "Validation failed: {details}" |
| `EmptyTitleError` | Title is empty/whitespace | "Task title cannot be empty" |
| `TitleTooLongError` | Title > 200 chars | "Task title must be 200 characters or less" |

### Error Response Structure

```python
{
    "success": False,
    "error": {
        "type": "TaskNotFoundError",
        "message": "Task with ID 99 not found"
    }
}
```

### Success Response Structure

```python
{
    "success": True,
    "data": {
        "id": 1,
        "title": "Buy groceries",
        "description": "Milk, eggs, bread",
        "completed": False,
        "created_at": "2025-12-29T10:30:00"
    }
}
```

---

## State Management

### In-Memory Storage

Tasks are stored in a dictionary for O(1) lookup by ID:

```python
_tasks: dict[int, Task] = {
    1: Task(id=1, title="Buy groceries", ...),
    2: Task(id=2, title="Call mom", ...),
}
```

### ID Generation

- Sequential integer starting at 1
- Never reused (even after deletion)
- Stored in `_next_id` counter

```python
_next_id: int = 1

def _generate_id(self) -> int:
    current_id = self._next_id
    self._next_id += 1
    return current_id
```

---

## Type Definitions (Python)

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Task:
    """Represents a todo task item."""
    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert task to dictionary representation."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "created_at": self.created_at.isoformat()
        }


class TaskManager:
    """Manages in-memory collection of tasks."""

    def __init__(self):
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    # ... method implementations
```

---

## Invariants

1. **ID Uniqueness**: No two tasks can have the same ID
2. **ID Immutability**: Task IDs cannot be changed after creation
3. **ID Monotonicity**: IDs always increase (never decrease or reuse)
4. **Title Non-Empty**: Every task must have a non-empty title
5. **Timestamp Immutability**: `created_at` is set once and never modified
6. **State Consistency**: `_tasks` dictionary always reflects current state
