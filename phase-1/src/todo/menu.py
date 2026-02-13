"""Interactive menu interface for the todo application."""

import sys

from .cli import format_error, format_task_list, format_success
from .exceptions import TodoError
from .manager import TaskManager


def display_header(task_count: int) -> None:
    """Display the application header with task count."""
    print("==============================================")
    print("TODO APPLICATION - PHASE I")
    print("==============================================")
    print(f"Current tasks: {task_count}")
    print()


def display_menu() -> None:
    """Display the menu options."""
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Mark Task Complete")
    print("6. Exit")
    print()


def get_user_choice() -> str:
    """Get and validate user input."""
    return input("Select an option (1-6): ").strip()


def handle_add_task(manager: TaskManager) -> None:
    """Handle adding a new task."""
    title = input("Enter task title: ").strip()
    if not title:
        print(format_error("Task title cannot be empty."))
        return

    description = input("Enter task description (optional): ").strip()

    try:
        task = manager.add_task(title, description)
        print(format_success(f"Task added: [{task.id}] {task.title}"))
    except TodoError as e:
        print(format_error(e.message))


def handle_view_tasks(manager: TaskManager) -> None:
    """Handle viewing all tasks."""
    tasks = manager.get_all_tasks()
    print(format_task_list(tasks, "All Tasks"))
    input("\nPress Enter to continue...")


def handle_update_task(manager: TaskManager) -> None:
    """Handle updating a task."""
    try:
        task_id = int(input("Enter task ID to update: ").strip())
    except ValueError:
        print(format_error("Invalid task ID. Please enter a number."))
        return

    try:
        task = manager.get_task(task_id)
        print(f"Current: {task.title}")
        if task.description:
            print(f"Description: {task.description}")

        new_title = input("Enter new title (leave empty to keep current): ").strip()
        new_desc = input("Enter new description (leave empty to keep current): ").strip()

        # Only update if new values are provided
        title_to_use = new_title if new_title else None
        desc_to_use = new_desc if new_desc else None

        if title_to_use is None and desc_to_use is None:
            print("No changes made.")
            return

        updated_task = manager.update_task(task_id, title_to_use, desc_to_use)
        print(format_success(f"Task [{updated_task.id}] updated"))
    except TodoError as e:
        print(format_error(e.message))


def handle_delete_task(manager: TaskManager) -> None:
    """Handle deleting a task."""
    try:
        task_id = int(input("Enter task ID to delete: ").strip())
    except ValueError:
        print(format_error("Invalid task ID. Please enter a number."))
        return

    try:
        task = manager.get_task(task_id)
        confirm = input(f"Delete task '{task.title}'? (y/n): ").strip().lower()
        if confirm == "y":
            manager.delete_task(task_id)
            print(format_success(f"Task [{task_id}] deleted"))
        else:
            print("Delete cancelled.")
    except TodoError as e:
        print(format_error(e.message))


def handle_mark_complete(manager: TaskManager) -> None:
    """Handle marking a task as complete."""
    try:
        task_id = int(input("Enter task ID to mark complete/pending: ").strip())
    except ValueError:
        print(format_error("Invalid task ID. Please enter a number."))
        return

    try:
        task = manager.toggle_complete(task_id)
        status = "completed" if task.completed else "pending"
        print(format_success(f"Task [{task.id}] marked as {status}"))
    except TodoError as e:
        print(format_error(e.message))


def run_menu(manager: TaskManager) -> None:
    """Run the interactive menu loop."""
    while True:
        # Display header with current task count
        task_count = manager.task_count()["total"]
        display_header(task_count)
        display_menu()

        choice = get_user_choice()
        print()  # Add spacing after input

        if choice == "1":
            handle_add_task(manager)
        elif choice == "2":
            handle_view_tasks(manager)
        elif choice == "3":
            handle_update_task(manager)
        elif choice == "4":
            handle_delete_task(manager)
        elif choice == "5":
            handle_mark_complete(manager)
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print(format_error("Invalid option. Please select 1-6."))

        print()  # Add spacing before next iteration
