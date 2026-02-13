# Research: Phase 1 - Todo Console Application

**Feature**: phase1-console
**Date**: 2025-12-29
**Status**: Complete

---

## Research Tasks Completed

### 1. Python CLI Framework Selection

**Decision**: Use Python's built-in `argparse` module

**Rationale**:
- Part of Python standard library (no external dependencies)
- Well-documented and widely understood
- Sufficient for Phase 1 requirements
- Aligns with YAGNI principle from Constitution

**Alternatives Considered**:
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| Click | Decorator-based, elegant | External dependency | Adds unnecessary complexity for Phase 1 |
| Typer | Type hints, auto-completion | External dependency | Over-engineered for 5 commands |
| Rich CLI | Beautiful output | External dependency | Optional enhancement, not core |

---

### 2. Python Project Structure Best Practices

**Decision**: Use `src/` layout with UV package manager

**Rationale**:
- `src/` layout prevents accidental imports from project root
- UV is mandated by Constitution
- Follows modern Python packaging standards (PEP 517/518)

**Structure**:
```
src/
└── todo/
    ├── __init__.py      # Package marker
    ├── __main__.py      # Entry point for `python -m todo`
    ├── models.py        # Task dataclass
    ├── manager.py       # TaskManager business logic
    └── cli.py           # CLI argument parsing
```

---

### 3. Data Class Implementation

**Decision**: Use Python `dataclasses` module

**Rationale**:
- Built-in since Python 3.7
- Automatic `__init__`, `__repr__`, `__eq__`
- Supports default values and field factories
- No external dependencies

**Alternatives Considered**:
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| Pydantic | Validation built-in | External dependency | Overkill for in-memory model |
| NamedTuple | Immutable | Less flexible | Tasks need mutability (completed status) |
| Plain class | Full control | Boilerplate | Dataclass does this better |
| attrs | Powerful | External dependency | Not needed for Phase 1 |

---

### 4. Testing Framework

**Decision**: Use `pytest` with standard assertions

**Rationale**:
- Industry standard for Python testing
- Simple assertion syntax
- Excellent fixture support
- Required by Constitution for TDD

**Test Strategy**:
- Unit tests for `Task` model validation
- Unit tests for `TaskManager` CRUD operations
- Integration tests for CLI commands
- Target: 80% code coverage (per SC-005)

---

### 5. ID Generation Strategy

**Decision**: Sequential integer with auto-increment counter

**Rationale**:
- Simple and predictable
- Easy to reference in CLI commands
- No external dependencies (no UUID library needed)
- Sufficient for single-user, in-memory storage

**Implementation**:
```python
class TaskManager:
    def __init__(self):
        self._next_id = 1

    def _generate_id(self) -> int:
        current = self._next_id
        self._next_id += 1
        return current
```

---

### 6. Input Validation Approach

**Decision**: Validate at TaskManager boundary (not CLI layer)

**Rationale**:
- Single point of validation
- Business rules stay with business logic
- CLI layer handles user interaction only
- Easier to test validation logic

**Validation Rules**:
| Field | Rule | Error |
|-------|------|-------|
| title | Non-empty, 1-200 chars | `EmptyTitleError`, `TitleTooLongError` |
| description | Max 1000 chars | `DescriptionTooLongError` |
| task_id | Positive integer, exists | `TaskNotFoundError` |

---

### 7. CLI Interactive vs Command Mode

**Decision**: Use interactive REPL mode with single-command support

**Rationale**:
- Interactive mode better for user experience
- Single-command mode useful for scripting/testing
- Both modes use same command parser

**Implementation**:
```bash
# Interactive mode (default)
$ python -m todo
Todo> add "Buy groceries"
Todo> list
Todo> exit

# Single command mode
$ python -m todo add "Buy groceries"
$ python -m todo list
```

---

### 8. Output Formatting

**Decision**: Plain text with ASCII borders (optional Rich enhancement)

**Rationale**:
- Works in all terminals
- No external dependencies for basic output
- Rich library can be added as optional enhancement
- Aligns with YAGNI - start simple

**Format Example**:
```
Task List:
─────────────────────────────────────────
[ ] 1. Buy groceries
    Description: Milk, eggs, bread
    Created: 2025-12-29 10:30:00

[x] 2. Call mom
    Created: 2025-12-29 09:15:00
─────────────────────────────────────────
Total: 2 tasks (1 completed, 1 pending)
```

---

### 9. Error Handling Strategy

**Decision**: Custom exception hierarchy with user-friendly messages

**Rationale**:
- Clear separation between internal errors and user-facing messages
- Consistent error format across CLI
- Easy to test error conditions

**Exception Hierarchy**:
```python
class TodoError(Exception):
    """Base exception for todo application."""
    pass

class ValidationError(TodoError):
    """Input validation failed."""
    pass

class TaskNotFoundError(TodoError):
    """Task with given ID does not exist."""
    pass
```

---

### 10. Timestamp Handling

**Decision**: Use `datetime.now()` with local timezone

**Rationale**:
- Simple for Phase 1 (single-user, no sync)
- No timezone complexity needed
- ISO 8601 format for display

**Note for Future Phases**: Phase II+ will require UTC storage with timezone conversion for multi-user support.

---

## Unknowns Resolved

| Unknown | Resolution |
|---------|------------|
| CLI framework | Built-in argparse |
| Data persistence | In-memory dict (Phase 1 scope) |
| Testing framework | pytest |
| ID generation | Sequential integer |
| Input validation | TaskManager boundary |

---

## Technical Decisions Summary

| Decision | Choice | Principle |
|----------|--------|-----------|
| CLI Framework | argparse (stdlib) | YAGNI |
| Data Model | dataclasses | YAGNI |
| Testing | pytest | Constitution mandate |
| ID Strategy | Sequential int | Simplicity |
| Validation | Business layer | Single responsibility |
| Output | Plain text + optional Rich | YAGNI |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Data loss on exit | Expected for Phase 1 | Document clearly in README |
| No concurrent access | N/A for single-user | Phase II addresses this |
| Terminal compatibility | Low | Use ASCII fallbacks |

---

## Next Steps

1. Generate `data-model.md` with final entity definitions
2. Generate `contracts/` with CLI interface contract
3. Create `quickstart.md` with setup instructions
4. Proceed to `/sp.tasks` for implementation breakdown
