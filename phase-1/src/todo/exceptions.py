"""Custom exceptions for the todo application."""


class TodoError(Exception):
    """Base exception for todo application errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ValidationError(TodoError):
    """Base exception for validation errors."""


class EmptyTitleError(ValidationError):
    """Raised when task title is empty."""

    def __init__(self):
        super().__init__("Task title cannot be empty")


class TitleTooLongError(ValidationError):
    """Raised when task title exceeds 200 characters."""

    def __init__(self, length: int):
        super().__init__(f"Task title must be 200 characters or less (got {length})")


class DescriptionTooLongError(ValidationError):
    """Raised when task description exceeds 1000 characters."""

    def __init__(self, length: int):
        super().__init__(f"Task description must be 1000 characters or less (got {length})")


class TaskNotFoundError(TodoError):
    """Raised when a task is not found."""

    def __init__(self, task_id: int):
        super().__init__(f"Task with ID {task_id} not found")


class InvalidIdError(TodoError):
    """Raised when an invalid task ID is provided."""

    def __init__(self):
        super().__init__("Please provide a valid task ID (number)")
