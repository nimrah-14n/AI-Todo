"""Unit tests for Task model."""

from datetime import datetime

import pytest

from todo.models import Task


class TestTaskCreation:
    """Tests for Task instantiation."""

    def test_create_task_with_required_fields(self):
        """Test creating a task with only required fields."""
        task = Task(id=1, title="Test task")
        assert task.id == 1
        assert task.title == "Test task"
        assert task.description == ""
        assert task.completed is False
        assert isinstance(task.created_at, datetime)

    def test_create_task_with_all_fields(self):
        """Test creating a task with all fields."""
        created = datetime.now()
        task = Task(
            id=1,
            title="Test task",
            description="Test description",
            completed=True,
            created_at=created,
        )
        assert task.id == 1
        assert task.title == "Test task"
        assert task.description == "Test description"
        assert task.completed is True
        assert task.created_at == created

    def test_create_task_defaults(self):
        """Test that default values are applied correctly."""
        task = Task(id=1, title="Test task")
        assert task.description == ""
        assert task.completed is False
        assert task.created_at is not None


class TestTaskToDict:
    """Tests for Task.to_dict() method."""

    def test_to_dict_returns_dict(self):
        """Test that to_dict returns a dictionary."""
        task = Task(id=1, title="Test task", description="Description")
        result = task.to_dict()
        assert isinstance(result, dict)

    def test_to_dict_contains_all_fields(self):
        """Test that to_dict contains all task fields."""
        created = datetime.now()
        task = Task(
            id=1,
            title="Test task",
            description="Test description",
            completed=True,
            created_at=created,
        )
        result = task.to_dict()
        assert result["id"] == 1
        assert result["title"] == "Test task"
        assert result["description"] == "Test description"
        assert result["completed"] is True
        assert result["created_at"] == created.isoformat()

    def test_to_dict_serializes_datetime(self):
        """Test that datetime is serialized to ISO format."""
        task = Task(id=1, title="Test task")
        result = task.to_dict()
        assert result["created_at"] == task.created_at.isoformat()
