# Todo Console Application

A simple command-line todo application built in Python. This is Phase 1 of a 5-phase project implementing an in-memory todo list with full CRUD functionality.

## Features

- **Add Tasks**: Create tasks with title and optional description
- **View Tasks**: List all, pending, or completed tasks
- **Complete Tasks**: Toggle task completion status
- **Update Tasks**: Modify task title and/or description
- **Delete Tasks**: Remove tasks from the list

## Installation

```bash
# Using pip
pip install -e .

# Using uv (recommended)
uv pip install -e .
```

## Usage

### Single Command Mode

```bash
# Add a task
python -m todo add "Buy groceries" --desc "Milk, eggs, bread"

# List all tasks
python -m todo list

# List pending tasks only
python -m todo list --pending

# List completed tasks only
python -m todo list --completed

# Complete a task (toggle)
python -m todo complete 1

# Update a task
python -m todo update 1 --title "Buy groceries and milk"

# Delete a task
python -m todo delete 1
```

### Interactive Mode

```bash
# Start interactive REPL
python -m todo

# Example session:
todo> add "Buy groceries" --desc "Milk, eggs"
[OK] Task added: [1] Buy groceries
todo> add "Call mom"
[OK] Task added: [2] Call mom
todo> list
Task List
----------------------------------------
[ ] 1. Buy groceries
    Description: Milk, eggs
    Created: 2025-12-30 10:00:00

[ ] 2. Call mom
    Created: 2025-12-30 10:01:00
----------------------------------------
Total: 2 tasks (0 completed, 2 pending)
todo> complete 1
[OK] Task [1] marked as completed
todo> exit
Goodbye!
```

## Project Structure

```
phase-1/
├── src/
│   └── todo/
│       ├── __init__.py          # Package version
│       ├── __main__.py          # Entry point
│       ├── cli.py               # CLI interface
│       ├── exceptions.py        # Custom exceptions
│       ├── manager.py           # TaskManager class
│       └── models.py            # Task dataclass
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures
│   ├── test_cli.py              # CLI tests
│   ├── test_manager.py          # TaskManager tests
│   └── test_models.py           # Task model tests
├── pyproject.toml               # Project configuration
└── README.md                    # This file
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/todo

# Run specific test file
pytest tests/test_manager.py
```

## Requirements

- Python 3.13+
- pytest (for testing)

## Data Storage

**Note**: This is Phase 1 - all data is stored in memory only. Tasks will be lost when the application exits. Future phases will add persistence.

## License

MIT
