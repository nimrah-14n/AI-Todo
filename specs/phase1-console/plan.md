# Implementation Plan: Phase 1 - Todo Console Application

**Branch**: `phase1-console-app` | **Date**: 2025-12-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/phase1-console/spec.md`

---

## Summary

Build an in-memory command-line todo application in Python that implements 5 basic CRUD features (Add, View, Complete, Update, Delete). Uses Python dataclasses for the Task model, a TaskManager class for business logic, and argparse for CLI interface. All data stored in memory with no persistence.

---

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: None (stdlib only: argparse, dataclasses, datetime)
**Storage**: In-memory dictionary (`dict[int, Task]`)
**Testing**: pytest with pytest-cov
**Target Platform**: Cross-platform CLI (Windows, macOS, Linux)
**Project Type**: Single Python package
**Performance Goals**: < 100ms command response time
**Constraints**: No external dependencies for core functionality, data lost on exit
**Scale/Scope**: Single user, in-memory, ~100s of tasks max

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | ✅ PASS | Spec created before plan |
| II. Test-First Development | ✅ PLANNED | Tasks will include test-first approach |
| III. Iterative Evolution | ✅ PASS | Phase 1 of 5, building foundation |
| IV. Monorepo Architecture | ✅ PASS | Using `src/` layout as specified |
| V. Clean Code & Simplicity | ✅ PASS | YAGNI applied - stdlib only |
| VI. Observability & Documentation | ✅ PLANNED | README, CLAUDE.md, PHRs |

### Technology Stack Compliance

| Requirement | Specified | Planned | Status |
|-------------|-----------|---------|--------|
| Runtime | Python 3.13+ | Python 3.13+ | ✅ |
| Package Manager | UV | UV | ✅ |
| AI Assistant | Claude Code | Claude Code | ✅ |
| Spec Management | Spec-Kit Plus | Spec-Kit Plus | ✅ |

---

## Project Structure

### Documentation (this feature)

```text
specs/phase1-console/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Technology decisions
├── data-model.md        # Entity definitions
├── quickstart.md        # Setup guide
├── contracts/
│   └── cli-interface.md # CLI contract
└── tasks.md             # Implementation tasks (next step)
```

### Source Code (repository root)

```text
src/
└── todo/
    ├── __init__.py          # Package init, version
    ├── __main__.py          # Entry point: python -m todo
    ├── models.py            # Task dataclass
    ├── manager.py           # TaskManager class
    ├── cli.py               # CLI argument parsing
    └── exceptions.py        # Custom exceptions

tests/
├── __init__.py
├── conftest.py              # pytest fixtures
├── test_models.py           # Task model tests
├── test_manager.py          # TaskManager tests
└── test_cli.py              # CLI integration tests
```

**Structure Decision**: Single Python package with `src/` layout. No frontend/backend separation needed for Phase 1 console application.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI Layer                             │
│  cli.py - argparse command parsing                          │
│  __main__.py - entry point                                  │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                      │
│  manager.py - TaskManager class                             │
│  - add_task(), get_task(), update_task()                    │
│  - delete_task(), toggle_complete()                         │
│  - get_all_tasks(), get_pending_tasks()                     │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       Data Layer                             │
│  models.py - Task dataclass                                 │
│  exceptions.py - Custom exceptions                          │
│  Storage: dict[int, Task] (in-memory)                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Design

### 1. Task Model (`models.py`)

```python
@dataclass
class Task:
    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
```

**Responsibilities**:
- Immutable ID after creation
- Serialization to dict (`to_dict()`)
- No validation (handled by TaskManager)

### 2. TaskManager (`manager.py`)

```python
class TaskManager:
    _tasks: dict[int, Task]
    _next_id: int
```

**Responsibilities**:
- CRUD operations on tasks
- Input validation (title, description)
- ID generation
- Filtering (all, pending, completed)

### 3. CLI Interface (`cli.py`)

```python
def create_parser() -> argparse.ArgumentParser
def handle_command(args, manager: TaskManager) -> None
def format_task_list(tasks: list[Task]) -> str
```

**Responsibilities**:
- Parse command-line arguments
- Route to TaskManager methods
- Format output for display
- Handle errors gracefully

### 4. Entry Point (`__main__.py`)

```python
def main():
    # Interactive mode or single command mode
```

**Responsibilities**:
- Application startup
- REPL loop for interactive mode
- Graceful exit handling

### 5. Exceptions (`exceptions.py`)

```python
class TodoError(Exception): ...
class ValidationError(TodoError): ...
class EmptyTitleError(ValidationError): ...
class TitleTooLongError(ValidationError): ...
class TaskNotFoundError(TodoError): ...
```

---

## Data Flow

### Add Task Flow

```
User Input: add "Buy groceries" --desc "Milk, eggs"
    │
    ▼
