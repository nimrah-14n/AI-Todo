# CLI Interface Contract: Phase 1 - Todo Console Application

**Feature**: phase1-console
**Date**: 2025-12-29
**Type**: Command Line Interface

---

## Overview

This document defines the command-line interface contract for the Phase 1 Todo application. All commands, arguments, and output formats are specified here.

---

## Application Entry Points

### Interactive Mode (REPL)

```bash
# Start interactive session
$ python -m todo

Todo App v1.0.0
Type 'help' for available commands, 'exit' to quit.

Todo> _
```

### Single Command Mode

```bash
# Execute single command and exit
$ python -m todo <command> [arguments]
```

---

## Command Reference

### 1. `add` - Create New Task

**Synopsis**:
```
add <title> [--desc <description>]
```

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<title>` | string | Yes | Task title (1-200 chars) |
| `--desc` | string | No | Task description (max 1000 chars) |

**Examples**:
```bash
# Add task with title only
Todo> add "Buy groceries"
✓ Task added: [1] Buy groceries

# Add task with description
Todo> add "Call mom" --desc "Wish her happy birthday"
✓ Task added: [2] Call mom

# Single command mode
$ python -m todo add "Review PR" --desc "Check the new feature branch"
✓ Task added: [3] Review PR
```

**Output Format**:
```
✓ Task added: [{id}] {title}
```

**Error Responses**:
| Condition | Exit Code | Message |
|-----------|-----------|---------|
| Empty title | 1 | `Error: Task title cannot be empty` |
| Title > 200 chars | 1 | `Error: Task title must be 200 characters or less` |
| Description > 1000 chars | 1 | `Error: Description must be 1000 characters or less` |

---

### 2. `list` - View Tasks

**Synopsis**:
```
list [--all | --pending | --completed]
```

**Arguments**:
| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `--all` | flag | No | Yes | Show all tasks |
| `--pending` | flag | No | No | Show only incomplete tasks |
| `--completed` | flag | No | No | Show only completed tasks |

**Examples**:
```bash
# List all tasks (default)
Todo> list

# List only pending tasks
Todo> list --pending

# List only completed tasks
Todo> list --completed
```

**Output Format**:
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

**Empty List Output**:
```
Task List:
─────────────────────────────────────────
No tasks found.
─────────────────────────────────────────
```

**Output Fields**:
| Field | Format | Description |
|-------|--------|-------------|
| Status | `[ ]` or `[x]` | Checkbox indicator |
| ID | Integer | Task identifier |
| Title | String | Task title |
| Description | String (indented) | Optional, shown if present |
| Created | `YYYY-MM-DD HH:MM:SS` | Creation timestamp |
| Summary | `Total: N tasks (X completed, Y pending)` | Footer summary |

---

### 3. `complete` - Toggle Completion Status

**Synopsis**:
```
complete <task_id>
```

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<task_id>` | integer | Yes | ID of task to toggle |

**Examples**:
```bash
# Mark task as complete
Todo> complete 1
✓ Task [1] marked as completed: Buy groceries

# Toggle back to pending
Todo> complete 1
✓ Task [1] marked as pending: Buy groceries
```

**Output Format**:
```
# When completing
✓ Task [{id}] marked as completed: {title}

# When un-completing
✓ Task [{id}] marked as pending: {title}
```

**Error Responses**:
| Condition | Exit Code | Message |
|-----------|-----------|---------|
| Task not found | 1 | `Error: Task with ID {id} not found` |
| Invalid ID format | 1 | `Error: Please provide a valid task ID (number)` |

---

### 4. `update` - Modify Task Details

**Synopsis**:
```
update <task_id> [--title <title>] [--desc <description>]
```

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<task_id>` | integer | Yes | ID of task to update |
| `--title` | string | No | New title (1-200 chars) |
| `--desc` | string | No | New description (max 1000 chars) |

**Note**: At least one of `--title` or `--desc` must be provided.

**Examples**:
```bash
# Update title only
Todo> update 1 --title "Buy groceries and fruits"
✓ Task [1] updated: Buy groceries and fruits

