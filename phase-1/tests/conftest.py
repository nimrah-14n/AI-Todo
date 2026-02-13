"""Pytest fixtures for todo tests."""

import pytest

from todo.manager import TaskManager
from todo.models import Task


@pytest.fixture
def task_manager():
    """Create a fresh TaskManager instance for each test."""
    return TaskManager()


@pytest.fixture
def sample_task(task_manager):
    """Create a sample task for testing."""
    return task_manager.add_task("Sample task", "Sample description")
