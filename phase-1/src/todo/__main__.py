"""Entry point for the todo application."""

import sys

from .cli import (
    create_parser,
    handle_command,
)
from .manager import TaskManager
from .menu import run_menu


def run_interactive(manager: TaskManager) -> None:
    """Run the interactive menu mode."""
    run_menu(manager)


def run_repl(manager: TaskManager) -> None:
    """Run the legacy REPL mode (command-based)."""
    print("Todo Application")
    print("Type 'help' for available commands, 'exit' to quit.")
    print()

    while True:
        try:
            cmd_input = input("todo> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            break

        if not cmd_input:
            continue

        parts = cmd_input.split()
        cmd = parts[0].lower()

        if cmd in ("exit", "quit", "q"):
            print("Goodbye!")
            break
        elif cmd in ("help", "h", "?"):
            print_help()
            continue

        # Parse the command
        parser = create_parser()
        try:
            args = parser.parse_args(parts)
        except SystemExit:
            continue

        handle_command(args, manager)


def print_help() -> None:
    """Print help message for interactive mode."""
    print("""
Available commands:
  add <title> [--desc <description>]  Add a new task
  list [--all|--pending|--completed]  List tasks (default: all)
  complete <task_id>                  Toggle task completion
  update <task_id> [--title <title>] [--desc <description>]  Update task
  delete <task_id>                    Delete a task
  help                                Show this help message
  exit                                Exit the application

Examples:
  todo> add "Buy groceries" --desc "Milk, eggs, bread"
  todo> list
  todo> complete 1
  todo> update 1 --title "Buy groceries and milk"
  todo> delete 1
""")


def main() -> None:
    """Main entry point."""
    import sys

    # Check if any arguments were provided
    if len(sys.argv) == 1:
        # No arguments - run interactive menu mode
        manager = TaskManager()
        run_interactive(manager)
        return

    # Check for --help or -h
    if "--help" in sys.argv or "-h" in sys.argv:
        show_full_help()
        return

    # Check for --repl flag (legacy mode)
    if "--repl" in sys.argv:
        sys.argv.remove("--repl")
        manager = TaskManager()
        run_repl(manager)
        return

    # Run single command mode using the full CLI parser
    manager = TaskManager()
    parser = create_parser()
    args = parser.parse_args(sys.argv[1:])
    handle_command(args, manager)


def show_full_help() -> None:
    """Show full help message."""
    print("""Todo Application

Usage: todo <command> [arguments]

Commands:
  add <title> [--desc <description>]  Add a new task
  list [--all|--pending|--completed]  List tasks (default: all)
  complete <task_id>                  Toggle task completion
  update <task_id> [--title <title>] [--desc <description>]  Update task
  delete <task_id>                    Delete a task
  help                                Show this help message

Options:
  -h, --help                          Show this help message
  --repl                              Use legacy REPL mode (command-based)

For interactive mode, run: todo
""")


def show_welcome_help() -> None:
    """Show welcome message and hint about interactive mode."""
    print("Todo Application - A simple command-line todo app")
    print()
    print("Usage: todo <command> [arguments]")
    print("       todo           (starts interactive mode)")
    print()
    print("Run 'todo --help' for full usage information.")


if __name__ == "__main__":
    main()
