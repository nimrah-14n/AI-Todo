"""Unit tests for TaskManager - all user stories."""

import pytest

from todo.exceptions import (
    DescriptionTooLongError,
    EmptyTitleError,
    TaskNotFoundError,
    TitleTooLongError,
)
from todo.manager import TaskManager, validate_description, validate_title


class TestValidateTitle:
    """Tests for title validation."""

    def test_valid_title(self):
        """Test that valid titles pass validation."""
        validate_title("Valid title")
        validate_title("A")
        validate_title("x" * 200)

    def test_empty_title_raises_error(self):
        """Test that empty title raises EmptyTitleError."""
        with pytest.raises(EmptyTitleError):
            validate_title("")
        with pytest.raises(EmptyTitleError):
            validate_title("   ")
        with pytest.raises(EmptyTitleError):
            validate_title("\t\n")

    def test_title_too_long_raises_error(self):
        """Test that title over 200 chars raises TitleTooLongError."""
        with pytest.raises(TitleTooLongError):
            validate_title("x" * 201)


class TestValidateDescription:
    """Tests for description validation."""

    def test_valid_description(self):
        """Test that valid descriptions pass validation."""
        validate_description("")
        validate_description("A" * 1000)

    def test_description_too_long_raises_error(self):
        """Test that description over 1000 chars raises DescriptionTooLongError."""
        with pytest.raises(DescriptionTooLongError):
            validate_description("x" * 1001)


# ============ User Story 1: Add Task ============

class TestAddTask:
    """Tests for User Story 1 - Add Task."""

    def test_add_task_with_title_only(self, task_manager):
        """Test adding a task with title only."""
        task = task_manager.add_task("Buy groceries")
        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == ""
        assert task.completed is False

    def test_add_task_with_description(self, task_manager):
        """Test adding a task with title and description."""
        task = task_manager.add_task("Call mom", "Wish her happy birthday")
        assert task.id == 1
        assert task.title == "Call mom"
        assert task.description == "Wish her happy birthday"

    def test_add_task_empty_title_raises_error(self, task_manager):
        """Test that adding task with empty title raises error."""
        with pytest.raises(EmptyTitleError):
            task_manager.add_task("")

    def test_add_task_title_too_long_raises_error(self, task_manager):
        """Test that adding task with long title raises error."""
        long_title = "x" * 201
        with pytest.raises(TitleTooLongError):
            task_manager.add_task(long_title)

    def test_add_task_generates_unique_sequential_ids(self, task_manager):
        """Test that each task gets a unique sequential ID."""
        task1 = task_manager.add_task("Task 1")
        task2 = task_manager.add_task("Task 2")
        task3 = task_manager.add_task("Task 3")
        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3
        assert task1.id != task2.id
        assert task2.id != task3.id

    def test_add_task_strips_whitespace(self, task_manager):
        """Test that whitespace is stripped from title and description."""
        task = task_manager.add_task("  Buy groceries  ", "  Milk, eggs  ")
        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs"


# ============ User Story 2: View Tasks ============

class TestGetTasks:
    """Tests for User Story 2 - View Tasks."""

    def test_get_all_tasks_returns_list(self, task_manager):
        """Test getting all tasks returns a list."""
        task_manager.add_task("Task 1")
        task_manager.add_task("Task 2")
        tasks = task_manager.get_all_tasks()
        assert isinstance(tasks, list)
        assert len(tasks) == 2

    def test_get_all_tasks_empty_list(self, task_manager):
        """Test that getting all tasks on empty manager returns empty list."""
        tasks = task_manager.get_all_tasks()
        assert tasks == []

    def test_get_all_tasks_sorted_by_id(self, task_manager):
        """Test that tasks are returned sorted by ID."""
        task_manager.add_task("Task 3")
        task_manager.add_task("Task 1")
        task_manager.add_task("Task 2")
        tasks = task_manager.get_all_tasks()
        assert tasks[0].id == 1
        assert tasks[1].id == 2
        assert tasks[2].id == 3

    def test_get_pending_tasks(self, task_manager):
        """Test getting only pending tasks."""
        task_manager.add_task("Task 1")  # pending
        task_manager.add_task("Task 2")  # pending
        task_manager.add_task("Task 3")
        task_manager.toggle_complete(3)  # mark as complete
        pending = task_manager.get_pending_tasks()
        assert len(pending) == 2
        assert all(not task.completed for task in pending)

    def test_get_completed_tasks(self, task_manager):
        """Test getting only completed tasks."""
        task_manager.add_task("Task 1")
        task_manager.add_task("Task 2")
        task_manager.add_task("Task 3")
        task_manager.toggle_complete(1)
        task_manager.toggle_complete(3)
        completed = task_manager.get_completed_tasks()
        assert len(completed) == 2
        assert all(task.completed for task in completed)

    def test_task_count(self, task_manager):
        """Test task count returns correct statistics."""
        task_manager.add_task("Task 1")  # pending
        task_manager.add_task("Task 2")
        task_manager.add_task("Task 3")
        task_manager.toggle_complete(2)
        count = task_manager.task_count()
        assert count["total"] == 3
        assert count["completed"] == 1
        assert count["pending"] == 2

    def test_get_task_by_id(self, task_manager):
        """Test getting a specific task by ID."""
        task_manager.add_task("Task 1")
        task = task_manager.add_task("Task 2")
        found = task_manager.get_task(2)
        assert found.id == 2
        assert found.title == "Task 2"


