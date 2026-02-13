# Feature Specification: Phase 1 - Todo In-Memory Console Application

**Feature Branch**: `phase1-console-app`
**Created**: 2025-12-29
**Status**: Draft
**Phase**: I of V
**Points**: 100

---

## Overview

Build a command-line todo application that stores tasks in memory using Python. This is the foundation for all subsequent phases and must implement the 5 Basic Level features using Spec-Driven Development.

### Scope

| In Scope | Out of Scope |
|----------|--------------|
| In-memory task storage | Database persistence |
| CLI interface | Web/GUI interface |
| Single-user operation | Multi-user/authentication |
| Basic CRUD operations | Advanced features (priorities, tags, due dates) |
| Python 3.13+ | Other programming languages |

---

## User Scenarios & Testing

### User Story 1 - Add a New Task (Priority: P1)

As a user, I want to add a new task to my todo list so that I can track things I need to do.

**Why this priority**: This is the foundational feature - without the ability to add tasks, no other features are useful. This enables the core value proposition.

**Independent Test**: Can be fully tested by running the add command and verifying the task appears in the list. Delivers immediate value as user can start tracking tasks.

**Acceptance Scenarios**:

1. **Given** the application is running, **When** I add a task with title "Buy groceries", **Then** the system confirms the task was added with a unique ID
2. **Given** the application is running, **When** I add a task with title "Call mom" and description "Wish her happy birthday", **Then** the system stores both title and description
3. **Given** I try to add a task, **When** I provide an empty title, **Then** the system rejects the input with an error message
4. **Given** I add multiple tasks, **When** I check the task IDs, **Then** each task has a unique sequential ID

---

### User Story 2 - View All Tasks (Priority: P1)

As a user, I want to view all my tasks so that I can see what I need to do.

**Why this priority**: Viewing tasks is essential to provide feedback that tasks were added and to see the current state. Without this, users cannot verify their actions.

**Independent Test**: Can be tested by listing tasks after adding them. Delivers value by showing the user their complete todo list.

**Acceptance Scenarios**:

1. **Given** I have added tasks, **When** I request to view all tasks, **Then** the system displays all tasks with their ID, title, and completion status
2. **Given** I have no tasks, **When** I request to view all tasks, **Then** the system displays a message indicating the list is empty
3. **Given** I have tasks with descriptions, **When** I view the task list, **Then** I can see the description for each task
4. **Given** I have completed and pending tasks, **When** I view the list, **Then** completed tasks show a different status indicator than pending tasks

---

### User Story 3 - Mark Task as Complete (Priority: P2)

As a user, I want to mark a task as complete so that I can track my progress.

**Why this priority**: Completing tasks is the primary workflow action after adding and viewing. This enables the core productivity loop.

**Independent Test**: Can be tested by marking a task complete and verifying its status changes in the list view.

**Acceptance Scenarios**:

1. **Given** I have a pending task with ID 1, **When** I mark task 1 as complete, **Then** the task status changes to completed
2. **Given** I have a completed task with ID 1, **When** I mark task 1 as incomplete, **Then** the task status changes back to pending (toggle behavior)
3. **Given** I try to complete a task, **When** I provide a non-existent task ID, **Then** the system displays an error message
4. **Given** I complete a task, **When** I view the task list, **Then** the completed task shows a completion indicator (e.g., [x] vs [ ])

---

### User Story 4 - Update Task Details (Priority: P3)

As a user, I want to update a task's title or description so that I can correct mistakes or add more detail.

**Why this priority**: Updating is less critical than core CRUD but enables users to refine their tasks without deleting and recreating.

**Independent Test**: Can be tested by updating a task's title and verifying the change persists in the list view.

**Acceptance Scenarios**:

1. **Given** I have a task with ID 1, **When** I update the title to "Buy groceries and milk", **Then** the task title is updated
2. **Given** I have a task with ID 1, **When** I update only the description, **Then** the title remains unchanged and description is updated
3. **Given** I try to update a task, **When** I provide a non-existent task ID, **Then** the system displays an error message
4. **Given** I update a task, **When** I provide an empty title, **Then** the system rejects the update with an error message

---

### User Story 5 - Delete a Task (Priority: P3)

As a user, I want to delete a task so that I can remove items I no longer need to track.

**Why this priority**: Delete is a cleanup operation, less frequently needed than add/view/complete but essential for list management.

**Independent Test**: Can be tested by deleting a task and verifying it no longer appears in the list.

**Acceptance Scenarios**:

1. **Given** I have a task with ID 1, **When** I delete task 1, **Then** the task is removed from the list
2. **Given** I try to delete a task, **When** I provide a non-existent task ID, **Then** the system displays an error message
3. **Given** I delete a task, **When** I view the task list, **Then** the deleted task no longer appears
4. **Given** I delete task ID 2, **When** I add a new task, **Then** the new task gets a new unique ID (IDs are not reused)

---

### Edge Cases

- What happens when the user enters a very long title (>200 characters)?
  - System MUST reject with error message (no truncation) to prevent silent data loss
- What happens when the user enters special characters in title/description?
  - System should accept and display them correctly
- What happens when the user enters a negative or non-numeric task ID?
  - System should display an error message
- What happens when the application restarts?
  - All tasks are lost (in-memory only - this is expected behavior for Phase 1)
