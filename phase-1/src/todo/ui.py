"""UI utilities for CLI animations and visual indicators."""

import os
import sys
import time
from typing import Optional


# Professional icons for each command
ICONS = {
    "add": "[ADD]",
    "delete": "[DEL]",
    "update": "[EDIT]",
    "list": "[LIST]",
    "complete": "[DONE]",
    "success": "[OK]",
    "error": "[ERR]",
    "info": "[INFO]",
    "pending": "[PENDING]",
}


def show_loading_dots(
    message: str,
    dots: int = 3,
    interval: float = 0.15,
    iterations: int = 2
) -> None:
    """Show a simple loading animation with dots.

    Args:
        message: The message to display before the dots
        dots: Number of dots in the animation
        interval: Time between dot updates in seconds
        iterations: Number of animation cycles
    """
    # Allow forcing animations via environment variable
    force_anim = os.getenv("TODO_FORCE_ANIMATIONS", "0") == "1"

    # Skip animation if not in interactive terminal (unless forced)
    if not sys.stdout.isatty() and not force_anim:
        print(message)
        return

    for _ in range(iterations):
        for i in range(dots + 1):
            sys.stdout.write(f"\r{message}{'.' * i}{' ' * (dots - i)}")
            sys.stdout.flush()
            time.sleep(interval)

    sys.stdout.write(f"\r{message}\n")
    sys.stdout.flush()


def show_spinner(
    message: str,
    chars: str = "|/-\\",
    interval: float = 0.08,
    duration: float = 0.5
) -> None:
    """Show a simple spinner animation.

    Args:
        message: The message to display before the spinner
        chars: Characters to use for the spinner
        interval: Time between character updates
        duration: Total duration of the animation in seconds
    """
    # Skip animation if not in interactive terminal
    if not sys.stdout.isatty():
        print(message)
        return

    start_time = time.time()
    idx = 0

    while time.time() - start_time < duration:
        sys.stdout.write(f"\r{message} {chars[idx % len(chars)]}")
        sys.stdout.flush()
        time.sleep(interval)
        idx += 1

    sys.stdout.write(f"\r{message} \n")
    sys.stdout.flush()


def print_with_animation(
    message: str,
    prefix: Optional[str] = None,
    animate: bool = True
) -> None:
    """Print a message with optional animation effect.

    Args:
        message: The message to display
        prefix: Optional prefix icon/text
        animate: Whether to use animation
    """
    full_message = f"{prefix} {message}" if prefix else message

    if animate and sys.stdout.isatty():
        # Small delay for effect
        sys.stdout.write(full_message)
        sys.stdout.flush()
        time.sleep(0.05)
        print()
    else:
        print(full_message)


def format_success(message: str, icon: str = ICONS["success"]) -> str:
    """Format a success message with icon.

    Args:
        message: The success message
        icon: Icon to use (default: [OK])

    Returns:
        Formatted message string
    """
    return f"{icon} {message}"


def format_error(message: str, icon: str = ICONS["error"]) -> str:
    """Format an error message with icon.

    Args:
        message: The error message
        icon: Icon to use (default: [ERR])

    Returns:
        Formatted message string
    """
    return f"{icon} {message}"


def format_info(message: str, icon: str = ICONS["info"]) -> str:
    """Format an info message with icon.

    Args:
        message: The info message
        icon: Icon to use (default: [INFO])

    Returns:
        Formatted message string
    """
    return f"{icon} {message}"


def format_command_icon(command: str) -> str:
    """Get the icon for a specific command.

    Args:
        command: Command name (add, delete, update, list, complete)

    Returns:
        Icon string for the command
    """
    return ICONS.get(command, "[CMD]")


def format_task_status(completed: bool) -> str:
    """Format task status with visual indicator.

    Args:
        completed: Whether the task is completed

    Returns:
        Formatted status string
    """
    return ICONS["complete"] if completed else ICONS["pending"]