# Update description only
Todo> update 1 --desc "Milk, eggs, bread, apples"
✓ Task [1] updated: Buy groceries and fruits

# Update both
Todo> update 1 --title "Shopping" --desc "Weekly grocery run"
✓ Task [1] updated: Shopping
```

**Output Format**:
```
✓ Task [{id}] updated: {title}
```

**Error Responses**:
| Condition | Exit Code | Message |
|-----------|-----------|---------|
| Task not found | 1 | `Error: Task with ID {id} not found` |
| Invalid ID format | 1 | `Error: Please provide a valid task ID (number)` |
| Empty title | 1 | `Error: Task title cannot be empty` |
| Title > 200 chars | 1 | `Error: Task title must be 200 characters or less` |
| No updates specified | 1 | `Error: Please specify --title or --desc to update` |

---

### 5. `delete` - Remove Task

**Synopsis**:
```
delete <task_id>
```

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<task_id>` | integer | Yes | ID of task to delete |

**Examples**:
```bash
Todo> delete 1
✓ Task [1] deleted: Buy groceries
```

**Output Format**:
```
✓ Task [{id}] deleted: {title}
```

**Error Responses**:
| Condition | Exit Code | Message |
|-----------|-----------|---------|
| Task not found | 1 | `Error: Task with ID {id} not found` |
| Invalid ID format | 1 | `Error: Please provide a valid task ID (number)` |

---

### 6. `help` - Show Usage Information

**Synopsis**:
```
help [command]
```

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `[command]` | string | No | Specific command to get help for |

**Examples**:
```bash
# General help
Todo> help

# Command-specific help
Todo> help add
```

**Output Format (General)**:
```
Todo App - Command Line Task Manager

Usage: todo <command> [options]

Commands:
  add <title> [--desc <desc>]     Add a new task
  list [--all|--pending|--completed]  List tasks
  complete <id>                   Toggle task completion
  update <id> [--title] [--desc]  Update task details
  delete <id>                     Delete a task
  help [command]                  Show this help
  exit                            Exit the application

Examples:
  todo add "Buy groceries" --desc "Milk and eggs"
  todo list --pending
  todo complete 1

Type 'help <command>' for detailed information.
```

---

### 7. `exit` - Exit Application

**Synopsis**:
```
exit
```

**Aliases**: `quit`, `q`, Ctrl+C, Ctrl+D

**Output Format**:
```
Goodbye!
```

---

## Error Handling

### Standard Error Format

```
Error: {message}
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | User error (invalid input, task not found) |
| 2 | System error (unexpected failure) |

### Unknown Command

```
Error: Unknown command 'foo'. Type 'help' for available commands.
```

---

## Input Parsing Rules

### Title Parsing

1. Titles can be quoted or unquoted
2. Quoted titles preserve spaces: `"Buy groceries"`
3. Unquoted titles end at first flag: `Buy --desc` → title is "Buy"

### Flag Parsing

1. Flags start with `--`
2. Flag values follow the flag name
3. Flag values can be quoted for spaces

**Examples**:
```bash
# These are equivalent
add "Buy groceries" --desc "Weekly shopping"
add Buy groceries --desc Weekly shopping     # Only "Buy" is title!

# Correct for multi-word unquoted
add "Buy groceries" --desc "Weekly shopping"
```

---

## Interactive Mode Behavior

### Prompt

```
Todo>
```

### Special Keys

| Key | Action |
|-----|--------|
| Enter | Execute command |
| Ctrl+C | Cancel current input / Exit |
| Ctrl+D | Exit application |
| Up Arrow | Previous command (if history supported) |

### Empty Input

Empty input (just pressing Enter) shows a hint:
```
Todo>
Type 'help' for available commands.
Todo>
```

---

## Output Symbols

| Symbol | Meaning |
|--------|---------|
| `✓` | Success |
| `[ ]` | Pending task |
| `[x]` | Completed task |
| `Error:` | Error message prefix |

---

## Version Information

```bash
$ python -m todo --version
Todo App v1.0.0
```
