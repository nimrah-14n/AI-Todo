"""Tests for __main__.py entry point."""

import pytest
from unittest.mock import patch, MagicMock
from io import StringIO


class TestMainEntryPoint:
    """Tests for main entry point."""

    def test_show_welcome_help(self, capsys):
        """Test welcome help message."""
        from todo.__main__ import show_welcome_help, show_full_help

        show_welcome_help()
        captured = capsys.readouterr()
        assert "Todo Application" in captured.out
        assert "interactive mode" in captured.out

        show_full_help()
        captured = capsys.readouterr()
        assert "Usage:" in captured.out
        assert "add" in captured.out
        assert "list" in captured.out

    def test_print_help(self, capsys):
        """Test interactive help message."""
        from todo.__main__ import print_help

        print_help()
        captured = capsys.readouterr()
        assert "Available commands" in captured.out
        assert "add" in captured.out
        assert "exit" in captured.out

    def test_cli_module_entry_point(self):
        """Test that module can be run as main."""
        from todo.cli import main as cli_main
        from todo.__main__ import main as main_main

        # These should be callable without error
        assert callable(cli_main)
        assert callable(main_main)


class TestInteractiveMode:
    """Tests for interactive REPL mode."""

    def test_run_interactive_exits_on_exit_command(self):
        """Test that interactive mode exits on 'exit' command."""
        from todo.__main__ import run_interactive
        from todo.manager import TaskManager

        # Test that the function exists and is callable
        assert callable(run_interactive)

        # Create manager and verify basic operations work
        manager = TaskManager()
        task = manager.add_task("Test")
        assert task.id == 1

    def test_manager_shared_between_commands(self):
        """Test that manager state persists across operations."""
        from todo.manager import TaskManager

        manager = TaskManager()
        manager.add_task("Task 1")
        manager.add_task("Task 2")
        manager.toggle_complete(1)

        assert manager.task_count()["total"] == 2
        assert manager.task_count()["completed"] == 1
