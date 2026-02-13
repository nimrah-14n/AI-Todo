# Quickstart Guide: Phase 1 - Todo Console Application

**Feature**: phase1-console
**Date**: 2025-12-29

---

## Prerequisites

Before starting, ensure you have:

| Requirement | Version | Check Command |
|-------------|---------|---------------|
| Python | 3.13+ | `python --version` |
| UV | Latest | `uv --version` |

### Installing Prerequisites

**Python 3.13+**:
- Download from [python.org](https://www.python.org/downloads/)
- Or use pyenv: `pyenv install 3.13.0`

**UV Package Manager**:
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

---

## Quick Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd hackathon-todo
```

### 2. Create Virtual Environment

```bash
# Using UV (recommended)
uv venv

# Activate the environment
# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install all dependencies
uv pip install -e .

# Or install dev dependencies too
uv pip install -e ".[dev]"
```

### 4. Run the Application

```bash
# Interactive mode
python -m todo

# Or single command mode
python -m todo add "My first task"
```

---

## Project Structure

```
hackathon-todo/
├── src/
│   └── todo/
│       ├── __init__.py      # Package init
│       ├── __main__.py      # Entry point
│       ├── models.py        # Task dataclass
│       ├── manager.py       # TaskManager logic
│       ├── cli.py           # CLI interface
│       └── exceptions.py    # Custom exceptions
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_manager.py
│   └── test_cli.py
├── specs/                   # Specifications
├── pyproject.toml          # Project config
├── CLAUDE.md               # Agent instructions
└── README.md               # Documentation
```

---

## Basic Usage

### Start Interactive Mode

```bash
$ python -m todo

Todo App v1.0.0
Type 'help' for available commands, 'exit' to quit.

Todo> _
```

### Add a Task

```bash
Todo> add "Buy groceries"
✓ Task added: [1] Buy groceries

Todo> add "Call mom" --desc "Wish her happy birthday"
✓ Task added: [2] Call mom
```

### View Tasks

```bash
Todo> list

Task List:
─────────────────────────────────────────
[ ] 1. Buy groceries
    Created: 2025-12-29 10:30:00

[ ] 2. Call mom
    Description: Wish her happy birthday
    Created: 2025-12-29 10:31:00
─────────────────────────────────────────
Total: 2 tasks (0 completed, 2 pending)
```

### Complete a Task

```bash
Todo> complete 1
✓ Task [1] marked as completed: Buy groceries
```

### Update a Task

```bash
Todo> update 2 --title "Call parents" --desc "Sunday dinner plans"
✓ Task [2] updated: Call parents
```

### Delete a Task

```bash
Todo> delete 1
✓ Task [1] deleted: Buy groceries
```

### Exit

```bash
Todo> exit
Goodbye!
```

---

## Single Command Mode

You can also run commands directly without entering interactive mode:

```bash
# Add a task
python -m todo add "Review PR"

# List all tasks
python -m todo list

# List only pending
python -m todo list --pending

# Complete a task
python -m todo complete 1

# Update a task
python -m todo update 1 --title "New title"

# Delete a task
python -m todo delete 1
```

---

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/todo --cov-report=html

# Run specific test file
pytest tests/test_manager.py

# Run with verbose output
pytest -v
```

---

## Development Commands

### Code Formatting

```bash
# Format code
ruff format src/ tests/

# Check formatting
ruff format --check src/ tests/
```

### Linting

```bash
# Run linter
ruff check src/ tests/

# Auto-fix issues
ruff check --fix src/ tests/
```

### Type Checking

```bash
# Run mypy
mypy src/
```

---

## Configuration Files

### pyproject.toml

```toml
[project]
name = "todo"
version = "1.0.0"
description = "A simple todo console application"
requires-python = ">=3.13"
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=4.0",
    "ruff>=0.1",
    "mypy>=1.0",
]

[project.scripts]
todo = "todo.__main__:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]

[tool.ruff]
line-length = 100
target-version = "py313"

[tool.mypy]
python_version = "3.13"
strict = true
```

---

## Troubleshooting

### Python version mismatch

```bash
# Check Python version
python --version

# Use specific Python version
python3.13 -m todo
```

### Module not found

```bash
# Ensure you're in the project root
cd hackathon-todo

# Reinstall in development mode
uv pip install -e .
```

### UV not found

```bash
# Reinstall UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or add to PATH
export PATH="$HOME/.cargo/bin:$PATH"
```

---

## Next Steps

1. Review the [Specification](./spec.md) for detailed requirements
2. Check [Data Model](./data-model.md) for entity definitions
3. Read [CLI Contract](./contracts/cli-interface.md) for interface details
4. Run `/sp.tasks` to generate implementation tasks

---

## Getting Help

```bash
# In-app help
Todo> help

# Command-specific help
Todo> help add

# Version info
python -m todo --version
```
