"""CLI interface for the todo application."""

import argparse
import sys

from .exceptions import TodoError
from .manager import TaskManager
from .models import Task
from .ui import (
    format_success,
    format_error,
    format_command_icon,
    format_task_status,
    show_loading_dots,
)


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser with all commands."""
    parser = argparse.ArgumentParser(
        prog="todo",
        description="A simple command-line todo application",
        epilog="Use 'todo <command> --help' for more information on a command.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", help="Task title")
    add_parser.add_argument("--desc", "-d", default="", help="Task description")

    # List command
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_group = list_parser.add_mutually_exclusive_group()
    list_group.add_argument("--all", "-a", action="store_true", help="Show all tasks")
    list_group.add_argument(
        "--pending", "-p", action="store_true", help="Show only pending tasks"
    )
    list_group.add_argument(
        "--completed", "-c", action="store_true", help="Show only completed tasks"
    )

    # Complete command
    complete_parser = subparsers.add_parser(
        "complete", help="Toggle task completion status"
    )
    complete_parser.add_argument("task_id", type=int, help="Task ID to toggle")

    # Update command
    update_parser = subparsers.add_parser("update", help="Update task details")
    update_parser.add_argument("task_id", type=int, help="Task ID to update")
    update_parser.add_argument("--title", "-t", help="New task title")
    update_parser.add_argument("--desc", "-d", help="New task description")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("task_id", type=int, help="Task ID to delete")

    return parser


def format_task(task: Task) -> str:
    """Format a single task for display."""
    status_icon = format_task_status(task.completed)
    lines = [
        f"{status_icon} {task.id}. {task.title}",
    ]
    if task.description:
        lines.append(f"    Description: {task.description}")
    lines.append(f"    Created: {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    return "\n".join(lines)


def format_task_list(tasks: list[Task], title: str = "Task List") -> str:
    """Format a list of tasks for display."""
    if not tasks:
        return f"{title}:\n  No tasks found."

    lines = [title, "-" * 40]
    for task in tasks:
        lines.append(format_task(task))
        lines.append("")  # Empty line between tasks
    lines.append("-" * 40)

    total = len(tasks)
    completed = sum(1 for t in tasks if t.completed)
    pending = total - completed
    lines.append(f"Total: {total} tasks ({completed} completed, {pending} pending)")

    return "\n".join(lines)


def handle_add(args, manager: TaskManager) -> None:
    """Handle the add command."""
    icon = format_command_icon("add")
    show_loading_dots(f"{icon} Adding task")
    try:
        task = manager.add_task(args.title, args.desc)
        print(format_success(f"Task added: [{task.id}] {task.title}"))
    except TodoError as e:
        print(format_error(e.message))
        sys.exit(1)


def handle_list(args, manager: TaskManager) -> None:
    """Handle the list command."""
    if args.all or (not args.pending and not args.completed):
        tasks = manager.get_all_tasks()
        title = "All Tasks"
    elif args.pending:
        tasks = manager.get_pending_tasks()
        title = "Pending Tasks"
    else:
        tasks = manager.get_completed_tasks()
        title = "Completed Tasks"

    print(format_task_list(tasks, title))


def handle_complete(args, manager: TaskManager) -> None:
    """Handle the complete command."""
    icon = format_command_icon("complete")
    show_loading_dots(f"{icon} Updating task status")
    try:
        task = manager.toggle_complete(args.task_id)
        status = "completed" if task.completed else "pending"
        print(format_success(f"Task [{task.id}] marked as {status}"))
    except TodoError as e:
        print(format_error(e.message))
        sys.exit(1)


def handle_update(args, manager: TaskManager) -> None:
    """Handle the update command."""
    icon = format_command_icon("update")
    show_loading_dots(f"{icon} Updating task")
    try:
        task = manager.update_task(args.task_id, args.title, args.desc)
        print(format_success(f"Task [{task.id}] updated"))
    except TodoError as e:
        print(format_error(e.message))
        sys.exit(1)


def handle_delete(args, manager: TaskManager) -> None:
    """Handle the delete command."""
    icon = format_command_icon("delete")
    show_loading_dots(f"{icon} Deleting task")
    try:
        manager.delete_task(args.task_id)
        print(format_success(f"Task [{args.task_id}] deleted"))
    except TodoError as e:
        print(format_error(e.message))
        sys.exit(1)


def handle_command(args, manager: TaskManager) -> None:
    """Route the command to the appropriate handler."""
    commands = {
        "add": handle_add,
        "list": handle_list,
        "complete": handle_complete,
        "update": handle_update,
        "delete": handle_delete,
    }

    if args.command is None:
        print("Error: No command specified. Use 'todo --help' for usage.")
        sys.exit(1)

    handler = commands.get(args.command)
    if handler:
        handler(args, manager)
    else:
        print(f"Error: Unknown command '{args.command}'. Use 'todo --help' for usage.")
        sys.exit(1)


def main():
    """Main CLI entry point for single-command mode."""
    parser = create_parser()
    args = parser.parse_args()

    manager = TaskManager()
    handle_command(args, manager)
