"""CLI integration tests."""

import pytest
from io import StringIO
import sys

from todo.cli import (
    create_parser,
    format_task,
    format_task_list,
    format_success,
    format_error,
    handle_command,
)
from todo.manager import TaskManager
from todo.models import Task
from datetime import datetime


class TestParser:
    """Tests for argument parser."""

    def test_add_command_parsing(self):
        """Test parsing add command."""
        parser = create_parser()
        args = parser.parse_args(["add", "Buy groceries"])
        assert args.command == "add"
        assert args.title == "Buy groceries"
        assert args.desc == ""

    def test_add_command_with_description(self):
        """Test parsing add command with description."""
        parser = create_parser()
        args = parser.parse_args(["add", "Buy groceries", "--desc", "Milk, eggs"])
        assert args.command == "add"
        assert args.title == "Buy groceries"
        assert args.desc == "Milk, eggs"

    def test_list_command_parsing(self):
        """Test parsing list command."""
        parser = create_parser()
        args = parser.parse_args(["list"])
        assert args.command == "list"
        assert args.all is False
        assert args.pending is False
        assert args.completed is False

    def test_list_all_flag(self):
        """Test parsing list --all flag."""
        parser = create_parser()
        args = parser.parse_args(["list", "--all"])
        assert args.all is True

    def test_list_pending_flag(self):
        """Test parsing list --pending flag."""
        parser = create_parser()
        args = parser.parse_args(["list", "--pending"])
        assert args.pending is True

    def test_list_completed_flag(self):
        """Test parsing list --completed flag."""
        parser = create_parser()
        args = parser.parse_args(["list", "--completed"])
        assert args.completed is True

    def test_complete_command_parsing(self):
        """Test parsing complete command."""
        parser = create_parser()
        args = parser.parse_args(["complete", "1"])
        assert args.command == "complete"
        assert args.task_id == 1

    def test_update_command_parsing(self):
        """Test parsing update command."""
        parser = create_parser()
        args = parser.parse_args(["update", "1", "--title", "New title"])
        assert args.command == "update"
        assert args.task_id == 1
        assert args.title == "New title"

    def test_update_command_with_desc(self):
        """Test parsing update command with description."""
        parser = create_parser()
        args = parser.parse_args(["update", "1", "--desc", "New description"])
        assert args.command == "update"
        assert args.task_id == 1
        assert args.desc == "New description"

    def test_delete_command_parsing(self):
        """Test parsing delete command."""
        parser = create_parser()
        args = parser.parse_args(["delete", "1"])
        assert args.command == "delete"
        assert args.task_id == 1


class TestFormatting:
    """Tests for output formatting."""

    def test_format_task_pending(self):
        """Test formatting a pending task."""
        task = Task(
            id=1,
            title="Buy groceries",
            description="Milk, eggs",
            completed=False,
            created_at=datetime(2025, 12, 29, 10, 30, 0),
        )
        result = format_task(task)
        assert "[PENDING] 1. Buy groceries" in result
        assert "Description: Milk, eggs" in result
        assert "Created: 2025-12-29 10:30:00" in result

    def test_format_task_completed(self):
        """Test formatting a completed task."""
        task = Task(
            id=1,
            title="Buy groceries",
            completed=True,
            created_at=datetime(2025, 12, 29, 10, 30, 0),
        )
        result = format_task(task)
        assert "[DONE] 1. Buy groceries" in result

    def test_format_task_without_description(self):
        """Test formatting a task without description."""
        task = Task(
            id=1,
            title="Buy groceries",
            created_at=datetime(2025, 12, 29, 10, 30, 0),
        )
        result = format_task(task)
        assert "Description:" not in result

    def test_format_task_list_empty(self):
        """Test formatting empty task list."""
        result = format_task_list([], "Empty List")
        assert "No tasks found" in result

    def test_format_task_list_with_tasks(self):
        """Test formatting task list with tasks."""
        tasks = [
            Task(
                id=1,
                title="Task 1",
                completed=False,
                created_at=datetime(2025, 12, 29, 10, 30, 0),
            ),
            Task(
                id=2,
                title="Task 2",
                completed=True,
                created_at=datetime(2025, 12, 29, 10, 31, 0),
            ),
        ]
        result = format_task_list(tasks, "Test List")
        assert "Task 1" in result
        assert "Task 2" in result
        assert "Total: 2 tasks" in result

    def test_format_success(self):
        """Test success message formatting."""
        result = format_success("Task added")
        assert "[OK] Task added" == result

    def test_format_error(self):
        """Test error message formatting."""
        result = format_error("Something went wrong")
        assert "[ERR] Something went wrong" == result


class TestHandleCommand:
    """Tests for command handlers."""

    def test_handle_add_command(self, capsys):
        """Test handling add command."""
        manager = TaskManager()
        parser = create_parser()
        args = parser.parse_args(["add", "Buy groceries"])
        handle_command(args, manager)
        captured = capsys.readouterr()
        assert "[OK] Task added" in captured.out
        assert "[1]" in captured.out
        assert "Buy groceries" in captured.out

    def test_handle_list_command(self, capsys):
        """Test handling list command."""
        manager = TaskManager()
        manager.add_task("Task 1")
        parser = create_parser()
        args = parser.parse_args(["list"])
        handle_command(args, manager)
        captured = capsys.readouterr()
        assert "Task 1" in captured.out

    def test_handle_complete_command(self, capsys):
        """Test handling complete command."""
        manager = TaskManager()
        manager.add_task("Task 1")
        parser = create_parser()
        args = parser.parse_args(["complete", "1"])
        handle_command(args, manager)
        captured = capsys.readouterr()
        assert "[OK]" in captured.out
        assert "completed" in captured.out

    def test_handle_update_command(self, capsys):
        """Test handling update command."""
        manager = TaskManager()
        manager.add_task("Task 1")
        parser = create_parser()
        args = parser.parse_args(["update", "1", "--title", "Updated task"])
        handle_command(args, manager)
        captured = capsys.readouterr()
        assert "[OK]" in captured.out
        assert "updated" in captured.out

    def test_handle_delete_command(self, capsys):
        """Test handling delete command."""
        manager = TaskManager()
        manager.add_task("Task 1")
        parser = create_parser()
        args = parser.parse_args(["delete", "1"])
        handle_command(args, manager)
        captured = capsys.readouterr()
        assert "[OK]" in captured.out
        assert "deleted" in captured.out



class TestCLIIntegration:
    """End-to-end CLI tests."""

    def test_full_workflow(self, capsys):
        """Test a complete workflow: add, list, complete, list, delete."""
        manager = TaskManager()

        # Add tasks
        parser = create_parser()
        args = parser.parse_args(["add", "Buy groceries", "--desc", "Milk, eggs"])
        handle_command(args, manager)

        args = parser.parse_args(["add", "Call mom"])
        handle_command(args, manager)

        # List all
        args = parser.parse_args(["list"])
        handle_command(args, manager)

        # Complete task 1
        args = parser.parse_args(["complete", "1"])
        handle_command(args, manager)

        # List pending
        args = parser.parse_args(["list", "--pending"])
        handle_command(args, manager)

        # Update task 2
        args = parser.parse_args(["update", "2", "--title", "Call mom (birthday)"])
        handle_command(args, manager)

        # Delete task 1
        args = parser.parse_args(["delete", "1"])
        handle_command(args, manager)

        # List all
        args = parser.parse_args(["list"])
        handle_command(args, manager)

        captured = capsys.readouterr()
        assert "Buy groceries" in captured.out
        assert "Call mom" in captured.out
        assert "Call mom (birthday)" in captured.out
        assert "deleted" in captured.out