- What happens when the user enters duplicate task titles?
  - System should allow it (titles don't need to be unique)

---

## Requirements

### Functional Requirements

- **FR-001**: System MUST allow users to add a new task with a title (required) and description (optional)
- **FR-002**: System MUST assign a unique sequential integer ID to each new task
- **FR-003**: System MUST display all tasks with their ID, title, description, and completion status
- **FR-004**: System MUST allow users to mark a task as complete/incomplete (toggle)
- **FR-005**: System MUST allow users to update a task's title and/or description
- **FR-006**: System MUST allow users to delete a task by ID
- **FR-007**: System MUST validate that task titles are not empty (1-200 characters)
- **FR-008**: System MUST display appropriate error messages for invalid operations
- **FR-009**: System MUST provide a clear command-line interface with help/usage information
- **FR-010**: System MUST store all tasks in memory (no persistence required)

### Non-Functional Requirements

- **NFR-001**: System MUST be written in Python 3.13+
- **NFR-002**: System MUST use UV as the package manager
- **NFR-003**: System MUST follow clean code principles (PEP 8)
- **NFR-004**: System MUST have a clear project structure (`/src` folder)
- **NFR-005**: System MUST include comprehensive unit tests
- **NFR-006**: System MUST provide clear, user-friendly CLI output

### Key Entities

- **Task**: Represents a todo item
  - `id`: Unique integer identifier (auto-generated)
  - `title`: String, required, 1-200 characters
  - `description`: String, optional, max 1000 characters
  - `completed`: Boolean, default False
  - `created_at`: Timestamp of creation

- **TaskManager**: Manages the collection of tasks
  - Maintains list of tasks in memory
  - Handles CRUD operations
  - Generates unique IDs

---

## CLI Interface Specification

### Execution Modes

The application supports two execution modes:
1. **Interactive REPL Mode**: Continuous prompt for multiple commands (`python -m todo`)
2. **Single-Command Mode**: Execute one command and exit (`python -m todo add "Task"`)

### Commands

| Command | Arguments | Description |
|---------|-----------|-------------|
| `add` | `<title>` `[--desc <description>]` | Add a new task |
| `list` | `[--all\|--pending\|--completed]` | List tasks (default: all) |
| `complete` | `<task_id>` | Toggle task completion status |
| `update` | `<task_id>` `[--title <title>]` `[--desc <description>]` | Update task details |
| `delete` | `<task_id>` | Delete a task |
| `help` | | Show usage information |
| `exit` | | Exit the application |

### Output Format

```
Task List:
─────────────────────────────────────────
[ ] 1. Buy groceries
    Description: Milk, eggs, bread
    Created: 2025-12-29 10:30:00

[x] 2. Call mom
    Description: Wish her happy birthday
    Created: 2025-12-29 09:15:00
─────────────────────────────────────────
Total: 2 tasks (1 completed, 1 pending)
```

### Error Messages

| Scenario | Message |
|----------|---------|
| Empty title | "Error: Task title cannot be empty" |
| Title too long | "Error: Task title must be 200 characters or less" |
| Task not found | "Error: Task with ID {id} not found" |
| Invalid ID format | "Error: Please provide a valid task ID (number)" |
| Unknown command | "Error: Unknown command '{cmd}'. Type 'help' for usage" |

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: All 5 basic features (add, delete, update, view, complete) work correctly
- **SC-002**: All acceptance scenarios pass when tested
- **SC-003**: Error handling covers all edge cases gracefully
- **SC-004**: Code follows PEP 8 style guidelines (verified by linter)
- **SC-005**: Unit test coverage is at least 80%
- **SC-006**: Application starts and responds to commands within 100ms
- **SC-007**: README provides clear setup and usage instructions

### Definition of Done

- [ ] All functional requirements implemented
- [ ] All acceptance scenarios pass
- [ ] Unit tests written and passing
- [ ] Code reviewed against PEP 8
- [ ] README.md with setup instructions
- [ ] CLAUDE.md with agent instructions
- [ ] Spec files committed to `/specs` folder
- [ ] Demo video recorded (max 90 seconds)

---

## Project Structure

```
hackathon-todo/
├── .specify/                    # Spec-Kit configuration
│   └── memory/
│       └── constitution.md      # Project principles
├── specs/
│   └── phase1-console/
│       ├── spec.md              # This file
│       ├── plan.md              # Technical plan
│       └── tasks.md             # Implementation tasks
├── src/
│   └── todo/
│       ├── __init__.py
│       ├── main.py              # CLI entry point
│       ├── models.py            # Task data model
│       ├── manager.py           # TaskManager logic
│       └── cli.py               # CLI interface
├── tests/
│   └── test_todo.py             # Unit tests
├── pyproject.toml               # UV/Python config
├── CLAUDE.md                    # Claude Code instructions
├── AGENTS.md                    # Cross-agent rules
└── README.md                    # Setup documentation
```

---

## Dependencies

| Dependency | Purpose | Required |
|------------|---------|----------|
| Python 3.13+ | Runtime | Yes |
| UV | Package manager | Yes |
| pytest | Testing framework | Yes (dev) |

---

## Clarifications

### Session 2025-12-29

- Q: When a user enters a title exceeding 200 characters, should the system truncate it automatically or reject it with an error? → A: Reject with error message (no truncation)
- Q: Should the application support both interactive REPL mode AND single-command mode, or only one mode? → A: Both modes supported (interactive REPL + single-command)
- Q: Should the optional `rich` library be included for enhanced CLI output? → A: Plain ASCII only, no external dependencies (YAGNI)

---

## Constraints & Assumptions

### Constraints
1. No database - all data stored in memory
2. No external API calls
3. Single-user only
4. Must use Spec-Driven Development workflow
5. All code generated via Claude Code

### Assumptions
1. User has Python 3.13+ installed
2. User has UV package manager installed
3. User is comfortable with command-line interfaces
4. Data loss on application exit is acceptable for Phase 1