cli.py: parse_args() → Namespace(command='add', title='Buy groceries', desc='Milk, eggs')
    │
    ▼
cli.py: handle_command() → calls manager.add_task()
    │
    ▼
manager.py: add_task()
    ├── validate_title() → OK or raise EmptyTitleError/TitleTooLongError
    ├── validate_description() → OK or raise DescriptionTooLongError
    ├── generate_id() → 1
    ├── create Task(id=1, title='Buy groceries', ...)
    └── store in _tasks[1]
    │
    ▼
cli.py: format_success() → "✓ Task added: [1] Buy groceries"
    │
    ▼
Output to stdout
```

---

## Testing Strategy

### Test Pyramid

```
        ┌─────────────┐
        │ Integration │  test_cli.py (10%)
        │    Tests    │  - Full command execution
        └──────┬──────┘
               │
        ┌──────▼──────┐
        │    Unit     │  test_manager.py, test_models.py (90%)
        │    Tests    │  - TaskManager methods
        └─────────────┘  - Task model behavior
```

### Test Coverage Goals

| Component | Target | Tests |
|-----------|--------|-------|
| models.py | 100% | Task creation, to_dict() |
| manager.py | 100% | All CRUD operations, edge cases |
| cli.py | 80% | Command parsing, output formatting |
| exceptions.py | 100% | Exception instantiation |
| **Overall** | **≥80%** | |

### Key Test Scenarios

1. **Happy Path**: Add, list, complete, update, delete
2. **Validation**: Empty title, long title, invalid ID
3. **Edge Cases**: Empty list, duplicate titles, toggle twice
4. **Error Handling**: Task not found, invalid command

---

## Implementation Phases

### Phase A: Foundation (Models & Exceptions)

1. Create `exceptions.py` with custom exceptions
2. Create `models.py` with Task dataclass
3. Write unit tests for models

### Phase B: Business Logic (TaskManager)

1. Create `manager.py` with TaskManager class
2. Implement validation functions
3. Implement CRUD methods
4. Write comprehensive unit tests

### Phase C: CLI Interface

1. Create `cli.py` with argument parser
2. Implement command handlers
3. Implement output formatting
4. Create `__main__.py` entry point

### Phase D: Integration & Polish

1. Write CLI integration tests
2. Add help text and documentation
3. Create README.md
4. Verify all acceptance criteria

---

## Acceptance Criteria Mapping

| Requirement | Implementation | Test |
|-------------|----------------|------|
| FR-001: Add task | `manager.add_task()` | `test_add_task_*` |
| FR-002: Unique IDs | `manager._generate_id()` | `test_id_uniqueness` |
| FR-003: Display tasks | `cli.format_task_list()` | `test_list_*` |
| FR-004: Toggle complete | `manager.toggle_complete()` | `test_toggle_*` |
| FR-005: Update task | `manager.update_task()` | `test_update_*` |
| FR-006: Delete task | `manager.delete_task()` | `test_delete_*` |
| FR-007: Validate title | `manager.validate_title()` | `test_validation_*` |
| FR-008: Error messages | Exception classes | `test_error_*` |
| FR-009: Help/usage | argparse built-in | `test_help` |
| FR-010: In-memory storage | `_tasks: dict` | `test_storage` |

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Data loss on exit | Expected | Low | Document clearly |
| Unicode issues | Low | Medium | Test with special chars |
| Windows path issues | Medium | Low | Use pathlib |
| Test flakiness | Low | Medium | Avoid time-dependent tests |

---

## Definition of Done

- [ ] All functional requirements implemented
- [ ] All acceptance scenarios pass
- [ ] Unit test coverage ≥ 80%
- [ ] Code passes ruff linting
- [ ] README.md complete with setup instructions
- [ ] CLAUDE.md updated with project context
- [ ] All spec files committed
- [ ] Demo video recorded (max 90 seconds)

---

## Complexity Tracking

> **No Constitution violations detected. YAGNI principles followed.**

| Decision | Complexity Level | Justification |
|----------|------------------|---------------|
| No database | Minimal | Phase 1 scope is in-memory |
| No external deps | Minimal | stdlib sufficient |
| Single package | Minimal | No need for monorepo in Phase 1 |

---

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Execute tasks in TDD order (red-green-refactor)
3. Create PHR for each significant implementation step
4. Submit Phase 1 deliverables by deadline

---

## References

- [Feature Specification](./spec.md)
- [Research Document](./research.md)
- [Data Model](./data-model.md)
- [CLI Contract](./contracts/cli-interface.md)
- [Quickstart Guide](./quickstart.md)
- [Constitution](../../.specify/memory/constitution.md)