# ============ User Story 3: Complete Task ============

class TestToggleComplete:
    """Tests for User Story 3 - Mark Task Complete."""

    def test_toggle_complete_pending_to_completed(self, task_manager):
        """Test toggling a pending task to completed."""
        task = task_manager.add_task("Task 1")
        assert task.completed is False
        updated = task_manager.toggle_complete(1)
        assert updated.completed is True

    def test_toggle_complete_completed_to_pending(self, task_manager):
        """Test toggling a completed task back to pending."""
        task = task_manager.add_task("Task 1")
        task_manager.toggle_complete(1)
        updated = task_manager.toggle_complete(1)
        assert updated.completed is False

    def test_toggle_complete_task_not_found(self, task_manager):
        """Test that toggling non-existent task raises error."""
        with pytest.raises(TaskNotFoundError):
            task_manager.toggle_complete(999)


# ============ User Story 4: Update Task ============

class TestUpdateTask:
    """Tests for User Story 4 - Update Task Details."""

    def test_update_task_title(self, task_manager):
        """Test updating task title."""
        task_manager.add_task("Old title")
        updated = task_manager.update_task(1, title="New title")
        assert updated.title == "New title"

    def test_update_task_description(self, task_manager):
        """Test updating task description."""
        task_manager.add_task("Task", "Old description")
        updated = task_manager.update_task(1, description="New description")
        assert updated.description == "New description"

    def test_update_task_both_fields(self, task_manager):
        """Test updating both title and description."""
        task_manager.add_task("Old title", "Old description")
        updated = task_manager.update_task(
            1, title="New title", description="New description"
        )
        assert updated.title == "New title"
        assert updated.description == "New description"

    def test_update_task_not_found(self, task_manager):
        """Test that updating non-existent task raises error."""
        with pytest.raises(TaskNotFoundError):
            task_manager.update_task(999, title="New title")

    def test_update_task_empty_title_raises_error(self, task_manager):
        """Test that updating with empty title raises error."""
        task_manager.add_task("Task")
        with pytest.raises(EmptyTitleError):
            task_manager.update_task(1, title="")

    def test_update_task_partial(self, task_manager):
        """Test that updating one field doesn't change the other."""
        task_manager.add_task("Title", "Description")
        task_manager.update_task(1, description="New description")
        task = task_manager.get_task(1)
        assert task.title == "Title"
        assert task.description == "New description"


# ============ User Story 5: Delete Task ============

class TestDeleteTask:
    """Tests for User Story 5 - Delete Task."""

    def test_delete_task_success(self, task_manager):
        """Test deleting a task removes it from the list."""
        task_manager.add_task("Task 1")
        task_manager.add_task("Task 2")
        task_manager.delete_task(1)
        tasks = task_manager.get_all_tasks()
        assert len(tasks) == 1
        assert tasks[0].id == 2

    def test_delete_task_not_found(self, task_manager):
        """Test that deleting non-existent task raises error."""
        with pytest.raises(TaskNotFoundError):
            task_manager.delete_task(999)

    def test_delete_task_id_not_reused(self, task_manager):
        """Test that deleted task IDs are not reused."""
        task_manager.add_task("Task 1")
        task_manager.add_task("Task 2")
        task_manager.delete_task(1)
        new_task = task_manager.add_task("Task 3")
        assert new_task.id == 3  # Should be 3, not 1

    def test_delete_task_after_complete(self, task_manager):
        """Test that completed tasks can be deleted."""
        task = task_manager.add_task("Task")
        task_manager.toggle_complete(1)
        task_manager.delete_task(1)
        tasks = task_manager.get_all_tasks()
        assert len(tasks) == 0
